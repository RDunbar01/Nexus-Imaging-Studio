# Nexus Imaging Studio

## Start locally: Python and application requirements

Download the full [3.2.13 package](releases/3.2.13/). The native application requires **Windows and Python with Tkinter/Tcl-Tk**; use **64-bit CPython 3.12**. It does **not** require PyTorch. No approved standalone hosted browser trial is supplied, and an HTML preview is not a way to execute physical-disk operations.

The source uses APIs introduced in Python 3.8, but neither the installer nor the app enforces or qualifies a complete Python-version range. Therefore, 3.12 is the recommended interpreter, not a guarantee that all newer or older versions work. Windows/Tk launch, administrator prompts and physical-device writes remain unqualified by safe-file/mock tests. Back up data and verify the exact device before any authorized write.

## Current release licensing

This Nexus release is not offered under Apache License 2.0. Nexus-owned software may be used only for personal, non-commercial purposes. Any other use, including commercial use, modification or redistribution, requires express written consent from the rights holder. Third-party code, models, datasets and separately licensed components retain their own licenses and notices. Previously granted rights and rights that cannot lawfully be restricted remain unchanged.


> The reviewed 3.2.13 source, installer and data components are published on the main branch. Windows/hardware acceptance remains pending; publication is not hardware certification.

**3.2.13 · published source and installer components · experimental software**

Experimental Windows disk-imaging and formatting tooling for the Nexus OS workflow.

## Current baseline and release status

Previous baseline: **3.2.12**. Published package: **3.2.13**. Use the matching application, installer and package metadata together.

Use backups and verify the exact target device before any write. The audited code fails closed on uncertain boot/system/partition safety flags, checks bounds and reports partial verification honestly. Automated tests used safe files and mocks, not physical disk writes, administrator prompts or native exFAT operations.

## Start and inspect the original project

Use the exact launch instructions accompanying the matching release package. The [preserved previous README](docs/README_PREVIOUS.md) contains the original workflow, research citations, credits, downloads and limitations. Treat its release-specific statements as historical; historical software and its original licenses remain preserved.

## Evidence and licensing

Developed by Rich Dunbar / Nexus Emerging Technology with AI-assisted coding. Retain existing licenses, attribution and third-party notices. No additional Windows, physical GPU, device-write or model-quality qualification is claimed by this documentation refresh. No live browser-trial deployment is created by this README.

## 3.2.13 installation files

[Installation instructions](releases/3.2.13/INSTALL.txt) · [Python installer](releases/3.2.13/installer.py) · [Package directory](releases/3.2.13) · [Validation record](releases/3.2.13/RELEASE_VALIDATION.json).

Download the entire version directory together, not the installer alone. Keep its manifest and data file alongside installer.py. Every distributed component is at most 10,000,000 bytes. The complete licensing-corrected package has passed independent package review and isolated no-launch extraction; Windows/hardware acceptance remains pending. Publication of these components does not imply hardware certification.
