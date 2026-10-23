# Nexus Imaging Studio

Disk-image inspection and Windows removable-media tools for the Nexus OS development workflow. **Browser edition 1.0** provides read-only image analysis; the **3.2.13 desktop application** handles physical media.

**[Open the browser trial](https://rdunbar01.github.io/Nexus-Imaging-Studio/Nexus_Imaging_Studio_Browser_v1.html)** · [Download the single HTML](Nexus_Imaging_Studio_Browser_v1.html) · [Get the Windows application](releases/3.2.13/) · [Wiki](https://github.com/RDunbar01/Nexus-Imaging-Studio/wiki/Welcome-to-NEXUS-Imaging-Studio)

## Try it now

Open the trial and choose **Try synthetic image** to inspect a clearly labeled, generated MBR fixture, or select your own local image. Nothing is uploaded. No Python, PyTorch, installation or physical drive is required for the browser tools.

The single HTML embeds the interface, algorithms and worker code so reviewers can open it directly from GitHub Pages or keep a local offline copy. This packaging makes an online trial simple; it does not give a browser Windows raw-disk access.

## What works in the browser

- Read local, uncompressed image files and inspect MBR partition bounds and overlaps using a selected 512- or 4096-byte sector size.
- Check primary GPT header and entry-array CRC32 values, partition bounds and overlaps. GPT table inspection is capped at 4 MiB.
- Detect an ISO 9660 descriptor signature. This is a format clue, not a USB-boot compatibility verdict.
- Calculate SHA-256 in a background worker using 4 MiB chunks, cancel it, and compare the result with a reference hash supplied by the user.
- Export inspection JSON, a session log and a non-executable preparation checklist with a manually entered capacity comparison.

**The browser edition cannot flash, format, erase, back up, repair or recover physical drives.** It does not enumerate or select a disk. It does not validate backup GPT, filesystem contents, bootloaders or firmware boot compatibility. A matching reference hash establishes matching bytes, not the identity of the publisher. Compressed images must be decompressed separately.

## What requires the Windows application

The 3.2.13 Python/Tk application writes supported images to selected removable media, reports readback coverage, backs up raw disks with acquisition records, manages supported partitions/volumes and scans supported read-only images for deleted-file candidates. AEGIS records operation status and uses deterministic responses to recognized errors; it is not a language model.

**Flashing, formatting, repartitioning and logical erase can permanently destroy data.** Back up the entire target to another physical device, confirm its exact identity, and use disposable media for evaluation. A completed write does not make every ISO USB-bootable. Logical overwrite is not a firmware-level sanitization guarantee.

## Install the desktop application

1. Download the entire [3.2.13 directory](releases/3.2.13/). Keep `Nexus_imaging_Data_001.nxd`, `package_manifest.json` and `installer.py` together.
2. Use **64-bit CPython 3.12 with Tkinter/Tcl-Tk**. Run `python installer.py --no-launch` to inspect the plan and extract without starting the application.
3. From the extracted directory, run `python Nexus_Imaging_Studio_v3_2_13_Experimental_exFAT.pyw --preview` for a non-destructive local interface preview. It does not enumerate physical disks or enable hardware operations.
4. Follow the [installation instructions](releases/3.2.13/INSTALL.txt) for authorized native operations. Keep application files and logs off the target drive.

There is **no PyTorch requirement**. Python 3.12 is recommended; a complete older/newer version range has not been qualified. The experimental native exFAT path requires its separately obtained pinned backend; drivers and backend binaries are not bundled. The browser edition does not replace this backend.

## Engineering contribution

Developed by **Rich Dunbar / Nexus Emerging Technology with AI-assisted coding**. The desktop workflow combines raw-disk operations with target-identity checks, protected-disk guards, bounds checks, logs and explicit partial-verification reporting. The browser edition makes the read-only preparation stage accessible without installing that privileged workflow: bounded metadata reads, chunked hashing, cancellation and portable reports.

## Validation and limits

Browser source tests cover SHA-256 reference vectors, malformed/truncated image metadata, CRC failures, overlapping partitions, bounded reads, cancellation, stale-result rejection and full-DOM interactions with file/worker shims. These are synthetic tests, not Windows or physical-storage qualification. See [browser validation](validation/browser_v1.json) and [native validation](releases/3.2.13/RELEASE_VALIDATION.json).

The native package remains unchanged. Its recorded checks cover parsing, synthetic file-backed algorithms, mocked safety paths and isolated extraction, not Windows/Tk launch, UAC, physical writes or native exFAT operation. Installer data parts are at most 10,000,000 bytes; each distributed file is below 20,000,000 bytes. Historical guides remain available as historical records, not the current browser feature list.

## Credits and use

The browser inspector uses Nexus-owned JavaScript and standard browser APIs, with no bundled external runtime. The native application uses Python, Tcl/Tk and Microsoft storage facilities. See [third-party notices](THIRD_PARTY_NOTICES.md).

Personal use and internal commercial testing and evaluation are permitted for Nexus-owned material. Distribution, modification, production deployment and other commercial use require express written consent. Third-party licenses and previously granted rights remain unchanged. See [LICENSE](LICENSE) and [evaluation permission](COMMERCIAL_EVALUATION_PERMISSION.md).
