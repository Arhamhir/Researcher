import { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { paperAPI } from '../services/api';
import './ProcessingPage.css';

function ProcessingPage() {
  const { paperId } = useParams();
  const navigate = useNavigate();
  const [status, setStatus] = useState('parsing');
  const [progress, setProgress] = useState(0);
  const [error, setError] = useState('');
  const [messageIndex, setMessageIndex] = useState(0);

  const statusMessages = [
    'Reviewing your paper with focused academic rigor.',
    'Cross-checking methods, citations, and clarity.',
    'Synthesizing reviewer feedback into a final verdict.',
    'Validating novelty against existing literature.',
    'Almost done. Preparing your report now.'
  ];

  const stages = [
    { id: 'parsing', label: 'Parsing PDF', icon: '📄' },
    { id: 'methodology', label: 'Methodology Review', icon: '🔬' },
    { id: 'novelty', label: 'Novelty Assessment', icon: '💡' },
    { id: 'citation', label: 'Citation Analysis', icon: '📚' },
    { id: 'clarity', label: 'Clarity Evaluation', icon: '✍️' },
    { id: 'validation', label: 'Final Validation', icon: '✅' },
  ];

  useEffect(() => {
    let pollInterval;
    let currentStage = 0;

    const pollStatus = async () => {
      try {
        const response = await paperAPI.pollReviewStatus(paperId);
        console.log('[POLL] Response:', response);
        
        if (response.status === 'complete' || response.status === 'completed') {
          setStatus('completed');
          setProgress(100);
          clearInterval(pollInterval);
          
          // Navigate to review dashboard after short delay
          setTimeout(() => {
            navigate(`/review/${paperId}`);
          }, 1500);
        } else if (response.status === 'failed') {
          setError('Review process failed. Please try again.');
          clearInterval(pollInterval);
        } else {
          // Update progress from backend
          const newProgress = response.progress || Math.min(currentStage * 16 + Math.random() * 10, 95);
          setProgress(newProgress);
          setStatus(stages[currentStage % stages.length].id);
          currentStage++;
        }
      } catch (err) {
        console.error('[POLL] Error:', err);
        if (err.response?.status !== 404) {
          setError('Failed to check review status.');
          clearInterval(pollInterval);
        }
      }
    };

    // Poll every 2 seconds
    pollStatus();
    pollInterval = setInterval(pollStatus, 2000);

    return () => {
      if (pollInterval) {
        clearInterval(pollInterval);
      }
    };
  }, [paperId, navigate]);

  useEffect(() => {
    const messageInterval = setInterval(() => {
      setMessageIndex((prev) => (prev + 1) % statusMessages.length);
    }, 3000);

    return () => clearInterval(messageInterval);
  }, [statusMessages.length]);

  const currentStageIndex = stages.findIndex(s => s.id === status);

  return (
    <div className="processing-page">
      <div className="container">
        <div className="processing-shell">
          <div className="processing-header">
            <h1>Reviewing Your Paper</h1>
            <p>Your report is being crafted with focused academic scrutiny.</p>
          </div>

          <div className="processing-card card">
            {error ? (
              <div className="error-state">
                <div className="error-icon">❌</div>
                <h2>Review Failed</h2>
                <p>{error}</p>
                <button 
                  className="btn btn-primary"
                  onClick={() => navigate('/')}
                >
                  Upload Another Paper
                </button>
              </div>
            ) : (
              <>
                <div className="review-pulse">
                  <div className="pulse-ring"></div>
                  <div className="pulse-core"></div>
                </div>
                <p className="status-text" key={messageIndex}>
                  {statusMessages[messageIndex]}
                </p>
                <p className="status-subtext">We will be done in a short while.</p>

                <div className="progress-section">
                  <div className="progress-bar-container">
                    <div 
                      className="progress-bar-fill" 
                      style={{ width: `${progress}%` }}
                    />
                  </div>
                  <p className="progress-percentage">{Math.round(progress)}% Complete</p>
                </div>

                {status === 'completed' && (
                  <div className="completion-message">
                    <div className="completion-icon">🎉</div>
                    <h2>Review Complete!</h2>
                    <p>Redirecting to your AI-generated review...</p>
                  </div>
                )}
              </>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

export default ProcessingPage;
