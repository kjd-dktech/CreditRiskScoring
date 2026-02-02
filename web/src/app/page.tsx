'use client'
import { useEffect, useState } from 'react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { SAMPLES, loadDynamicPresets, type DynamicPreset } from '@/lib/samples'
import { useToast } from '@/components/ui/toast'
import {
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
  RadialBarChart,
  RadialBar,
  PolarAngleAxis,
} from 'recharts'

type PredictResponse = {
  probability: number
  prediction: number
  risk_level: 'Low' | 'Medium' | 'High'
  confidence: number
}

type ExplainResponse = {
  prediction: number
  probability: number
  base_value: number
  top_features: { feature: string; contribution: number; impact: string }[]
}

export default function Home() {
  const [form, setForm] = useState({
    Total_Amount: 1000,
    Total_Amount_to_Repay: 1200,
    duration: 90,
    Lender_portion_to_be_repaid: 1200,
    New_versus_Repeat: "Repeat Loan",
    loan_type: 'Type_1',
  })
  const [loanTypes, setLoanTypes] = useState<string[]>([])
  const [NewRepeatLoan, setNewRepeatLoan] = useState<string[]>([])
  const [loading, setLoading] = useState(false)
  const [pred, setPred] = useState<PredictResponse | null>(null)
  const [explain, setExplain] = useState<ExplainResponse | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [history, setHistory] = useState<any[]>([])
  const [dynPresets, setDynPresets] = useState<DynamicPreset[] | null>(null)
  const [showSci, setShowSci] = useState(false)
  const { push } = useToast()
  useEffect(() => {
    const loadHistory = async () => {
      // restore history
      try {
        const raw = localStorage.getItem('history')
        if (raw) setHistory(JSON.parse(raw))
      } catch {}
    }
    loadHistory()
  }, [])

  // try to load dynamic presets shipped as public/presets.json
  useEffect(() => {
    let mounted = true
    loadDynamicPresets('')
      .then((p) => { if (mounted) setDynPresets(p) })
      .catch(() => {})
    return () => { mounted = false }
  }, [])

  // persist history
  useEffect(() => {
    try {
      localStorage.setItem('history', JSON.stringify(history))
    } catch {}
  }, [history])

  // reset scientific display on new predictions
  useEffect(() => {
    setShowSci(false)
  }, [pred?.probability])

  const onChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    const { name, value } = e.target
    setForm((s) => {
      if (name === 'loan_type') return { ...s, loan_type: String(value) }
      if (name === 'New_versus_Repeat') return { ...s, New_versus_Repeat: String(value) }
      const n = Number(value)
      if (!Number.isFinite(n)) return s
      if (name === 'duration') {
        const v = Math.max(1, Math.floor(n))
        return { ...s, duration: v }
      }
      const v = Math.max(0, n)
      return { ...s, [name]: v } as any
    })
  }

  const validate = () => {
    const nums = [
      form.Total_Amount,
      form.Total_Amount_to_Repay,
      form.duration,
      form.Lender_portion_to_be_repaid,
    ]
    if (nums.some((n) => n === null || Number.isNaN(n))) return 'Valeurs numériques invalides'
    if (form.Total_Amount <= 0) return 'Total_Amount doit être > 0'
    if (form.Total_Amount_to_Repay < form.Total_Amount) return 'A rembourser doit être ≥ montant total'
    if (!form.loan_type) return 'Type de prêt requis'
    return null
  }

  const submit = async () => {
    setLoading(true)
    setError(null)
    setExplain(null)
    try {
      const v = validate()
      if (v) throw new Error(v)
      const r = await fetch('api/predict', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(form),
      })
      if (!r.ok) throw new Error(`Predict failed: ${r.status}`)
      const data: PredictResponse = await r.json()
      setPred(data)
      setHistory((h) => [{ ts: Date.now(), form, pred: data }, ...h].slice(0, 20))
      push({ type: 'success', title: 'OK', message: 'Prédiction effectuée' })
    } catch (e: any) {
      setError(e.message)
      push({ type: 'error', title: 'Erreur', message: e.message })
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    const loadMeta = async () => {
      try {
        const r = await fetch('api/metadata')
        if (!r.ok) return
        const data = await r.json()
        if (Array.isArray(data?.loan_types) && data.loan_types.length) {
          setLoanTypes(data.loan_types)
          // ensure current selection is valid against metadata
          setForm((s) => ({
            ...s,
            loan_type: data.loan_types.includes(s.loan_type) ? s.loan_type : data.loan_types[0],
          }))
        }
        if (Array.isArray(data?.new_repeat_loan) && data.new_repeat_loan.length) {
          setNewRepeatLoan(data.new_repeat_loan)
          // ensure current selection is valid against metadata
          setForm((s) => ({
            ...s,
            repeat_status: data.new_repeat_loan.includes(s.New_versus_Repeat) ? s.New_versus_Repeat : data.loan_types[0],
          }))
        }
  } catch {}
    }
    loadMeta()
  }, [])

  const explainFn = async () => {
    setLoading(true)
    setError(null)
    try {
      const r = await fetch('api/explain', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json'},
        body: JSON.stringify(form),
      })
      if (!r.ok) throw new Error(`Explain failed: ${r.status}`)
      const data: ExplainResponse = await r.json()
      setExplain(data)
      push({ type: 'info', title: 'Explications', message: 'Top features mises à jour' })
    } catch (e: any) {
      setError(e.message)
      push({ type: 'error', title: 'Erreur', message: e.message })
    } finally {
      setLoading(false)
    }
  }

  return (
    <div>
      <h1 className="text-3xl font-semibold mb-6">Scoring de Crédit : Demo</h1>
  <div className="grid md:grid-cols-2 gap-6 items-start">
        <div className="card p-5">
          <h2 className="text-lg font-medium mb-4">Profile de prêt</h2>
          <div className="space-y-3">
            <div className="flex items-center gap-2">
              <span className="text-sm text-slate-300">Presets</span>
              <select
                className="rounded-md bg-slate-800 border border-slate-700 px-3 py-2 text-sm"
                onChange={(e) => {
                  const val = e.target.value
                  // prefer dynamic presets if available
                  if (val && dynPresets) {
                    const found = dynPresets.find((x) => x.name === val)
                    if (found) return setForm(found.data)
                  }
                  if (val && SAMPLES[val]) setForm(SAMPLES[val])
                }}
              >
                <option value="">Choisir…</option>
                {dynPresets?.map((p) => (
                  <option key={p.name} value={p.name}>{p.name}</option>
                ))}
                {Object.keys(SAMPLES).map((k) => (
                  <option key={k} value={k}>{k}</option>
                ))}
              </select>
            </div>
            {([
              ['Total_Amount', 'Montant total'],
              ['Total_Amount_to_Repay', 'Montant à rembourser'],
              ['duration', 'Durée (jours)'],
              ['Lender_portion_to_be_repaid', 'Part prêteur à rembourser'],
            ] as const).map(([key, label]) => (
              <label key={key} className="block">
                <span className="block text-sm text-slate-300">{label}</span>
                <Input
                  type="number"
                  name={key}
                  value={(form as any)[key]}
                  onChange={onChange}
                  className="mt-1"
                  min={key === 'duration' ? 1 : 0}
                  step={key === 'duration' ? 1 : 0.01}
                />
              </label>
            ))}
            <label className="block">
              <span className="block text-sm text-slate-300">Statut du client</span>
              <select
                name="New_versus_Repeat"
                value={form.New_versus_Repeat}
                onChange={onChange}
                className="mt-1 w-full rounded-md bg-slate-800 border border-slate-700 px-3 py-2 focus:outline-none focus:ring-2 focus:ring-sky-500"
              >
                {(NewRepeatLoan.length ? NewRepeatLoan : [ 
                                                    'New Loan',
                                                    'Repeat Loan'
                                                  ]).map((t) => (
                  <option key={t} value={t}>{t}</option>
                ))}
              </select>
            </label>

            <label className="block">
              <span className="block text-sm text-slate-300">Type de prêt (Détails sur la page "Á propos")</span>
              <select
                name="loan_type"
                value={form.loan_type}
                onChange={onChange}
                className="mt-1 w-full rounded-md bg-slate-800 border border-slate-700 px-3 py-2 focus:outline-none focus:ring-2 focus:ring-sky-500"
              >
                {(loanTypes.length ? loanTypes : [
                                                  'Type_1','Type_2','Type_4','Type_5','Type_6', 'Type_7','Type_9','Type_10',
                                                  'Type_11','Type_12','Type_14','Type_15','Type_16', 'Type_17','Type_19','Type_20',
                                                  'Type_13','Type_21','Type_22'
                                                ]).map((t) => (
                  <option key={t} value={t}>{t}</option>
                ))}
              </select>
            </label>
            <div className="flex gap-3 pt-2">
              <Button onClick={submit} disabled={loading}>{loading ? 'Calcul...' : 'Prédire'}</Button>
              <Button onClick={explainFn} disabled={loading || !pred} variant="secondary">{loading ? 'Analyse...' : 'Expliquer'}</Button>
            </div>
            {error && <p className="text-rose-400">{error}</p>}
          </div>
  </div>
  <div className="space-y-6">
          <div className="card p-5">
            <h2 className="text-lg font-medium mb-4">Résultats</h2>
            {pred ? (
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div className="rounded-md border border-slate-800 p-3">
                  <div className="text-xs text-slate-400 mb-2">Probabilité défaut</div>
                  <div className="h-40">
                    <ResponsiveContainer width="100%" height="100%">
                      <RadialBarChart innerRadius="70%" outerRadius="100%" data={[{ name: 'p', value: Math.round(pred.probability * 100) }]} startAngle={180} endAngle={0}>
                        <PolarAngleAxis type="number" domain={[0, 100]} tick={false} />
                        <RadialBar dataKey="value" cornerRadius={10} fill="#0ea5e9" />
                      </RadialBarChart>
                    </ResponsiveContainer>
                  </div>
                      <div className="flex items-center gap-2 text-xl font-semibold">
                        {(pred.probability * 100).toFixed(1)}%
                        {pred.probability < 0.1 && (
                          <button
                            type="button"
                            onClick={() => setShowSci((s) => !s)}
                            className="text-xs font-normal px-2 py-0.5 rounded border border-slate-600 text-slate-300 hover:bg-slate-700"
                            aria-label="Afficher l'écriture scientifique"
                            title="Afficher l'écriture scientifique"
                          >
                            Sci
                          </button>
                        )}
                      </div>
                      {pred.probability < 0.1 && showSci && (
                        <div className="text-sm text-slate-400 mt-1">p = {pred.probability.toExponential(2)}</div>
                      )}
                </div>
                <div className="grid grid-cols-2 gap-4">
                  <Stat label="Prédiction" value={pred.prediction === 1 ? 'Défaut' : 'OK'} />
                  <Stat label="Risque" value={<RiskBadge level={pred.risk_level} />} />
                  <Stat label="Certitude (modèle)" value={(pred.confidence * 100).toFixed(1) + '%'} />
                </div>
              </div>
            ) : (
              <p className="text-slate-400">Soumettez un profil pour voir les résultats.</p>
            )}
          </div>

          <div className="card p-5">
            <h2 className="text-lg font-medium mb-4">Top Features (SHAP)</h2>
            {explain?.top_features ? (
              <div className="h-64">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={explain.top_features.map((f) => ({ name: f.feature, value: Math.abs(f.contribution), sign: f.contribution }))} layout="vertical" margin={{ left: 50, right: 16, top: 8, bottom: 8 }}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#1f2937" />
                    <XAxis type="number" hide />
                    <YAxis type="category" dataKey="name" tick={{ fill: '#9ca3af', fontSize: 12 }} width={120} />
                    <Tooltip formatter={(value: any, _name: any, p: any) => [`${p.payload.sign.toFixed(4)}`, 'Contribution']} />
                    <Bar dataKey="value" fill="#0ea5e9" />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            ) : (
              <p className="text-slate-400">Cliquez sur "Expliquer" pour voir l'importance des variables.</p>
            )}
          </div>

          {/* Historique sous les résultats */}
          <div className="card p-5">
            <h2 className="text-lg font-medium mb-4">Historique (local)</h2>
            <div className="flex items-center justify-between mb-2">
              <span className="text-sm text-slate-400">Derniers essais</span>
              <Button
                variant="secondary"
                onClick={() => {
                  setHistory([])
                  try { localStorage.removeItem('history') } catch {}
                  push({ type: 'info', title: 'Historique', message: 'Historique vidé' })
                }}
              >
                Vider
              </Button>
            </div>
            {history.length === 0 ? (
              <p className="text-slate-400">Aucun essai enregistré.</p>
            ) : (
              <ul className="space-y-2 max-h-64 overflow-auto">
                {history.map((h, i) => (
                  <li key={i} className="flex items-center justify-between gap-3">
                    <div className="text-sm text-slate-300">
                      <span className="text-slate-400">{new Date(h.ts).toLocaleTimeString()} · </span>
                      {h.form.loan_type} · {(h.pred.probability*100).toFixed(1)}%
                    </div>
                    <Button variant="secondary" onClick={() => setForm(h.form)}>Recharger</Button>
                  </li>
                ))}
              </ul>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}

function Stat({ label, value }: { label: string; value: string | React.ReactNode }) {
  return (
    <div className="rounded-md border border-slate-700 p-3">
      <div className="text-xs text-slate-400">{label}</div>
      <div className="text-xl font-semibold">{value}</div>
    </div>
  )
}

function RiskBadge({ level }: { level: 'Low' | 'Medium' | 'High' }) {
  const color = level === 'High' ? 'bg-rose-500/20 text-rose-200 border-rose-500/40' : level === 'Medium' ? 'bg-amber-500/20 text-amber-200 border-amber-500/40' : 'bg-emerald-500/20 text-emerald-200 border-emerald-500/40'
  return <span className={`inline-flex items-center px-2 py-1 rounded-md border text-sm ${color}`}>{level}</span>
}
