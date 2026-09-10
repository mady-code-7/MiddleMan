import './ProgressIndicator.css'

/**
 * ProgressIndicator
 * Shows which real backend step is currently in flight.
 * `step` is one of: 'idle' | 'fetching' | 'compressing' | 'delivering' | 'done'
 * Layout-only for now — App.jsx will drive `step` from real /process responses.
 */
const STEPS = [
  { key: 'fetching', label: 'Fetching from source' },
  { key: 'compressing', label: 'Compressing on server' },
  { key: 'delivering', label: 'Delivering to you' },
]

export default function ProgressIndicator({ step }) {
  if (step === 'idle') return null

  const activeIndex = STEPS.findIndex((s) => s.key === step)

  return (
    <div className="progress" role="status" aria-live="polite">
      {STEPS.map((s, i) => {
        const state =
          step === 'done' || i < activeIndex
            ? 'complete'
            : i === activeIndex
            ? 'active'
            : 'pending'

        return (
          <div className={`progress__step is-${state}`} key={s.key}>
            <span className="progress__dot" />
            <span className="progress__label">{s.label}</span>
          </div>
        )
      })}
    </div>
  )
}
