import lampSrc from "../attached_assets/lamp.png";

// Glass panel centre and width as fractions of the (cropped) lamp image.
const GLASS_X = "49.6%";
const GLASS_Y = "19.5%";
const GLASS_WIDTH = 0.74;
const HALO_WIDTH = `${GLASS_WIDTH * 1.6 * 100}%`;

const LAMP_ON = "brightness(1.18) saturate(1.12) contrast(1.04) sepia(0.06)";
const LAMP_OFF = "brightness(0.55) saturate(0.75) contrast(0.95)";

// No element here sets z-index, transform or opacity on the wrappers, so the
// z-10/20/30 layers stack directly in the stage's stacking context.
export function Lamp({ on }: { on: boolean }) {
  return (
    <div className="pointer-events-none absolute inset-x-0 bottom-0 flex select-none justify-center">
      <div className="relative h-[70vh] min-[900px]:h-[90vh]" style={{ aspectRatio: "264 / 1106" }}>
        {/* floor bounce */}
        <div
          aria-hidden
          className="absolute left-1/2 bottom-0 z-10 h-[18vh] w-[55vw]"
          style={{
            translate: "-50% 45%",
            background:
              "radial-gradient(ellipse 60% 40% at 50% 50%, rgba(255, 170, 90, 0.18), transparent 70%)",
            filter: "blur(30px)",
            mixBlendMode: "screen",
            opacity: on ? 1 : 0,
            transition: "opacity var(--t-halo) var(--ease)",
          }}
        />

        {/* halo, behind the glass */}
        <div
          aria-hidden
          className="absolute z-20 aspect-square"
          style={{
            left: GLASS_X,
            top: GLASS_Y,
            width: HALO_WIDTH,
            translate: "-50% -50%",
            mixBlendMode: "screen",
            opacity: on ? 1 : 0,
            transition: "opacity var(--t-halo) var(--ease)",
          }}
        >
          <div className="halo-breathe absolute inset-0">
            <div
              className="halo-drift absolute -inset-1/2"
              style={{
                background: "radial-gradient(circle, rgba(255, 170, 90, 0.22), transparent 60%)",
                filter: "blur(40px)",
              }}
            />
            <div
              className="absolute inset-0"
              style={{
                background: "radial-gradient(circle, rgba(255, 196, 128, 0.55), transparent 35%)",
              }}
            />
          </div>
        </div>

        <img
          src={lampSrc}
          alt="Luma, a cast-iron street lantern with hammered glass panels"
          draggable={false}
          className="relative z-30 h-full w-full select-none object-contain"
          style={{
            filter: on ? LAMP_ON : LAMP_OFF,
            transition: "filter var(--t-lamp) var(--ease)",
          }}
        />

        {/* lit glass: warm light clipped to the lamp's own silhouette */}
        <div
          aria-hidden
          className="absolute inset-0 z-30"
          style={{
            maskImage: `url(${lampSrc})`,
            maskSize: "100% 100%",
            WebkitMaskImage: `url(${lampSrc})`,
            WebkitMaskSize: "100% 100%",
            background: `radial-gradient(ellipse 46% 11% at ${GLASS_X} ${GLASS_Y}, rgba(255, 196, 128, 0.75), rgba(255, 170, 90, 0.25) 55%, transparent 100%)`,
            mixBlendMode: "screen",
            opacity: on ? 1 : 0,
            transition: "opacity var(--t-lamp) var(--ease)",
          }}
        />
      </div>
    </div>
  );
}
