import { useState, useRef } from 'react'
import { uploadDocument, createUser } from '../services/api'

const ACCEPTED = ['.csv', '.xlsx', '.xls', '.pdf']
const MAX_MB = 10

const NIGERIAN_BANKS = [
  'GTBank', 'Access Bank', 'Zenith Bank', 'UBA', 'First Bank',
  'Stanbic IBTC', 'Sterling Bank', 'Polaris Bank', 'FCMB', 'Fidelity Bank',
  'Union Bank', 'Ecobank', 'Keystone Bank', 'Heritage Bank', 'Wema Bank',
  'Kuda Bank', 'OPay', 'PalmPay', 'Moniepoint', 'Carbon',
  'FairMoney', 'Piggyvest', 'Cowrywise', 'Payoneer', 'Wise', 'Other',
]

const NIGERIAN_STATES = [
  'Abia', 'Adamawa', 'Akwa Ibom', 'Anambra', 'Bauchi', 'Bayelsa',
  'Benue', 'Borno', 'Cross River', 'Delta', 'Ebonyi', 'Edo', 'Ekiti',
  'Enugu', 'FCT (Abuja)', 'Gombe', 'Imo', 'Jigawa', 'Kaduna', 'Kano',
  'Katsina', 'Kebbi', 'Kogi', 'Kwara', 'Lagos', 'Nasarawa', 'Niger',
  'Ogun', 'Ondo', 'Osun', 'Oyo', 'Plateau', 'Rivers', 'Sokoto',
  'Taraba', 'Yobe', 'Zamfara',
]

export default function UploadStep({ onUploadComplete }) {
  const [file, setFile] = useState(null)
  const [dragging, setDragging] = useState(false)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [progress, setProgress] = useState(0)
  const fileRef = useRef()

  const [fullName, setFullName] = useState('')
  const [email, setEmail] = useState('')
  const [tin, setTin] = useState('')
  const [bankName, setBankName] = useState('')
  const [stateOfResidence, setStateOfResidence] = useState('')

  function validateFile(f) {
    const ext = '.' + f.name.split('.').pop().toLowerCase()
    if (!ACCEPTED.includes(ext)) return `Unsupported format "${ext}". Allowed: ${ACCEPTED.join(', ')}`
    if (f.size > MAX_MB * 1024 * 1024) return `File exceeds ${MAX_MB}MB limit`
    return null
  }

  function handleFileSelect(f) {
    const err = validateFile(f)
    if (err) { setError(err); return }
    setError('')
    setFile(f)
  }

  function onDrop(e) {
    e.preventDefault()
    setDragging(false)
    const f = e.dataTransfer.files[0]
    if (f) handleFileSelect(f)
  }

  async function handleUpload() {
    if (!file) return
    if (!fullName.trim()) { setError('Please enter your full name.'); return }
    if (!email.trim()) { setError('Please enter your email address.'); return }
    if (!bankName) { setError('Please select your bank or fintech app.'); return }
    if (!stateOfResidence) { setError('Please select your state of residence for correct tax rates.'); return }

    setLoading(true)
    setError('')
    setProgress(10)

    try {
      const user = await createUser({
        email: email.trim(),
        full_name: fullName.trim(),
        tin: tin.trim() || null,
        state_of_residence: stateOfResidence,
      })
      setProgress(30)

      const result = await uploadDocument(file, user.user_id, bankName)
      setProgress(100)

      onUploadComplete({
        ...result,
        user_id: user.user_id,
        bank_name: bankName,
        state_of_residence: stateOfResidence,
      })
    } catch (err) {
      const msg = err.response?.data?.detail || err.message || 'Upload failed'
      setError(typeof msg === 'string' ? msg : JSON.stringify(msg))
    } finally {
      setLoading(false)
    }
  }

  const inputClass = "w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-green-500"

  return (
    <div className="max-w-2xl mx-auto">
      <h2 className="text-2xl font-bold text-gray-800 mb-1">Upload Bank Statement</h2>
      <p className="text-gray-500 text-sm mb-6">
        Your details are used to generate an NDPR-compliant personalised tax report.
      </p>

      {/* User details */}
      <div className="bg-gray-50 border border-gray-200 rounded-xl p-4 mb-6 space-y-3">
        <p className="text-sm font-semibold text-gray-700">Taxpayer Information</p>

        <div className="grid grid-cols-2 gap-3">
          <div>
            <label className="text-xs text-gray-500 mb-1 block">Full Name *</label>
            <input
              type="text"
              placeholder="e.g. Chinedu Udeze"
              value={fullName}
              onChange={e => setFullName(e.target.value)}
              className={inputClass}
            />
          </div>
          <div>
            <label className="text-xs text-gray-500 mb-1 block">Email Address *</label>
            <input
              type="email"
              placeholder="e.g. chinedu@email.com"
              value={email}
              onChange={e => setEmail(e.target.value)}
              className={inputClass}
            />
          </div>
        </div>

        <div className="grid grid-cols-2 gap-3">
          <div>
            <label className="text-xs text-gray-500 mb-1 block">TIN (optional)</label>
            <input
              type="text"
              placeholder="Tax Identification Number"
              value={tin}
              onChange={e => setTin(e.target.value)}
              className={inputClass}
            />
          </div>
          <div>
            <label className="text-xs text-gray-500 mb-1 block">State of Residence *</label>
            <select
              value={stateOfResidence}
              onChange={e => setStateOfResidence(e.target.value)}
              className={inputClass}
            >
              <option value="">— Select State —</option>
              {NIGERIAN_STATES.map(s => (
                <option key={s} value={s}>{s}</option>
              ))}
            </select>
          </div>
        </div>

        <div>
          <label className="text-xs text-gray-500 mb-1 block">Bank / Fintech App *</label>
          <select
            value={bankName}
            onChange={e => setBankName(e.target.value)}
            className={inputClass}
          >
            <option value="">— Select Bank or Fintech —</option>
            {NIGERIAN_BANKS.map(b => (
              <option key={b} value={b}>{b}</option>
            ))}
          </select>
        </div>
      </div>

      {/* Drop zone */}
      <div
        onClick={() => !loading && fileRef.current.click()}
        onDragOver={(e) => { e.preventDefault(); setDragging(true) }}
        onDragLeave={() => setDragging(false)}
        onDrop={onDrop}
        className={`border-2 border-dashed rounded-xl p-10 text-center cursor-pointer transition-colors duration-200 ${
          dragging ? 'border-green-500 bg-green-50'
          : file ? 'border-green-400 bg-green-50'
          : 'border-gray-300 hover:border-green-400 hover:bg-green-50'
        }`}
      >
        <input
          ref={fileRef}
          type="file"
          accept={ACCEPTED.join(',')}
          className="hidden"
          onChange={(e) => e.target.files[0] && handleFileSelect(e.target.files[0])}
        />
        {file ? (
          <div>
            <div className="text-4xl mb-3">📄</div>
            <p className="font-semibold text-gray-800">{file.name}</p>
            <p className="text-sm text-gray-500 mt-1">{(file.size / 1024 / 1024).toFixed(2)} MB</p>
            <button
              onClick={(e) => { e.stopPropagation(); setFile(null); setError('') }}
              className="mt-3 text-sm text-red-500 hover:underline"
            >
              Remove
            </button>
          </div>
        ) : (
          <div>
            <div className="text-5xl mb-4">📂</div>
            <p className="font-semibold text-gray-700 text-lg">Drag & drop your bank statement here</p>
            <p className="text-gray-400 text-sm mt-1">or click to browse</p>
            <div className="flex flex-wrap gap-2 justify-center mt-4">
              {ACCEPTED.map(ext => (
                <span key={ext} className="px-2 py-1 bg-gray-100 text-gray-600 text-xs rounded font-mono">{ext}</span>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* Progress */}
      {loading && (
        <div className="mt-4">
          <div className="flex justify-between text-sm text-gray-600 mb-1">
            <span>Processing…</span><span>{progress}%</span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-2">
            <div className="h-2 rounded-full transition-all duration-700"
              style={{ width: `${progress}%`, backgroundColor: '#008751' }} />
          </div>
          <p className="text-xs text-gray-400 mt-2">Parsing document and classifying transactions…</p>
        </div>
      )}

      {error && (
        <div className="mt-4 p-3 bg-red-50 border border-red-200 rounded-lg text-red-700 text-sm">{error}</div>
      )}

      <div className="mt-4 p-3 bg-blue-50 border border-blue-100 rounded-lg">
        <p className="text-xs text-blue-700">
          <span className="font-semibold">Supported banks:</span>{' '}
          GTBank · Access · Zenith · UBA · First Bank · Kuda · OPay · PalmPay · Moniepoint · Stanbic IBTC · Payoneer · Wise
        </p>
      </div>

      <button
        onClick={handleUpload}
        disabled={!file || loading}
        className="mt-6 w-full py-3 rounded-xl font-semibold text-white text-lg transition-opacity disabled:opacity-40"
        style={{ backgroundColor: '#008751' }}
      >
        {loading ? 'Processing…' : 'Upload & Analyse'}
      </button>
    </div>
  )
}
