function fmtNaira(n) {
  return '₦' + Number(n || 0).toLocaleString('en-NG', { minimumFractionDigits: 2 })
}

// NTA 2025 progressive bands (PwC, reviewed 29 May 2026)
const NTA_BANDS = [
  [800_000, 0.00],
  [2_200_000, 0.15],
  [9_000_000, 0.18],
  [13_000_000, 0.21],
  [25_000_000, 0.23],
  [Infinity, 0.25],
]

function computeLiveSummary(transactions, annualRent = 0) {
  let grossIncome = 0
  transactions.forEach((t) => {
    if (t.category === 'taxable_income' && t.direction === 'credit') {
      grossIncome += Number(t.amount || 0)
    }
  })

  // Rent Relief: lower of NGN 500,000 or 20% of annual rent
  const rentRelief = annualRent > 0 ? Math.min(500_000, 0.20 * annualRent) : 0

  // Allowable deductions from classified transactions
  let deductions = 0
  transactions.forEach((t) => {
    if (t.category === 'deductible_expense' && t.direction === 'debit') {
      deductions += Number(t.amount || 0)
    }
  })

  const taxable = Math.max(0, grossIncome - rentRelief - deductions)

  let tax = 0
  let rem = taxable
  for (const [limit, rate] of NTA_BANDS) {
    if (rem <= 0) break
    const chunk = Math.min(rem, limit)
    tax += chunk * rate
    rem -= chunk
  }

  return { grossIncome, rentRelief, deductions, taxable, tax }
}

export default function TaxSummaryCard({ transactions, annualRent = 0 }) {
  const { grossIncome, rentRelief, deductions, taxable, tax } = computeLiveSummary(transactions, annualRent)

  const items = [
    { label: 'Gross Income', value: fmtNaira(grossIncome), highlight: false },
    { label: 'Rent Relief (NTA 2025)', value: rentRelief > 0 ? fmtNaira(rentRelief) : 'Nil', highlight: false },
    { label: 'Est. Taxable Income', value: fmtNaira(taxable), highlight: false },
    { label: 'Est. Tax Liability', value: fmtNaira(tax), highlight: true },
  ]

  return (
    <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-5">
      <h3 className="text-sm font-bold text-gray-700 mb-4 uppercase tracking-wide">
        Live Tax Estimate
      </h3>
      <div className="space-y-3">
        {items.map((item) => (
          <div key={item.label} className="flex justify-between items-center">
            <span className="text-xs text-gray-500">{item.label}</span>
            <span
              className={`text-sm font-semibold ${
                item.highlight ? 'text-white px-2 py-0.5 rounded' : 'text-gray-800'
              }`}
              style={item.highlight ? { backgroundColor: '#008751' } : {}}
            >
              {item.value}
            </span>
          </div>
        ))}
      </div>
      <p className="text-xs text-gray-400 mt-4">
        * Live estimate (NTA 2025). Final figure computed on confirmation.
      </p>
    </div>
  )
}
