import './styles.css';
import { Music, Pause, Play, Repeat, Shuffle, SkipBack, SkipForward } from 'lucide-solid';
import { createSignal, Show, type VoidComponent } from 'solid-js';
import { render } from 'solid-js/web';
import * as zebar from 'zebar';

import { usePopupWindow } from './lib/popup';
import { runScript, sleep } from './lib/shell';

interface SpotifyState {
  running: boolean;
  state?: 'playing' | 'paused' | 'stopped';
  shuffling?: boolean;
  repeating?: boolean;
  position?: number;
  name?: string;
  artist?: string;
  album?: string;
  artwork?: string;
  duration?: number;
}

type Command = 'status' | 'playpause' | 'next' | 'previous' | 'shuffle' | 'repeat';

const clock = (seconds = 0) => {
  const total = Math.max(0, Math.floor(seconds));
  return `${Math.floor(total / 60)}:${String(total % 60).padStart(2, '0')}`;
};

const [state, setState] = createSignal<SpotifyState>({ running: false });
let latest = 0;
let latestAction = 0;

// A status result is stale once any newer command starts; an action result is
// stale only once a newer action starts, so a poll cannot discard a seek.
async function command(...args: [Command] | ['seek', string]) {
  const id = ++latest;
  const isAction = args[0] !== 'status';
  if (isAction) latestAction = id;
  const { stdout } = await runScript('spotify.js', ...args);
  let next: SpotifyState;
  try {
    next = JSON.parse(stdout);
  } catch {
    return;
  }
  if (isAction ? id === latestAction : id === latest) setState(next);
}

// Each show starts a new generation, and a loop exits once its generation is
// stale, so a hide during an in-flight status check still stops polling.
let generation = 0;
async function poll(current: number) {
  // oxlint-disable-next-line no-unmodified-loop-condition -- hide and show change `generation`
  while (current === generation) {
    // oxlint-disable-next-line no-await-in-loop -- polls are sequential by design
    await command('status').catch(() => {});
    // oxlint-disable-next-line no-await-in-loop -- polls are sequential by design
    await sleep(1000);
  }
}
const { hide } = usePopupWindow('spotify', {
  onShow: () => void poll(++generation),
  onHide: () => {
    generation++;
  },
});
const openSpotify = () => void zebar.shellExec('/usr/bin/open', ['-a', 'Spotify']).then(hide);

const ICON = { size: 16, 'stroke-width': 2 } as const;

const Player: VoidComponent = () => {
  // The seek position while the user drags the slider, in percent.
  const [drag, setDrag] = createSignal<number | null>(null);

  const hasTrack = () => state().running && Boolean(state().name);
  const playing = () => state().state === 'playing';
  const progress = () => {
    const { position = 0, duration } = state();
    return duration ? (position / duration) * 100 : 0;
  };
  const shownProgress = () => drag() ?? progress();
  const elapsed = () => (shownProgress() / 100) * (state().duration ?? 0);

  const title = () =>
    state().running ? state().name || 'Nothing playing' : 'Spotify is not running';
  // Podcasts have no artist, so the artist line shows the show name.
  const artist = () => state().artist || state().album || '';
  const album = () => (state().artist ? state().album || '' : state().name ? 'Podcast' : '');

  return (
    <div class="popup" id="spotify">
      <Show when={state().artwork}>
        {artwork => <img class="backdrop" alt="" src={artwork()} />}
      </Show>
      <div id="player" classList={{ idle: !hasTrack() }}>
        <button id="now-playing" aria-label="Open Spotify" onClick={openSpotify}>
          <Show
            when={state().artwork}
            fallback={
              <span id="cover" class="placeholder">
                <Music size={22} stroke-width={1.75} />
              </span>
            }
          >
            {artwork => <img id="cover" alt="" src={artwork()} />}
          </Show>
          <span id="track">
            <span id="title">{title()}</span>
            <span id="artist">{artist()}</span>
            <span id="album">{album()}</span>
          </span>
        </button>
        <div id="progress">
          <input
            id="seek"
            type="range"
            min="0"
            max="100"
            step="0.1"
            aria-label="Playback position"
            disabled={!hasTrack()}
            value={shownProgress()}
            style={{ '--progress': String(shownProgress() / 100) }}
            onInput={event => setDrag(event.currentTarget.valueAsNumber)}
            onChange={event => {
              const target = Math.round(
                (event.currentTarget.valueAsNumber / 100) * (state().duration ?? 0),
              );
              void command('seek', String(target)).finally(() => setDrag(null));
            }}
          />
          <div id="times">
            <span>{clock(elapsed())}</span>
            <span>{clock(state().duration)}</span>
          </div>
        </div>
        <div id="controls">
          <button
            class="toggle"
            aria-label="Shuffle"
            aria-pressed={Boolean(state().shuffling)}
            onClick={() => void command('shuffle')}
          >
            <Shuffle {...ICON} />
          </button>
          <button aria-label="Previous track" onClick={() => void command('previous')}>
            <SkipBack {...ICON} fill="currentColor" />
          </button>
          <button
            id="playpause"
            aria-label={playing() ? 'Pause' : 'Play'}
            classList={{ paused: !playing() }}
            onClick={() => void command('playpause')}
          >
            <Show when={playing()} fallback={<Play {...ICON} fill="currentColor" />}>
              <Pause {...ICON} fill="currentColor" />
            </Show>
          </button>
          <button aria-label="Next track" onClick={() => void command('next')}>
            <SkipForward {...ICON} fill="currentColor" />
          </button>
          <button
            class="toggle"
            aria-label="Repeat"
            aria-pressed={Boolean(state().repeating)}
            onClick={() => void command('repeat')}
          >
            <Repeat {...ICON} />
          </button>
        </div>
      </div>
    </div>
  );
};

render(() => <Player />, document.getElementById('root')!);
