import React from "react";
import { COLORS } from "../utils/colors";

interface DataStreamLineProps {
  x1: number;
  y1: number;
  x2: number;
  y2: number;
  progress: number; // 0–1: how far the stream has traveled
  opacity?: number;
  color?: string;
  width?: number;
  curved?: boolean;
}

export const DataStreamLine: React.FC<DataStreamLineProps> = ({
  x1,
  y1,
  x2,
  y2,
  progress,
  opacity = 1,
  color = COLORS.streamCyan,
  width = 1.5,
  curved = true,
}) => {
  const dx = x2 - x1;
  const dy = y2 - y1;
  const len = Math.sqrt(dx * dx + dy * dy);

  // Control point for cubic bezier (perpendicular offset)
  const mx = (x1 + x2) / 2;
  const my = (y1 + y2) / 2;
  const offset = curved ? len * 0.15 : 0;
  const cx = mx - (dy / len) * offset;
  const cy = my + (dx / len) * offset;

  const pathD = `M ${x1} ${y1} Q ${cx} ${cy} ${x2} ${y2}`;

  // Approximate path length for dash animation
  const pathLen = len * 1.05;
  const dashLen = pathLen * 0.3;
  const dashOffset = pathLen - progress * (pathLen + dashLen);

  return (
    <svg
      style={{
        position: "absolute",
        top: 0,
        left: 0,
        width: "100%",
        height: "100%",
        overflow: "visible",
        opacity,
        pointerEvents: "none",
      }}
    >
      {/* Base line (faint) */}
      <path
        d={pathD}
        fill="none"
        stroke={color}
        strokeWidth={width * 0.4}
        strokeOpacity={0.2}
      />
      {/* Animated traveling dash */}
      <path
        d={pathD}
        fill="none"
        stroke={color}
        strokeWidth={width}
        strokeLinecap="round"
        strokeDasharray={`${dashLen} ${pathLen}`}
        strokeDashoffset={dashOffset}
        style={{ filter: `drop-shadow(0 0 4px ${color})` }}
      />
    </svg>
  );
};
