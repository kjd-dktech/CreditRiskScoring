export default function About() {
  return (
    <div className="prose prose-invert max-w-none">
      <h1 className="font-bold">À propos</h1>

      <p className="mb-0 mt-2">
        Cette démo évalue le risque de crédit à partir d&apos;un modèle de stacking entrainé, avec un
        pré-traitement normalisé et une interprétabilité via SHAP (Top features).
      </p>
      <ul>
        <li><u>Entrées</u>: montants, durée, type de prêt (Type1..Type24)</li>
        <li><u>Sorties</u>: probabilité de défaut, classe, niveau de risque, confiance</li>
        {/*<li>Explication: importance des variables (valeurs SHAP)</li>*/}
      </ul>
      <p><u>Stack</u>: FastAPI, Next.js, Tailwind, charts Recharts.</p>
          {/* Image mapping loan_type - placed in web/public/loan_type_mapping.png */}
          <div className="mt-6">
            <h2 className="font-semibold">Mapping loan_type</h2>
            <p className="text-sm text-slate-400">Schéma de correspondance des types de prêt (codification utilisée)</p>
            <div className="mt-3">
              <img src="/loan_type_mapping.png" alt="Loan type mapping" className="w-full max-w-2xl rounded border border-slate-700" />
            </div>
          </div>
        </div>
  )
}
