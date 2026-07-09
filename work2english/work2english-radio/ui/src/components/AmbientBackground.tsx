import { useMemo } from "react";

/**
 * AmbientBackground — the deep-space stage everything floats on.
 *
 * Three slow aurora blobs drift (violet + cyan + deep indigo), a low-density
 * particle field rises slowly, and a faint vignette frames the dashboard.
 * Motion is deliberately low-frequency: this is a calm presence, not a screen
 * saver. Honors prefers-reduced-motion via CSS (see index.css).
 */

interface Particle {
  left: string;
  size: string;
  delay: string;
  duration: string;
  opacity: number;
}

function buildParticles(count: number): Particle[] {
  // Deterministic so we don't reshuffle every render.
  return Array.from({ length: count }, (_, i) => {
    const seed = (i * 9301 + 49297) % 233280;
    const rnd = seed / 233280;
    const rnd2 = ((i * 4099 + 7919) % 233280) / 233280;
    return {
      left: `${Math.round(rnd * 100)}%`,
      size: `${1 + Math.round(rnd2 * 2.5)}px`,
      delay: `${(rnd2 * -40).toFixed(1)}s`,
      duration: `${(28 + rnd * 24).toFixed(0)}s`,
      opacity: 0.15 + rnd2 * 0.4,
    };
  });
}

export default function AmbientBackground() {
  const particles = useMemo(() => buildParticles(28), []);

  return (
    <div
      aria-hidden
      className="pointer-events-none fixed inset-0 overflow-hidden"
    >
      {/* Base gradient */}
      <div className="absolute inset-0 bg-[radial-gradient(120%_120%_at_50%_-10%,#0b0f1f_0%,#05060b_55%,#030408_100%)]" />

      {/* Aurora blobs */}
      <div className="absolute -top-32 -left-24 h-[42rem] w-[42rem] rounded-full bg-iris/25 blur-[140px] animate-drift" />
      <div
        className="absolute top-1/3 -right-32 h-[38rem] w-[38rem] rounded-full bg-azure/15 blur-[150px] animate-drift"
        style={{ animationDelay: "-8s" }}
      />
      <div
        className="absolute -bottom-40 left-1/3 h-[34rem] w-[34rem] rounded-full bg-plasma/15 blur-[150px] animate-drift"
        style={{ animationDelay: "-16s" }}
      />

      {/* Fine grid texture */}
      <div
        className="absolute inset-0 opacity-[0.04]"
        style={{
          backgroundImage:
            "linear-gradient(rgba(255,255,255,0.6) 1px, transparent 1px), linear-gradient(90deg, rgba(255,255,255,0.6) 1px, transparent 1px)",
          backgroundSize: "64px 64px",
          maskImage:
            "radial-gradient(100% 70% at 50% 40%, black 30%, transparent 80%)",
        }}
      />

      {/* Rising particles */}
      {particles.map((p, i) => (
        <span
          key={i}
          className="absolute bottom-[-10px] rounded-full bg-mist animate-drift"
          style={{
            left: p.left,
            width: p.size,
            height: p.size,
            opacity: p.opacity,
            animationDelay: p.delay,
            animationDuration: p.duration,
            boxShadow: "0 0 6px rgba(192,132,252,0.5)",
          }}
        />
      ))}

      {/* Vignette */}
      <div className="absolute inset-0 bg-[radial-gradient(120%_120%_at_50%_50%,transparent_60%,rgba(0,0,0,0.55)_100%)]" />
    </div>
  );
}
