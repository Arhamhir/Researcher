import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { paperAPI } from '../services/api';
import './UploadPage.css';

function UploadPage() {
  const navigate = useNavigate();
  const [file, setFile] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [error, setError] = useState('');
  const [dragActive, setDragActive] = useState(false);
  
  // Processing state
  const [isProcessing, setIsProcessing] = useState(false);
  const [paperId, setPaperId] = useState(null);
  const [processingProgress, setProcessingProgress] = useState(0);
  const [messageIndex, setMessageIndex] = useState(0);

  const statusMessages = [
    'Reviewing your paper with focused academic rigor.',
    'Cross-checking methods, citations, and clarity.',
    'Synthesizing reviewer feedback into a final verdict.',
    'Validating novelty against existing literature.',
    'Almost done. Preparing your report now.'
  ];

  const handleDrag = (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true);
    } else if (e.type === "dragleave") {
      setDragActive(false);
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFileSelect(e.dataTransfer.files[0]);
    }
  };

  const handleFileInput = (e) => {
    if (e.target.files && e.target.files[0]) {
      handleFileSelect(e.target.files[0]);
    }
  };

  const handleFileSelect = (selectedFile) => {
    if (selectedFile.type !== 'application/pdf') {
      setError('Please select a PDF file');
      return;
    }
    
    if (selectedFile.size > 10 * 1024 * 1024) { // 10MB limit
      setError('File size must be less than 10MB');
      return;
    }

    setFile(selectedFile);
    setError('');
  };

  const handleUpload = async () => {
    if (!file) return;

    setError('');
    setUploading(true);
    setIsProcessing(true);  // Show loader immediately
    setProcessingProgress(10);  // Start at 10% to show something is happening
    setUploadProgress(0);

    try {
      const response = await paperAPI.uploadPaper(file, (progressEvent) => {
        const progress = Math.round((progressEvent.loaded * 100) / progressEvent.total);
        // Update visual progress (0-30%) during upload phase
        const displayProgress = 10 + (progress * 0.2);
        setProcessingProgress(displayProgress);
      });

      // Start processing with the paper ID
      setPaperId(response.paper_id);
      setUploading(false);
      // isProcessing stays true, polling takes over for analysis phase
    } catch (err) {
      setError(err.response?.data?.detail || 'Upload failed. Please try again.');
      setUploading(false);
      setIsProcessing(false);
    }
  };

  const handleRemoveFile = () => {
    setFile(null);
    setError('');
    setUploadProgress(0);
  };

  // Polling effect for review status
  useEffect(() => {
    if (!isProcessing || !paperId) return;

    let pollInterval;
    let currentStage = 0;

    const pollStatus = async () => {
      try {
        const response = await paperAPI.pollReviewStatus(paperId);
        console.log('[POLL] Response:', response);
        
        if (response.status === 'complete' || response.status === 'completed') {
          setProcessingProgress(100);
          clearInterval(pollInterval);
          
          // Navigate to review dashboard after short delay
          setTimeout(() => {
            navigate(`/review/${paperId}`);
          }, 1500);
        } else if (response.status === 'failed') {
          setError('Review process failed. Please try again.');
          clearInterval(pollInterval);
          setIsProcessing(false);
        } else {
          // Update progress from backend
          const newProgress = response.progress || Math.min(currentStage * 16 + Math.random() * 10, 95);
          setProcessingProgress(newProgress);
          currentStage++;
        }
      } catch (err) {
        console.error('[POLL] Error:', err);
        if (err.response?.status !== 404) {
          setError('Failed to check review status.');
          clearInterval(pollInterval);
          setIsProcessing(false);
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
  }, [isProcessing, paperId, navigate]);

  // Message rotation effect
  useEffect(() => {
    if (!isProcessing) return;

    const messageInterval = setInterval(() => {
      setMessageIndex((prev) => (prev + 1) % statusMessages.length);
    }, 3000);

    return () => clearInterval(messageInterval);
  }, [isProcessing, statusMessages.length]);

  return (
    <div className="upload-page">
      <div className="container">
        {isProcessing ? (
          // Processing state
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
                    onClick={() => {
                      setIsProcessing(false);
                      setPaperId(null);
                      setError('');
                    }}
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
                        style={{ width: `${processingProgress}%` }}
                      />
                    </div>
                    <p className="progress-percentage">{Math.round(processingProgress)}% Complete</p>
                  </div>

                  {processingProgress === 100 && (
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
        ) : (
          // Upload state
          <div className="upload-layout">
            <div className="upload-hero">
              <h1>Blackline Paper Review</h1>
              <p>Minimal, fast, and honest AI peer review for academic papers.</p>
              <div className="upload-hero-meta">
                <span className="meta-pill">PDF Only</span>
                <span className="meta-pill">Max 10MB</span>
                <span className="meta-pill">AI Agents</span>
              </div>
            </div>

            <div className="upload-panel card">
              {!file ? (
                <div
                  className={`drop-zone ${dragActive ? 'drag-active' : ''}`}
                  onDragEnter={handleDrag}
                  onDragLeave={handleDrag}
                  onDragOver={handleDrag}
                  onDrop={handleDrop}
                >
                  <div className="drop-zone-icon">
                    <svg width="64" height="64" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                      <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                      <polyline points="17 8 12 3 7 8" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                      <line x1="12" y1="3" x2="12" y2="15" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                    </svg>
                  </div>
                  
                  <h3>Drag and drop your PDF here</h3>
                  <p>or</p>
                  
                  <label htmlFor="file-input" className="btn btn-primary">
                    Browse Files
                  </label>
                  <input
                    id="file-input"
                    type="file"
                    accept=".pdf"
                    onChange={handleFileInput}
                    style={{ display: 'none' }}
                  />
                  
                  <p className="file-requirements">
                    PDF only • Max 10MB
                  </p>
                </div>
              ) : (
                <div className="file-selected">
                  <div className="file-info">
                    <div className="file-icon">
                      <svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                        <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                        <polyline points="14 2 14 8 20 8" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                      </svg>
                    </div>
                    <div className="file-details">
                      <h4>{file.name}</h4>
                      <p>{(file.size / 1024 / 1024).toFixed(2)} MB</p>
                    </div>
                    {!uploading && (
                      <button className="btn-remove" onClick={handleRemoveFile}>
                        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                          <line x1="18" y1="6" x2="6" y2="18" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                          <line x1="6" y1="6" x2="18" y2="18" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                        </svg>
                      </button>
                    )}
                  </div>

                  {uploading && (
                    <div className="upload-progress">
                      <div className="progress-bar">
                        <div 
                          className="progress-fill" 
                          style={{ width: `${uploadProgress}%` }}
                        />
                      </div>
                      <p className="progress-text">{uploadProgress}% Uploaded</p>
                    </div>
                  )}

                  {!uploading && (
                    <button 
                      className="btn btn-primary btn-large"
                      onClick={handleUpload}
                    >
                      Start Review
                    </button>
                  )}
                </div>
              )}

              {error && (
                <div className="error-message">
                  <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                    <circle cx="12" cy="12" r="10" strokeWidth="2"/>
                    <line x1="12" y1="8" x2="12" y2="12" strokeWidth="2" strokeLinecap="round"/>
                    <line x1="12" y1="16" x2="12.01" y2="16" strokeWidth="2" strokeLinecap="round"/>
                  </svg>
                  {error}
                </div>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export default UploadPage;
