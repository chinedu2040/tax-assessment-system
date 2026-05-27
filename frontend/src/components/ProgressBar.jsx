export default function ProgressBar({ step }) {
  const steps = ['Upload', 'Review & Correct', 'Download Report']

  return (
    <div className="w-full py-6">
      <div className="max-w-2xl mx-auto">
        <div className="flex items-center justify-between relative">
          <div className="absolute top-4 left-0 right-0 h-0.5 bg-gray-200 z-0">
            <div
              className="h-full transition-all duration-500"
              style={{
                backgroundColor: '#008751',
                width: step === 1 ? '0%' : step === 2 ? '50%' : '100%',
              }}
            />
          </div>
          {steps.map((label, i) => {
            const num = i + 1
            const isActive = step === num
            const isDone = step > num
            return (
              <div key={num} className="flex flex-col items-center z-10">
                <div
                  className={`w-8 h-8 rounded-full flex items-center justify-center font-bold text-sm transition-colors duration-300 ${
                    isDone
                      ? 'text-white'
                      : isActive
                      ? 'text-white'
                      : 'bg-gray-200 text-gray-500'
                  }`}
                  style={isDone || isActive ? { backgroundColor: '#008751' } : {}}
                >
                  {isDone ? '✓' : num}
                </div>
                <span
                  className={`mt-2 text-xs font-medium ${
                    isActive ? 'text-gray-900' : isDone ? 'text-gray-600' : 'text-gray-400'
                  }`}
                >
                  {label}
                </span>
              </div>
            )
          })}
        </div>
        <p className="text-center text-gray-400 text-xs mt-3">
          Step {step} of {steps.length}
        </p>
      </div>
    </div>
  )
}
