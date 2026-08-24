import { useCountUp } from '../hooks/useCountUp';
import './ScoreCard.css';

function levelOf(percentage) {
  if (percentage >= 80) return 'Excellent';
  if (percentage >= 60) return 'Good';
  if (percentage >= 40) return 'Fair';
  return 'Needs work';
}

function ScoreCard({ title, Icon, score, maxScore = 10 }) {
  const percentage = (score / maxScore) * 100;
  const display = useCountUp(score);

  return (
    <div className="score-card">
      <div className="score-card-top">
        {Icon && (
          <span className="score-card-icon">
            <Icon size={18} />
          </span>
        )}
        <span className="score-title">{title}</span>
      </div>

      <div className="score-number">
        {display}
        <span className="score-max">/{maxScore}</span>
      </div>

      <p className="score-label">{levelOf(percentage)}</p>

      <div className="score-bar" role="presentation">
        <div className="score-bar-fill" style={{ width: `${percentage}%` }} />
      </div>
    </div>
  );
}

export default ScoreCard;
