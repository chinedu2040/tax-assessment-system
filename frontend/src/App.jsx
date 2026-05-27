import { useState } from 'react'
import Navbar from './components/Navbar'
import ProgressBar from './components/ProgressBar'
import UploadStep from './components/UploadStep'
import ReviewStep from './components/ReviewStep'
import ReportStep from './components/ReportStep'

export default function App() {
  const [step, setStep] = useState(1)
  const [uploadData, setUploadData] = useState(null)
  const [confirmData, setConfirmData] = useState(null)

  function handleUploadComplete(data) {
    setUploadData(data)
    setStep(2)
  }

  function handleConfirmComplete(data) {
    setConfirmData(data)
    setStep(3)
  }

  function handleReset() {
    setStep(1)
    setUploadData(null)
    setConfirmData(null)
  }

  return (
    <div className="min-h-screen flex flex-col bg-gray-50">
      <Navbar />

      <div className="max-w-7xl mx-auto w-full px-4 sm:px-6 lg:px-8">
        <ProgressBar step={step} />
      </div>

      <main className="flex-1 max-w-7xl mx-auto w-full px-4 sm:px-6 lg:px-8 pb-12">
        <div className="bg-white rounded-2xl shadow-sm border border-gray-100 p-6 sm:p-8">
          {step === 1 && (
            <UploadStep onUploadComplete={handleUploadComplete} />
          )}
          {step === 2 && uploadData && (
            <ReviewStep
              uploadData={uploadData}
              onConfirmComplete={handleConfirmComplete}
            />
          )}
          {step === 3 && confirmData && (
            <ReportStep confirmData={confirmData} />
          )}
        </div>

        {step === 3 && (
          <div className="text-center mt-6">
            <button
              onClick={handleReset}
              className="text-sm text-gray-500 hover:underline"
            >
              ← Start a new assessment
            </button>
          </div>
        )}
      </main>

      <footer className="text-center py-4 text-xs text-gray-400 border-t border-gray-100">
        Secure Tax Self-Assessment System · CSC/2018/169 · Udeze Chinedu Chinagorom · Supervised by Dr. H. O. Odukoya
      </footer>
    </div>
  )
}
