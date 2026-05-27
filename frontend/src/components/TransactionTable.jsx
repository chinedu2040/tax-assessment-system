const CATEGORIES = ['taxable_income', 'deductible_expense', 'non_taxable', 'needs_review']

const CAT_LABELS = {
  taxable_income: 'Taxable Income',
  deductible_expense: 'Deductible Expense',
  non_taxable: 'Non-Taxable',
  needs_review: 'Needs Review',
}

function fmtNaira(n) {
  return '₦' + Number(n || 0).toLocaleString('en-NG', { minimumFractionDigits: 2 })
}

function rowBg(t) {
  if (t.classification_method === 'flagged' || t.category === 'needs_review') return 'bg-amber-50'
  if (t.user_corrected) return 'bg-blue-50'
  return ''
}

export default function TransactionTable({ transactions, onCategoryChange }) {
  return (
    <div className="overflow-x-auto rounded-xl border border-gray-200">
      <table className="min-w-full text-xs">
        <thead>
          <tr className="text-left text-gray-500 uppercase tracking-wide" style={{ backgroundColor: '#f9fafb' }}>
            <th className="px-3 py-3 font-semibold">Date</th>
            <th className="px-3 py-3 font-semibold">Description</th>
            <th className="px-3 py-3 font-semibold text-right">Amount</th>
            <th className="px-3 py-3 font-semibold">Dir</th>
            <th className="px-3 py-3 font-semibold">Category</th>
            <th className="px-3 py-3 font-semibold">Sub-category</th>
            <th className="px-3 py-3 font-semibold">Method</th>
            <th className="px-3 py-3 font-semibold text-right">Conf</th>
          </tr>
        </thead>
        <tbody className="divide-y divide-gray-100">
          {transactions.map((t) => (
            <tr key={t.transaction_id} className={`${rowBg(t)} hover:bg-gray-50 transition-colors`}>
              <td className="px-3 py-2 whitespace-nowrap text-gray-600">{t.date || '—'}</td>
              <td className="px-3 py-2 max-w-xs">
                <span className="block truncate text-gray-800" title={t.description}>
                  {t.description || '—'}
                </span>
              </td>
              <td className="px-3 py-2 text-right font-mono text-gray-800">
                {fmtNaira(t.amount)}
              </td>
              <td className="px-3 py-2">
                <span
                  className={`inline-block px-1.5 py-0.5 rounded text-xs font-semibold ${
                    t.direction === 'credit'
                      ? 'bg-green-100 text-green-700'
                      : 'bg-red-100 text-red-700'
                  }`}
                >
                  {t.direction === 'credit' ? 'CR' : 'DR'}
                </span>
              </td>
              <td className="px-3 py-2">
                <select
                  value={t.category || ''}
                  onChange={(e) => onCategoryChange(t.transaction_id, e.target.value)}
                  className="border border-gray-200 rounded px-1.5 py-0.5 text-xs bg-white focus:outline-none focus:ring-1 focus:ring-green-400 cursor-pointer"
                >
                  {CATEGORIES.map((c) => (
                    <option key={c} value={c}>{CAT_LABELS[c]}</option>
                  ))}
                </select>
              </td>
              <td className="px-3 py-2 text-gray-500">{t.sub_category || '—'}</td>
              <td className="px-3 py-2">
                <span
                  className={`inline-block px-1.5 py-0.5 rounded text-xs ${
                    t.classification_method === 'rule'
                      ? 'bg-green-100 text-green-700'
                      : t.classification_method === 'nlp'
                      ? 'bg-blue-100 text-blue-700'
                      : t.classification_method === 'flagged'
                      ? 'bg-amber-100 text-amber-700'
                      : 'bg-purple-100 text-purple-700'
                  }`}
                >
                  {t.classification_method || '—'}
                </span>
              </td>
              <td className="px-3 py-2 text-right font-mono text-gray-500">
                {t.confidence_score != null ? Number(t.confidence_score).toFixed(2) : '—'}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}
