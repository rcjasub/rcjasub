import { useEffect, useRef, type RefObject } from "react";

const SIZE = 700;
const FOLLOW = 0.12; // lerp factor per frame

// Ambient warm spill that trails the pointer. Position is written straight to
// the DOM inside requestAnimationFrame -- never React state -- and the loop
// only runs while the light is still catching up to the pointer.
export function CursorLight({
  on,
  stageRef,
}: {
  on: boolean;
  stageRef: RefObject<HTMLDivElement | null>;
}) {
  const lightRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const stage = stageRef.current;
    const light = lightRef.current;
    if (!stage || !light) return;

    const target = { x: 0, y: 0 };
    const pos = { x: 0, y: 0 };
    let raf = 0;
    let inside = false;

    const write = () => {
      light.style.transform = `translate3d(${pos.x - SIZE / 2}px, ${pos.y - SIZE / 2}px, 0)`;
    };

    const tick = () => {
      const dx = target.x - pos.x;
      const dy = target.y - pos.y;
      pos.x += dx * FOLLOW;
      pos.y += dy * FOLLOW;
      write();
      raf = Math.abs(dx) > 0.3 || Math.abs(dy) > 0.3 ? requestAnimationFrame(tick) : 0;
    };

    const onMove = (e: PointerEvent) => {
      if (e.pointerType !== "mouse") return;
      target.x = e.clientX;
      target.y = e.clientY;
      if (!inside) {
        // re-entry: start where the pointer is instead of sweeping across
        inside = true;
        pos.x = target.x;
        pos.y = target.y;
        write();
        light.style.opacity = "1";
      }
      if (!raf) raf = requestAnimationFrame(tick);
    };

    const onLeave = () => {
      inside = false;
      light.style.opacity = "0";
    };

    stage.addEventListener("pointermove", onMove);
    stage.addEventListener("pointerleave", onLeave);
    document.documentElement.addEventListener("mouseleave", onLeave);
    window.addEventListener("blur", onLeave);
    return () => {
      cancelAnimationFrame(raf);
      stage.removeEventListener("pointermove", onMove);
      stage.removeEventListener("pointerleave", onLeave);
      document.documentElement.removeEventListener("mouseleave", onLeave);
      window.removeEventListener("blur", onLeave);
    };
  }, [stageRef]);

  return (
    <div
      aria-hidden
      className="cursor-light pointer-events-none absolute inset-0 z-0 overflow-hidden"
      style={{
        opacity: on ? 1 : 0,
        mixBlendMode: "screen",
        transition: "opacity var(--t-halo) var(--ease)",
      }}
    >
      <div
        ref={lightRef}
        className="absolute left-0 top-0"
        style={{
          width: SIZE,
          height: SIZE,
          opacity: 0,
          background: "radial-gradient(circle, rgba(255, 180, 110, 0.10), transparent 65%)",
          filter: "blur(60px)",
          transition: "opacity 600ms var(--ease)",
          willChange: "transform",
        }}
      />
    </div>
  );
}
