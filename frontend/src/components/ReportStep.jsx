import {
  BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell
} from 'recharts'
import { getReportDownloadUrl } from '../services/api'

function fmtNaira(n) {
  return '₦' + Number(n || 0).toLocaleString('en-NG', { minimumFractionDigits: 2 })
}

function SummaryCard({ label, value, sub }) {
  return (
    <div className="bg-white rounded-xl border border-gray-100 shadow-sm p-5">
      <p className="text-xs text-gray-500 uppercase tracking-wide font-semibold mb-1">{label}</p>
      <p className="text-xl font-bold text-gray-900">{value}</p>
      {sub && <p className="text-xs text-gray-400 mt-1">{sub}</p>}
    </div>
  )
}

export default function ReportStep({ confirmData }) {
  const { computation, report_id } = confirmData
  const downloadUrl = getReportDownloadUrl(report_id)

  const bandData = (computation.band_breakdown || []).map((b, i) => ({
    name: `Band ${i + 1} (${(b.rate * 100).toFixed(0)}%)`,
    tax: b.tax_amount,
    taxable: b.taxable_amount,
  }))

  return (
    <div className="max-w-3xl mx-auto">
      <h2 className="text-2xl font-bold text-gray-800 mb-1">Your Tax Assessment Report</h2>
      <p className="text-gray-500 text-sm mb-6">
        Based on FIRS 2024 Personal Income Tax Act guidelines.
      </p>

      {/* Summary cards 2×2 */}
      <div className="grid grid-cols-2 gap-4 mb-8">
        <SummaryCard
          label="Gross Income"
          value={fmtNaira(computation.gross_income)}
          sub="Total taxable credits"
        />
        <SummaryCard
          label="Total Relief"
          value={fmtNaira(
            (computation.total_cra || 0) +
            (computation.pension_relief || 0) +
            (computation.nhf_relief || 0) +
            (computation.nhis_relief || 0)
          )}
          sub="CRA + Pension + NHF + NHIS"
        />
        <SummaryCard
          label="Taxable Income"
          value={fmtNaira(computation.taxable_income)}
          sub="After all deductions"
        />
        <SummaryCard
          label="Tax Liability"
          value={fmtNaira(computation.tax_liability)}
          sub={`Effective rate: ${Number(computation.effective_rate || 0).toFixed(2)}%`}
        />
      </div>

      {/* Effective rate banner */}
      <div
        className="rounded-xl p-4 mb-8 text-white text-center"
        style={{ backgroundColor: '#008751' }}
      >
        <p className="text-sm font-medium opacity-80">Your Effective Tax Rate</p>
        <p className="text-4xl font-bold mt-1">
          {Number(computation.effective_rate || 0).toFixed(2)}%
        </p>
        <p className="text-xs opacity-70 mt-1">FIRS 2024 — Progressive Rate Schedule</p>
      </div>

      {/* Band breakdown chart */}
      {bandData.length > 0 && (
        <div className="bg-white rounded-xl border border-gray-100 shadow-sm p-5 mb-8">
          <h3 className="text-sm font-bold text-gray-700 mb-4 uppercase tracking-wide">
            Tax Band Breakdown
          </h3>
          <ResponsiveContainer width="100%" height={200}>
            <BarChart data={bandData} margin={{ top: 0, right: 0, bottom: 0, left: 0 }}>
              <XAxis dataKey="name" tick={{ fontSize: 10 }} />
              <YAxis tick={{ fontSize: 10 }} tickFormatter={(v) => '₦' + (v / 1000).toFixed(0) + 'k'} />
              <Tooltip
                formatter={(v) => fmtNaira(v)}
                labelStyle={{ fontSize: 11 }}
                contentStyle={{ fontSize: 11 }}
              />
              <Bar dataKey="tax" name="Tax Amount" radius={[4, 4, 0, 0]}>
                {bandData.map((_, i) => (
                  <Cell key={i} fill="#008751" />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>
      )}

      {/* Download button */}
      <div className="text-center mb-8">
        <a
          href={downloadUrl}
          target="_blank"
          rel="noopener noreferrer"
          className="inline-block px-12 py-4 rounded-xl font-bold text-white text-xl shadow-lg transition-transform hover:scale-105"
          style={{ backgroundColor: '#008751' }}
        >
          ⬇ Download PDF Report
        </a>
        <p className="text-xs text-gray-400 mt-2">
          Opens a professional PDF for submission to tax authorities
        </p>
      </div>

      {/* NDPR privacy notice */}
      <div
        className="rounded-xl p-4 border"
        style={{ backgroundColor: '#e8f5e9', borderColor: '#a5d6a7' }}
      >
        <div className="flex gap-3">
          <span className="text-2xl">🔒</span>
          <div>
            <p className="text-sm font-bold" style={{ color: '#005c38' }}>
              Your Privacy is Protected
            </p>
            <p className="text-xs mt-1" style={{ color: '#2e7d32' }}>
              Your uploaded bank statement has been permanently deleted from our server in
              compliance with the <strong>Nigeria Data Protection Regulation (NDPR)</strong>.
              Only the anonymised transaction records used for tax computation are retained.
            </p>
          </div>
        </div>
      </div>
    </div>
  )
}
