import { useCallback, useRef, useState } from "react";
import { playClick } from "./click";
import { CursorLight } from "./CursorLight";
import { Lamp } from "./Lamp";
import { LampSwitch } from "./Switch";

export default function App() {
  const [on, setOn] = useState(true);
  const stageRef = useRef<HTMLDivElement>(null);

  const toggle = useCallback(() => {
    playClick();
    setOn((v) => !v);
  }, []);

  return (
    <div
      ref={stageRef}
      data-on={on}
      className="relative h-dvh w-screen overflow-hidden bg-black text-white"
    >
      <CursorLight on={on} stageRef={stageRef} />
      <Lamp on={on} />

      <div className="absolute bottom-[6vh] right-3 z-40 min-[900px]:bottom-auto min-[900px]:right-[8vw] min-[900px]:top-1/2 min-[900px]:-translate-y-1/2">
        <LampSwitch on={on} onToggle={toggle} />
      </div>

      <div aria-hidden className="grain pointer-events-none absolute inset-0 z-50" />
    </div>
  );
}
