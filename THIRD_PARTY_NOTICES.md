# NEXUS Imaging Studio — Third-Party Notices and Credits

**Project:** NEXUS Imaging Studio v3.2.4  
**Maintainer:** NEXUS Emerging Technology  
**Notice date:** 8 October 2026

This file acknowledges open-source software used through the runtime and desktop interface of NEXUS Imaging Studio. The supplied source file was reviewed for imports and explicit upstream notices. No external Python packages, vendored libraries, or third-party repository attribution blocks were found. A source review **cannot prove the historical origin of every code fragment**.

## 1. Python and the Python Standard Library

**Credits:** Python Software Foundation; Python core developers and contributors.

**How used:** The project is written in Python and uses standard modules such as `ctypes`, `hashlib`, `json`, `math`, `os`, `pathlib`, `queue`, `re`, `shutil`, `struct`, `subprocess`, `sys`, `tempfile`, `threading`, `time`, `traceback`, `uuid`, and `winreg` (Windows). Python's own `tkinter` wrapper also comes from the standard library.

**License:** Python Software Foundation License Version 2, plus applicable licenses for software incorporated into the particular Python distribution.

**Official references:**
- [Python license and acknowledgements](https://docs.python.org/3/license.html)
- [Python Software Foundation](https://www.python.org/psf/)
- [CPython source](https://github.com/python/cpython)

**Distribution note:** The source-only repository does not bundle a Python runtime. If a future Windows executable includes a Python runtime, preserve and include the applicable bundled Python copyright and license notices.

## 2. Tcl and Tk — Graphical User Interface

**Credits:** Tcl/Tk project and contributors, including the copyright holders identified in the official Tcl and Tk license files.

**How used:** The application uses `tkinter` and `tkinter.ttk` to build its desktop windows, forms, canvases, dialogs, themes, and tree/table controls. `tkinter` interfaces with the Tcl/Tk GUI system provided by the Python installation.

**License:** Tcl/Tk permissive BSD-style license terms; applicable original copyright notices and license text must be retained when redistributing Tcl/Tk components.

**Official references:**
- [Tcl license.terms](https://github.com/tcltk/tcl/blob/main/license.terms)
- [Tk license.terms](https://github.com/tcltk/tk/blob/main/license.terms)
- [Tcl/Tk project](https://www.tcl-lang.org/)

**Distribution note:** The source-only repository does not vendor Tcl or Tk. If future installers or packaged executables include their libraries, include the original license files and copyright notices for the versions distributed.

## 3. Microsoft Windows Platform Dependencies (Not Open-Source Attribution)

**Microsoft** provides the Windows services and APIs on which the physical-media functions depend. This application calls Windows API libraries such as `kernel32`, `cfgmgr32`, `dwmapi`, and `advapi32`, and uses Windows **PowerShell**, **DiskPart**, and Storage cmdlets. These are operating-system facilities, not open-source components of the NEXUS project. Their use does not imply Microsoft sponsorship or endorsement.

## 4. File Format and Algorithm Background

The source contains application-level implementations of concepts such as GPT/MBR structures, EFI/FAT32 inspection, CRC32 and SHA-256 checks, and filesystem metadata analysis. These are widely documented technical mechanisms. **Their presence does not, by itself, establish that code was copied from any particular imaging or recovery repository.** Therefore no specific upstream product or author is identified as a code source without a provenance record.

## 5. Additional Third-Party Source Code: Provenance Register

No further direct source-code reuse was established from the uploaded single-file source. If NEXUS Imaging Studio incorporates copied or modified snippets from earlier development, complete the following fields for **each** source before public redistribution:

| Contributor / upstream project | Original repository or publication | Copied or adapted portion | License and copyright notice | Changes made |
| --- | --- | --- | --- | --- |
| *Add confirmed upstream source here* | *URL and specific revision* | *File / function / lines* | *License and copyright holder* | *NEXUS modifications* |

Do not replace upstream license terms with a NEXUS license. Contact the upstream author if the license is unclear; do not publish a claim of original authorship for third-party code.

## 6. NEXUS Project License

At the time of preparation, the submitted repository did not include an Imaging Studio-specific LICENSE file. License terms for original NEXUS-authored code must be selected separately. Third-party licenses remain in force regardless of the NEXUS project's eventual license.

---

*Attribution was prepared against the single-file `Nexus_Imaging_Studio.pyw` v3.2.4 source supplied on 8 October 2026. It is a dependency and source-notice audit, not an independently verified complete historical provenance analysis.*
