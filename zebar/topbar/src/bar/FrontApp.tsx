import type { VoidComponent } from 'solid-js';

import { windowManager } from './window-manager';

export const FrontApp: VoidComponent = () => <span id="front-app">{windowManager()?.app}</span>;
