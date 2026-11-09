# Wisdom native Save / Copy / Preview — TEST handoff

This supersedes Wisdom's standalone Generate/Update workflow. The existing shared
controller owns all publication and stable-slot handling. There is no app resolver,
second generator, profile query authority or backend payload change.

`output-controls.js` opts into `workflow:'saved-copy-preview'` and registers the
instance on `EduvizeProfileAdapter.outputActions`. Accounts' already reviewed generic
Save hook takes the shared lock before the profile PUT. `draft({savedCommit})` builds
only from that exact confirmed config; it never refreshes or rereads live fields for
a Save update. With savedCommit=null, first Copy reads the native saved config fresh.
Subsequent Copy and new-tab navigation are shared controller behavior. Preview URL
uses only the existing current-draft URL builder and preview=1, with no persistence.

The HTML recipe removes only Generate, relabels Open as Otevřít náhled, hides the
internal browser-save node at first paint without adding any local recovery loader.
The hidden local node remains for Accounts to reconcile its internal Save path. Cloud Save is
labelled Uložit nastavení. Other controls are not moved. Legacy native local bootstrap
and autosave are bypassed only for the new workflow; centralized scoped recovery is
the authority for local unsaved drafts. Existing old stored entries are not deleted.

Local draft recovery is explicitly CANCELLED by the user's latest instruction.
No recovery capability is registered, no recovery helper is loaded, and no Restore,
Discard, capture, scoped store or f928 dependency is requested. Any pure helper files
remaining in source history are inert and are excluded from runtime additions.
Existing dirty/beforeunload/profile-navigation guards and confirmed cloud baseline
remain unchanged. No storage.clear or prefix pruning is performed. The hidden
internal local-save node is retained for Accounts' own removal of pre-PUT side effects;
the native Wisdom local startup/autosave bypass remains enabled for this workflow.

## Concrete source-format findings and scoped fixes

The Wisdom legacy preview includes output-integrity/kiosk style roles that the
isolated public page did not include. Existing Wisdom quote roles and their bounded
font sizes are already shared and are kept unchanged. Only app-owned published CSS
adds the preview's header weight650, native font family, kiosk padding0 and hidden
secondary citation details for NSP/kiosk. No News font or geometry is copied.
Public canvas previously used top0 while the native segment viewport centered both
axes. It now uses the same translate(-50%,-50%) with center origin and unchanged
aspect-preserving fit. Web removes that transform as before. Icon markup/assets and
mode-specific metrics stay the existing shared Wisdom implementation.

These are static source and pure technical comparisons. No browser/provider campaign
was run. Exact latest served CSS inputs remain Server's fresh CAS responsibility.
Actual visual acceptance of font/icon/scale/spacing and all relevant orientations
belongs to the user. Native standalone kiosk preview still follows its existing URL
viewport behavior; no claim is made that opening a different physical browser aspect
ratio emulates a configured kiosk viewport. Such a concrete discrepancy must be
reported separately rather than changing shared preview architecture here.

## Finite deployment

Owned runtime replacements: assets/output-controls.js, assets/wisdom.js,
assets/published.js, assets/published.css. No new runtime addition. Native config carrier uses prepare_saved_copy_config.py
over Server's actual fresh config preimage; never replace whole historical HTML.
The helper requires the exact input SHA and produces a separate exclusive candidate
only with a reviewed after SHA. Default is metadata-only dry run. It preserves V3,
environment injection, cache carriers, other handlers and all unrelated bytes.

Shared requirements: the current saved-copy-preview controller with new-tab preview,
Accounts confirmed-Save snapshot hook and central urgent NoDraft patch.
Keep the current shared geometry/kiosk setter, strict saved payload adapter, reader,
backend module, licence/ownership guards and renderer dependency closure unchanged.
No wheel/backend/database migration or additional public route is introduced.

Source changes and targeted tests are handed to main→Server immediately. Only Server
deploys under standing TEST GO, lock/CAS/rollback/headroom. Commit/CI/handoff is not
deployment; no repaired-on-TEST claim until Server returns release ID and URL.
No production change or RC declaration is authorized.
