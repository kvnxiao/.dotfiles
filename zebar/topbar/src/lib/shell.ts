import * as zebar from 'zebar';

const OSASCRIPT = '/usr/bin/osascript';
// `htmlPath` is the canonical path of `dist/<widget>.html`, and the JXA scripts
// are not bundled, so they are resolved from the pack root.
const SCRIPTS_DIR = zebar.currentWidget().htmlPath.replace(/dist\/[^/]+$/, 'scripts/');

export const sleep = (ms: number) => new Promise<void>(resolve => setTimeout(resolve, ms));

export function runScript(name: string, ...args: string[]) {
  return zebar.shellExec(OSASCRIPT, ['-l', 'JavaScript', SCRIPTS_DIR + name, ...args]);
}
