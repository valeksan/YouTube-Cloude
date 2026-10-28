# Third-party notices

The root MIT license describes the maintainer's own contributions. It does
not replace licenses of dependencies or establish rights over inherited code.
The unresolved provenance findings are in [docs/LICENSING_AUDIT.md](docs/LICENSING_AUDIT.md).

## Source included in this repository

`recipes/freetype/__init__.py`, `recipes/kivy/__init__.py`, and
`recipes/kivy/*.patch` are derived from
[python-for-android](https://github.com/kivy/python-for-android).
Copyright (c) 2010-2025 Kivy Team and other contributors.
The full MIT license is in [recipes/LICENSE](recipes/LICENSE).
The recipes contain local changes described in their module docstrings.
The audit records the upstream revision used for comparison; it does not
claim that revision was the original import source.

## Python dependencies

These are upstream license families, not an exhaustive bill of materials
for a particular executable. Use the license texts and third-party notices
from the exact installed versions, including native libraries in wheels.

| Component | Upstream license | Source |
| --- | --- | --- |
| NumPy | BSD-3-Clause | https://github.com/numpy/numpy |
| Pillow | MIT-CMU | https://github.com/python-pillow/Pillow |
| PyCryptodome | BSD-2-Clause / public domain, plus version-specific third-party notices | https://github.com/Legrandin/pycryptodome |
| reedsolo | Unlicense OR MIT-0 in current upstream; check the selected release | https://github.com/tomerfiliba-org/reedsolomon |
| PySide6, Shiboken6, Qt | LGPLv3 / GPLv3 / commercial alternatives, depending on component | https://code.qt.io/cgit/pyside/pyside-setup.git/ |
| Kivy, Plyer, python-for-android, Buildozer | MIT; native dependencies have separate licenses | https://github.com/kivy |
| Requests | Apache-2.0; its dependencies have their own terms | https://github.com/psf/requests |
| google-api-python-client, google-auth, google-auth-oauthlib (optional upload) | Apache-2.0 | https://github.com/googleapis |

Desktop release builds collect available license/notice files from installed
Python distributions into `legal/packages/`, with versions and checksums in
`legal/build-environment.json`. This deliberately includes build tools;
it is a build-environment inventory, not proof that every listed package is
bundled. Native libraries and the final Nuitka report require separate review.
An empty or missing license entry is an unresolved finding, not permission.
The release collector fails when a required runtime/Qt distribution lacks
actual notice files; a metadata license label does not satisfy that check.

Qt builds must preserve the license texts and copyright notices for the
actual libraries/modules shipped. They must also satisfy the applicable
source and replacement/relinking requirements. The collector alone does not
establish LGPL compliance, and no commercial Qt entitlement is assumed.

Android release builds are disabled while the licensing and codec route is
reviewed; no APK is produced by the release workflow. The retained Kivy UI and
python-for-android recipes keep their own notices above. If Android builds are
re-enabled, target Python/native packages need their own inventory, license and
source review; the host Python inventory must not be presented as an APK one.

## External programs

FFmpeg and ffprobe are invoked as separate processes. New desktop builds
from this branch require a separately installed copy; the release workflow
does not copy them into the application. Existing path overrides and runtime
support for older/user-supplied bundles remain available.

Previous Linux builds used John Van Sickle's static binaries, whose supplier
states GPLv3: https://johnvansickle.com/ffmpeg/ . Windows/macOS builds selected
FFmpeg via Chocolatey/Homebrew. This notice does not retroactively correct
those releases. Reintroducing bundling requires an exact version/configuration,
license and copyright notices, and a compliant way to supply corresponding
source for FFmpeg and the included libraries. A generic upstream URL is not
a substitute for that work.

7-Zip and yt-dlp are located on PATH and invoked as separate processes.
Their distributions retain their own licenses (including component-specific
terms); this workflow does not bundle either program.

## Redistribution

Keep this notice and the applicable full license texts with distributions.
Review [the outstanding release work](docs/LICENSING_AUDIT.md#release-checklist)
before publishing binaries. A draft release is not a licensing clearance.
