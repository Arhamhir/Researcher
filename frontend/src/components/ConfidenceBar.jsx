import { useCountUp } from '../hooks/useCountUp';
import './ConfidenceBar.css';

const LEVELS = ['Low', 'Medium', 'High'];

function ConfidenceBar({ confidence, averageScore }) {
  const activeIndex = LEVELS.indexOf(confidence);
  const displayScore = useCountUp(averageScore ?? 0);

  return (
    <div className="confidence-card card">
      <div className="confidence-metric">
        <p className="confidence-label mono">Critic confidence</p>
        <div className="confidence-segments" role="img" aria-label={`Confidence: ${confidence || 'unknown'}`}>
          {LEVELS.map((level, index) => (
            <span
              key={level}
              className={`confidence-segment ${index <= activeIndex ? 'is-filled' : ''}`}
            />
          ))}
        </div>
        <p className="confidence-value">{confidence || '—'}</p>
      </div>

      <div className="confidence-divider" aria-hidden="true" />

      <div className="score-metric">
        <p className="confidence-label mono">Average score</p>
        <div className="average-score">
          <span className="score-value">{displayScore}</span>
          <span className="score-total">/10</span>
        </div>
      </div>
    </div>
  );
}

export default ConfidenceBar;
