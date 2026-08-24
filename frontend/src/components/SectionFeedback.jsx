import { useId, useState } from 'react';
import { IconChevron, IconCheck } from './icons';
import './SectionFeedback.css';

function SectionFeedback({ title, Icon, score, issues, suggestions, additionalInfo, defaultExpanded = false }) {
  const [expanded, setExpanded] = useState(defaultExpanded);
  const bodyId = useId();
  const hasIssues = issues && issues.length > 0;
  const hasSuggestions = suggestions && suggestions.length > 0;
  const isClean = !hasIssues && !hasSuggestions;

  return (
    <div className={`section-feedback ${expanded ? 'is-expanded' : ''}`}>
      <button
        type="button"
        className="feedback-header"
        onClick={() => setExpanded((v) => !v)}
        aria-expanded={expanded}
        aria-controls={bodyId}
      >
        <span className="feedback-title">
          {Icon && (
            <span className="feedback-icon">
              <Icon size={18} />
            </span>
          )}
          <span>{title}</span>
        </span>
        <span className="feedback-header-right">
          <span className="feedback-score">
            {score}<span className="feedback-score-max">/10</span>
          </span>
          <IconChevron size={18} className="feedback-chevron" />
        </span>
      </button>

      <div className="feedback-collapse" id={bodyId}>
        <div className="feedback-collapse-inner">
          <div className="feedback-body">
            {additionalInfo && (
              <div className="additional-info">
                <strong>{additionalInfo.label}:</strong> {additionalInfo.value}
              </div>
            )}

            {hasIssues && (
              <div className="feedback-block">
                <h4>Issues identified</h4>
                <ul className="issues-list">
                  {issues.map((issue, index) => (
                    <li key={index}>{issue}</li>
                  ))}
                </ul>
              </div>
            )}

            {hasSuggestions && (
              <div className="feedback-block">
                <h4>Suggestions</h4>
                <ul className="suggestions-list">
                  {suggestions.map((suggestion, index) => (
                    <li key={index}>{suggestion}</li>
                  ))}
                </ul>
              </div>
            )}

            {isClean && (
              <div className="no-feedback">
                <IconCheck size={18} />
                <p>No issues found. This section meets quality standards.</p>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

export default SectionFeedback;
