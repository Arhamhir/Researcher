import { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { paperAPI } from '../services/api';
import VerdictBanner from '../components/VerdictBanner';
import ScoreCard from '../components/ScoreCard';
import SectionFeedback from '../components/SectionFeedback';
import ConfidenceBar from '../components/ConfidenceBar';
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
        setError(err.response?.data?.detail || 'Failed to load review data');
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
          <div className="loading-state card">
            <div className="loading-spinner"></div>
            <p>Loading review results...</p>
          </div>
        </div>
      </div>
    );
  }

  if (error || !reviewData) {
    return (
      <div className="review-dashboard">
        <div className="container">
          <div className="error-state card">
            <h2>Failed to Load Review</h2>
            <p>{error}</p>
            <button className="btn btn-primary" onClick={() => navigate('/')}>
              Return to Upload
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
    critic
  } = reviewData;

  const safeMethodology = methodology_review || { score: 0, issues: [], suggestions: [] };
  const safeNovelty = novelty_review || { score: 0, issues: [], suggestions: [], similarity_max: null };
  const safeCitation = citation_review || { score: 0, issues: [], suggestions: [] };
  const safeClarity = clarity_review || { score: 0, issues: [], suggestions: [] };


  return (
    <div className="review-dashboard">
      <div className="container">
        <div className="dashboard-header">
          <h1>AI Peer Review Report</h1>
          <p className="paper-id">Paper ID: {paperId}</p>
          <button 
            className="btn btn-secondary"
            onClick={() => navigate('/')}
          >
            Review Another Paper
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
          <h2>Agent Report Grid</h2>
        </div>

        <div className="metrics-grid">
          <ScoreCard
            title="Methodology"
            score={safeMethodology.score}
            maxScore={10}
          />
          <ScoreCard
            title="Clarity"
            score={safeClarity.score}
            maxScore={10}
          />
          <ScoreCard
            title="Citation"
            score={safeCitation.score}
            maxScore={10}
          />
          <ScoreCard
            title="Novelty"
            score={safeNovelty.score}
            maxScore={10}
          />
        </div>

        <div className="feedback-section">
          <h2>Agent Feedback Reports</h2>

          <div className="feedback-grid">
            <SectionFeedback
              title="Methodology Agent"
              score={safeMethodology.score}
              issues={safeMethodology.issues}
              suggestions={safeMethodology.suggestions}
            />

            <SectionFeedback
              title="Clarity Agent"
              score={safeClarity.score}
              issues={safeClarity.issues}
              suggestions={safeClarity.suggestions}
            />

            <SectionFeedback
              title="Citation Agent"
              score={safeCitation.score}
              issues={safeCitation.issues}
              suggestions={safeCitation.suggestions}
            />

            <SectionFeedback
              title="Novelty Agent"
              score={safeNovelty.score}
              issues={safeNovelty.issues}
              suggestions={safeNovelty.suggestions}
              additionalInfo={safeNovelty.similarity_max !== undefined && safeNovelty.similarity_max !== null && {
                label: 'Max Similarity with Existing Work',
                value: `${(safeNovelty.similarity_max * 100).toFixed(1)}%`
              }}
            />
          </div>
        </div>

        {critic && critic.issues && critic.issues.length > 0 && (
          <div className="critic-section card">
            <div className="critic-header">
              <h3>Critic Agent Validation</h3>
              <span className="retry-badge">
                {critic.retry_count > 0 ? `${critic.retry_count} retries` : 'No retries needed'}
              </span>
            </div>
            <div className="critic-issues">
              <h4>Critical Issues Identified:</h4>
              <ul>
                {critic.issues.map((issue, index) => (
                  <li key={index}>{issue}</li>
                ))}
              </ul>
            </div>
          </div>
        )}

      </div>
    </div>
  );
}

export default ReviewDashboard;
