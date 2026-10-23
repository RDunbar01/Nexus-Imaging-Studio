# Nexus Imaging Studio

Windows disk-imaging and removable-media tools built for the Nexus OS development workflow. Version **3.2.13** combines image writing, backup, partition management and verification in a Python/Tk desktop application.

[Download 3.2.13](releases/3.2.13/) · [Installation instructions](releases/3.2.13/INSTALL.txt) · [Validation record](releases/3.2.13/RELEASE_VALIDATION.json)

**Flashing, formatting, repartitioning and logical erase can permanently destroy data. Back up the whole disk to another physical device, verify the target identity and use disposable media for evaluation.**

## What it does

- Write supported disk images to selected removable media and report readback verification coverage.
- Back up removable disks to raw images with SHA-256 and acquisition records.
- Inspect and manage partitions, format supported volumes and assign drive letters. Additional data partitions require a suitable image layout and available space.
- Scan supported read-only disk images for deleted-file candidates and extract selected results to a separate destination.
- Perform verified logical overwrites and record operation status, errors and bounded recovery responses through the AEGIS subsystem.

## Engineering contribution

Developed by **Rich Dunbar / Nexus Emerging Technology with AI-assisted coding** to make repeated Nexus OS media preparation easier to inspect and repeat. The contribution is the desktop workflow and AEGIS safety layer around raw disk I/O and Windows storage facilities: target-identity checks, protected-disk guards, bounds checks, operation logs and explicit reporting of partial verification.

AEGIS uses deterministic responses to recognized errors, not a language model. Its safeguards do not replace checking the selected disk. A successful image write does not make every ISO USB-bootable, and logical overwrite is not a guarantee of firmware-level sanitization or deleted-file recovery.

## Start locally

1. Download the entire [3.2.13 directory](releases/3.2.13/). Keep `Nexus_imaging_Data_001.nxd`, `package_manifest.json` and `installer.py` together.
2. Use **64-bit CPython 3.12 with Tkinter/Tcl-Tk**. Run `python installer.py --no-launch` to review the installation plan and extract the application without starting it.
3. For a non-destructive interface preview, run `python Nexus_Imaging_Studio_v3_2_13_Experimental_exFAT.pyw --preview` from the extracted directory. This mode does not enumerate physical disks or enable hardware operations.
4. For an authorized Windows media operation, launch that same `.pyw` file without `--preview`, review any administrator prompt and confirm the exact target before writing. Keep the application and logs off the target drive.

There is **no PyTorch requirement** and no hosted browser trial. The preview is a local Tk interface, not an HTML disk writer. Python 3.12 is the recommended interpreter; a complete older/newer version range has not been qualified. The experimental native exFAT path requires its separately obtained, pinned backend and is not validated by the preview. Backend binaries and drivers are not bundled.

Installer data parts are at most 10,000,000 bytes; individual distributed files remain below 20,000,000 bytes.

## Validation and limits

Recorded checks cover source parsing, synthetic file-backed algorithms, mocked safety paths and isolated package extraction. They do not establish Windows/Tk launch, UAC behavior, physical-media writes or native exFAT operation. The application remains experimental on Windows and physical storage. A failed operation may already have changed the disk; retain logs and inspect the actual state before deciding what to do next.

The [historical README](docs/README_PREVIOUS.md) contains earlier workflow notes and attribution. Use the current package's instructions and validation records for 3.2.13.

## Credits and license

Python and its standard library are provided by the Python Software Foundation and contributors; Tkinter uses Tcl/Tk. Win32 APIs, PowerShell Storage cmdlets and DiskPart are Microsoft platform facilities. See [third-party notices](THIRD_PARTY_NOTICES.md).

Personal use and internal commercial testing and evaluation are permitted for Nexus-owned material. Distribution, modification, production deployment and other commercial use require express written consent. Third-party licenses and previously granted rights remain unchanged. See the [license](LICENSE) and [evaluation permission](COMMERCIAL_EVALUATION_PERMISSION.md).
