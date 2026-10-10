import './styles.css';
import type { VoidComponent } from 'solid-js';
import { render } from 'solid-js/web';

import { AppleLogo } from './bar/AppleLogo';
import { Battery } from './bar/Battery';
import { Clock } from './bar/Clock';
import { FrontApp } from './bar/FrontApp';
import { PopupButton } from './bar/PopupButton';
import { SpotifyIcon } from './bar/SpotifyIcon';
import { Workspaces } from './bar/Workspaces';

const Bar: VoidComponent = () => (
  <div id="bar">
    <div class="side">
      <PopupButton popup="apple-menu" width={180} height={108} id="apple" label="Apple menu">
        <AppleLogo />
      </PopupButton>
      <Workspaces />
      <FrontApp />
    </div>
    {/* Empty column under the notch. */}
    <div />
    <div class="side right">
      <PopupButton popup="spotify" width={320} height={185} id="spotify-button" label="Spotify">
        <SpotifyIcon />
      </PopupButton>
      <Battery />
      <Clock />
    </div>
  </div>
);

render(() => <Bar />, document.getElementById('root')!);
