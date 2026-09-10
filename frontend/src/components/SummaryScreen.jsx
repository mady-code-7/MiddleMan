import SubjectBanner from './SubjectBanner'
import './SummaryScreen.css'

/**
 * SummaryScreen
 * Final "receipt"-style recap shown after all three real steps complete.
 * Doubles as the live-demo fallback view and a report screenshot.
 *
 * result: { originalSize, compressedSize, savingsPercent, testsPassed, testsTotal, downloadUrl }
 */
export default function SummaryScreen({ result, onDownload, onReset }) {
  if (!result) return null

  const networkingStats = {
    originalSize: result.originalSize,
    compressedSize: result.compressedSize,
    savingsPercent: result.savingsPercent,
  }
  const testingStats = {
    passed: result.testsPassed,
    total: result.testsTotal,
  }

  return (
    <div className="summary">
      <div className="summary__header">
        <span className="summary__check">✓</span>
        <div>
          <div className="summary__title">Transfer complete</div>
          <div className="summary__subtitle">
            {result.savingsPercent}% smaller — delivered over your connection
          </div>
        </div>
      </div>

      <div className="summary__banners">
        <SubjectBanner type="cloud" />
        <SubjectBanner type="networking" stats={networkingStats} />
        <SubjectBanner type="testing" stats={testingStats} />
      </div>

      <div className="summary__actions">
        <button className="summary__download" onClick={onDownload}>
          Download compressed file
        </button>
        <button className="summary__reset" onClick={onReset}>
          Start another
        </button>
      </div>
    </div>
  )
}
