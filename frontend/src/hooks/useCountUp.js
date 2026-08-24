import { useEffect, useRef, useState } from 'react';

const prefersReducedMotion = () =>
  typeof window !== 'undefined' &&
  window.matchMedia?.('(prefers-reduced-motion: reduce)').matches;

/**
 * Animates a number counting up to `value` on mount / whenever it changes.
 * Used for score reveals — small, but it's the difference between a report
 * that feels computed live and one that just appears.
 */
export function useCountUp(value, duration = 700, decimals = 1) {
  const [display, setDisplay] = useState(prefersReducedMotion() ? value : 0);
  const frame = useRef(null);

  useEffect(() => {
    const target = Number(value) || 0;

    if (prefersReducedMotion()) {
      // Reduced motion: jump straight to the final value, no rAF loop.
      // eslint-disable-next-line react-hooks/set-state-in-effect
      setDisplay(target);
      return undefined;
    }

    const start = performance.now();
    const from = 0;

    const tick = (now) => {
      const t = Math.min((now - start) / duration, 1);
      const eased = 1 - Math.pow(1 - t, 3); // ease-out-cubic
      setDisplay(from + (target - from) * eased);
      if (t < 1) {
        frame.current = requestAnimationFrame(tick);
      } else {
        setDisplay(target);
      }
    };

    frame.current = requestAnimationFrame(tick);
    return () => cancelAnimationFrame(frame.current);
  }, [value, duration]);

  return display.toFixed(decimals);
}
