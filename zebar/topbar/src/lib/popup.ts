import { LogicalPosition } from '@tauri-apps/api/dpi';
import { Window } from '@tauri-apps/api/window';
import * as zebar from 'zebar';

import { sleep } from './shell';

const BAR_HEIGHT = 38;
const POPUP_Y = BAR_HEIGHT + 4;

// Must match `monitorSelection` in the bar preset in zpack.json.
const MONITOR = { type: 'primary' } as const;

interface PopupRequest {
  at: number;
  open: boolean;
  x: number;
}

interface PopupHidden {
  at: number;
  reason: 'blur' | 'escape' | 'request';
}

const key = (kind: string, name: string) => `popup-${kind}:${name}`;
const nextFrame = () => new Promise<void>(resolve => requestAnimationFrame(() => resolve()));

function readJson(name: string): Record<string, unknown> | null {
  try {
    const value: unknown = JSON.parse(localStorage.getItem(name) ?? 'null');
    return typeof value === 'object' && value !== null ? { ...value } : null;
  } catch {
    return null;
  }
}

function readRequest(name: string): PopupRequest | null {
  const value = readJson(key('request', name));
  const { at, open, x } = value ?? {};
  return typeof at === 'number' && typeof open === 'boolean' && typeof x === 'number'
    ? { at, open, x }
    : null;
}

function readHidden(name: string): PopupHidden | null {
  const value = readJson(key('hidden', name));
  const { at, reason } = value ?? {};
  return typeof at === 'number' &&
    (reason === 'blur' || reason === 'escape' || reason === 'request')
    ? { at, reason }
    : null;
}

const writeRequest = (name: string, request: PopupRequest) =>
  localStorage.setItem(key('request', name), JSON.stringify(request));

function popupX(anchor: HTMLElement, width: number) {
  const rect = anchor.getBoundingClientRect();
  const centered = rect.left + rect.width / 2 - width / 2;
  return Math.round(Math.min(Math.max(centered, 8), window.innerWidth - width - 8));
}

function startPopup(name: string, x: number, width: number, height: number) {
  return zebar.startWidget(name, {
    anchor: 'top_left',
    offsetX: `${x}px`,
    offsetY: `${POPUP_Y}px`,
    width: `${width}px`,
    height: `${height}px`,
    monitorSelection: MONITOR,
    dockToEdge: { enabled: false, edge: null, windowMargin: '0px' },
  });
}

/**
 * Create the popup widget `name` hidden, and return handlers for its anchor
 * button: `press` on pointer down and `toggle` on click. `onOpenChange` runs
 * with the popup's requested or reported open state; `dispose` stops it.
 *
 * - The bar decides whether a click opens or closes the popup, and stores the
 *   requested state under one key, so the popup applies only the latest request.
 * - Popups are created once and then hidden and shown, because Zebar 3.3.1
 *   leaks a native window each time a widget closes.
 */
export function createPopup(
  name: string,
  anchor: HTMLElement,
  width: number,
  height: number,
  onOpenChange: (open: boolean) => void,
) {
  void startPopup(name, popupX(anchor, width), width, height);
  let pressedAt = 0;

  const onStorage = (event: StorageEvent) => {
    if (event.key === key('shown', name)) onOpenChange(true);
    if (event.key === key('hidden', name)) onOpenChange(false);
  };
  window.addEventListener('storage', onStorage);

  const press = () => {
    pressedAt = Date.now();
  };

  const toggle = async () => {
    const hidden = readHidden(name);
    // Pressing the anchor of an open popup blurs the popup, which hides it
    // before the click arrives; that click must not reopen it.
    if (hidden?.reason === 'blur' && hidden.at >= pressedAt - 100) return;

    const last = readRequest(name);
    const shownAt = Number(localStorage.getItem(key('shown', name)) ?? 0);
    // An open request the popup never acknowledged within 2 s did not open it.
    const isOpen =
      last !== null &&
      last.open &&
      last.at > (hidden?.at ?? 0) &&
      (shownAt >= last.at || Date.now() - last.at < 2000);
    const request: PopupRequest = { at: Date.now(), open: !isOpen, x: popupX(anchor, width) };
    writeRequest(name, request);
    onOpenChange(request.open);
    if (!request.open) return;

    // macOS suspends the page of a window hidden for more than a few seconds,
    // so the popup misses the request until its window is visible again. The bar
    // shows the window itself, and the resumed page then applies the request.
    try {
      const label = localStorage.getItem(key('instance', name));
      const popupWindow = label ? await Window.getByLabel(label) : null;
      await popupWindow?.setPosition(new LogicalPosition(request.x, POPUP_Y));
      await popupWindow?.show();
    } catch {
      // The acknowledgement wait below recreates the popup.
    }

    // A hidden webview can take over a second to run its storage listener.
    for (let waited = 0; waited < 2000; waited += 100) {
      if (Number(localStorage.getItem(key('shown', name)) ?? 0) >= request.at) return;
      // oxlint-disable-next-line no-await-in-loop -- polls are sequential by design
      await sleep(100);
      // oxlint-disable-next-line no-await-in-loop -- a newer click replaces this request
      if (readRequest(name)?.at !== request.at) return;
    }
    // No acknowledgement means the popup is gone, for example after a reload.
    writeRequest(name, { ...request, at: Date.now() });
    await startPopup(name, request.x, width, height);
  };

  return { press, toggle, dispose: () => window.removeEventListener('storage', onStorage) };
}

/**
 * Manage the current popup widget's window: show it on request from the bar,
 * and hide it on blur or Escape.
 *
 * Popup widgets must keep `zOrder: "normal"`: Zebar 3.3.1 applies `top_most`
 * to a widget started at runtime off the main thread, and AppKit aborts.
 */
export function usePopupWindow(
  name: string,
  events: { onShow?: () => void; onHide?: () => void } = {},
) {
  const widget = zebar.currentWidget();
  const tauriWindow = widget.tauriWindow;
  let visible = false;
  // Each show or hide takes a new token and stops after an await once a newer
  // one starts, so the last request wins even while window calls are pending.
  let transition = 0;

  const show = async (request: PopupRequest) => {
    const id = ++transition;
    visible = true;
    await tauriWindow.setPosition(new LogicalPosition(request.x, POPUP_Y));
    if (id !== transition) return;
    await tauriWindow.show();
    if (id !== transition) return;
    // Added after the window is visible so the entrance transition runs. A hide
    // before the next frame must win, or the hidden popup keeps `shown`.
    document.body.classList.remove('hiding');
    requestAnimationFrame(() => {
      if (visible) document.body.classList.add('shown');
    });
    localStorage.setItem(key('shown', name), String(Date.now()));
    events.onShow?.();
  };
  const hide = async (reason: PopupHidden['reason']) => {
    if (!visible) return;
    const id = ++transition;
    visible = false;
    // macOS shows a window's last drawn frame when the window reappears, so the
    // transparent state must be drawn, without a transition, before hiding.
    document.body.classList.add('hiding');
    document.body.classList.remove('shown');
    const hidden: PopupHidden = { at: Date.now(), reason };
    localStorage.setItem(key('hidden', name), JSON.stringify(hidden));
    events.onHide?.();
    await nextFrame();
    await nextFrame();
    if (id === transition) await tauriWindow.hide();
  };

  // A newer copy of this popup replaces this one.
  localStorage.setItem(key('instance', name), widget.id);
  const apply = (request: PopupRequest | null) => {
    if (request?.open && Date.now() - request.at < 2000) void show(request);
    else void hide('request');
  };
  window.addEventListener('storage', event => {
    if (event.key === key('instance', name) && event.newValue !== widget.id) void widget.close();
    if (event.key === key('request', name)) apply(readRequest(name));
  });
  window.addEventListener('blur', () => void hide('blur'));
  window.addEventListener('keydown', event => {
    if (event.key === 'Escape') void hide('escape');
  });

  apply(readRequest(name));
  if (!visible) void tauriWindow.hide();

  return { hide: () => hide('request') };
}
