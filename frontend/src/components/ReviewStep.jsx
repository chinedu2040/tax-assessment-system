import { useState } from 'react'
import TransactionTable from './TransactionTable'
import TaxSummaryCard from './TaxSummaryCard'
import { confirmTransactions } from '../services/api'

export default function ReviewStep({ uploadData, onConfirmComplete }) {
  const [transactions, setTransactions] = useState(uploadData.transactions)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  function handleCategoryChange(txnId, newCategory) {
    setTransactions((prev) =>
      prev.map((t) =>
        t.transaction_id === txnId
          ? { ...t, category: newCategory, user_corrected: true, classification_method: 'user_correction' }
          : t
      )
    )
  }

  async function handleConfirm() {
    setLoading(true)
    setError('')
    try {
      const payload = {
        document_id: uploadData.document_id,
        transactions: transactions.map((t) => ({
          transaction_id: t.transaction_id,
          category: t.category,
          sub_category: t.sub_category || null,
          user_corrected: t.user_corrected || false,
        })),
        user_id: uploadData.user_id,
        tax_year: new Date().getFullYear(),
      }
      const result = await confirmTransactions(payload)
      onConfirmComplete(result)
    } catch (err) {
      const msg = err.response?.data?.detail || err.message || 'Confirmation failed'
      setError(typeof msg === 'string' ? msg : JSON.stringify(msg))
    } finally {
      setLoading(false)
    }
  }

  const summary = uploadData.summary || {}
  const needsReview = transactions.filter(
    (t) => t.category === 'needs_review' || t.classification_method === 'flagged'
  ).length

  return (
    <div className="w-full">
      <div className="mb-6">
        <h2 className="text-2xl font-bold text-gray-800 mb-1">Review & Correct Transactions</h2>
        <p className="text-gray-500 text-sm">
          Rows highlighted in <span className="bg-amber-100 px-1 rounded text-amber-700 font-medium">amber</span> need your attention.
          Rows in <span className="bg-blue-100 px-1 rounded text-blue-700 font-medium">blue</span> have been corrected by you.
        </p>
      </div>

      {/* Summary pills */}
      <div className="flex flex-wrap gap-3 mb-6">
        {[
          { label: 'Total', value: summary.total || transactions.length, color: 'bg-gray-100 text-gray-700' },
          { label: 'Taxable Income', value: summary.taxable_income_count, color: 'bg-green-100 text-green-700' },
          { label: 'Deductible', value: summary.deductible_count, color: 'bg-blue-100 text-blue-700' },
          { label: 'Non-Taxable', value: summary.non_taxable_count, color: 'bg-gray-100 text-gray-600' },
          { label: 'Needs Review', value: needsReview, color: 'bg-amber-100 text-amber-700' },
        ].map((s) => (
          <div key={s.label} className={`px-3 py-1.5 rounded-full text-xs font-semibold ${s.color}`}>
            {s.label}: {s.value ?? 0}
          </div>
        ))}
      </div>

      <div className="flex flex-col lg:flex-row gap-6">
        <div className="flex-1 min-w-0">
          <TransactionTable
            transactions={transactions}
            onCategoryChange={handleCategoryChange}
          />
        </div>
        <div className="lg:w-64 flex-shrink-0">
          <div className="sticky top-6">
            <TaxSummaryCard transactions={transactions} />
          </div>
        </div>
      </div>

      {error && (
        <div className="mt-4 p-3 bg-red-50 border border-red-200 rounded-lg text-red-700 text-sm">
          {error}
        </div>
      )}

      <div className="mt-6 flex justify-end">
        <button
          onClick={handleConfirm}
          disabled={loading}
          className="px-8 py-3 rounded-xl font-semibold text-white text-lg transition-opacity disabled:opacity-40"
          style={{ backgroundColor: '#008751' }}
        >
          {loading ? 'Generating Report…' : 'Confirm & Generate Report'}
        </button>
      </div>
    </div>
  )
}
