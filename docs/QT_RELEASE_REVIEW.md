# Qt release review: evidence and remaining work

Status: **incomplete; not a license clearance or legal opinion**. Keep the
release notice checks enabled and do not publish the reviewed binaries solely
because a check passes. This document records a particular build, not the
composition of future builds.

## Evidence from release workflow run 40619387477

Run: https://github.com/valeksan/YouTube-Cloude/actions/runs/40619387477
Commit: `752c82fd6db9fd66603dc0ac401fd59c4eeb727a`.

| Platform | Evidence | Outcome |
| --- | --- | --- |
| Linux | `licensing-review-linux-amd64/build-environment.json` and job log | Required notices missing for PySide6-Addons, PySide6-Essentials and shiboken6; compilation did not start. |
| macOS | `licensing-review-macos-arm64/build-environment.json` and job log | Same required-notice failure; compilation did not start. |
| Windows | Job log and `binaries-windows-amd64` artifact | The collector passed and the build succeeded; the workflow uploaded a downloadable artifact. This does **not** establish completeness of notices or LGPL compliance. |

The Linux and macOS inventories record PySide6, PySide6-Addons,
PySide6-Essentials and shiboken6 at `6.12.0`, plus PySide6-Pdf and
PySide6-WebEngine at `6.12.0.140`. These inventories report no notice files
for those six packages. The Windows install log records the same versions;
its collector succeeded, but the collector only verifies that required
packages have at least one discovered notice file and no missing declared
notice paths. It does not check that all required license and copyright texts
for their bundled native libraries are present. Do not infer the set of
actually shipped native libraries from installed packages alone.

The Windows log records Nuitka `--onefile`, Qt plugins `iconengines`,
`imageformats`, `platforms`, `styles` and `tls`, and 3312 data files from
`--include-package-data=PySide6`. A onefile executable's extracted payload
and replacement behavior require inspection and an actual replacement test.
The compilation report is supporting evidence, not a substitute for checking
the final payload. The Windows artifact is an Actions download even though
the release job was skipped; a draft or failed release run does not make an
uploaded artifact private.

## Authoritative starting points

- The matching PySide source tree has a `LICENSES` directory at
  https://code.qt.io/cgit/pyside/pyside-setup.git/tree/LICENSES?h=6.12.0 .
  Record an immutable revision and hashes when using source texts; a version
  label or generic LGPL text alone does not establish the applicable notices
  for every Qt module, plugin or bundled third-party component.
- Qt's explanation of obligations is at
  https://www.qt.io/development/open-source-lgpl-obligations . Consult the
  actual licenses for the exact components as well; different modules and
  embedded third-party code may have different terms.
- PySide's source is not automatically the corresponding source for Qt and
  every native library shipped by a wheel. Identify the exact source and build
  configuration for each actual binary, including any downstream changes.

## Before enabling release publication

1. Pin and record exact dependency versions, platform wheel filenames and
   hashes. Preserve the wheel metadata and the compilation reports. Avoid
   treating `pip`'s installed environment as the final artifact inventory.
2. Extract each final artifact on its target platform. Inventory Qt/PySide,
   plugins, QML data and other native libraries with versions and hashes;
   compare this list with the compilation report and the wheels. Review the
   licenses and copyright notices for every included component, including
   PySide6-Pdf/WebEngine if actually shipped.
3. Obtain version-matched upstream and third-party license texts, notices and
   corresponding sources from authoritative locations. Record source URLs,
   immutable revisions, hashes, patches and build instructions. Verify that
   the notices accompany each distribution in an accessible form. Extend the
   collector only after establishing a reproducible mapping; do not satisfy a
   required-package check using an arbitrary generic license file.
4. For each selected LGPL component, document and test the applicable method
   for using a modified compatible library, including replacement, relinking
   and installation information where required. On Windows explicitly test
   the onefile payload; successful extraction or dynamic loading alone is not
   proof that recipients can replace and run the modified library. If this
   cannot be demonstrated, change the packaging or provide a verified
   alternative route before publishing.
5. Record the reviewer, date, exact artifact hashes, results and unresolved
   items. Independently resolve inherited project-code permissions and other
   dependencies. Re-run on all target platforms after changes; do not mark
   this checklist complete based on the 2026-10-28 build.
