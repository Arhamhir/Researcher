import './SectionFeedback.css';

function SectionFeedback({ title, icon, score, issues, suggestions, additionalInfo }) {
  return (
    <div className="section-feedback">
      <div className="feedback-header">
        <div className="feedback-title">
          <span className="feedback-icon">{icon}</span>
          <h3>{title}</h3>
        </div>
        <div className="feedback-score">
          {score}/10
        </div>
      </div>

      {additionalInfo && (
        <div className="additional-info">
          <strong>{additionalInfo.label}:</strong> {additionalInfo.value}
        </div>
      )}

      {issues && issues.length > 0 && (
        <div className="feedback-section">
          <h4>Issues Identified</h4>
          <ul className="issues-list">
            {issues.map((issue, index) => (
              <li key={index}>{issue}</li>
            ))}
          </ul>
        </div>
      )}

      {suggestions && suggestions.length > 0 && (
        <div className="feedback-section">
          <h4>Suggestions for Improvement</h4>
          <ul className="suggestions-list">
            {suggestions.map((suggestion, index) => (
              <li key={index}>{suggestion}</li>
            ))}
          </ul>
        </div>
      )}

      {(!issues || issues.length === 0) && (!suggestions || suggestions.length === 0) && (
        <div className="no-feedback">
          <p>No issues found. This section meets quality standards.</p>
        </div>
      )}
    </div>
  );
}

export default SectionFeedback;
