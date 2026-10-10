import { createSignal, onCleanup, type VoidComponent } from 'solid-js';

const clockFormat = new Intl.DateTimeFormat('en-US', {
  weekday: 'short',
  month: 'short',
  day: 'numeric',
  hour: 'numeric',
  minute: '2-digit',
});

function formatClock(date: Date) {
  const parts = Object.fromEntries(
    clockFormat.formatToParts(date).map(({ type, value }) => [type, value]),
  );
  return `${parts.weekday} ${parts.month} ${parts.day}  ${parts.hour}:${parts.minute} ${parts.dayPeriod}`;
}

export const Clock: VoidComponent = () => {
  const [now, setNow] = createSignal(new Date());
  // Timers pause during sleep, so a once-a-minute timer shows a stale time after wake.
  const timer = setInterval(() => setNow(new Date()), 1000);
  onCleanup(() => clearInterval(timer));
  return <span id="calendar">{formatClock(now())}</span>;
};
