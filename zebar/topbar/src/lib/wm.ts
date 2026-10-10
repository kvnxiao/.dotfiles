// AeroSpace adapter. Replace this module to support another window manager;
// the bar only uses `watchWindowManager` and `focusWorkspace`.
import * as zebar from 'zebar';

import { sleep } from './shell';

export interface WindowManagerState {
  focused: string;
  occupied: string[];
  app: string;
}

const AEROSPACE = '/opt/homebrew/bin/aerospace';
const EVENTS = ['focused-workspace-changed', 'focus-changed', 'window-detected'];
// AeroSpace reports Zebar as focused while a popup has focus.
const IGNORED_APPS = new Set(['Zebar']);

const run = (args: string[]) => zebar.shellExec(AEROSPACE, args);
const lines = (stdout: string) =>
  stdout
    .split('\n')
    .map(line => line.trim())
    .filter(Boolean);

async function getState(): Promise<WindowManagerState | null> {
  const [focused, occupied, app] = await Promise.all([
    run(['list-workspaces', '--focused']),
    run(['list-workspaces', '--monitor', 'all', '--empty', 'no']),
    run(['list-windows', '--focused', '--format', '%{app-name}']),
  ]);
  if (focused.code !== 0 || occupied.code !== 0) return null;
  return {
    focused: focused.stdout.trim(),
    occupied: lines(occupied.stdout),
    app: app.code === 0 ? app.stdout.trim() : '',
  };
}

export const focusWorkspace = (name: string) => run(['workspace', name]);

export function watchWindowManager(onChange: (state: WindowManagerState) => void) {
  let app = '';
  let running = false;
  let again = false;
  // Runs one query at a time; events during a run collapse into one more run.
  const refresh = async () => {
    again = true;
    if (running) return;
    running = true;
    while (again) {
      again = false;
      // oxlint-disable-next-line no-await-in-loop -- runs are sequential by design
      const state = await getState().catch(() => null);
      if (!state) continue;
      if (!IGNORED_APPS.has(state.app)) app = state.app;
      onChange({ ...state, app });
    }
    running = false;
  };

  // Zebar can drop the exit event of a process that exits before its listener
  // is registered, so only subscribe once the AeroSpace server answers.
  const connect = async () => {
    // oxlint-disable-next-line no-await-in-loop -- retries are sequential by design
    while (!(await getState().catch(() => null))) await sleep(2000);
    const proc = await zebar.shellSpawn(AEROSPACE, ['subscribe', ...EVENTS]);
    proc.onStdout(() => void refresh());
    proc.onExit(() => setTimeout(() => void connect(), 2000));
    void refresh();
  };
  void connect();

  // AeroSpace emits no event when a window on an unfocused workspace closes.
  setInterval(() => void refresh(), 10000);
}
