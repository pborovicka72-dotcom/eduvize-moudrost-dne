# Wisdom: ordinary output controls V2 — TEST only

This patch follows the app adapter/renderer in PR3. It replaces that commit's unsafe
live-form getter with `EduvizeWisdomOutputAdapter.fromSaved(config,presentation)`.
The compatibility `draft(presentation,config)` requires the same explicit saved
configuration; no form read or default exists in either path.

`output-controls.js` mounts ONE frozen shared OutputActions V2 controller with
`{schoolId,profileId,appId,presentation}`. It passes no slotId, resolver or matcher.
It reuses authenticated school tokens through the existing client. Generate reads
the current saved profile fresh through frozen SavedOutputSettings V2 and feeds
`load(context).config` into the strict getter. Unsaved content is never published.
Missing settings/Presentation or changed profile/token/mode fail closed.

Ordinary native cloud Save stays in the existing profile component. Its adapter
read now preserves values/segment/topics/authors and adds full `presentation`.
It calls no registry operation. Legacy native configurations remain readable;
before first generation the user saves once to record full Presentation.
NSP geometry uses the selected canonical segment; kiosk dimensions come from the
mounted preview iframe's explicit data-preview-width/height. Native apply restores
saved kiosk dimensions through the existing shared
`EduvizeSegmentSelection.setKioskGeometry` setter before mode changes; it never
replaces the iframe or simulates clicks. This requires the reviewed Styles PR33
setter addition (source head ccbfb792b6d1f917dca4fda05cb41e112fd65bea). No inferred defaults
or query/localStorage profile authority is added.

The new Generate/Update button sits in the existing output action row. Existing
Copy and Open controls retain their row; Open becomes a semantic button without
link default navigation. Their legacy query-link handlers are disabled atomically
by the managed flag in the same HTML/JS release. Common V2 owns all three handlers.
Ordinary Save and preview selectors keep their current controllers. There is no
technical publication panel/controller in the Wisdom source or actual C6308
Wisdom config export; the guarded builder refuses unknown technical markup rather
than leaving a second controller mounted. Shared sidebar removal remains owned by
Accounts, outside this app patch.

## Required source/runtime files

Changes against PR3 head c47697ee9267119109fc0e536e28c52cd44af96e:

- config.html: exact new script carriers, Generate button and status, Open button,
  one explicit controls install before profile-adapter-ready.
- assets/wisdom.js: managed guard around the old Copy/Open handlers only.
- assets/output-adapter.js: strict saved-config getter, replacing PR3 getter.
- assets/output-controls.js: app wiring, native Save presentation wrapper.
- assets/load-saved-app.js: exact shared frozen helper, SHA256
  aaed63744c373940d4380e2941ad117af3ca69b3bae24cce9b89e067026207b5.

Shared V2 runtime requirements (Server/Accounts integration, not copies here):

- design-system/output-actions.js SHA256
  48bd6c1ec321c6eb37478ce6ae861999630bfa80d99477c5792cdb040c94c050.
- design-system/output-client.js SHA256
  ef4ce8544cf5a91aff7f3669fcd62205cd0e32d656ad3df4db7b55967c923341.
- Existing nsp-geometry.js, preview-viewport.js, output-modes.js,
  configuration-profiles.js and existing authenticated profile UI.
- Frozen V2 backend slot lookup patches + current registry, never a whole core copy.

The published renderer, backend wheel/module and public dependency closure from
OUTPUT-INTEGRATION.md remain unchanged. No shared CSS or text roles are changed.

The offline script `scripts/apply_wisdom_actions_v2.py` applies only semantic source
carrier hunks to actual staged HTML/JS, preserving cache pins, environment scripts
and other current overlays. Use --write only on a staged builder source tree;
source owner never runs it against a live release. Unknown markup fails closed.

## Proof boundaries

CI adds native Save/read-only and fresh saved-generation regressions, including a
form changed after Save, missing stored data/Presentation, mode mismatch and
token/profile races. Existing adapter, renderer and wheel tests remain.
App binding tests mock only the shared mount/client boundary; frozen shared V2's
separate protocol tests cover its writes, readonly Copy/Open and cross-device lookup.
This is source integration, not a claim that live TEST or layout acceptance passed.
Server must deploy it atomically with the required shared V2 and PR3 renderer/module,
then verify real Save→Generate→anonymous link, Update/same URL, new-browser Copy/Open,
all modes and preserved layout in a coordinated serial TEST slot. No production.
