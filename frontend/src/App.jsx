import { useState } from 'react'
import UploadForm from './components/UploadForm'
import ProgressIndicator from './components/ProgressIndicator'
import SubjectBanner from './components/SubjectBanner'
import SummaryScreen from './components/SummaryScreen'
import './App.css'

/**
 * App
 * Basic layout wiring for now. `step` and `result` are driven by local
 * state only — no real /process, /run-tests, or /download calls yet.
 * Section 11 (Build Order) covers wiring this to the Flask backend next.
 */
export default function App() {
  const [step, setStep] = useState('idle') // idle | fetching | compressing | delivering | done
  const [showCloudBanner, setShowCloudBanner] = useState(false)
  const [result, setResult] = useState(null)

  function handleSubmit(payload) {
    // Placeholder sequence just to preview the layout end-to-end.
    // Will be replaced with real fetch() calls to the Flask backend.
    setStep('fetching')
    setShowCloudBanner(true)

    setTimeout(() => setStep('compressing'), 1200)
    setTimeout(() => setStep('delivering'), 2400)
    setTimeout(() => {
      setStep('done')
      setResult({
        originalSize: '18.4 MB',
        compressedSize: '4.9 MB',
        savingsPercent: 73,
        testsPassed: 5,
        testsTotal: 5,
      })
    }, 3400)
  }

  function handleReset() {
    setStep('idle')
    setShowCloudBanner(false)
    setResult(null)
  }

  const isProcessing = step !== 'idle' && step !== 'done'

  return (
    <div className="app">
      <header className="app__header">
        <h1 className="app__title">MiddleMan</h1>
        <p className="app__tagline">
          We do the downloading. You get the smaller file.
        </p>
      </header>

      <main className="app__main">
        {step === 'done' && result ? (
          <SummaryScreen
            result={result}
            onDownload={() => {}}
            onReset={handleReset}
          />
        ) : (
          <>
            <UploadForm onSubmit={handleSubmit} disabled={isProcessing} />

            <ProgressIndicator step={step} />

            {showCloudBanner && <SubjectBanner type="cloud" />}
          </>
        )}
      </main>

      <footer className="app__footer">
        <span>Cloud Computing · Networking · Testing &amp; QA</span>
      </footer>
    </div>
  )
}
