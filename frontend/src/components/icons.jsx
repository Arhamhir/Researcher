/**
 * Shared line-icon set. One consistent stroke weight and viewBox so the
 * same mark for an agent reads identically in the pipeline diagram, the
 * scoreboard, and the detailed report — the icon becomes a recognizable
 * label for that dimension rather than one-off decoration.
 */
const base = {
  viewBox: '0 0 24 24',
  fill: 'none',
  stroke: 'currentColor',
  strokeWidth: 1.6,
  strokeLinecap: 'round',
  strokeLinejoin: 'round',
};

function Svg({ children, size = 22, className, title }) {
  return (
    <svg width={size} height={size} aria-hidden={title ? undefined : true} role={title ? 'img' : undefined} {...base} className={className}>
      {title && <title>{title}</title>}
      {children}
    </svg>
  );
}

/** Methodology — a flask: rigor, experimental design. */
export function IconMethodology(props) {
  return (
    <Svg {...props}>
      <path d="M10 2v5.2L4.8 18.1A2 2 0 0 0 6.6 21h10.8a2 2 0 0 0 1.8-2.9L14 7.2V2" />
      <path d="M8.5 2h7" />
      <path d="M7.5 15h9" />
    </Svg>
  );
}

/** Novelty — fingerprint arcs: how distinct this work is from what exists. */
export function IconNovelty(props) {
  return (
    <Svg {...props}>
      <path d="M12 3a7 7 0 0 0-7 7c0 3.2.6 5.6 1.5 7.8" />
      <path d="M12 3a7 7 0 0 1 7 7c0 1.6-.15 3-.4 4.3" />
      <path d="M8.5 20.2C7.4 17.8 7 14.8 7 12a5 5 0 0 1 9.6-2" />
      <path d="M9.5 21c-1.1-2.6-1.6-5.7-1.6-9a4 4 0 0 1 8 0c0 1 -.1 2 -.3 3" />
      <path d="M12.5 21.5c-.9-2-1.3-4-1.3-6.5" />
    </Svg>
  );
}

/** Citation — a chain link: how this work connects to prior literature. */
export function IconCitation(props) {
  return (
    <Svg {...props}>
      <path d="M9.5 14.5 14.5 9.5" />
      <path d="M11 6.5 12.3 5.2a3.2 3.2 0 0 1 4.5 4.5L15.5 11" />
      <path d="M13 17.5 11.7 18.8a3.2 3.2 0 0 1-4.5-4.5L8.5 13" />
    </Svg>
  );
}

/** Clarity — aligned lines: readable structure and flow. */
export function IconClarity(props) {
  return (
    <Svg {...props}>
      <path d="M4 6h16" />
      <path d="M4 12h16" />
      <path d="M4 18h10" />
    </Svg>
  );
}

/** Parse — a document being read. */
export function IconParse(props) {
  return (
    <Svg {...props}>
      <path d="M7 3h7l4 4v13a1 1 0 0 1-1 1H7a1 1 0 0 1-1-1V4a1 1 0 0 1 1-1Z" />
      <path d="M14 3v4h4" />
      <path d="M9 12.5h6M9 16h4" />
    </Svg>
  );
}

/** Synthesize — converging lines: four reviews becoming one verdict. */
export function IconSynthesize(props) {
  return (
    <Svg {...props}>
      <path d="M5 5v3.2a3 3 0 0 0 1.3 2.5L11 14" />
      <path d="M19 5v3.2a3 3 0 0 1-1.3 2.5L13 14" />
      <path d="M12 14v7" />
      <circle cx="12" cy="16.5" r="0" />
    </Svg>
  );
}

/** Report — a finished, checked document. */
export function IconReport(props) {
  return (
    <Svg {...props}>
      <path d="M6 3.5h9l3 3V20a.5.5 0 0 1-.5.5h-11A.5.5 0 0 1 6 20V4a.5.5 0 0 1 .5-.5Z" />
      <path d="m9.5 12.5 1.8 1.8L14.8 10.5" />
    </Svg>
  );
}

export function IconUpload(props) {
  return (
    <Svg {...props}>
      <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
      <path d="M17 8 12 3 7 8" />
      <path d="M12 3v12" />
    </Svg>
  );
}

export function IconFile(props) {
  return (
    <Svg {...props}>
      <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8Z" />
      <path d="M14 2v6h6" />
    </Svg>
  );
}

export function IconClose(props) {
  return (
    <Svg {...props}>
      <path d="M18 6 6 18" />
      <path d="M6 6l12 12" />
    </Svg>
  );
}

export function IconAlert(props) {
  return (
    <Svg {...props}>
      <circle cx="12" cy="12" r="9.25" />
      <path d="M12 7.5v5.5" />
      <path d="M12 16.2v.1" />
    </Svg>
  );
}

export function IconCheck(props) {
  return (
    <Svg {...props}>
      <circle cx="12" cy="12" r="9.25" />
      <path d="m8 12.5 2.7 2.7L16.2 9.7" />
    </Svg>
  );
}

export function IconChevron(props) {
  return (
    <Svg {...props}>
      <path d="m7 9.5 5 5 5-5" />
    </Svg>
  );
}
