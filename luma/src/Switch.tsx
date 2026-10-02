// Brass inline cord switch. Drawn in CSS for now (no switch photo yet): the
// ON and OFF layers are separate elements that cross-fade, so either can be
// replaced with an <img src={switchOn}> without touching the button.

const BRASS =
  "linear-gradient(90deg, #3d2b12 0%, #8a6a32 14%, #d9b56c 32%, #f6e2a6 42%, #c79b4f 58%, #7a5a26 80%, #2e200c 100%)";
const ROCKER_FACE =
  "linear-gradient(90deg, #2a1d0b 0%, #6e5223 20%, #c59a52 45%, #e5c785 52%, #9c773a 75%, #3a2a10 100%)";

function SwitchArt({ flipped }: { flipped: boolean }) {
  return (
    <div className="absolute inset-0 flex justify-center">
      {/* cord */}
      <div
        className="absolute inset-y-0 left-1/2 w-[5px] -translate-x-1/2 rounded-full"
        style={{ background: "linear-gradient(90deg, #050505, #3a3a3a 45%, #0a0a0a)" }}
      />
      {/* body */}
      <div
        className="absolute top-1/2 h-[104px] w-[46px] -translate-y-1/2 rounded-[14px]"
        style={{
          background: BRASS,
          boxShadow:
            "inset 0 1px 0 rgba(255,240,200,0.45), inset 0 -2px 3px rgba(0,0,0,0.55), 0 12px 24px rgba(0,0,0,0.7)",
        }}
      >
        {/* seam screws */}
        <div className="absolute left-1/2 top-[7px] h-[6px] w-[6px] -translate-x-1/2 rounded-full bg-[#4a3616] shadow-[inset_0_1px_1px_rgba(0,0,0,0.6)]" />
        <div className="absolute bottom-[7px] left-1/2 h-[6px] w-[6px] -translate-x-1/2 rounded-full bg-[#4a3616] shadow-[inset_0_1px_1px_rgba(0,0,0,0.6)]" />
        {/* rocker well */}
        <div className="absolute inset-x-[9px] top-[22px] bottom-[22px] rounded-[6px] bg-[#1c1307] shadow-[inset_0_2px_4px_rgba(0,0,0,0.8)]">
          {/* rocker, tilted toward its pressed end */}
          <div
            className="absolute inset-[2px] rounded-[5px]"
            style={{
              background: ROCKER_FACE,
              transform: `perspective(90px) rotateX(${flipped ? -16 : 16}deg)`,
              boxShadow: flipped
                ? "inset 0 -10px 10px rgba(0,0,0,0.5)"
                : "inset 0 10px 10px rgba(0,0,0,0.5)",
            }}
          />
        </div>
      </div>
    </div>
  );
}

export function LampSwitch({ on, onToggle }: { on: boolean; onToggle: () => void }) {
  const fade = "opacity var(--t-switch) var(--ease)";
  return (
    <button
      type="button"
      aria-pressed={on}
      aria-label="Illumination"
      onClick={onToggle}
      className="group flex cursor-pointer flex-col items-center rounded-md px-4 py-3 outline-offset-4 focus-visible:outline-2 focus-visible:outline-[#ffc07a]"
    >
      <span className="relative block h-[180px] w-[60px] transition-transform duration-300 group-active:scale-[0.97]">
        <span className="absolute inset-0" style={{ opacity: on ? 1 : 0, transition: fade }}>
          <SwitchArt flipped={false} />
        </span>
        <span
          className="absolute inset-0"
          style={{
            opacity: on ? 0 : 1,
            filter: "brightness(0.62) saturate(0.7)",
            transition: fade,
          }}
        >
          <SwitchArt flipped />
        </span>
      </span>
    </button>
  );
}
