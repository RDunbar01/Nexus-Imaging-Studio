# NEXUS Imaging Studio

**AEGIS removable-media imaging, recovery, verification, and disk management**

![Version](https://img.shields.io/badge/version-3.2.4-1776b6)
![Platform](https://img.shields.io/badge/platform-Windows-0078D4)
![Language](https://img.shields.io/badge/language-Python-3776AB)
![Status](https://img.shields.io/badge/status-experimental-orange)

**NEXUS Imaging Studio v3.2.4** is a Windows desktop utility for creating bootable USB media, making raw disk-image backups, managing removable partitions, examining deleted-file candidates, and performing verified logical overwrites. Its **AEGIS** subsystem adds guarded device selection, raw-write readback checks, diagnostic logs, and bounded recovery responses to known storage errors.

Built with **Python, Tkinter, Windows PowerShell Storage commands, and Win32 disk APIs**, the application provides a themed interface without requiring a third-party Python package for its main functionality.

> [!WARNING]
> **Some operations permanently destroy data.** Flashing, factory reset, formatting, partition deletion, and whole-device logical erase can overwrite the selected removable device. Back up important data and verify the disk number, capacity, and identity before confirming an action. Use disposable test media when evaluating this release.

## Contents

- [Features](#features)
- [Requirements](#requirements)
- [Installation and launch](#installation-and-launch)
- [Using NEXUS Imaging Studio](#using-nexus-imaging-studio)
- [AEGIS safeguards and verification](#aegis-safeguards-and-verification)
- [Supported formats](#supported-formats)
- [Settings, logs, and recovery memory](#settings-logs-and-recovery-memory)
- [Testing status](#testing-status)
- [Known limitations](#known-limitations)
- [Troubleshooting](#troubleshooting)
- [Repository layout](#repository-layout)
- [Open-source acknowledgements](#open-source-acknowledgements)
- [License and attribution](#license-and-attribution)

## Features

| Workspace | Implemented functions |
| --- | --- |
| **Flash / Clone** | Flash supported image files to removable media through guarded raw disk I/O; inspect MBR/GPT and EFI structures; monitor progress; verify written bytes. |
| **Factory Reset / Reclaim** | Remove existing removable-disk partitions, reclaim the media, and create a normal Windows-readable volume with GPT or MBR. |
| **Disk Manager** | Inspect partitions; create and format data partitions; extend eligible partitions; assign/remove drive letters; change online/read-only state; open mounted volumes. |
| **Raw Image Backup** | Read a removable disk into an image, calculate SHA-256, and create an acquisition manifest. |
| **Undelete Lab** | Scan an existing raw image for supported deleted-file metadata and file signatures; extract selected candidates to a separate location with SHA-256 manifests. |
| **Verified Logical Erase** | Write zeros across the host-addressable space of a selected removable disk, read the range back, and produce an audit report. |
| **AEGIS Diagnostics** | Record error classifications and bounded recovery history; inspect removable-media policy, permissions, and device state; export operational logs. |
| **Desktop UI** | Nine built-in NEXUS themes, DPI-aware rendering, status displays, progress telemetry, and keyboard-operable controls. |

### Three distinct meanings of recovery

- **Factory reset / reclaim** restores a disk to usable *empty* storage. It is destructive and **does not recover deleted files**.
- **Undelete Lab** attempts to identify and extract file candidates from a *read-only disk image*. Results are not guaranteed.
- **AEGIS adaptive recovery** remembers recognized operational failures and chooses bounded, deterministic response paths. It **does not use a language model, rewrite its own code, or autonomously bypass safeguards**.

## Requirements

| Component | Requirement |
| --- | --- |
| Operating system | **Windows**, with PowerShell Storage cmdlets and Win32 storage APIs for physical-disk operations |
| Python | Python 3.8+ recommended; Python 3.10+ is a sensible modern installation choice |
| Desktop UI | Tkinter / Tcl-Tk installed with Python |
| Privileges | **Administrator rights** for physical media access; the app requests elevation on Windows |
| Targets | Detected **USB / SD / MMC** devices; Windows boot/system disks are excluded by application checks |
| Source images | A local image file, or existing removable media for backup and acquisition |
| External packages | None required by the uploaded `.pyw` source |

**Important:** Software restrictions are not a substitute for checking the target manually. Use a dedicated test USB drive before using the app on valuable media.

## Installation and launch

1. Install a current Python 3 distribution for Windows. Ensure **Tkinter / Tcl-Tk** is included.
2. Download or clone the repository.
3. Keep `Nexus_Imaging_Studio.pyw` on a local disk, **not on the removable disk you intend to operate on**.
4. Open Windows Terminal or PowerShell in the repository folder.
5. Launch:

```powershell
py -3 Nexus_Imaging_Studio.pyw
```

On Windows, the application requests elevation through **User Account Control (UAC)** if necessary. After approval, its graphical interface opens. Alternatively, launch the `.pyw` file through its Python file association.

### Non-destructive UI preview

To inspect the interface without enumerating or writing physical devices:

```powershell
py -3 Nexus_Imaging_Studio.pyw --preview
```

The `--preview` mode does not enable hardware operations. It can also run on another desktop OS with Python and Tkinter installed, but **physical-media functionality is Windows-only**.

### Application self-test

In the interface, open **Help → Run non-destructive application self-test**. This checks selected UI elements, function availability, and an **in-memory** logical overwrite example. It **does not test actual USB hardware**.

## Using NEXUS Imaging Studio

### 1. Flash an image to USB

1. Connect a **disposable or backed-up** USB / SD device.
2. Select the target from **Target Device / Media**. Review its disk number, size, bus type, and identity.
3. Choose **Select Image** and open an `.img`, `.iso`, `.raw`, or `.bin` file.
4. Review the image validation result and select a verification mode.
5. Optionally enable **Create and mount a data partition from remaining space**.
6. Select **Flash Image**, read the deletion warning, and complete the typed confirmation.
7. Review the write, locked verification, and host-visible structure checks in the operation log.
8. Use **Safe Eject**; remove the drive only when Windows confirms it is safe.

The program validates supported MBR/GPT partition maps and checks for an EFI boot loader (`EFI/BOOT/BOOTX64.EFI`). An ordinary optical ISO **is not necessarily a USB-bootable image**. Advanced raw mode permits an explicit bypass of boot validation but **does not certify bootability**.

### 2. Factory reset / reclaim

Use **Factory Reset / Reclaim** to remove existing partitions and create a new data volume. Choose:

- Partition layout: **GPT** or **MBR**
- Filesystem: **exFAT**, **NTFS**, or **FAT32** where Windows formatting permits it
- Label and optional full format

This erases the existing partition map and data. It is not a non-destructive repair or undelete operation.

### 3. Make a raw image backup

Select removable media, then use **File → Create image backup from selected media** (also available through Disk Manager).

The application writes a new raw `.img` file and an adjacent `.acquisition.json` manifest with the source identity and SHA-256 hash. It does not overwrite an existing backup filename. **A live source can change during acquisition; consistency is not guaranteed.** For evidence-sensitive work, use a suitable hardware write blocker and an appropriate forensic procedure.

### 4. Scan an image for recoverable files

1. Open **Undelete Lab**.
2. Select an existing raw source image, or acquire one from the selected removable drive first.
3. Choose **Combined**, **Metadata only**, or **Signature carving**.
4. Run **Scan Source** and review the candidate list and warnings.
5. Select candidates and an **output folder on a separate storage location**.
6. Use **Recover Selected** or **Recover All** to extract copies.

The source image is opened read-only. Extracted copies and their SHA-256 values are recorded in `recovery_manifest.json`. **A recovered candidate is not proof that its original contents are intact.** Signature carving can include files that were never deleted.

### 5. Perform a verified logical erase

> [!CAUTION]
> **Irreversible operation.** This overwrites the selected device's host-addressable bytes with zeros and verifies them with a full readback. It is **not** an SSD firmware sanitize, cryptographic erase, hardware purge, or certified forensic sanitization process.

Open **Verified Logical Erase**, choose a removable device, select a report location on **another physical disk**, and enter the device-specific confirmation phrase. The operation writes an audit JSON document. Cancellation, error, or readback mismatch leaves an **INCOMPLETE** report rather than a successful erase result. The erased disk is left unformatted.

## AEGIS safeguards and verification

### Device-selection safeguards

- Only enumerates eligible **USB / SD / MMC** disks for normal operations.
- Refuses Windows system or boot disks through software checks.
- Re-checks target geometry and stable identifiers before sensitive operations.
- Avoids automatically selecting a different target after ambiguous media re-enumeration.
- Uses volume locking/dismounting and guarded raw access for supported workflows.
- Requires explicit confirmation for destructive operations.

### Image verification modes

| Mode | Meaning |
| --- | --- |
| **AEGIS Adaptive (recommended)** | Performs the applicable locked exact readback and evaluates host-visible boot/partition health; uses recorded operational error classes to adjust bounded recovery behavior. |
| **Strict forensic byte-for-byte** | Compares image bytes with raw-media readback **while the certification handle and volume locks are retained**, before Windows storage refresh. This is an application-level byte check, not an independent forensic certification. |
| **Structure only** | Validates the supported on-device boot/partition structure; **does not perform a full byte-for-byte payload comparison**. |

The exact locked verification happens **before** Windows is allowed to refresh or normalize disk metadata. Subsequent host-visible boot/GPT structure checks are separate. Windows may legitimately modify some filesystem bookkeeping after handoff; the application does not claim the disk remains byte-identical forever.

### Bounded failure handling

AEGIS records recognized error classes, such as access denial, write protection, device I/O faults, incomplete reclaim, and verification mismatch. It may adjust settle times or attempt controlled reacquisition of the **same verified target**. Persistent failures stop the operation rather than granting broader permissions or treating damaged media as safe.

## Supported formats

| Task | Formats or scope |
| --- | --- |
| Raw image selection for flashing | `.img`, `.iso`, `.raw`, `.bin` |
| Strict USB boot validation | Supported MBR/GPT USB image layouts with EFI System Partition and `BOOTX64.EFI` |
| Windows data volume creation | exFAT, NTFS, FAT32 (Windows formatting restrictions apply) |
| Undelete image input | Uncompressed sector images (`.img`, `.raw`, `.bin`; picker also permits `.dd` / `.iso`) |
| Undelete metadata analysis | Bounded NTFS, FAT32, and exFAT scenarios |
| Signature carving | PNG, JPEG, PDF, ZIP/Office Open XML, RIFF-derived WAV/AVI/WebP |
| Backup output | Raw `.img` with JSON acquisition metadata |
| Erase evidence | JSON audit record for logical overwrite and readback |

Not every variant within these format families is supported. For example, **encrypted BitLocker volumes, NTFS EFS/compressed streams, unsupported filesystem extensions, and guaranteed recovery of fragmented or overwritten files are outside the recovery implementation's scope**.

## Settings, logs, and recovery memory

The application stores settings and bounded AEGIS operational history locally:

```text
%APPDATA%\NEXUS_Imaging_Studio\settings.json
%APPDATA%\NEXUS_Imaging_Studio\recovery_engine.json
```

The runtime log is written to the Windows temporary directory:

```text
%TEMP%\NEXUS_Imaging_Studio_v3.2.4_RECLAIM_REPAIR.log
```

Use **Export Log** in the interface to save a readable operation log. Logs and manifests may include drive serials, file paths, and device details: **review them before sharing publicly**.

## Testing status

**This README describes features present in the supplied v3.2.4 Python source.** Source-code checks do **not** establish that a physical USB device, bootloader, or forensic recovery operation has been independently qualified.

| Check | Status | Scope |
| --- | --- | --- |
| Python source syntax | **Passed** | AST parse of uploaded `.pyw` source |
| Module loading | **Passed** | Imported without launching GUI or performing disk I/O |
| Verification-mode normalization | **Passed** | Exercised representative mode strings |
| In-memory erase/readback | **Passed** | Simulated zero overwrite and SHA-256 readback on a bytearray |
| Real removable-device flashing | **Not tested here** | Requires Windows, elevated permissions, sacrificial removable media |
| USB boot on real hardware | **Not tested here** | Requires firmware/hardware test |
| Physical-device erase and safe eject | **Not tested here** | Requires Windows and controlled test media |
| Real-world undelete success rate | **Not established** | Requires independent recovery corpus and comparison |

The source header refers to a **companion validation report**, but that report is **not included in this repository starter package**.

## Known limitations

- **Windows-only for physical disk operations.** Other operating systems are limited to interface preview.
- Strict validated UEFI flashing currently requires a **512-byte logical-sector target**; general 4Kn conversion is not implemented.
- Flashing an ISO as a raw image does not automatically make a non-hybrid optical ISO bootable on USB.
- File recovery is bounded by implementation limits; it cannot guarantee completeness, restore overwritten/TRIMmed data, or reconstruct arbitrary fragmented files.
- Whole-device zero overwrite does not reach remapped flash cells, firmware-reserved areas, or wear-leveling spare capacity.
- Readback verifies bytes at a point in time, not long-term media reliability or firmware boot compatibility.
- The recovery-memory subsystem is **deterministic and auditable**, not a self-modifying AI system.
- The project is a Python `.pyw` source distribution. This package does not contain a signed Windows installer or compiled executable.

## Troubleshooting

| Symptom | Suggested action |
| --- | --- |
| App does not launch | Check Python and Tkinter; run the command from a terminal to inspect errors; inspect `%TEMP%` log. |
| Administrator prompt denied | Relaunch and approve UAC. Raw-media operations require elevation. |
| No removable disk shown | Connect USB/SD/MMC media, choose **Rescan**, and check Windows Disk Management. Internal SATA/NVMe devices are intentionally not offered. |
| Raw access denied | Close apps using the disk, inspect **Diagnostics**, check write policy/read-only switches, and export the log. |
| Image validation rejected | Use a supported hybrid USB image; advanced raw bypasses only the validator and offers no bootability guarantee. |
| Locked readback mismatch | Treat it as a write/read error. Test a different port/device and retain diagnostics. Do not assume a checksum mismatch is harmless. |
| Recovery returned no candidates | Inspect scan notes and image/filesystem support. Deleted data may be overwritten or outside supported recovery layouts. |
| Safe eject not confirmed | Leave the device connected; close applications and use Windows **Safely Remove Hardware**. |

## Repository layout

```text
NEXUS-Imaging-Studio/
├── README.md                 # Project overview, safety, acknowledgements
├── THIRD_PARTY_NOTICES.md     # Third-party credit and upstream license links
└── Nexus_Imaging_Studio.pyw  # Windows Tkinter application and AEGIS backend
```

Optional future additions: screenshots, separate verification fixtures, an explicit `LICENSE` file for original NEXUS code, and the referenced hardware-validation report.

## Open-source acknowledgements

NEXUS Imaging Studio is built using established open-source programming and interface technologies. The following projects and their contributors are acknowledged for the components **actually referenced by the supplied v3.2.4 source**:

| Project / contributors | Role in NEXUS Imaging Studio | Applicable license / upstream documentation |
| --- | --- | --- |
| **Python Software Foundation (PSF), Python core developers, and contributors** | The Python language and standard library, including `ctypes`, `hashlib`, `json`, `pathlib`, `threading`, `subprocess`, and other built-in modules | [Python license and acknowledgements](https://docs.python.org/3/license.html) — PSF License Version 2 and applicable incorporated-software notices |
| **Tcl/Tk project and its contributors** | Tk's desktop UI toolkit, accessed from Python via `tkinter` and `tkinter.ttk` | [Tcl license](https://github.com/tcltk/tcl/blob/main/license.terms) and [Tk license](https://github.com/tcltk/tk/blob/main/license.terms) — permissive Tcl/Tk (BSD-style) terms |

**Microsoft platform acknowledgement:** The program also uses Windows **Win32 APIs, PowerShell Storage cmdlets, DiskPart, and Windows storage-management services**. These are Windows platform facilities, **not** open-source code contributions being claimed by NEXUS.

**Provenance scope:** A source-import and attribution-notice inspection found **no external `pip` dependencies, vendored third-party packages, or explicit copied-code credits** in the supplied single-file application. This is *not* a proof that no algorithms or code fragments were adapted from other repositories during its development. If a source function, shader, icon, asset, or code block was copied or adapted from another project, retain its exact copyright/license notice and list its author, source URL, license, and relevant modifications in [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md) before release. Credits for runtime dependencies must not be mistaken for verified attribution of individually adapted code fragments.

## License and attribution

**NEXUS Imaging Studio** is a project of **NEXUS Emerging Technology**. The names and rights of Python, Tcl/Tk, and Microsoft remain with their respective owners and contributors. Acknowledgement does not imply those projects or vendors endorse NEXUS Imaging Studio.

**No project-level `LICENSE` file was provided for this Python application.** The upstream licenses listed above govern their respective software, **not** the original NEXUS code. Do not assume the Apache 2.0 license used for a separate NEXUS Web LLM project automatically applies to Imaging Studio. Select and include the intended project license before publishing redistribution permissions.

---

*Version 3.2.4 · October 2026 · Experimental software — validate with disposable media before production use.*
