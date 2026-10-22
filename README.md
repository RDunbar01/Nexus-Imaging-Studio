# Nexus Imaging Studio

## Current release licensing

This Nexus release is not offered under Apache License 2.0. Nexus-owned software may be used only for personal, non-commercial purposes. Any other use, including commercial use, modification or redistribution, requires express written consent from the rights holder. Third-party code, models, datasets and separately licensed components retain their own licenses and notices. Previously granted rights and rights that cannot lawfully be restricted remain unchanged.


> Draft release staging: the 3.2.13 installer and data components are included below. Windows/hardware acceptance and merge review remain pending; this is not a published release.

**Next-release package staging · not a published application update**

Experimental Windows disk-imaging and formatting tooling for the Nexus OS workflow.

## Current baseline and release status

Verified baseline: **3.2.12**. Next identifier: **3.2.13**. Do not tag or label a binary with a new version until its application, installer and package metadata agree.

Use backups and verify the exact target device before any write. The audited code fails closed on uncertain boot/system/partition safety flags, checks bounds and reports partial verification honestly. Automated tests used safe files and mocks, not physical disk writes, administrator prompts or native exFAT operations.

## Start and inspect the original project

Use the exact launch instructions accompanying the matching release package. The [preserved previous README](docs/README_PREVIOUS.md) contains the original workflow, research citations, credits, downloads and limitations. Treat its release-specific statements as historical; this staged update does not silently replace its software or relicense dependencies.

## Evidence and licensing

Developed by Rich Dunbar / Nexus Emerging Technology with AI-assisted coding. Retain existing licenses, attribution and third-party notices. No additional Windows, physical GPU, device-write or model-quality qualification is claimed by this documentation refresh. No live browser-trial deployment is created by this README.

## Staged 3.2.13 installation files

[Installation instructions](releases/3.2.13/INSTALL.txt) · [Python installer](releases/3.2.13/installer.py) · [Package directory](releases/3.2.13) · [Validation record](releases/3.2.13/RELEASE_VALIDATION.json).

Download the entire version directory together, not the installer alone. Keep its manifest and data file alongside installer.py. Every distributed component is at most 10,000,000 bytes. The complete licensing-corrected package has passed independent package review and isolated no-launch extraction; Windows/hardware acceptance remains pending. No new live release or hardware certification is implied.
