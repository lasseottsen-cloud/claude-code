import React from "react";
import { COLORS } from "../utils/colors";

interface Particle {
  angle: number;
  speed: number;
  size: number;
  color: string;
}

interface ParticleSystemProps {
  cx: number;
  cy: number;
  progress: number; // 0–1: 0=explosion start, 1=fully dispersed/faded
  count?: number;
  seed?: number;
}

function seededRandom(seed: number): () => number {
  let s = seed;
  return () => {
    s = (s * 1664525 + 1013904223) & 0xffffffff;
    return (s >>> 0) / 0xffffffff;
  };
}

const PARTICLE_COLORS = [
  COLORS.streamCyan,
  COLORS.streamBlue,
  COLORS.glowPurple,
  "#FFFFFF",
  "#FF9800",
];

export const ParticleSystem: React.FC<ParticleSystemProps> = ({
  cx,
  cy,
  progress,
  count = 32,
  seed = 42,
}) => {
  const rand = seededRandom(seed);

  const particles: Particle[] = Array.from({ length: count }, () => ({
    angle: rand() * Math.PI * 2,
    speed: 80 + rand() * 200,
    size: 3 + rand() * 6,
    color: PARTICLE_COLORS[Math.floor(rand() * PARTICLE_COLORS.length)],
  }));

  return (
    <svg
      style={{
        position: "absolute",
        top: 0,
        left: 0,
        width: "100%",
        height: "100%",
        overflow: "visible",
        pointerEvents: "none",
      }}
    >
      {particles.map((p, i) => {
        const dist = p.speed * progress;
        const x = cx + Math.cos(p.angle) * dist;
        const y = cy + Math.sin(p.angle) * dist;
        const opacity = Math.max(0, 1 - progress * 1.2);
        const size = p.size * (1 - progress * 0.5);
        return (
          <circle
            key={i}
            cx={x}
            cy={y}
            r={size}
            fill={p.color}
            opacity={opacity}
            style={{ filter: `blur(${(1 - progress) * 1.5}px)` }}
          />
        );
      })}
    </svg>
  );
};
