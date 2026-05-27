export default function Navbar() {
  return (
    <nav className="w-full" style={{ backgroundColor: '#008751' }}>
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 bg-white rounded-full flex items-center justify-center">
              <span className="text-sm font-bold" style={{ color: '#008751' }}>₦</span>
            </div>
            <div>
              <h1 className="text-white font-bold text-lg leading-tight">
                Secure Tax Self-Assessment System
              </h1>
              <p className="text-green-200 text-xs">For Nigerian Freelancers · FIRS 2024 · NDPR Compliant</p>
            </div>
          </div>
          <div className="hidden sm:flex items-center gap-4 text-green-100 text-sm">
            <span>CSC/2018/169</span>
            <span className="text-green-300">|</span>
            <span>Udeze Chinedu Chinagorom</span>
          </div>
        </div>
      </div>
    </nav>
  )
}
