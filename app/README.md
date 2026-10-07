# Simulated Clash Tracker App

A local React/TypeScript/Vite prototype packaged with Capacitor. It accepts only
invented `source=mock` events; it has no connection to a detector, a recording,
Clash Royale or live gameplay. The HUD is an ordinary non-interactive section
inside this App. All text, controls and letter icons are rendered as UI; no game
art, model weights or screenshot is shipped.

## Run locally

Use Node 24 and npm 11. Direct dependencies are pinned in `package.json` and
transitive dependencies in `package-lock.json`.

```powershell
Set-Location 'E:\CODEX\royal app\app'
npm.cmd ci
npm.cmd test
npm.cmd run typecheck
npm.cmd run build
npm.cmd run preview
```

Preview binds only to `127.0.0.1`, normally at
`http://127.0.0.1:4173`. `npm.cmd run dev` provides local development at port 5173.
Runtime fonts and assets are bundled or use system fonts; there is no cloud,
account, API or remote font requirement.

## Demonstration

The initial state is `已发现 0/8`. Each button click consumes exactly one event:
Witch at 12 seconds, then Balloon at 28 seconds, giving `已发现 2/8`.
The playback button is then disabled. Reset clears the complete in-memory state
and allows replay. Refresh also clears it. There is no localStorage, IndexedDB,
SQLite or persistent user data to migrate or back up in this resettable demo.

The independent event consumer validates the five typed fields, rejects future
sources and unexpected fields, preserves accepted events on input error, and
deduplicates event IDs. An identical replay is a no-op; a conflicting ID is
rejected. History sorts by timestamp and then ASCII event ID. Discoveries use
first occurrence in that order, show at most eight unique cards and explicitly
retain later unique cards as overflow. Multiple events for one card do not
increase the discovered count. The fixed mock stream has no overflow.

The event interface has no observation converter. Detection, deployment
confirmation, cycle, evolution and elixir remain outside this prototype.

## Android source project

```powershell
npm.cmd run android:sync
```

`android/` is generated from the official Capacitor package and contains a normal
single-activity WebView App. Build assets are copied from local `dist/`; the
Capacitor configuration has no remote `server.url`. No overlay, capture,
Accessibility, input-control or Internet permission is declared. Unused template
file-provider plumbing is removed because this prototype uses no shared files.

Android build requires a local JDK and an Android SDK containing the generated
project's platform and build tools. Generating/syncing the source is not evidence
of a built or tested APK. This task does not install system tools or publish an
App. Native capture or inference would require a separate approved module.

## Dependency provenance

Dependencies come from the official npm registry. React, Vite, Tailwind,
Capacitor, Vitest and DefinitelyTyped packages use MIT licenses; TypeScript uses
Apache-2.0. Exact versions and registry integrity hashes are in the lockfile.
Capacitor 8.4.3 is intentionally pinned: the checked latest 8.5.2 CLI introduced
an audited `xcode`/`uuid` development-tool vulnerability, and 8.4.3 avoids it.
There is no dependency upgrade or override of the existing offline Python stack.
