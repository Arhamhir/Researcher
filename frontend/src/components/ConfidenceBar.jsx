import './ConfidenceBar.css';

function ConfidenceBar({ confidence, averageScore }) {
  const getConfidenceLevel = () => {
    if (confidence === 'High') return 100;
    if (confidence === 'Medium') return 65;
    return 35;
  };

  const confidenceLevel = getConfidenceLevel();

  return (
    <div className="confidence-bar-container card">
      <div className="confidence-header">
        <h3>AI Confidence & Overall Score</h3>
      </div>
      
      <div className="confidence-content">
        <div className="confidence-metric">
          <label>Decision Confidence</label>
          <div className="confidence-visual">
            <div className="confidence-bar">
              <div 
                className={`confidence-fill confidence-${confidence.toLowerCase()}`}
                style={{ width: `${confidenceLevel}%` }}
              >
                <span className="confidence-label">{confidence}</span>
              </div>
            </div>
          </div>
        </div>

        <div className="score-metric">
          <label>Average Score</label>
          <div className="average-score">
            <span className="score-value">{averageScore}</span>
            <span className="score-total">/10</span>
          </div>
        </div>
      </div>
    </div>
  );
}

export default ConfidenceBar;
