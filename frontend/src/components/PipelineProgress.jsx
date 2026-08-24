import {
  IconParse,
  IconMethodology,
  IconNovelty,
  IconCitation,
  IconClarity,
  IconSynthesize,
  IconReport,
  IconCheck,
} from './icons';
import './PipelineProgress.css';

const AGENTS = [
  { key: 'methodology', label: 'Methodology', Icon: IconMethodology },
  { key: 'novelty', label: 'Novelty', Icon: IconNovelty },
  { key: 'citation', label: 'Citation', Icon: IconCitation },
  { key: 'clarity', label: 'Clarity', Icon: IconClarity },
];

/** Where progress (0-100) puts each real stage of the review graph. */
function stageStatus(progress) {
  const parse = progress >= 15 ? 'done' : 'active';
  const agents = progress < 15 ? 'pending' : progress < 72 ? 'active' : 'done';
  const synthesize = progress < 72 ? 'pending' : progress < 94 ? 'active' : 'done';
  const report = progress < 94 ? 'pending' : progress >= 100 ? 'done' : 'active';
  return { parse, agents, synthesize, report };
}

function Node({ status, Icon, label, className = '' }) {
  return (
    <div className={`pl-node pl-node-${status} ${className}`}>
      <div className="pl-node-icon">
        {status === 'done' ? <IconCheck size={18} /> : Icon && <Icon size={18} />}
      </div>
      <span className="pl-node-label">{label}</span>
    </div>
  );
}

/**
 * Visualizes the actual review graph: parse the PDF, fan out to four
 * reviewers running in parallel, fan back in to the critic, then the
 * report. This mirrors backend/app/graph/graph.py exactly — nothing here
 * implies sequential agent work that isn't happening.
 */
function PipelineProgress({ progress }) {
  const { parse, agents, synthesize, report } = stageStatus(progress);

  return (
    <div className="pipeline" role="group" aria-label="Review pipeline progress">
      <Node status={parse} Icon={IconParse} label="Parse" />

      <div className={`pl-branch pl-branch-${parse === 'pending' ? 'pending' : 'open'}`} aria-hidden="true">
        <span className="pl-branch-line" />
      </div>

      <div className="pl-agents">
        <p className="pl-agents-eyebrow">4 reviewers · running in parallel</p>
        <div className="pl-agents-row">
          {AGENTS.map(({ key, label, Icon }) => (
            <Node key={key} status={agents} Icon={Icon} label={label} className="pl-node-agent" />
          ))}
        </div>
      </div>

      <div className={`pl-branch pl-branch-${agents === 'done' ? 'open' : 'pending'}`} aria-hidden="true">
        <span className="pl-branch-line" />
      </div>

      <Node status={synthesize} Icon={IconSynthesize} label="Synthesize" />
      <Node status={report} Icon={IconReport} label="Report" />
    </div>
  );
}

export default PipelineProgress;
