# Browser edition development

The browser edition is an intentionally read-only companion to native Imaging Studio 3.2.13. It does not call the native application or use its raw-device interfaces.

## Build

Use Python 3.12 or a compatible Python 3 interpreter:

    python browser/build.py

The resulting `browser/dist/Nexus_Imaging_Studio_Browser_v1.html` is self-contained. Copy the generated HTML to the repository root when publishing. No minifier, remote script or third-party browser bundle is required.

## Safe tests

Use a current Node.js version supporting `File`, `Blob` and `node:crypto` (tested with Node.js 24). Install `jsdom@26.1.0` (the tested version) from npm in a local development environment for the DOM test; it is a test-only dependency and is not included in the application.

    node browser/tests/test_core.cjs
    node browser/tests/test_ui.cjs

Tests use synthetic in-memory files only. The DOM test uses file/worker shims and executes the actual inline app and hash-worker source. It does not establish physical-disk, Windows, or real-browser compatibility. The application never exposes a disk-writing action.

## Boundaries

The MBR bounds/overlap checks and GPT CRC/partition checks reflect the desktop application's read-only preflight concepts, not a full port of its boot validation. The browser does not walk EFI FAT directories, inspect the backup GPT, recover deleted files, or validate bootloaders. The synthetic demo contains an MBR partition entry but no filesystem or bootloader. All metadata parser and hash implementation code in this browser edition is Nexus-owned JavaScript; standard browser APIs provide file reads, workers and downloads.

A report or checklist is evidence of the stated checks only, not permission to flash a disk. Logs retain the latest 100 entries for bounded session memory. SHA-256 processing is cancellable and reads files in 4 MiB worker chunks; metadata tables above 4 MiB are refused.
