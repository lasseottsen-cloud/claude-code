import type { IconId } from "./layout";

// Each icon has a color accent and a simple SVG shape descriptor
export const ICON_CONFIG: Record<
  IconId,
  { color: string; emoji: string; label: string }
> = {
  BLS:       { color: "#FF6B35", emoji: "📊", label: "BLS" },
  BMD:       { color: "#E53935", emoji: "📋", label: "BMD" },
  Sevdesk:   { color: "#00BCD4", emoji: "🧾", label: "Sevdesk" },
  Excel:     { color: "#217346", emoji: "📈", label: "Excel" },
  OneDrive:  { color: "#0078D4", emoji: "☁️",  label: "OneDrive" },
  Dropbox:   { color: "#0061FF", emoji: "📦", label: "Dropbox" },
  Email:     { color: "#9C27B0", emoji: "✉️",  label: "E-Mail" },
  Craftnote: { color: "#FF9800", emoji: "🔨", label: "Craftnote" },
};
