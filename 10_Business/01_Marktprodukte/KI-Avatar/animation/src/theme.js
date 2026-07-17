// Design-System des AI Business Checker — eine Quelle für alle Szenen.
export const THEME = {
  bg: '#0e1726',
  bgCard: '#16233a',
  ink: '#f3f6fb',
  muted: '#8fa3bf',
  teal: '#19b8a6',
  coral: '#ef5350',
  amber: '#f5a623',
  line: '#26364f',
  font: 'Segoe UI, Inter, system-ui, sans-serif',
};

// Ampel für den Risiko-Score (0 = harmlos, 10 = Finger weg)
export const scoreColor = (score) =>
  score >= 7 ? THEME.coral : score >= 4 ? THEME.amber : THEME.teal;

export const scoreLabel = (score) =>
  score >= 7 ? 'HOHES RISIKO' : score >= 4 ? 'VORSICHT GEBOTEN' : 'UNAUFFÄLLIG';
