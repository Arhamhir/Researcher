import './VerdictBanner.css';

function VerdictBanner({ decision, critic }) {
  if (!decision) return null;

  const getVerdictColor = (verdict) => {
    if (verdict.toLowerCase().includes('accept')) return 'success';
    if (verdict.toLowerCase().includes('reject')) return 'danger';
    return 'warning';
  };

  const verdictColor = getVerdictColor(decision.decision);

  return (
    <div className={`verdict-banner verdict-${verdictColor}`}>
      <div className="verdict-content">
        <div className="verdict-details">
          <h2 className="verdict-decision">{decision.decision}</h2>
          <p className="verdict-justification">{decision.justification}</p>
          {decision.scores && (
            <div className="verdict-scores">
              <span>Methodology: {decision.scores.methodology}/10</span>
              <span>•</span>
              <span>Novelty: {decision.scores.novelty}/10</span>
              <span>•</span>
              <span>Citations: {decision.scores.citation}/10</span>
              <span>•</span>
              <span>Clarity: {decision.scores.clarity}/10</span>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default VerdictBanner;
