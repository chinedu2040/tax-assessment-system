function fmtNaira(n) {
  return '₦' + Number(n || 0).toLocaleString('en-NG', { minimumFractionDigits: 2 })
}

function computeLiveSummary(transactions) {
  let grossIncome = 0
  transactions.forEach((t) => {
    if (t.category === 'taxable_income' && t.direction === 'credit') {
      grossIncome += Number(t.amount || 0)
    }
  })
  const craFixed = Math.max(200_000, 0.01 * grossIncome)
  const craPercent = 0.20 * grossIncome
  const totalCRA = craFixed + craPercent
  const pension = 0.08 * grossIncome
  const nhf = 0.025 * grossIncome
  const nhis = 0.05 * grossIncome
  const taxable = Math.max(0, grossIncome - totalCRA - pension - nhf - nhis)

  // Simple band computation
  const bands = [
    [300_000, 0.07],
    [300_000, 0.11],
    [500_000, 0.15],
    [500_000, 0.19],
    [1_600_000, 0.21],
    [Infinity, 0.24],
  ]
  let tax = 0
  let rem = taxable
  for (const [limit, rate] of bands) {
    if (rem <= 0) break
    const chunk = Math.min(rem, limit)
    tax += chunk * rate
    rem -= chunk
  }
  tax = Math.max(tax, 0.01 * grossIncome)

  return { grossIncome, totalCRA, taxable, tax }
}

export default function TaxSummaryCard({ transactions }) {
  const { grossIncome, totalCRA, taxable, tax } = computeLiveSummary(transactions)

  const items = [
    { label: 'Gross Income', value: fmtNaira(grossIncome), highlight: false },
    { label: 'Est. CRA', value: fmtNaira(totalCRA), highlight: false },
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
        * Live estimate based on current categories. Final figure computed after confirmation.
      </p>
    </div>
  )
}
