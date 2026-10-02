// Synthesized brass click: a short bandpassed noise burst plus a fast sine ping.
// The AudioContext is created lazily on the first toggle (a user gesture),
// never at module load. Each click's nodes stop and disconnect themselves.

const MASTER_GAIN = 0.14;
const NOISE_SECONDS = 0.018;

let ctx: AudioContext | null = null;
let master: GainNode | null = null;
let noise: AudioBuffer | null = null;

function setup(): { ctx: AudioContext; master: GainNode; noise: AudioBuffer } {
  if (!ctx || !master || !noise) {
    ctx = new AudioContext();
    master = ctx.createGain();
    master.gain.value = MASTER_GAIN;
    master.connect(ctx.destination);

    const length = Math.ceil(ctx.sampleRate * NOISE_SECONDS);
    noise = ctx.createBuffer(1, length, ctx.sampleRate);
    const data = noise.getChannelData(0);
    for (let i = 0; i < length; i++) {
      data[i] = (Math.random() * 2 - 1) * (1 - i / length);
    }
  }
  return { ctx, master, noise };
}

export function playClick(): void {
  const { ctx, master, noise } = setup();
  if (ctx.state === "suspended") void ctx.resume();
  const t = ctx.currentTime;

  const burst = ctx.createBufferSource();
  burst.buffer = noise;
  const band = ctx.createBiquadFilter();
  band.type = "bandpass";
  band.frequency.value = 2200;
  band.Q.value = 1.4;
  const burstGain = ctx.createGain();
  burstGain.gain.setValueAtTime(1, t);
  burstGain.gain.exponentialRampToValueAtTime(0.001, t + NOISE_SECONDS);
  burst.connect(band).connect(burstGain).connect(master);
  burst.onended = () => {
    burst.disconnect();
    band.disconnect();
    burstGain.disconnect();
  };

  const ping = ctx.createOscillator();
  ping.type = "sine";
  ping.frequency.value = 1100;
  const pingGain = ctx.createGain();
  pingGain.gain.setValueAtTime(0.0001, t);
  pingGain.gain.exponentialRampToValueAtTime(0.45, t + 0.002);
  pingGain.gain.exponentialRampToValueAtTime(0.0001, t + 0.08);
  ping.connect(pingGain).connect(master);
  ping.onended = () => {
    ping.disconnect();
    pingGain.disconnect();
  };

  burst.start(t);
  burst.stop(t + NOISE_SECONDS);
  ping.start(t);
  ping.stop(t + 0.09);
}
