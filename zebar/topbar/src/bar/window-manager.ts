import { createSignal } from 'solid-js';

import { watchWindowManager, type WindowManagerState } from '../lib/wm';

const [windowManager, setWindowManager] = createSignal<WindowManagerState>();
watchWindowManager(state => setWindowManager(state));

export { windowManager };
