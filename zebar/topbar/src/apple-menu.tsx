import './styles.css';
import { Activity, Lock, Settings } from 'lucide-solid';
import { For, type VoidComponent } from 'solid-js';
import { Dynamic, render } from 'solid-js/web';
import * as zebar from 'zebar';

import { usePopupWindow } from './lib/popup';

const { hide } = usePopupWindow('apple-menu');

const ITEMS = [
  {
    icon: Settings,
    label: 'Settings',
    run: () => zebar.shellExec('/usr/bin/open', ['-a', 'System Settings']),
  },
  {
    icon: Activity,
    label: 'Activity',
    run: () => zebar.shellExec('/usr/bin/open', ['-a', 'Activity Monitor']),
  },
  {
    icon: Lock,
    label: 'Lock Screen',
    run: () => zebar.shellExec('/usr/bin/pmset', ['displaysleepnow']),
  },
];

const AppleMenu: VoidComponent = () => (
  <div class="popup">
    <For each={ITEMS}>
      {item => (
        // The command runs before the menu hides: hiding first can cancel it.
        <button class="menu-item" onClick={() => void item.run().then(hide)}>
          <Dynamic
            component={item.icon}
            class="menu-icon"
            size={15}
            stroke-width={1.75}
            aria-hidden="true"
          />
          {item.label}
        </button>
      )}
    </For>
  </div>
);

render(() => <AppleMenu />, document.getElementById('root')!);
