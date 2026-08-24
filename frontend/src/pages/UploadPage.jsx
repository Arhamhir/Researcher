import { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { paperAPI } from '../services/api';
import PipelineProgress from '../components/PipelineProgress';
import {
  IconUpload,
  IconFile,
  IconClose,
  IconAlert,
  IconCheck,
  IconParse,
  IconMethodology,
  IconNovelty,
  IconCitation,
  IconClarity,
  IconSynthesize,
  IconReport,
} from '../components/icons';
import './UploadPage.css';

const PROCESS_STEPS = [
  {
    Icon: IconUpload,
    title: 'Upload',
    body: 'Drop in a PDF. No account, no queue, no formatting requirements.',
  },
  {
    Icon: IconParse,
    title: 'Parse',
    body: 'Sections are located automatically — abstract, methodology, results, references — from whatever headings the paper actually uses.',
  },
  {
    Icon: IconSynthesize,
    title: 'Review, in parallel',
    body: 'Four independent reviewers read the relevant sections at the same time, each scoring only their own dimension.',
  },
  {
    Icon: IconReport,
    title: 'Verdict',
    body: 'Scores are cross-checked for contradictions, then combined into one calibrated decision with full written justification.',
  },
];

const REVIEWERS = [
  {
    Icon: IconMethodology,
    title: 'Methodology',
    body: 'Checks experimental design, baselines, and reproducibility. Rewards rigor described in the paper — partial credit for methods that are sound but under-detailed.',
  },
  {
    Icon: IconNovelty,
    title: 'Novelty',
    body: 'Compares your abstract and introduction against everything already reviewed, to flag likely overlap or duplicate submissions.',
  },
  {
    Icon: IconCitation,
    title: 'Citation',
    body: "Reads for how well claims are grounded in prior work — whether that's a dedicated related-work section or citations woven through the text.",
  },
  {
    Icon: IconClarity,
    title: 'Clarity',
    body: 'Judges whether the argument is easy to follow end to end — not whether it matches one reviewer’s personal writing style.',
  },
];

const VALUE_PROPS = [
  {
    title: 'Minutes, not months',
    body: "Traditional peer review can take three to six months to come back. Get a full four-dimension review while you're still on the same page.",
  },
  {
    title: 'Transparent scoring',
    body: 'Every score ships with the specific issues and suggestions behind it — never a bare verdict with no way to see the reasoning.',
  },
  {
    title: 'Consistent, not political',
    body: 'The same four reviewers, the same rubric, every submission. No reviewer relationships, reputation, or politics in the loop.',
  },
];

const STATUS_MESSAGES = [
  'Parsing the PDF and locating each section.',
  'Four reviewers are reading in parallel: methodology, novelty, citation, clarity.',
  'The critic is checking their scores for contradictions.',
  'Writing up the final verdict.',
];

const MAX_FILE_BYTES = 10 * 1024 * 1024;

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
  const dragCounter = useRef(0);

  const handleDrag = (e) => {
    e.preventDefault();
    e.stopPropagation();
  };

  const handleDragEnter = (e) => {
    handleDrag(e);
    dragCounter.current += 1;
    setDragActive(true);
  };

  const handleDragLeave = (e) => {
    handleDrag(e);
    dragCounter.current -= 1;
    if (dragCounter.current <= 0) {
      dragCounter.current = 0;
      setDragActive(false);
    }
  };

  const handleDrop = (e) => {
    handleDrag(e);
    dragCounter.current = 0;
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
      setError('That file isn’t a PDF. Convert it and try again.');
      return;
    }

    if (selectedFile.size > MAX_FILE_BYTES) {
      setError('That file is over 10MB. Trim it down and try again.');
      return;
    }

    setFile(selectedFile);
    setError('');
  };

  const handleUpload = async () => {
    if (!file) return;

    setError('');
    setUploading(true);
    setIsProcessing(true); // Show the pipeline immediately
    setProcessingProgress(10);
    setUploadProgress(0);

    try {
      const response = await paperAPI.uploadPaper(file, (progressEvent) => {
        const progress = Math.round((progressEvent.loaded * 100) / progressEvent.total);
        // Map the upload's own 0-100% onto the first slice of the pipeline (10-30%)
        setProcessingProgress(10 + progress * 0.2);
      });

      setPaperId(response.paper_id);
      setUploading(false);
      // isProcessing stays true; polling below takes over for the review phase
    } catch (err) {
      setError(err.response?.data?.detail || 'The upload didn’t go through. Try again.');
      setUploading(false);
      setIsProcessing(false);
    }
  };

  const handleRemoveFile = () => {
    setFile(null);
    setError('');
    setUploadProgress(0);
  };

  const handleReset = () => {
    setIsProcessing(false);
    setPaperId(null);
    setError('');
    setFile(null);
    setProcessingProgress(0);
  };

  // Poll review status once a paper has been submitted for review
  useEffect(() => {
    if (!isProcessing || !paperId) return;

    let pollInterval;
    let currentStage = 0;

    const pollStatus = async () => {
      try {
        const response = await paperAPI.pollReviewStatus(paperId);

        if (response.status === 'complete' || response.status === 'completed') {
          setProcessingProgress(100);
          clearInterval(pollInterval);
          setTimeout(() => navigate(`/review/${paperId}`), 1200);
        } else if (response.status === 'failed') {
          setError('The review didn’t finish. Try uploading the paper again.');
          clearInterval(pollInterval);
          setIsProcessing(false);
        } else {
          const newProgress = response.progress ?? Math.min(30 + currentStage * 12, 92);
          setProcessingProgress(newProgress);
          currentStage++;
        }
      } catch (err) {
        if (err.response?.status !== 404) {
          setError('Lost the connection while checking on your review.');
          clearInterval(pollInterval);
          setIsProcessing(false);
        }
      }
    };

    pollStatus();
    pollInterval = setInterval(pollStatus, 2000);

    return () => clearInterval(pollInterval);
  }, [isProcessing, paperId, navigate]);

  // The caption is a pure function of progress — no state needed for it.
  const messageIndex = Math.min(
    Math.floor(processingProgress / (100 / STATUS_MESSAGES.length)),
    STATUS_MESSAGES.length - 1
  );

  return (
    <div className="upload-page">
      <div className="container">
        {isProcessing ? (
          <div className="processing-shell">
            {error ? (
              <div className="state-card card">
                <div className="state-icon state-icon-danger">
                  <IconAlert size={30} />
                </div>
                <h2>Something went wrong</h2>
                <p>{error}</p>
                <button className="btn btn-primary" onClick={handleReset}>
                  Upload another paper
                </button>
              </div>
            ) : (
              <div className="processing-card card">
                <PipelineProgress progress={processingProgress} />

                <p className="status-text mono" aria-live="polite">
                  {processingProgress >= 100 ? 'Review complete.' : STATUS_MESSAGES[messageIndex]}
                </p>

                <div className="progress-section">
                  <div className="progress-bar-container">
                    <div className="progress-bar-fill" style={{ width: `${processingProgress}%` }} />
                  </div>
                  <p className="progress-percentage">{Math.round(processingProgress)}% complete</p>
                </div>

                {processingProgress >= 100 && (
                  <div className="completion-message">
                    <div className="state-icon state-icon-success">
                      <IconCheck size={26} />
                    </div>
                    <p>Redirecting to your report&hellip;</p>
                  </div>
                )}
              </div>
            )}
          </div>
        ) : (
          <div className="upload-layout">
            <div className="upload-hero">
              <h1>
                Upload a paper.
                <br />
                Get a{' '}
                <span className="hero-highlight">
                  blackline
                  <svg className="hero-underline" viewBox="0 0 172 12" preserveAspectRatio="none" aria-hidden="true">
                    <path d="M2 8.5C40 3 120 2 170 7.5" pathLength="1" />
                  </svg>
                </span>{' '}
                review.
              </h1>
              <p>
                Four reviewers score methodology, novelty, citations, and clarity in
                parallel. A critic cross-checks the four verdicts for contradictions
                and turns them into one calibrated decision &mdash; full written
                reasoning included, no months-long queue.
              </p>
              <div className="upload-hero-meta">
                <span className="meta-pill">PDF only</span>
                <span className="meta-pill">Under 10MB</span>
                <span className="meta-pill">4 parallel reviewers</span>
                <span className="meta-pill">No sign-up required</span>
              </div>
            </div>

            <div className="upload-panel card" id="upload-panel">
              {!file ? (
                <div
                  className={`drop-zone ${dragActive ? 'drag-active' : ''}`}
                  onDragEnter={handleDragEnter}
                  onDragOver={handleDrag}
                  onDragLeave={handleDragLeave}
                  onDrop={handleDrop}
                >
                  <div className="drop-zone-icon">
                    <IconUpload size={40} />
                  </div>

                  <h3>Drag and drop your PDF here</h3>
                  <p className="drop-zone-or">or</p>

                  <label htmlFor="file-input" className="btn btn-primary">
                    Browse files
                  </label>
                  <input
                    id="file-input"
                    className="sr-only"
                    type="file"
                    accept=".pdf,application/pdf"
                    onChange={handleFileInput}
                  />

                  <p className="file-requirements">PDF only &middot; Max 10MB</p>
                </div>
              ) : (
                <div className="file-selected">
                  <div className="file-info">
                    <div className="file-icon">
                      <IconFile size={26} />
                    </div>
                    <div className="file-details">
                      <h4>{file.name}</h4>
                      <p>{(file.size / 1024 / 1024).toFixed(2)} MB</p>
                    </div>
                    {!uploading && (
                      <button
                        className="btn-remove"
                        onClick={handleRemoveFile}
                        aria-label="Remove selected file"
                      >
                        <IconClose size={18} />
                      </button>
                    )}
                  </div>

                  {uploading && (
                    <div className="upload-progress">
                      <div className="progress-bar">
                        <div className="progress-fill" style={{ width: `${uploadProgress}%` }} />
                      </div>
                      <p className="progress-text">{uploadProgress}% uploaded</p>
                    </div>
                  )}

                  {!uploading && (
                    <button className="btn btn-primary btn-large" onClick={handleUpload}>
                      Start review
                    </button>
                  )}
                </div>
              )}

              {error && (
                <div className="error-message" role="alert">
                  <IconAlert size={18} />
                  {error}
                </div>
              )}
            </div>
          </div>
        )}
      </div>

      {!isProcessing && (
        <>
          <section id="how-it-works" className="landing-section">
            <div className="container">
              <div className="landing-heading">
                <span className="landing-kicker mono">How it works</span>
                <h2>From PDF to verdict, four steps.</h2>
                <p>No setup, no reviewer accounts to wrangle &mdash; the whole pipeline runs the moment you drop in a file.</p>
              </div>
              <ol className="process-strip">
                {PROCESS_STEPS.map(({ Icon, title, body }, index) => (
                  <li className="process-step" key={title}>
                    <div className="process-step-top">
                      <span className="process-step-number mono">{String(index + 1).padStart(2, '0')}</span>
                      <div className="process-step-icon">
                        <Icon size={22} />
                      </div>
                    </div>
                    <h3>{title}</h3>
                    <p>{body}</p>
                  </li>
                ))}
              </ol>
            </div>
          </section>

          <section id="reviewers" className="landing-section landing-section-alt">
            <div className="container">
              <div className="landing-heading">
                <span className="landing-kicker mono">The four reviewers</span>
                <h2>Every submission gets the same rubric.</h2>
                <p>Each reviewer only ever judges its own dimension &mdash; no single agent can see (or be swayed by) the others' scores.</p>
              </div>
              <div className="reviewer-grid">
                {REVIEWERS.map(({ Icon, title, body }) => (
                  <div className="reviewer-card" key={title}>
                    <div className="reviewer-card-icon">
                      <Icon size={24} />
                    </div>
                    <h3>{title}</h3>
                    <p>{body}</p>
                  </div>
                ))}
              </div>
            </div>
          </section>

          <section className="landing-section">
            <div className="container">
              <div className="landing-heading">
                <span className="landing-kicker mono">Why Researcher</span>
                <h2>Honest feedback, on your timeline.</h2>
              </div>
              <div className="value-grid">
                {VALUE_PROPS.map(({ title, body }) => (
                  <div className="value-card" key={title}>
                    <h3>{title}</h3>
                    <p>{body}</p>
                  </div>
                ))}
              </div>

              <div className="landing-cta card">
                <div>
                  <h3>Ready to see where your paper stands?</h3>
                  <p>Upload a PDF and get scored feedback on methodology, novelty, citations, and clarity in one pass.</p>
                </div>
                <a href="#upload-panel" className="btn btn-primary btn-large">
                  Upload a paper
                </a>
              </div>
            </div>
          </section>
        </>
      )}
    </div>
  );
}

export default UploadPage;
