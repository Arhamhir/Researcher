import './ScoreCard.css';

function ScoreCard({ title, icon, score, maxScore }) {
  const percentage = (score / maxScore) * 100;
  
  const getScoreLabel = (percentage) => {
    if (percentage >= 80) return 'Excellent';
    if (percentage >= 60) return 'Good';
    if (percentage >= 40) return 'Fair';
    return 'Needs Improvement';
  };

  return (
    <div className="score-card">
      <div className="score-card-header">
        <div>
          <p className="score-title">{title}</p>
          <p className="score-label">{getScoreLabel(percentage)}</p>
        </div>
        <div className="score-number">
          {score}<span className="score-max">/{maxScore}</span>
        </div>
      </div>

      <div className="score-bar">
        <div 
          className="score-bar-fill" 
          style={{ width: `${percentage}%` }}
        />
      </div>
    </div>
  );
}

export default ScoreCard;
