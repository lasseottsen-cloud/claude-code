export type IconId =
  | "BLS"
  | "BMD"
  | "Sevdesk"
  | "Excel"
  | "OneDrive"
  | "Dropbox"
  | "Email"
  | "Craftnote";

export const ICON_POSITIONS: Record<IconId, { x: number; y: number }> = {
  BLS:       { x: 280,  y: 230 },
  BMD:       { x: 1640, y: 230 },
  Sevdesk:   { x: 140,  y: 540 },
  Excel:     { x: 1780, y: 540 },
  OneDrive:  { x: 280,  y: 850 },
  Dropbox:   { x: 1640, y: 850 },
  Email:     { x: 700,  y: 200 },
  Craftnote: { x: 1220, y: 200 },
};

export const CENTER = { x: 960, y: 540 };

export const ICON_RADIUS = 44;
