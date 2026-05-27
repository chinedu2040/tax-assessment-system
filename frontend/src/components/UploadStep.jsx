import { useState, useRef } from 'react'
import { uploadDocument, createUser } from '../services/api'

const ACCEPTED = ['.csv', '.xlsx', '.xls', '.pdf']
const MAX_MB = 10

export default function UploadStep({ onUploadComplete }) {
  const [file, setFile] = useState(null)
  const [dragging, setDragging] = useState(false)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [progress, setProgress] = useState(0)
  const fileRef = useRef()

  function validateFile(f) {
    const ext = '.' + f.name.split('.').pop().toLowerCase()
    if (!ACCEPTED.includes(ext)) {
      return `Unsupported format "${ext}". Please upload ${ACCEPTED.join(', ')}`
    }
    if (f.size > MAX_MB * 1024 * 1024) {
      return `File exceeds ${MAX_MB}MB limit`
    }
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
    setLoading(true)
    setError('')
    setProgress(10)

    try {
      // Create or fetch user
      const user = await createUser({
        email: 'freelancer@example.com',
        full_name: 'Nigerian Freelancer',
        tin: null,
      })
      setProgress(30)

      const result = await uploadDocument(file, user.user_id)
      setProgress(100)

      onUploadComplete({ ...result, user_id: user.user_id })
    } catch (err) {
      const msg = err.response?.data?.detail || err.message || 'Upload failed'
      setError(typeof msg === 'string' ? msg : JSON.stringify(msg))
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="max-w-2xl mx-auto">
      <h2 className="text-2xl font-bold text-gray-800 mb-1">Upload Bank Statement</h2>
      <p className="text-gray-500 text-sm mb-6">
        Supports GTBank, Access Bank, Zenith, UBA, Kuda, OPay, PalmPay and more
      </p>

      {/* Drop zone */}
      <div
        onClick={() => !loading && fileRef.current.click()}
        onDragOver={(e) => { e.preventDefault(); setDragging(true) }}
        onDragLeave={() => setDragging(false)}
        onDrop={onDrop}
        className={`border-2 border-dashed rounded-xl p-12 text-center cursor-pointer transition-colors duration-200 ${
          dragging
            ? 'border-green-500 bg-green-50'
            : file
            ? 'border-green-400 bg-green-50'
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
            <p className="text-sm text-gray-500 mt-1">
              {(file.size / 1024 / 1024).toFixed(2)} MB
            </p>
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
            <p className="font-semibold text-gray-700 text-lg">
              Drag & drop your bank statement here
            </p>
            <p className="text-gray-400 text-sm mt-1">or click to browse</p>
            <div className="flex flex-wrap gap-2 justify-center mt-4">
              {ACCEPTED.map((ext) => (
                <span
                  key={ext}
                  className="px-2 py-1 bg-gray-100 text-gray-600 text-xs rounded font-mono"
                >
                  {ext}
                </span>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* Progress bar */}
      {loading && (
        <div className="mt-4">
          <div className="flex justify-between text-sm text-gray-600 mb-1">
            <span>Processing…</span>
            <span>{progress}%</span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-2">
            <div
              className="h-2 rounded-full transition-all duration-700"
              style={{ width: `${progress}%`, backgroundColor: '#008751' }}
            />
          </div>
          <p className="text-xs text-gray-400 mt-2">
            Parsing document and classifying transactions…
          </p>
        </div>
      )}

      {/* Error */}
      {error && (
        <div className="mt-4 p-3 bg-red-50 border border-red-200 rounded-lg text-red-700 text-sm">
          {error}
        </div>
      )}

      {/* Tips */}
      <div className="mt-6 p-4 bg-blue-50 border border-blue-100 rounded-lg">
        <p className="text-sm font-semibold text-blue-800 mb-2">Supported banks &amp; formats</p>
        <p className="text-xs text-blue-700">
          GTBank · Access Bank · Zenith Bank · UBA · First Bank · Kuda · OPay · PalmPay ·
          Sterling Bank · Stanbic IBTC · Payoneer CSV · Wise export
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
