import './SubjectBanner.css'

/**
 * SubjectBanner
 * Renders one subject-representation banner (Section 4 of PROJECT_PLAN.md).
 * Banners are pre-written; they are only ever rendered by the parent
 * right after the real corresponding backend step has completed.
 *
 * type: 'cloud' | 'networking' | 'testing'
 * stats: optional data to fill in the pre-written template
 *   - networking: { originalSize, compressedSize, savingsPercent }
 *   - testing: { passed, total }
 */
const BANNERS = {
  cloud: {
    icon: '☁️',
    title: 'Cloud Computing Used',
    body: () => 'Your file is being processed on a cloud server (Render), not your device.',
  },
  networking: {
    icon: '📡',
    title: 'Networking Used',
    body: (stats) =>
      stats
        ? `The compressed file was delivered over your network connection. Original size: ${stats.originalSize} → Compressed: ${stats.compressedSize} — saving ${stats.savingsPercent}% of your bandwidth.`
        : 'The compressed file was delivered over your network connection.',
  },
  testing: {
    icon: '✅',
    title: 'Testing & QA Used',
    body: (stats) =>
      stats
        ? `${stats.passed}/${stats.total} automated tests passed — verified compression, error handling, and delivery correctness.`
        : 'Automated tests verified compression, error handling, and delivery correctness.',
  },
}

export default function SubjectBanner({ type, stats }) {
  const banner = BANNERS[type]
  if (!banner) return null

  return (
    <div className={`subject-banner subject-banner--${type}`} role="status">
      <span className="subject-banner__icon" aria-hidden="true">
        {banner.icon}
      </span>
      <div className="subject-banner__text">
        <div className="subject-banner__title">{banner.title}</div>
        <div className="subject-banner__body">{banner.body(stats)}</div>
      </div>
    </div>
  )
}
