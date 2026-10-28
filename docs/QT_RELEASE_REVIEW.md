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
for those six packages. The Windows install log records the same versions.
The Windows notice ZIP records exactly one notice for each of those six
packages: `LicenseRef-Qt-Commercial.txt`. The previous collector accepted that
commercial reference without evidence of a commercial entitlement. The updated
collector requires LGPL-3.0 and GPL-3.0 texts for required Qt packages, but it
does not check that all required license and copyright texts
for their bundled native libraries are present. Do not infer the set of
actually shipped native libraries from installed packages alone.

The Windows log records Nuitka `--onefile`, Qt plugins `iconengines`,
`imageformats`, `platforms`, `styles` and `tls`, and 3312 data files from
`--include-package-data=PySide6`. A onefile executable's extracted payload
and replacement behavior require inspection and an actual replacement test.
The report lists Qt6Core, Qt6Gui, Qt6Network, Qt6Pdf, Qt6Svg, Qt6Widgets and
shiboken DLLs. The GUI executable SHA-256 is
`83144c0bc41e8974a3e1d8516469d0c2d83bb59cb9b0d2f55b264a117cdef547`.
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

## Wheel identifiers and source reference

The run's Windows install log names the following wheels. The hashes below
are published by the PyPI JSON API for those exact filenames, retrieved on
2026-10-28. The workflow did not save its downloaded wheel bytes or verify
these hashes, so this table is an identification aid, **not proof of the
hashes of the wheels actually installed in that run**. A future build must
download and verify the files itself before claiming reproducibility.

| Wheel filename | PyPI SHA-256 |
| --- | --- |
| `pyside6-6.12.0-cp310-abi3-win_amd64.whl` | `31a8d2893f2f28ab483b1534dde0438f27af6e234593de30425cb4729052d8f8` |
| `pyside6_essentials-6.12.0-cp310-abi3-win_amd64.whl` | `c9a95102aa23c1f86516a30d5a9be37552d324eee7e567eb7508973f1218cb42` |
| `pyside6_addons-6.12.0-cp310-abi3-win_amd64.whl` | `98d8d62010da6605344cee83e5c96fb846170a1f2d924523f10f5d92078b02b0` |
| `pyside6_pdf-6.12.0.140-cp310-abi3-win_amd64.whl` | `4971ba1a0ca15e7c29cfd808e9600aeb46b2305dad01456eb09fa3197166268e` |
| `pyside6_webengine-6.12.0.140-cp310-abi3-win_amd64.whl` | `f9b61b1d457a591ee590a6b80515f25a3e61e2576a2a0a70566380f9d9de4ab0` |
| `shiboken6-6.12.0-cp310-abi3-win_amd64.whl` | `a1906cb8116869178c64b6bab52623bbc8b4ceed7b30bfc3c9aa0f6e67f6438e` |

The Linux and macOS logs name the following additional wheels; the same
qualification about published versus actually verified hashes applies:

| Wheel filename | PyPI SHA-256 |
| --- | --- |
| `pyside6-6.12.0-cp310-abi3-macosx_14_0_universal2.whl` | `efea4c2f2aa54403c45de825865a902a1960a1cc9d5aaa92d4ebb8f4c4cd0708` |
| `pyside6-6.12.0-cp310-abi3-manylinux_2_34_x86_64.whl` | `d13ed4d0053cc20f3e4e0fdbf12790a9b7f958d7e22c0843411ecfa8c799e2a9` |
| `pyside6_essentials-6.12.0-cp310-abi3-macosx_14_0_universal2.whl` | `0867b709a724db28b161227c7d6ecb5ed10cc09226a53542417ac6dee1308239` |
| `pyside6_essentials-6.12.0-cp310-abi3-manylinux_2_34_x86_64.whl` | `16f4b5e41daf49235ae048458243da9efe5f3d8040f9cc5aa454ce69893d3bd9` |
| `pyside6_addons-6.12.0-cp310-abi3-macosx_14_0_universal2.whl` | `1d9bcd294ce1c9829194c7d13b01f771a2254b86cb3462cc3399321d2797fdac` |
| `pyside6_addons-6.12.0-cp310-abi3-manylinux_2_34_x86_64.whl` | `4ab38c0017f0453671a9313d3a53ca1c0e378924f54b07e596bcea94a9642391` |
| `pyside6_pdf-6.12.0.140-cp310-abi3-macosx_14_0_universal2.whl` | `74287989dd24a82ac1604e27a2d4530a0ab71ff03cdf878c16fdbcf5144373fb` |
| `pyside6_pdf-6.12.0.140-cp310-abi3-manylinux_2_34_x86_64.whl` | `0c94370b6b9d65fbfe54f9d6d25df0677db0cdcfd0a842a63958a3603a42007c` |
| `pyside6_webengine-6.12.0.140-cp310-abi3-macosx_14_0_universal2.whl` | `9a1de2da360d1817c08e9400a2a2fc5234beb3022a22123e15355169e183074e` |
| `pyside6_webengine-6.12.0.140-cp310-abi3-manylinux_2_34_x86_64.whl` | `c041c9921d7c91c9e51a2c027f434d05c3c59baa2c8f17b71dc8194e77791f06` |
| `shiboken6-6.12.0-cp310-abi3-macosx_14_0_universal2.whl` | `47105e05baf57d35453e07d240bbe59cb4b8d9565377ea5134ff9fb37d4f5c02` |
| `shiboken6-6.12.0-cp310-abi3-manylinux_2_34_x86_64.whl` | `3bde565bb0890044b5c7f63808adddede5abc241e9395a2bfed61919884d6240` |

The upstream `pyside-setup` annotated tag `v6.12.0` resolves to commit
`f50facb83fc3dc5f3240c854668c7a6dd93871b2` (checked with `git ls-remote`
against `https://code.qt.io/pyside/pyside-setup.git`). The tagged source is a
candidate reference; matching it to the distributor's actual wheel build,
and obtaining the source and licenses of included Qt libraries and other
native components, remain open. The `6.12.0.140` wheels require their own
source/build provenance; do not assume their contents are covered solely by
the PySide tag.

Candidate upstream Qt sources for modules named in the Windows compilation
report (resolved from the annotated `v6.12.0` tags on 2026-10-28):

| Repository | Peeled tag commit | Example reported binaries |
| --- | --- | --- |
| `https://code.qt.io/qt/qtbase.git` | `025bdad181de241e81bf853c8a2d7bf3d19261a9` | Qt6Core, Qt6Gui, Qt6Network, Qt6Widgets |
| `https://code.qt.io/qt/qtsvg.git` | `883a58532078d003cefef0a549bfe9f885ce41f5` | Qt6Svg and SVG plugins |

These source references are candidates, not evidence of the precise sources,
patches or build configuration used for a given wheel. In particular, the
report also lists Qt6Pdf and PDF/image plugins, whose provenance and
third-party notices still need separate review.

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
