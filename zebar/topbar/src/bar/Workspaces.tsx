import { createMemo, For, Show, type VoidComponent } from 'solid-js';

import { focusWorkspace } from '../lib/wm';
import { windowManager } from './window-manager';

const KANJI = ['一', '二', '三', '四', '五', '六', '七', '八', '九', '十'];

// Workspace names are stable identities, so <For> keys each button by name.
export const Workspaces: VoidComponent = () => {
  const workspaces = createMemo(() => {
    const current = windowManager();
    if (!current) return [];
    const names = current.occupied.includes(current.focused)
      ? current.occupied
      : [...current.occupied, current.focused];
    return names.toSorted((a, b) => a.localeCompare(b, undefined, { numeric: true }));
  });

  return (
    <Show when={workspaces().length > 0}>
      <div id="spaces">
        <For each={workspaces()}>
          {name => (
            <button
              class="space"
              classList={{ focused: name === windowManager()?.focused }}
              onClick={() => void focusWorkspace(name)}
            >
              {KANJI[Number(name) - 1] ?? name}
            </button>
          )}
        </For>
      </div>
    </Show>
  );
};
