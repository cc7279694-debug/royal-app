# Offline Clash Tracker App

A local React/TypeScript/Vite prototype packaged with Capacitor. Mock mode accepts
invented `source=mock` events. Recorded mode imports a prepared local Oracle-event
JSON and plays it automatically. Assisted mode imports externally prepared
detector candidates and JPEG evidence from user-provided recordings for human
review. The App runs no detector and does not read video or connect to Clash
Royale or live gameplay. The HUD is an ordinary section inside this App. All
text, controls and letter icons are rendered as UI; no game art, model weights
or recording screenshot is shipped in the APK.

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

## Mock demonstration

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

## Recorded Oracle demonstration

Choose **Recorded 模式**, import the private `recorded-oracle-demo.json` supplied
with this module, then start at 1× or 4×. The prepared five verified engine events
appear chronologically, taking the discovered deck from0/8 to5/8. Pause freezes
the virtual clock and history; continue excludes paused wall time. Restart clears
history and starts from0 at the chosen speed. Switching modes resets both views;
leaving the visible App pauses Recorded playback. Refresh/cold restart clears the
in-memory import, so reimport the JSON. Mock Witch/Balloon remains separate.

`RecordedEventSource.fromFile()` accepts only the bounded
`recorded_oracle_demo_v1` envelope: `selection=verified_scored_only`,
`timeline=engine_first_seen_seconds`, source replay/evaluation SHA256, excluded
unscored count and five-field `OpponentCardPlayed` events. Files must be nonempty
and at most2MiB; there are at most5000 events, timestamps0..86400 seconds, known
card IDs and unique event IDs. Recorded confidence remains null. Malformed imports
keep the previous data, paused, and show a safe error. Repeated plays of one card
add history but not another deck slot.

The separate standard-library exporter in `tools/recorded_replay` selects the
evaluation's matched event IDs from the frozen engine replay after checking source
manifest hashes and the5 verified/4 unscored partition. It preserves actual engine
IDs and first-seen times, never copies GT times or invents events. The App does not
filter or rerun the engine. The old raw nine-event projection is not an importable
demo. The private JSON and export receipts remain Git ignored and are not bundled
into the APK. Source hashes/selection labels are provenance metadata, not a digital
signature: arbitrary user-edited JSON is not independently authenticated by the App.

Playback is explicitly retrospective **离线 Oracle 回放**, not live recognition.
Witch retains the documented3s actual confirmation delay. The four unscored outputs
are excluded from this demo only; their history/Unknown status is unchanged.

## Offline Assisted candidate review

Choose **Assisted 模式** and import the private `candidates.json` prepared by
`tools/assisted_tracking`. This is the versioned
`offline_assisted_candidates_v1` packet, separate from Oracle replay. It holds
detector candidates, source/provenance hashes, a bounded selection summary and
native JPEG evidence. It does not import reviewer or confirmation fields. Every
candidate starts **pending**, even when the raw detector engine records a support
time in `confirmed_at`. That field is preserved raw prediction metadata, not an
App decision or human-confirmed play.

Select a candidate, inspect its evidence and use **确认对手卡牌**, **排除候选** or
**应用修正**. Source-pixel boxes scale with their native screenshot and are
explicitly labelled **检测器候选框（未经GT确认）**. A shared frame can contain boxes
from several exported candidates. Card/owner corrections preserve the original
prediction and return the row to pending, requiring a fresh confirmation. Restore
a confirmed or excluded row to pending when needed. The confirmed deck includes
only explicitly confirmed, non-Unknown opponent cards. Repeated confirmations of
one card retain all review records and consume one slot; overflow beyond eight
unique cards is retained and shown. Exclusion is not Negative evidence.

**手动补漏 / 添加 Unknown** adds a separate pending record at a user-entered
recording time. Empty card ID and unknown/own ownership stay outside the confirmed
deck. A known opponent card may then be confirmed explicitly. Manual IDs are
trimmed, lowercased and normalized to underscores, bounded and validated. Display
labels for Hog Rider, Goblin Barrel and Firecracker are available for manual
choices; they do not mean the current detector supports those cards.

The importer bounds files to24MiB, evidence to128 native images, each decoded
JPEG to512KiB, and candidates to5000. It validates the exact schema, IDs/counts,
references, finite times/confidence, source dimensions/xyxy boxes, JPEG MIME and
header dimensions, and decoded-image SHA256. SVG, external URLs and file paths
cannot be used as image sources. Invalid imports keep the previous review.
Hashes establish packet/source consistency, not authentication of arbitrary
user-edited data. A corrupt JPEG that fails rendering displays an error.

Imports, images and user decisions stay only in memory. Reset, switching modes,
refresh or reopening clears Assisted data and requires reimport. There is no
SQLite, IndexedDB, localStorage, migration, persistent review export or cloud
service in this MVP. The private packet is externally selected, ignored and
never bundled in `dist`/the APK or tracked in Git.

Assisted uses its own review reducer and confirmed-card projection. It does not
create `OpponentCardPlayed`, change Oracle selection, run the formal event engine,
declare human GT/training labels or estimate card cycle/elixir. Screenshot
coverage is partial; detector absence does not establish card absence. Mock and
Recorded keep their existing contracts. No native plugin/permission, capture,
cross-App overlay, game interaction, runtime or dependency is added.

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
project's platform and build tools. Generating/syncing the source alone is not
evidence of a built or tested APK. The separately authorized Milestone2 now has
a Debug APK and an actual API37 emulator launch/play/reset check, using ignored
project-local Temurin21.0.12.1+1, Android36 rev2, build-tools35.0.0 and Gradle8.14.3.
There was no App source change, global environment change or release signing.
See [build evidence and commands](../docs/VERIFICATION_MILESTONE2.md).
The merged APK adds only AndroidX's own signature receiver permission; the
absence of capture/overlay/Accessibility/Internet permissions remains verified.
The previous Mock APK's physical-phone smoke was subsequently reported passed by
the user. Module3D has a newly built Debug APK with local native-document-picker
import and automatic5/8 replay tested in an isolated Android emulator; this new
APK's physical-phone acceptance was explicitly confirmed by the user on2026-10-08:
`MODULE_3D_REAL_DEVICE_ACCEPTED` (local import,0/8→5/8, replay controls/speeds, Mock,
and exclusion of unscored events). This records user acceptance, not an agent-run
device test; phone model/OS and device-side checksum were not supplied. See
[Module3D verification](../docs/VERIFICATION_MODULE3D_OFFLINE.md). Native capture or
inference still requires a separate approved module.

## Dependency provenance

Dependencies come from the official npm registry. React, Vite, Tailwind,
Capacitor, Vitest and DefinitelyTyped packages use MIT licenses; TypeScript uses
Apache-2.0. Exact versions and registry integrity hashes are in the lockfile.
Capacitor 8.4.3 is intentionally pinned: the checked latest 8.5.2 CLI introduced
an audited `xcode`/`uuid` development-tool vulnerability, and 8.4.3 avoids it.
There is no dependency upgrade or override of the existing offline Python stack.
