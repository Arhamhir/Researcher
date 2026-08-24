import './VerdictBanner.css';

function verdictTone(decision) {
  const d = decision.toLowerCase();
  if (d.includes('accept')) return 'moss';
  if (d.includes('reject')) return 'redline';
  return 'accent';
}

function VerdictBanner({ decision, critic }) {
  if (!decision) return null;

  const tone = verdictTone(decision.decision);
  const scores = decision.scores || {};
  const retried = critic?.retry_count > 0;

  return (
    <div className={`verdict-panel verdict-tone-${tone}`}>
      <div className="verdict-stamp-wrap">
        <div className="verdict-stamp">
          <span className="verdict-stamp-text">{decision.decision}</span>
        </div>
      </div>

      <div className="verdict-details">
        <p className="verdict-eyebrow mono">Final decision</p>
        <p className="verdict-justification">{decision.justification}</p>

        {Object.keys(scores).length > 0 && (
          <div className="verdict-scores">
            <span className="verdict-score-chip">
              <span className="chip-label">Methodology</span>
              <span className="chip-value">{scores.methodology}</span>
            </span>
            <span className="verdict-score-chip">
              <span className="chip-label">Novelty</span>
              <span className="chip-value">{scores.novelty}</span>
            </span>
            <span className="verdict-score-chip">
              <span className="chip-label">Citation</span>
              <span className="chip-value">{scores.citation}</span>
            </span>
            <span className="verdict-score-chip">
              <span className="chip-label">Clarity</span>
              <span className="chip-value">{scores.clarity}</span>
            </span>
          </div>
        )}

        {retried && (
          <p className="verdict-retry-note">
            The critic sent this back for {critic.retry_count} additional pass
            {critic.retry_count > 1 ? 'es' : ''} before finalizing it.
          </p>
        )}
      </div>
    </div>
  );
}

export default VerdictBanner;
