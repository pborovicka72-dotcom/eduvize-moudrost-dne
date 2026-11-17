# Wisdom public output — TEST integration

This is an additive application adapter and renderer. It does not replace the registry,
output actions, profile storage, shared typography, licence checks or gateway policy.
No production deployment is authorized.

## Backend

Build `eduvize-wisdom-output` from the reviewed commit, then install the wheel into
the administration image alongside its existing `eduvize_admin` package.
Python >=3.12; the only Python dependency is pydantic >=2.8,<3, already required by core.
The wheel includes `eduvize_wisdom/data/approved.json`. Its bytes must equal the editor's
`data/approved.json`; the CI verifies this. Publication uses these approved packaged
bytes, not arbitrary browser content or external URLs.

Add `eduvize_wisdom.output_adapter` to the EXISTING comma-separated
`EDUVIZE_OUTPUT_ADAPTER_MODULES`; retain all other modules. Do not duplicate a wisdom
adapter in another registry. `get_output_adapters()` returns the existing
`Adapter(validate, '/eduvize-moudrost-dne/published.html', prepare=prepare)` interface.
Core owns profile binding, active-profile policy, app.wisdom entitlement, idempotency,
revisions, atomic publication and public theme checks. This app adds no private API.

## Existing common action registration

Load `assets/output-adapter.js` in the existing config page after its profile adapter.
The common action owner can call `EduvizeWisdomOutputAdapter.draft(presentation)`;
it awaits and validates the existing profile adapter and returns the closed v1 draft.
It creates no controls or resolver. Its common-action caller must first complete the
normal cloud profile load/save and provide the verified context and canonical
presentation, as for the other apps. The getter maps the existing form as follows:

```js
const config = EduvizeProfileAdapter.read();
const payload = {
  audience: config.values.audience,
  dailyCount: Number(config.values.dailyCount),
  authorRepeat: config.values.authorRepeat,
  showSourceLink: config.values.showSourceLink,
  topics: config.topics,
  authors: config.authors
};
```

The common action owner supplies the existing schemaVersion=1/payloadVersion=1 draft
and canonical Presentation from the selected web/NSP/kiosk mode and geometry.
Do not put outputType, segment, school/profile IDs, arbitrary quotes, source URLs or
theme in the payload. Validate the existing form first. Unknown filters and an empty
filtered corpus reject the draft. Generation/update uses the shared actions only.
The existing query URL builder remains an admin preview, not a published link.

`prepare` freezes `{settings,catalogSHA256,quotes}` and no media into the snapshot.
Only allowlisted public quote fields leave the adapter. Source selection is immutable
until the ordinary update/publish operation; profile-active styling is fetched from
the output-scoped theme endpoint. Daily quote rotation uses Europe/Prague.

## Static renderer and dependency allowlist

Deploy only these app runtime additions:

- `/eduvize-moudrost-dne/published.html`
- `/eduvize-moudrost-dne/assets/published.js`
- `/eduvize-moudrost-dne/assets/published.css`

Reuse the CURRENT coordinated styles release, preserving News overlays and repaired
Wisdom roles. The renderer's exact same-origin static closure under
`/eduvize-styly/design-system/` is:

- `admin-tokens.css`, `app-icons.css`, `editorial-output.css`, `output-header.css`
- `kiosk-reading.css` (imported by output-header.css)
- `nsp-geometry.js`, `segment-profile.js`, `app-icons.js`
- `output-client.js`, `output-runtime.js`, `editorial-output.js`
- `assets/eduvize-logo-compact-animated.svg`

No legacy active-theme/admin-auth/output-modes/output-header.js/segment-display.js,
settings.js/wisdom.js or public catalog fetch is needed. Do not grant anonymous access
to legacy configuration pages or private profile endpoints. An optional interactive
citation opens a public HTTPS source only when enabled; display mode has no link.

Dynamic reads are solely `/api/public/v1/outputs/{id}` and its `/theme`, authorized by
the existing core. `/o/{id}` resolves to the fixed renderer with `edu-output={id}`.
No profile query authority, cookies or administrator session are required by the
renderer. Preserve core revoked/licence/profile checks and existing security policy.

## Checks and release acceptance

Portable GitHub CI runs closed payload/catalog tests, renderer lifecycle/timezone
tests, wheel build and isolated installed-wheel catalog loading. Private core is not
copied into this repository; registry HTTP integration tests are run with the actual
reviewed core by the combined TEST builder:

```sh
python -m unittest discover -s tests -p 'test_output_adapter.py' -v
```

Local integration also covers create/publish, all modes, private ownership, immutable
drafts, stable URL on update, changed theme, restart, removed licence and revocation.
This does not replace live acceptance. Server remains the sole VPS executor.
After deployment use the existing test profile through ordinary generate/update UI:
verify anonymous snapshot+theme+renderer, short/long quotes, author and whitespace in
large landscape/portrait NSP preview AND actual output, plus web/kiosk smoke. Record
the actual output URL/release/geometry and keep production untouched. No SQL seeding,
profile creation/deletion or manual publication panel is needed.
