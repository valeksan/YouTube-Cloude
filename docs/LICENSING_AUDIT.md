# Licensing review — 2026-10-27

Baseline: `main` at `7c357fdc71ead92e1decbcfd200fa0d9f6df06fb`.
Status: **incomplete; this change does not certify the whole tree as MIT**.

## Confirmed changes and evidence

- `f8cf70b85bfc619c881b6adf79edf4c329b702f7` added MIT `LICENSE`,
  README/packaging metadata, and removed YTV1 from the format registry/CLI.
- The initial tree `edc2b88` includes `coder.py` without a license file.
  `365cc4b041bb34f492465eb30fa5fa8a41660ada` records the earlier unresolved
  licensing issue. The upstream repository returned `license: null` on the
  audit date; that metadata alone is not proof of either permission or its absence.
- PR #2 was closed without merging. Its closing comment reports an original
  codebase, but no permission document or full provenance comparison is
  attached: https://github.com/valeksan/YouTube-Cloude/pull/2 .
- `v1.1.2` resolves to `35e0068fbd6602b5dc1fe00e48413d540ce539a0`, before
  the MIT/YTV1 change. Current source fixes do not change that release.

## Inherited implementation: unresolved

Compare `git show edc2b88:coder.py` with the baseline source:

| Original code | Current location | Finding |
| --- | --- | --- |
| 16-entry bit-to-BGR table, around line 30 | `core.py`, `COLORS` | Same ordered mapping; still used by YTV2. |
| `"█" * 64` and UTF-8 EOF encoding | `core.py`, `EOF_MARKER` / `EOF_BYTES` | Same framing convention. |
| `read_key_from_file`, around line 556 | `core.py`, `read_key_from_file` | Similar control flow; five consecutive identical lines beginning with `try:`. |
| Encoder/decoder and later fork improvements | `encoder.py`, `decoder.py`, `utils.py`, GUIs | A full function-level comparison against the sources listed in README credits is still needed. |

These observations are evidence of continuity, not a legal conclusion that
each constant or short idiom is copyrightable. Conversely, deleting a format,
renaming symbols, translating comments, or changing a few lines does not prove
independent authorship. Do not describe a cosmetic rewrite as a clean-room rewrite.

For substantive retained material, record the originating revision, author,
license/permission and affected paths. If permission cannot be established,
remove it or arrange a documented independent implementation from requirements.
Do not invent permission, transfer authorship, or remove existing credits.

## Legacy protocol

At the baseline, `FORMATS` exposes YTV2 and YTV3. The active header patterns
require `FORMAT:`; the old no-format header and XOR encryption are absent.
AES-CBC decoding was removed earlier. README and UI descriptions that still
promised YTV1/CBC are corrected by this change. Historical benchmark results
and changelog entries remain explicitly historical.

YTV2 continues to use the color palette/framing conventions above. Removing
YTV1 does not establish that every shared helper is newly authored. No wire
format, palette or EOF changes are made in this licensing PR.

## Android recipes: confirmed third-party source

Comparison reference:
https://github.com/kivy/python-for-android/tree/56c7c5a826ee92615a273dfa13ee05df968a29e8

The Kivy and FreeType recipe implementations are modified versions of the
upstream recipes. The three Kivy patches match upstream after normalizing
line endings/trailing newlines. Their MIT copyright and permission text is
preserved in `recipes/LICENSE`. This reference establishes a comparison,
not an assertion about which revision was originally copied.

FreeType the library has its own licensing alternatives; the MIT license of
the build recipe does not license the native library. Android's SDL, Python,
OpenSSL and other native/target components also need their own inventory.

## FFmpeg and desktop packaging

The baseline workflow extracted only FFmpeg/ffprobe binaries and bundled
them. John Van Sickle explicitly identifies its Linux static builds as
GPLv3. Windows/macOS version/configuration and corresponding sources were
not recorded. The workflow had no explicit step supplying their license
texts or corresponding source.

This change stops copying FFmpeg/ffprobe into new desktop packages. Users
install them separately or select paths in the CLI/GUI. Test-only FFmpeg
installation remains. Restoring bundling is separate work requiring a pinned
build, checksums, all applicable notices, source delivery and verification.

Available Python license files and an environment inventory are collected
before compilation and copied inside desktop outputs, plus a separate ZIP.
This is useful evidence, not a complete native-library SBOM or proof of
license compatibility. Existing release assets have not been unpacked in
this review; no claim is made about every notice already inside them.

The collector requires actual notice files for the runtime and Qt binding
distributions. A metadata-only license name is insufficient. The Linux
PySide6-Essentials, PySide6-Addons and Shiboken6 6.12.0 wheels tested during
this change had no recorded license texts; the new release check rejects
that environment before compilation. Supplying reviewed, version-matched
notices and fulfilling source/relinking obligations remains release work.
Do not bypass the check by removing Qt from `--require`.

README and package metadata now qualify MIT as applying to the maintainer's
own contributions and explicitly mark the inherited-code review as pending.
The existing MIT grant is preserved; no new license or permission from
upstream authors is inferred.

Android release builds are disabled in this change. The Kivy UI and recipes
remain in the tree, but the release workflow no longer builds or publishes an
APK. The current implementation depends on `ffmpeg`/`ffprobe` subprocesses and
hardcodes the GPL `libx264` encoder; Android has no system FFmpeg and the Kivy
UI has no path override, so an APK without a bundled codec cannot perform
encode/decode. Re-enabling Android requires either a reviewed GPL-compliant
bundle (complete corresponding source and notices) or an LGPL FFmpeg build with
a non-GPL H.264 encoder such as MediaCodec, plus a target native-library
inventory. Until then there is nothing to stage into an APK release.

## Release checklist

- [ ] Resolve inherited code provenance and all retained fork contributions.
- [ ] Compare final Nuitka reports/native libraries against notices on each OS.
- [ ] Record exact Qt/PySide/Shiboken versions/modules, corresponding sources,
  and verify the applicable LGPL replacement/relinking route, including Windows
  onefile packaging; or document valid alternative licensing.
- [ ] If Android is re-enabled: inventory APK target Python/native libraries,
  preserve their complete notices, resolve the FFmpeg/libx264 licensing route,
  and fulfill applicable source obligations. Host metadata is insufficient.
- [ ] Inspect old release assets and prepare corrections/source delivery for
  previously bundled FFmpeg and other components as required.
- [ ] Rebuild and inspect each final artifact before publishing a new release.

The workflow creates GitHub releases as drafts pending this review and
honors `dry_run` without creating a release/tag. Build artifacts can still
be downloaded from Actions: a draft flag does not make distribution private
or satisfy licenses. Keep this PR in draft until the remaining scope is reviewed.
