import { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { paperAPI } from '../services/api';
import VerdictBanner from '../components/VerdictBanner';
import ScoreCard from '../components/ScoreCard';
import SectionFeedback from '../components/SectionFeedback';
import ConfidenceBar from '../components/ConfidenceBar';
import {
  IconMethodology,
  IconNovelty,
  IconCitation,
  IconClarity,
  IconAlert,
} from '../components/icons';
import './ReviewDashboard.css';

function ReviewDashboard() {
  const { paperId } = useParams();
  const navigate = useNavigate();
  const [reviewData, setReviewData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    const fetchReview = async () => {
      try {
        const response = await paperAPI.getReview(paperId);
        setReviewData(response);
      } catch (err) {
        setError(err.response?.data?.detail || 'The review couldn’t be loaded.');
      } finally {
        setLoading(false);
      }
    };

    fetchReview();
  }, [paperId]);

  if (loading) {
    return (
      <div className="review-dashboard">
        <div className="container">
          <div className="state-block card">
            <div className="loading-spinner" aria-hidden="true" />
            <p>Loading your review&hellip;</p>
          </div>
        </div>
      </div>
    );
  }

  if (error || !reviewData) {
    return (
      <div className="review-dashboard">
        <div className="container">
          <div className="state-block card">
            <div className="state-icon state-icon-danger">
              <IconAlert size={28} />
            </div>
            <h2>Couldn’t load this review</h2>
            <p>{error}</p>
            <button className="btn btn-primary" onClick={() => navigate('/')}>
              Back to upload
            </button>
          </div>
        </div>
      </div>
    );
  }

  const {
    methodology_review,
    novelty_review,
    citation_review,
    clarity_review,
    final_decision,
    critic,
  } = reviewData;

  const safeMethodology = methodology_review || { score: 0, issues: [], suggestions: [] };
  const safeNovelty = novelty_review || { score: 0, issues: [], suggestions: [], similarity_max: null };
  const safeCitation = citation_review || { score: 0, issues: [], suggestions: [] };
  const safeClarity = clarity_review || { score: 0, issues: [], suggestions: [] };

  const agents = [
    { key: 'methodology', title: 'Methodology', Icon: IconMethodology, ...safeMethodology },
    { key: 'novelty', title: 'Novelty', Icon: IconNovelty, ...safeNovelty },
    { key: 'citation', title: 'Citation', Icon: IconCitation, ...safeCitation },
    { key: 'clarity', title: 'Clarity', Icon: IconClarity, ...safeClarity },
  ];

  // Open the lowest-scoring report by default — that's the one worth reading first.
  const lowestScoreKey = agents.reduce(
    (lowest, agent) => (agent.score < lowest.score ? agent : lowest),
    agents[0]
  ).key;

  return (
    <div className="review-dashboard">
      <div className="container">
        <div className="dashboard-header">
          <div>
            <p className="dashboard-eyebrow mono">Review report</p>
            <h1>Your paper, reviewed</h1>
            <p className="paper-id mono">{paperId}</p>
          </div>
          <button className="btn btn-secondary" onClick={() => navigate('/')}>
            Review another paper
          </button>
        </div>

        <section className="final-section">
          <VerdictBanner decision={final_decision} critic={critic} />
          {final_decision && (
            <ConfidenceBar
              confidence={final_decision.confidence}
              averageScore={final_decision.average_score}
            />
          )}
        </section>

        <div className="section-divider">
          <h2>At a glance</h2>
        </div>

        <div className="metrics-grid">
          {agents.map((agent) => (
            <ScoreCard key={agent.key} title={agent.title} Icon={agent.Icon} score={agent.score} maxScore={10} />
          ))}
        </div>

        <div className="feedback-section">
          <h2>Reviewer reports</h2>
          <p className="feedback-section-hint">
            Each reviewer covers one dimension only. Expand a report to see its issues and suggestions.
          </p>

          <div className="feedback-list">
            {agents.map((agent) => (
              <SectionFeedback
                key={agent.key}
                title={`${agent.title} agent`}
                Icon={agent.Icon}
                score={agent.score}
                issues={agent.issues}
                suggestions={agent.suggestions}
                defaultExpanded={agent.key === lowestScoreKey}
                additionalInfo={
                  agent.key === 'novelty' &&
                  agent.similarity_max !== undefined &&
                  agent.similarity_max !== null && {
                    label: 'Highest lexical overlap with existing work',
                    value: `${(agent.similarity_max * 100).toFixed(1)}%`,
                  }
                }
              />
            ))}
          </div>
        </div>

        {critic && critic.issues && critic.issues.length > 0 && (
          <div className="critic-section card">
            <div className="critic-header">
              <h3>Critic validation</h3>
              <span className="retry-badge mono">
                {critic.retry_count > 0 ? `${critic.retry_count} retries` : 'No retries needed'}
              </span>
            </div>
            <ul className="critic-issues">
              {critic.issues.map((issue, index) => (
                <li key={index}>{issue}</li>
              ))}
            </ul>
          </div>
        )}
      </div>
    </div>
  );
}

export default ReviewDashboard;
