import { createSignal, onCleanup, Show, type VoidComponent } from 'solid-js';
import * as zebar from 'zebar';

// Battery body interior in SVG units: the level fills up to this width.
const LEVEL_WIDTH = 19;

export const Battery: VoidComponent = () => {
  const provider = zebar.createProvider({ type: 'battery' });
  const [battery, setBattery] = createSignal(provider.output);
  provider.onOutput(output => setBattery(output));
  onCleanup(() => void provider.stop());

  const percent = () => Math.round(battery()?.chargePercent ?? 0);
  // `isCharging` is false on AC power at full charge or when charging is held.
  const onPower = () => battery()?.state !== 'discharging';
  const levelWidth = () => Math.max((LEVEL_WIDTH * percent()) / 100, percent() > 0 ? 1.5 : 0);

  return (
    <Show when={battery()}>
      <span
        id="battery"
        classList={{
          charging: onPower(),
          critical: !onPower() && percent() < 10,
          low: !onPower() && percent() >= 10 && percent() < 20,
        }}
        role="img"
        aria-label={`Battery ${percent()}%${onPower() ? ', on power' : ''}`}
      >
        <span>{percent()}%</span>
        <svg width="26" height="17" viewBox="0 0 26 17" aria-hidden="true">
          <rect
            x="0.5"
            y="2.5"
            width="22"
            height="12"
            rx="3.5"
            fill="none"
            stroke="currentColor"
            stroke-opacity="0.5"
          />
          <path d="M24 6.5a1.5 1.5 0 0 1 0 4z" fill="currentColor" fill-opacity="0.5" />
          <rect class="level" x="2" y="4" width={levelWidth()} height="9" rx="2" />
          <Show when={onPower()}>
            <path class="bolt" d="M13.8.4 7.2 9.4H11l-1.4 7.2 6.6-9H12.4z" />
          </Show>
        </svg>
      </span>
    </Show>
  );
};
