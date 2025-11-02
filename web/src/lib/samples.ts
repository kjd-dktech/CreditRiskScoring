export type LoanForm = {
  Total_Amount: number
  Total_Amount_to_Repay: number
  duration: number
  Lender_portion_to_be_repaid: number
  New_versus_Repeat: string
  loan_type: string
}

// Default samples in case public/presets.json isn't available
export const SAMPLES: Record<string, LoanForm> = {
  "Low risk — Type_12": {
    Total_Amount: 2000,
    Total_Amount_to_Repay: 2500,
    duration: 90,
    Lender_portion_to_be_repaid: 2500,
    New_versus_Repeat: "Repeat Loan",
    loan_type: 'Type_12',
  },
  "Low risk — Type_22": {
    Total_Amount: 800,
    Total_Amount_to_Repay: 1200,
    duration: 180,
    Lender_portion_to_be_repaid: 1200,
    New_versus_Repeat: "New Loan",
    loan_type: 'Type_22',
  },
  "Low risk — Type_1": {
    Total_Amount: 1919,
    Total_Amount_to_Repay: 1989,
    duration: 7,
    Lender_portion_to_be_repaid: 597,
    New_versus_Repeat: "Repeat Loan",
    loan_type: 'Type_1',
  },
  "Low risk — Type_3": {
    Total_Amount: 5290.42,
    Total_Amount_to_Repay: 5449.14,
    duration: 7,
    Lender_portion_to_be_repaid: 597,
    New_versus_Repeat: "Repeat Loan",
    loan_type: 'Type_3',
  },
}

// Utility to fetch dynamic presets built from dataset (if shipped)
export type DynamicPreset = { name: string; data: LoanForm }
export async function loadDynamicPresets(baseUrl = ''): Promise<DynamicPreset[] | null> {
  try {
    const res = await fetch(`${baseUrl}/presets.json`, { cache: 'no-store' })
    if (!res.ok) return null
    const json = (await res.json()) as DynamicPreset[]
    if (!Array.isArray(json)) return null
    // quick shape check
    for (const it of json) {
      if (!it || typeof it !== 'object') return null
      if (typeof it.name !== 'string' || typeof it.data !== 'object') return null
    }
    return json
  } catch {
    return null
  }
}
