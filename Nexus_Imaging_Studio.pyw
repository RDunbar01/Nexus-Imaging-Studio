# NEXUS Imaging Studio v3.2.4. Verified reclaim and transaction repair build.
# Windows physical-device qualification is NOT performed by importing or self-testing this file.
# Release scope and reproducible tests are provided in the companion validation report.
from __future__ import annotations

import binascii
import traceback
import ctypes
from ctypes import wintypes
import hashlib
import json
import math
import os
import queue
import re
import shutil
import struct
import subprocess
import sys
import tempfile
import threading
import time
import uuid
from pathlib import Path
from tkinter import filedialog, messagebox, ttk
from tkinter import font as tkfont
import tkinter as tk

APP_NAME = "NEXUS Imaging Studio v3.2.4 CHROME / RAW ACCESS REPAIR"
APP_SUBTITLE = "Verified reclaim / bounded recovery / locked raw certification / host-safe handoff"
CHUNK = 4 * 1024 * 1024
EDGE_WIPE = 8 * 1024 * 1024
CREATE_NO_WINDOW = 0x08000000 if os.name == "nt" else 0
LOG_PATH = Path(tempfile.gettempdir()) / "NEXUS_Imaging_Studio_v3.2.4_RECLAIM_REPAIR.log"
ESP_GUID = uuid.UUID("c12a7328-f81f-11d2-ba4b-00a0c93ec93b")
APP_STATE_DIR = Path(os.getenv("APPDATA") or tempfile.gettempdir()) / "NEXUS_Imaging_Studio"
SETTINGS_PATH = APP_STATE_DIR / "settings.json"
RECOVERY_PATH = APP_STATE_DIR / "recovery_engine.json"
try:
    APP_STATE_DIR.mkdir(parents=True, exist_ok=True)
except Exception:
    pass

THEMES = {
    "NEXUS Chrome Honeycomb": {
        "BG": "#030609", "PANEL": "#0A1118", "PANEL_2": "#111E29", "BORDER": "#3C586D",
        "TEXT": "#F1F8FC", "MUTED": "#9CB0C0", "CYAN": "#39D4FF", "CYAN_2": "#087EAD",
        "GREEN": "#63DEC1", "AMBER": "#FFC36B", "RED": "#FF8391", "PURPLE": "#66BFFF",
        "SIDEBAR": "#020508", "NAV_ACTIVE": "#063E59", "GLASS": "#061B29", "ALPHA": 1.0,
        "GRAD_A": "#38CFFF", "GRAD_B": "#075B94"
    },
    "NEXUS Quantum Glass": {
        "BG": "#01040A", "PANEL": "#07101A", "PANEL_2": "#0A1724", "BORDER": "#20506D",
        "TEXT": "#F7FCFF", "MUTED": "#8FAABA", "CYAN": "#6EF2FF", "CYAN_2": "#20B7DD",
        "GREEN": "#62E8B6", "AMBER": "#FFC778", "RED": "#FF788E", "PURPLE": "#A58DFF",
        "SIDEBAR": "#010307", "NAV_ACTIVE": "#10293A", "GLASS": "#091521", "ALPHA": 0.996,
        "GRAD_A": "#86F6FF", "GRAD_B": "#7A74FF"
    },
    "NEXUS Hyperglass": {
        "BG": "#02050A", "PANEL": "#07111A", "PANEL_2": "#0B1824", "BORDER": "#1D415B",
        "TEXT": "#F5FBFF", "MUTED": "#8EABB9", "CYAN": "#61EDFF", "CYAN_2": "#1BB6D9",
        "GREEN": "#5AE7AE", "AMBER": "#FFC46E", "RED": "#FF738C", "PURPLE": "#A18CFF",
        "SIDEBAR": "#010409", "NAV_ACTIVE": "#112536", "GLASS": "#0A1520", "ALPHA": 0.994,
        "GRAD_A": "#7AF3FF", "GRAD_B": "#6A83FF"
    },
    "NEXUS Ultra": {
        "BG": "#03070C", "PANEL": "#08111A", "PANEL_2": "#0D1924", "BORDER": "#173244",
        "TEXT": "#F4FAFC", "MUTED": "#8AA4B4", "CYAN": "#56E7FF", "CYAN_2": "#169FC2",
        "GREEN": "#56DFA9", "AMBER": "#F5BC68", "RED": "#F16F83", "PURPLE": "#9D8BFF",
        "SIDEBAR": "#02060A", "NAV_ACTIVE": "#0D2834", "GLASS": "#0A151E", "ALPHA": 0.992,
        "GRAD_A": "#5DEBFF", "GRAD_B": "#527BFF"
    },
    "NEXUS HUD": {
        "BG": "#01070B", "PANEL": "#06131A", "PANEL_2": "#08202A", "BORDER": "#0A5262",
        "TEXT": "#E8FDFF", "MUTED": "#75AEB9", "CYAN": "#17F3F8", "CYAN_2": "#00BFD1",
        "GREEN": "#2BE6AE", "AMBER": "#FFC857", "RED": "#FF627A", "PURPLE": "#7F68FF",
        "SIDEBAR": "#010509", "NAV_ACTIVE": "#07313B", "GLASS": "#071820", "ALPHA": 0.982,
        "GRAD_A": "#00F5F5", "GRAD_B": "#168BFF"
    },
    "NEXUS Aurora": {
        "BG": "#040711", "PANEL": "#091321", "PANEL_2": "#0D1B2D", "BORDER": "#1C3C58",
        "TEXT": "#EFFCFF", "MUTED": "#83A8BE", "CYAN": "#21E6FF", "CYAN_2": "#0EA8D1",
        "GREEN": "#32E6A1", "AMBER": "#FFB84F", "RED": "#FF5E76", "PURPLE": "#9A78FF",
        "SIDEBAR": "#03060C", "NAV_ACTIVE": "#102B42", "GLASS": "#0B1827", "ALPHA": 0.975,
        "GRAD_A": "#15E8FF", "GRAD_B": "#8A61FF"
    },
    "NEXUS Obsidian": {
        "BG": "#050607", "PANEL": "#0D1115", "PANEL_2": "#141A20", "BORDER": "#29343F",
        "TEXT": "#F4FAFD", "MUTED": "#91A0AA", "CYAN": "#6CE9FF", "CYAN_2": "#2A9DB6",
        "GREEN": "#52D99B", "AMBER": "#DFAE56", "RED": "#E46779", "PURPLE": "#A28BE8",
        "SIDEBAR": "#020303", "NAV_ACTIVE": "#17232B", "GLASS": "#11171B", "ALPHA": 0.985,
        "GRAD_A": "#73EEFF", "GRAD_B": "#5966FF"
    },
    "NEXUS Spectre": {
        "BG": "#060511", "PANEL": "#100D22", "PANEL_2": "#18132E", "BORDER": "#40325C",
        "TEXT": "#F8F4FF", "MUTED": "#AA9BC1", "CYAN": "#55E7FF", "CYAN_2": "#3A9ED4",
        "GREEN": "#51E1A7", "AMBER": "#F0AF55", "RED": "#FF617E", "PURPLE": "#C071FF",
        "SIDEBAR": "#05030B", "NAV_ACTIVE": "#231A3B", "GLASS": "#151027", "ALPHA": 0.970,
        "GRAD_A": "#2BE7FF", "GRAD_B": "#D04CFF"
    },
    "NEXUS Arctic": {
        "BG": "#08121A", "PANEL": "#0E202B", "PANEL_2": "#15313F", "BORDER": "#2B6073",
        "TEXT": "#F2FDFF", "MUTED": "#9FC4CE", "CYAN": "#71F0FF", "CYAN_2": "#28B6CA",
        "GREEN": "#60E7B7", "AMBER": "#FFC568", "RED": "#FF7184", "PURPLE": "#A4A0FF",
        "SIDEBAR": "#061017", "NAV_ACTIVE": "#173B49", "GLASS": "#102A36", "ALPHA": 0.985,
        "GRAD_A": "#7FF5FF", "GRAD_B": "#6B9FFF"
    }
}

# Win32 file/disk I/O
GENERIC_READ = 0x80000000
GENERIC_WRITE = 0x40000000
FILE_SHARE_READ = 0x00000001
FILE_SHARE_WRITE = 0x00000002
OPEN_EXISTING = 3
FILE_ATTRIBUTE_NORMAL = 0x00000080
FILE_FLAG_WRITE_THROUGH = 0x80000000
INVALID_HANDLE_VALUE = ctypes.c_void_p(-1).value
FSCTL_LOCK_VOLUME = 0x00090018
FSCTL_UNLOCK_VOLUME = 0x0009001C
FSCTL_DISMOUNT_VOLUME = 0x00090020
FSCTL_ALLOW_EXTENDED_DASD_IO = 0x00090083
IOCTL_DISK_UPDATE_PROPERTIES = 0x00070140
IOCTL_DISK_DELETE_DRIVE_LAYOUT = 0x0007C100
_diskpart_lock = threading.Lock()
_diskpart_finished = None


class MediaOperationError(RuntimeError):
    """Stable failure code, separate from diagnostic text and disk properties."""
    def __init__(self, code, message):
        self.code = code
        super().__init__(f"[{code}] {message}")

TOKEN_ADJUST_PRIVILEGES = 0x0020
TOKEN_QUERY = 0x0008
SE_PRIVILEGE_ENABLED = 0x00000002

kernel32 = ctypes.WinDLL("kernel32", use_last_error=True) if os.name == "nt" else None
if kernel32:
    kernel32.GetCurrentProcess.argtypes = []
    kernel32.GetCurrentProcess.restype = wintypes.HANDLE
    kernel32.CreateFileW.argtypes = [
        wintypes.LPCWSTR, wintypes.DWORD, wintypes.DWORD, wintypes.LPVOID,
        wintypes.DWORD, wintypes.DWORD, wintypes.HANDLE,
    ]
    kernel32.CreateFileW.restype = wintypes.HANDLE
    kernel32.ReadFile.argtypes = [
        wintypes.HANDLE, wintypes.LPVOID, wintypes.DWORD,
        ctypes.POINTER(wintypes.DWORD), wintypes.LPVOID,
    ]
    kernel32.ReadFile.restype = wintypes.BOOL
    kernel32.WriteFile.argtypes = [
        wintypes.HANDLE, wintypes.LPCVOID, wintypes.DWORD,
        ctypes.POINTER(wintypes.DWORD), wintypes.LPVOID,
    ]
    kernel32.WriteFile.restype = wintypes.BOOL
    kernel32.FlushFileBuffers.argtypes = [wintypes.HANDLE]
    kernel32.FlushFileBuffers.restype = wintypes.BOOL
    kernel32.CloseHandle.argtypes = [wintypes.HANDLE]
    kernel32.CloseHandle.restype = wintypes.BOOL
    kernel32.DeviceIoControl.argtypes = [
        wintypes.HANDLE, wintypes.DWORD, wintypes.LPVOID, wintypes.DWORD,
        wintypes.LPVOID, wintypes.DWORD, ctypes.POINTER(wintypes.DWORD),
        wintypes.LPVOID,
    ]
    kernel32.DeviceIoControl.restype = wintypes.BOOL
    kernel32.SetFilePointerEx.argtypes = [
        wintypes.HANDLE, ctypes.c_longlong, ctypes.POINTER(ctypes.c_longlong),
        wintypes.DWORD,
    ]
    kernel32.SetFilePointerEx.restype = wintypes.BOOL

cfgmgr32 = ctypes.WinDLL("cfgmgr32", use_last_error=True) if os.name == "nt" else None
if cfgmgr32:
    cfgmgr32.CM_Locate_DevNodeW.argtypes = [ctypes.POINTER(wintypes.DWORD), wintypes.LPCWSTR, wintypes.DWORD]
    cfgmgr32.CM_Locate_DevNodeW.restype = wintypes.DWORD
    cfgmgr32.CM_Request_Device_EjectW.argtypes = [wintypes.DWORD, ctypes.POINTER(ctypes.c_int), wintypes.LPWSTR, wintypes.DWORD, wintypes.DWORD]
    cfgmgr32.CM_Request_Device_EjectW.restype = wintypes.DWORD

dwmapi = ctypes.WinDLL("dwmapi", use_last_error=True) if os.name == "nt" else None
if dwmapi:
    dwmapi.DwmSetWindowAttribute.argtypes = [wintypes.HWND, wintypes.DWORD, wintypes.LPCVOID, wintypes.DWORD]
    dwmapi.DwmSetWindowAttribute.restype = ctypes.c_long

advapi32 = ctypes.WinDLL("advapi32", use_last_error=True) if os.name == "nt" else None
if advapi32:
    advapi32.OpenProcessToken.argtypes = [wintypes.HANDLE, wintypes.DWORD, ctypes.POINTER(wintypes.HANDLE)]
    advapi32.OpenProcessToken.restype = wintypes.BOOL
    advapi32.LookupPrivilegeValueW.argtypes = [wintypes.LPCWSTR, wintypes.LPCWSTR, wintypes.LPVOID]
    advapi32.LookupPrivilegeValueW.restype = wintypes.BOOL
    advapi32.AdjustTokenPrivileges.argtypes = [wintypes.HANDLE, wintypes.BOOL, wintypes.LPVOID, wintypes.DWORD, wintypes.LPVOID, wintypes.LPVOID]
    advapi32.AdjustTokenPrivileges.restype = wintypes.BOOL


class LUID(ctypes.Structure):
    _fields_ = [("LowPart", wintypes.DWORD), ("HighPart", wintypes.LONG)]


class LUID_AND_ATTRIBUTES(ctypes.Structure):
    _fields_ = [("Luid", LUID), ("Attributes", wintypes.DWORD)]


class TOKEN_PRIVILEGES_1(ctypes.Structure):
    _fields_ = [("PrivilegeCount", wintypes.DWORD), ("Privileges", LUID_AND_ATTRIBUTES * 1)]


# ---------------------------------------------------------------------------
# General helpers
# ---------------------------------------------------------------------------

def enable_uhd_dpi_awareness() -> None:
    """Opt into crisp per-monitor Windows DPI rendering before Tk creates windows."""
    if os.name != "nt":
        return
    try:
        user32 = ctypes.windll.user32
        try:
            # DPI_AWARENESS_CONTEXT_PER_MONITOR_AWARE_V2 = -4
            if user32.SetProcessDpiAwarenessContext(ctypes.c_void_p(-4)):
                return
        except Exception:
            pass
        try:
            user32.SetProcessDPIAware()
        except Exception:
            pass
    except Exception:
        pass

def log_file(text: str) -> None:
    try:
        with LOG_PATH.open("a", encoding="utf-8") as f:
            f.write(time.strftime("%Y-%m-%d %H:%M:%S ") + text.rstrip() + "\n")
    except Exception:
        pass


def human_size(n: int) -> str:
    f = float(max(0, n))
    for unit in ("B", "KB", "MB", "GB", "TB"):
        if f < 1024 or unit == "TB":
            return f"{f:.1f} {unit}"
        f /= 1024
    return str(n)


def human_time(seconds: float) -> str:
    if not math.isfinite(seconds) or seconds < 0:
        return "—"
    seconds = int(seconds)
    h, rem = divmod(seconds, 3600)
    m, s = divmod(rem, 60)
    if h:
        return f"{h:d}h {m:02d}m"
    if m:
        return f"{m:d}m {s:02d}s"
    return f"{s:d}s"


def align_up(value: int, alignment: int) -> int:
    alignment = max(1, int(alignment))
    return ((int(value) + alignment - 1) // alignment) * alignment


def win_error(prefix: str) -> RuntimeError:
    n = ctypes.get_last_error()
    detail = ctypes.FormatError(n).strip()
    if n == 5:
        detail += (
            " NEXUS could not obtain raw-disk write access. Close Explorer or any program "
            "using the USB, check a physical SD/microSD lock switch, then use Factory Reset / "
            "Reclaim and retry."
        )
    exc = RuntimeError(f"{prefix} (Windows error {n}: {detail})")
    exc.winerror = n
    return exc


def crc32(data: bytes) -> int:
    return binascii.crc32(data) & 0xFFFFFFFF


def sanitize_label(value: str) -> str:
    value = re.sub(r"[^A-Za-z0-9 _.-]", "_", (value or "NEXUS_USB").strip())
    return (value[:32] or "NEXUS_USB").strip()


def load_json_file(path, default):
    try:
        if Path(path).is_file():
            return json.loads(Path(path).read_text(encoding="utf-8"))
    except Exception:
        pass
    return default


def save_json_file(path, value):
    temp_path = None
    try:
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        with tempfile.NamedTemporaryFile("w", encoding="utf-8", dir=path.parent, prefix="."+path.name+".", suffix=".tmp", delete=False) as f:
            temp_path = Path(f.name)
            json.dump(value, f, indent=2, sort_keys=True)
            f.flush()
            os.fsync(f.fileno())
        os.replace(temp_path, path)
        return True
    except Exception:
        return False
    finally:
        if temp_path is not None:
            try: temp_path.unlink(missing_ok=True)
            except OSError: pass


def hex_rgb(value):
    value = str(value).lstrip("#")
    if len(value) != 6:
        return (0, 0, 0)
    return tuple(int(value[i:i+2], 16) for i in (0, 2, 4))


def rgb_hex(rgb):
    return "#" + "".join(f"{max(0, min(255, int(v))):02X}" for v in rgb)


def blend_hex(a, b, t):
    ar = hex_rgb(a); br = hex_rgb(b); t = max(0.0, min(1.0, float(t)))
    return rgb_hex(tuple(ar[i] + (br[i] - ar[i]) * t for i in range(3)))


def normalize_verify_mode(value):
    value = str(value or "").strip()
    low = value.lower()
    if low.startswith("aegis adaptive") or low.startswith("smart verify"):
        return "Smart verify (recommended)"
    if low.startswith("strict forensic") or low.startswith("strict byte"):
        return "Strict byte-for-byte"
    if low.startswith("structure"):
        return "Structure only"
    return "Smart verify (recommended)"


def verification_display_name(value):
    mode = normalize_verify_mode(value)
    if mode == "Strict byte-for-byte":
        return "Strict forensic byte-for-byte"
    if mode == "Structure only":
        return "Structure only"
    return "AEGIS Adaptive (recommended)"


def mismatch_is_gpt_metadata(image_path, offset):
    try:
        with ImageReader(image_path) as reader:
            ranges = gpt_metadata_ignore_ranges(reader)
        off = int(offset)
        return any(int(a) <= off < int(b) for a, b in ranges)
    except Exception:
        return False


def _colorref(hex_value):
    r, g, b = hex_rgb(hex_value)
    return int(r | (g << 8) | (b << 16))


def apply_windows_dark_chrome(root, caption_bg="#02070B", caption_text="#E8FDFF", border="#075061"):
    if os.name != "nt" or not dwmapi:
        return False
    try:
        root.update_idletasks()
        user32 = ctypes.WinDLL("user32", use_last_error=True)
        user32.GetAncestor.argtypes = [wintypes.HWND, wintypes.UINT]
        user32.GetAncestor.restype = wintypes.HWND
        hwnd = user32.GetAncestor(wintypes.HWND(root.winfo_id()), 2) or wintypes.HWND(root.winfo_id())
        enabled = ctypes.c_int(1)
        ok = False
        for attr in (20, 19):
            try:
                if dwmapi.DwmSetWindowAttribute(hwnd, attr, ctypes.byref(enabled), ctypes.sizeof(enabled)) == 0:
                    ok = True
                    break
            except Exception:
                pass
        for attr, color in ((35, caption_bg), (36, caption_text), (34, border)):
            try:
                value = wintypes.DWORD(_colorref(color))
                dwmapi.DwmSetWindowAttribute(hwnd, attr, ctypes.byref(value), ctypes.sizeof(value))
            except Exception:
                pass
        return ok
    except Exception:
        return False


class RecoveryEngine:
    """Persistent adaptive recovery knowledge for known removable-media failure classes.

    This engine does not rewrite application code. It fingerprints failures, remembers
    the recovery path that was required, and escalates deterministic repair steps on
    later operations. This is intentionally bounded and auditable.
    """
    PATTERNS = [
        ("ACCESS_DENIED", ("windows error 5", "access is denied", "raw write access")),
        ("GPT_VERIFY_NORMALIZATION", ("gpt metadata", "mismatch at byte offset 528", "0x00000210")),
        ("HOST_POST_CERT_MUTATION", ("final host-visible verification failed", "post-cert audit mismatch", "0x0900400c", "0x090003e8")),
        ("VERIFY_MISMATCH", ("verification failed", "does not match the source", "byte-for-byte")),
        ("WRITE_PROTECTED", ("write protected", "write-protected", "still read-only", "remains read-only", "became read-only", "windows error 19")),
        ("PARTITION_BUSY", ("still reports target partitions", "could not lock", "dismount")),
        ("MEDIA_IO", ("short raw write", "verification read ended early", "i/o device error", "crc", "windows error 21", "device is not ready", "windows error 1117")),
        ("FORMAT_FAILURE", ("format-volume", "format failed", "filesystem")),
        ("SOFTWARE_REGRESSION", ("unexpected keyword argument", "typeerror", "attributeerror", "nameerror")),
    ]

    REMEDIES = {
        "RECLAIM_INCOMPLETE": "Cleanup could not verify an empty layout after Storage, DiskPart and native removal. Export the backend log; reconnect and reselect the USB before retrying.",
        "SOURCE_CHANGED": "Source image changed, shrank or grew during the operation. Obtain a stable local copy and retry; the partial target is not certified.",
        "STORAGE_COMMAND": "Inspect the command exit code and complete backend log. A returned command is not proof of a successful disk change.",
        "ACCESS_DENIED": "Review the original Windows error and RAW OPEN entries; close applications using this disk. Shared-compatible acquisition retains volume locks through verification.",
        "GPT_VERIFY_NORMALIZATION": "Exact image bytes are certified before Windows storage refresh. If a GPT mismatch persists inside the locked certification barrier, treat it as a real write/media fault.",
        "HOST_POST_CERT_MUTATION": "Do not retry the raw write solely because Windows changed filesystem bookkeeping after locked certification. v3.2.2 uses post-handoff structural health instead of retroactive byte re-certification.",
        "VERIFY_MISMATCH": "A mismatch that persists inside the locked certification barrier is a real write/readback failure and must fail closed.",
        "WRITE_PROTECTED": "Clear disk attributes through Storage cmdlets and DiskPart; inspect Windows removable-storage policy.",
        "PARTITION_BUSY": "Repeat hidden-volume dismount and wait longer for the mount manager before raw acquisition.",
        "MEDIA_IO": "Re-resolve the selected media by stable identity, refresh storage state, retry the raw transaction, then fail closed if the controller remains unstable.",
        "FORMAT_FAILURE": "Refresh the storage cache, bring disk online/writable, and retry formatting through the alternate backend.",
        "SOFTWARE_REGRESSION": "Fail closed and report an internal compatibility defect; do not blame or retire the removable media.",
    }

    def __init__(self, path=RECOVERY_PATH):
        self.path = Path(path)
        self.data = load_json_file(self.path, {"version": 1, "failures": {}, "last_success": None})
        if not isinstance(self.data, dict):
            self.data = {"version": 1, "failures": {}, "last_success": None}
        if not isinstance(self.data.get("failures"), dict): self.data["failures"] = {}
        clean = {}
        for key, entry in self.data["failures"].items():
            if not isinstance(entry, dict): continue
            try: count = max(0, int(entry.get("count", 0)))
            except (ValueError, TypeError): count = 0
            clean[str(key)] = dict(entry, count=count)
        # Reclassify historical false positives once; keep the occurrence history.
        if self.data.get("version", 1) < 2:
            migrated = {}
            for key, entry in clean.items():
                new_key = self.fingerprint(entry.get("last_error")) if entry.get("last_error") else key
                entry["remedy"] = self.REMEDIES.get(new_key, "Capture diagnostics and fail closed.")
                if new_key in migrated:
                    entry["count"] += migrated[new_key]["count"]
                migrated[new_key] = entry
            clean = migrated
            self.data["version"] = 2
        self.data["failures"] = clean

    def fingerprint(self, error_text):
        text = str(error_text or "").lower()
        code = re.search(r"\[([a-z_]+)\]", text)
        if code and code.group(1).upper() in self.REMEDIES:
            return code.group(1).upper()
        if "still reports target partitions" in text:
            return "RECLAIM_INCOMPLETE"
        # Discard dictionary/JSON state fields such as IsReadOnly: False.
        text = re.sub(r"['\"]?(?:isreadonly|read-only|readonly)['\"]?\s*[:=]\s*(?:false|0)\b", "", text)
        if re.search(r"['\"]?isreadonly['\"]?\s*[:=]\s*true\b", text):
            return "WRITE_PROTECTED"
        for key, parts in self.PATTERNS:
            if any(p.lower() in text for p in parts):
                return key
        return "UNKNOWN"

    def record_failure(self, error_text):
        key = self.fingerprint(error_text)
        entry = self.data["failures"].setdefault(key, {"count": 0, "last": None, "last_error": "", "remedy": self.REMEDIES.get(key, "Capture diagnostics and fail closed.")})
        entry["remedy"] = self.REMEDIES.get(key, "Capture diagnostics and fail closed.")
        entry["count"] = int(entry.get("count", 0)) + 1
        entry["last"] = time.strftime("%Y-%m-%dT%H:%M:%S")
        entry["last_error"] = str(error_text)[:1200]
        save_json_file(self.path, self.data)
        return key, entry

    def record_success(self, operation="flash"):
        self.data["last_success"] = {"operation": operation, "time": time.strftime("%Y-%m-%dT%H:%M:%S")}
        save_json_file(self.path, self.data)

    def count(self, key):
        return int(self.data.get("failures", {}).get(key, {}).get("count", 0))

    def adaptive_profile(self):
        return {
            "aggressive_reclaim": self.count("ACCESS_DENIED") > 0 or self.count("PARTITION_BUSY") > 0 or self.count("RECLAIM_INCOMPLETE") > 0,
            "mount_manager_delay": 1.25 if self.count("ACCESS_DENIED") > 0 else 0.25,
            "prefer_smart_verify": self.count("GPT_VERIFY_NORMALIZATION") > 0 or self.count("VERIFY_MISMATCH") > 0,
            "extra_media_check": self.count("MEDIA_IO") > 0,
        }

    def summary(self):
        failures = self.data.get("failures", {})
        if not failures:
            return "AEGIS recovery memory: clean — no recorded failures."
        parts = [f"{k}:{int(v.get('count',0))}" for k, v in sorted(failures.items()) if int(v.get('count',0)) > 0]
        return "AEGIS recovery memory — " + ", ".join(parts)

    def reset(self):
        self.data = {"version": 1, "failures": {}, "last_success": None}
        save_json_file(self.path, self.data)


def enable_privilege(name: str) -> bool:
    """Enable a privilege that is already present in the elevated process token."""
    if os.name != "nt" or not advapi32 or not kernel32:
        return False
    token = wintypes.HANDLE()
    if not advapi32.OpenProcessToken(kernel32.GetCurrentProcess(), TOKEN_ADJUST_PRIVILEGES | TOKEN_QUERY, ctypes.byref(token)):
        return False
    try:
        luid = LUID()
        if not advapi32.LookupPrivilegeValueW(None, name, ctypes.byref(luid)):
            return False
        tp = TOKEN_PRIVILEGES_1()
        tp.PrivilegeCount = 1
        tp.Privileges[0].Luid = luid
        tp.Privileges[0].Attributes = SE_PRIVILEGE_ENABLED
        ctypes.set_last_error(0)
        if not advapi32.AdjustTokenPrivileges(token, False, ctypes.byref(tp), 0, None, None):
            return False
        return ctypes.get_last_error() == 0
    finally:
        kernel32.CloseHandle(token)


def enable_raw_disk_privileges():
    results = {}
    for name in ("SeManageVolumePrivilege", "SeBackupPrivilege", "SeRestorePrivilege"):
        try:
            results[name] = enable_privilege(name)
        except Exception:
            results[name] = False
    return results


def storage_write_policy_diagnostics():
    """Return active Windows registry policies that can block removable-media writes."""
    if os.name != "nt":
        return []
    try:
        import winreg
    except Exception:
        return []
    found = []

    def read_dword(root, path, name):
        try:
            with winreg.OpenKey(root, path, 0, winreg.KEY_READ) as k:
                value, _ = winreg.QueryValueEx(k, name)
                return int(value)
        except Exception:
            return 0

    if read_dword(winreg.HKEY_LOCAL_MACHINE, r"SYSTEM\CurrentControlSet\Control\StorageDevicePolicies", "WriteProtect"):
        found.append(r"HKLM StorageDevicePolicies\WriteProtect=1")

    roots = [
        ("HKLM", winreg.HKEY_LOCAL_MACHINE),
        ("HKCU", winreg.HKEY_CURRENT_USER),
    ]
    base = r"SOFTWARE\Policies\Microsoft\Windows\RemovableStorageDevices"

    def scan(root_name, root, path, depth=0):
        if depth > 3:
            return
        if read_dword(root, path, "Deny_Write"):
            found.append(f"{root_name} {path}\\Deny_Write=1")
        try:
            with winreg.OpenKey(root, path, 0, winreg.KEY_READ) as k:
                i = 0
                while True:
                    try:
                        child = winreg.EnumKey(k, i)
                    except OSError:
                        break
                    scan(root_name, root, path + "\\" + child, depth + 1)
                    i += 1
        except Exception:
            pass

    for root_name, root in roots:
        scan(root_name, root, base)
    return found


def raw_access_diagnostics(number=None):
    lines = [f"Administrator: {'YES' if is_admin() else 'NO'}"]
    policies = storage_write_policy_diagnostics()
    lines.append("Windows removable-write policy: " + ("BLOCKED — " + "; ".join(policies) if policies else "no active Deny_Write/WriteProtect policy detected"))
    try:
        disabled = get_automount_disabled()
        lines.append("Windows automount: " + ("DISABLED / shielded for raw access" if disabled else "enabled"))
    except Exception:
        pass
    if number is not None:
        try:
            d = get_disk(int(number))
            lines.extend([
                f"Disk {d.get('Number')} / {d.get('FriendlyName')}",
                f"Bus: {d.get('BusType')}   Health: {d.get('HealthStatus')}   Operational: {d.get('OperationalStatus')}",
                f"Read-only: {d.get('IsReadOnly')}   Offline: {d.get('IsOffline')}   Partitions: {d.get('NumberOfPartitions')}",
                f"Logical sector: {d.get('LogicalSectorSize') or 512} B   Physical sector: {d.get('PhysicalSectorSize') or 0} B",
            ])
        except Exception as e:
            lines.append(f"Disk status query failed: {e}")
    return lines


# ---------------------------------------------------------------------------
# Image / boot structure validation (preserved and extended from v1.4)
# ---------------------------------------------------------------------------


def image_stamp(path):
    st = Path(path).stat()
    return (st.st_dev, st.st_ino, st.st_size, st.st_mtime_ns, st.st_ctime_ns)


class SourceImageGuard:
    """Read-only source handle denying write/delete sharing on Windows."""
    def __init__(self, path, expected_stamp=None):
        self.path = Path(path)
        self.handle = None
        try:
            if os.name == 'nt':
                self.handle = open_handle(str(self.path.resolve()), GENERIC_READ, FILE_SHARE_READ)
            self.stamp = image_stamp(self.path)
            if expected_stamp is not None and tuple(expected_stamp) != self.stamp:
                raise MediaOperationError('SOURCE_CHANGED', 'Source changed after selection. Reselect and validate the image.')
            if self.stamp[2] <= 0:
                raise MediaOperationError('SOURCE_CHANGED', 'Source image is empty.')
        except BaseException:
            self.close()
            raise

    def check(self):
        if image_stamp(self.path) != self.stamp:
            raise MediaOperationError('SOURCE_CHANGED', 'Source image changed during the operation; the target is incomplete.')

    def close(self):
        if self.handle is not None:
            self.handle.close()
            self.handle = None


def copy_image_stream(source, handle, total, sector, checkpoint=None, progress=None):
    """Bounded stream copy: truncation/growth must never certify a partial image."""
    digest = hashlib.sha256()
    done = 0
    raw_seek(handle, 0)
    while done < total:
        if checkpoint:
            checkpoint()
        wanted = min(CHUNK, total - done)
        block = source.read(wanted)
        if len(block) != wanted:
            raise MediaOperationError('SOURCE_CHANGED', f'Source image ended early at byte {done + len(block)} of {total}.')
        digest.update(block)
        done += len(block)
        if done == total and len(block) % sector:
            block += b'\x00' * (sector - len(block) % sector)
        raw_write(handle, block)
        if progress:
            progress(done, total)
    if source.read(1):
        raise MediaOperationError('SOURCE_CHANGED', 'Source image grew during copying; no bytes beyond the confirmed length were written.')
    return digest.hexdigest()


class ImageReader:
    def __init__(self, path):
        self.path = Path(path)
        self.f = self.path.open("rb")
        self.size = self.path.stat().st_size

    def read_at(self, off, n):
        if off < 0 or n < 0 or off + n > self.size:
            return b""
        self.f.seek(off)
        return self.f.read(n)

    def close(self):
        self.f.close()

    def __enter__(self):
        return self

    def __exit__(self, *_):
        self.close()


class RawHandleReader:
    def __init__(self, handle, size):
        self.handle = handle
        self.size = size

    def read_at(self, off, n):
        if off < 0 or n < 0 or off + n > self.size:
            return b""
        raw_seek(self.handle, off)
        return raw_read(self.handle, n)


def parse_mbr(reader):
    mbr = reader.read_at(0, 512)
    if len(mbr) < 512 or mbr[510:512] != b"\x55\xAA":
        return {"valid": False, "partitions": [], "protective_gpt": False}
    parts, protective = [], False
    for i in range(4):
        e = mbr[446 + i * 16:446 + (i + 1) * 16]
        ptype = e[4]
        first = struct.unpack_from("<I", e, 8)[0]
        sectors = struct.unpack_from("<I", e, 12)[0]
        if ptype and sectors:
            parts.append({"type": ptype, "first_lba": first, "sectors": sectors})
            protective |= ptype == 0xEE
    return {"valid": True, "partitions": parts, "protective_gpt": protective}


def parse_gpt(reader):
    try:
        g=_gpt_header(reader,1,512)
        if g["entries_lba"]*512+g["entries_span"]>g["first"]*512 or g["last"]>=g["backup"]-g["entries_span"]//512:
            raise ValueError("GPT metadata overlaps usable space.")
        parts=[];intervals=[]
        for i in range(g["count"]):
            e=g["entries"][i*g["esize"]:(i+1)*g["esize"]]
            if e[:16]==b"\0"*16:continue
            first,last=struct.unpack_from("<QQ",e,32)
            if not g["first"]<=first<=last<=g["last"]:raise ValueError("GPT partition exceeds usable geometry.")
            intervals.append((first,last))
            parts.append({"index":i+1,"type_guid":str(uuid.UUID(bytes_le=e[:16])),"first_lba":first,"last_lba":last,"sectors":last-first+1})
        intervals.sort()
        if any(a[1]>=b[0] for a,b in zip(intervals,intervals[1:])):raise ValueError("Overlapping GPT partitions.")
        return {"valid":True,"partitions":parts}
    except (ValueError,struct.error,OverflowError) as exc:
        return {"valid":False,"error":str(exc),"partitions":[]}


def fat32_info(reader, part_offset):
    bs = reader.read_at(part_offset, 512)
    if len(bs) < 512 or bs[510:512] != b"\x55\xAA":
        return {"valid": False, "error": "FAT boot sector signature missing"}
    bps = struct.unpack_from("<H", bs, 11)[0]
    spc = bs[13]
    reserved = struct.unpack_from("<H", bs, 14)[0]
    fats = bs[16]
    root_entries = struct.unpack_from("<H", bs, 17)[0]
    fat16 = struct.unpack_from("<H", bs, 22)[0]
    fat32 = struct.unpack_from("<I", bs, 36)[0]
    root_cluster = struct.unpack_from("<I", bs, 44)[0]
    if bps not in (512, 1024, 2048, 4096) or spc == 0 or (spc & (spc - 1)):
        return {"valid": False, "error": "Invalid FAT geometry"}
    if not reserved or not fats or not fat32 or root_entries != 0 or fat16 != 0 or root_cluster < 2:
        return {"valid": False, "error": "EFI System Partition is not valid FAT32"}
    return {
        "valid": True,
        "bps": bps,
        "spc": spc,
        "fat_off": part_offset + reserved * bps,
        "data_off": part_offset + (reserved + fats * fat32) * bps,
        "root_cluster": root_cluster,
    }


def fat32_next(reader, info, cluster):
    raw = reader.read_at(info["fat_off"] + cluster * 4, 4)
    return (struct.unpack("<I", raw)[0] & 0x0FFFFFFF) if len(raw) == 4 else 0x0FFFFFFF


def fat32_cluster(reader, info, cluster):
    size = info["bps"] * info["spc"]
    return reader.read_at(info["data_off"] + (cluster - 2) * size, size)


def fat_name(raw11):
    base = raw11[:8].decode("ascii", "ignore").rstrip()
    ext = raw11[8:11].decode("ascii", "ignore").rstrip()
    return base + (("." + ext) if ext else "")


def fat32_find(reader, info, start_cluster, wanted):
    cluster, seen, wanted = start_cluster, set(), wanted.upper()
    while 2 <= cluster < 0x0FFFFFF8 and cluster not in seen and len(seen) < 4096:
        seen.add(cluster)
        data = fat32_cluster(reader, info, cluster)
        if not data:
            return None
        for pos in range(0, len(data), 32):
            e = data[pos:pos + 32]
            if len(e) < 32 or e[0] == 0x00:
                return None
            if e[0] == 0xE5 or e[11] == 0x0F:
                continue
            if fat_name(e[:11]).upper() == wanted:
                high = struct.unpack_from("<H", e, 20)[0]
                low = struct.unpack_from("<H", e, 26)[0]
                return {
                    "attr": e[11],
                    "cluster": (high << 16) | low,
                    "size": struct.unpack_from("<I", e, 28)[0],
                }
        cluster = fat32_next(reader, info, cluster)
    return None


def validate_efi_tree(reader, esp_offset):
    info = fat32_info(reader, esp_offset)
    if not info.get("valid"):
        return {"valid": False, "error": info.get("error")}
    efi = fat32_find(reader, info, info["root_cluster"], "EFI")
    if not efi or not (efi["attr"] & 0x10):
        return {"valid": False, "error": "EFI directory missing"}
    boot = fat32_find(reader, info, efi["cluster"], "BOOT")
    if not boot or not (boot["attr"] & 0x10):
        return {"valid": False, "error": "EFI/BOOT directory missing"}
    loader = fat32_find(reader, info, boot["cluster"], "BOOTX64.EFI")
    if not loader or loader["size"] <= 0:
        return {"valid": False, "error": "EFI/BOOT/BOOTX64.EFI missing or empty"}
    return {"valid": True, "loader_size": loader["size"]}


def detect_iso9660(reader):
    # ISO9660 Primary Volume Descriptor is at logical block 16, block size 2048.
    sig = reader.read_at(16 * 2048, 7)
    return len(sig) >= 6 and sig[1:6] == b"CD001"


def validate_boot_reader(reader, suffix=""):
    out = {
        "valid": False,
        "format": "unknown",
        "errors": [],
        "warnings": [],
        "loader_size": 0,
        "optical_iso": False,
    }
    if reader.size < 1024 * 1024:
        out["errors"].append("Image is too small to be a bootable USB image.")
        return out
    mbr = parse_mbr(reader)
    if not mbr["valid"]:
        optical = suffix.lower() == ".iso" and detect_iso9660(reader)
        out["optical_iso"] = optical
        if optical:
            out["errors"].append(
                "Optical ISO detected, but it has no USB MBR/GPT map. Raw flashing may not boot from USB. "
                "Use a hybrid USB image or enable Advanced / Force raw image only if you understand the risk."
            )
        elif suffix.lower() == ".iso":
            out["errors"].append(
                "ISO has no USB MBR/GPT partition map. Use a hybrid USB image or Advanced / Force raw image."
            )
        else:
            out["errors"].append("No valid MBR signature at sector 0.")
        return out
    if mbr["protective_gpt"]:
        gpt = parse_gpt(reader)
        if not gpt.get("valid"):
            out["errors"].append(gpt.get("error", "Invalid GPT"))
            return out
        out["format"] = "GPT"
        esps = [p for p in gpt["partitions"] if p["type_guid"].lower() == str(ESP_GUID)]
        if not esps:
            out["errors"].append("GPT has no EFI System Partition.")
            return out
        esp_offset = esps[0]["first_lba"] * 512
    else:
        out["format"] = "MBR"
        esps = [p for p in mbr["partitions"] if p["type"] == 0xEF]
        if not esps:
            out["errors"].append("MBR has no EFI partition. UEFI boot cannot be validated.")
            return out
        esp_offset = esps[0]["first_lba"] * 512
    tree = validate_efi_tree(reader, esp_offset)
    if not tree.get("valid"):
        out["errors"].append(tree.get("error", "Invalid EFI tree"))
        return out
    out["valid"] = True
    out["loader_size"] = tree["loader_size"]
    if suffix.lower() == ".iso":
        out["warnings"].append(
            "ISO accepted because it contains a valid raw USB partition map and UEFI loader."
        )
    return out


def validate_boot_image(path):
    p = Path(path)
    try:
        if not p.is_file():
            return {"valid": False, "errors": ["Image does not exist."], "warnings": []}
        st = p.stat()
        with ImageReader(p) as r:
            result = validate_boot_reader(r, p.suffix)
        end = p.stat()
        if (st.st_size, st.st_mtime_ns) != (end.st_size, end.st_mtime_ns):
            return {"valid": False, "errors": ["Source image changed during validation."], "warnings": []}
        result["_path"] = str(path)
        result["_stamp"] = (st.st_size, st.st_mtime_ns)
        return result
    except Exception as exc:
        return {"valid": False, "errors": [f"Image validation error: {exc}"], "warnings": []}


# ---------------------------------------------------------------------------
# Privilege / process helpers
# ---------------------------------------------------------------------------

def is_admin():
    try:
        return os.name == "nt" and bool(ctypes.windll.shell32.IsUserAnAdmin())
    except Exception:
        return False


def relaunch_as_admin():
    if os.name != "nt":
        return False
    exe = sys.executable
    params = "" if getattr(sys, "frozen", False) else f'"{os.path.abspath(__file__)}"'
    return ctypes.windll.shell32.ShellExecuteW(None, "runas", exe, params, None, 1) > 32


def run_ps(script, timeout=240):
    script = "[Console]::OutputEncoding=[System.Text.UTF8Encoding]::new($false); $OutputEncoding=[Console]::OutputEncoding; " + script
    p = subprocess.run(
        [
            "powershell.exe", "-NoLogo", "-NoProfile", "-NonInteractive",
            "-ExecutionPolicy", "Bypass", "-Command", script,
        ],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=timeout,
        creationflags=CREATE_NO_WINDOW,
    )
    if p.returncode:
        raise RuntimeError((p.stderr or p.stdout or "PowerShell failed").strip())
    return (p.stdout or "").strip()


def ps_json(script, timeout=240):
    raw = run_ps(script, timeout=timeout)
    if not raw:
        return []
    v = json.loads(raw)
    return v if isinstance(v, list) else [v]


def run_diskpart(lines, timeout=180, preflight=None):
    """Use script mode so failed selection stops before destructive commands.

    Microsoft documents a 15-second shutdown gap between scripts. Recheck the
    selected target AFTER that gap, immediately before launching a fallback.
    Exit status is checked; callers must still verify the actual disk state.
    """
    global _diskpart_finished
    commands = [str(line) for line in lines]
    if any('\n' in line or '\r' in line for line in commands):
        raise ValueError('DiskPart commands must be single lines.')
    path = None
    with _diskpart_lock:
        if _diskpart_finished is not None:
            delay = max(0.0, 15.0 - (time.monotonic() - _diskpart_finished))
            if delay:
                time.sleep(delay)
        try:
            with tempfile.NamedTemporaryFile('w', suffix='.txt', encoding='ascii',
                                             newline='', delete=False) as f:
                path = Path(f.name)
                f.write('\r\n'.join(commands + ['exit', '']))
            if preflight:
                preflight()
            try:
                proc = subprocess.run(
                    ['diskpart.exe', '/s', str(path)], capture_output=True,
                    text=True, errors='replace', timeout=timeout,
                    creationflags=CREATE_NO_WINDOW)
            finally:
                _diskpart_finished = time.monotonic()
            out = ((proc.stdout or '') + '\n' + (proc.stderr or '')).strip()
            log_file('DISKPART: ' + out)
            # noerr steps are optional attribute normalization. Their messages
            # cannot prove failure of a subsequent clean; its postcondition does.
            if proc.returncode:
                raise MediaOperationError('STORAGE_COMMAND',
                    f'DiskPart exited with code {proc.returncode}: {out}')
            return out
        finally:
            if path is not None:
                path.unlink(missing_ok=True)


def enumerate_usb_disks():
    return ps_json(r'''$ErrorActionPreference='Stop'
$items=Get-Disk|Where-Object{$_.Size -gt 0 -and -not $_.IsBoot -and -not $_.IsSystem -and ($_.BusType -in @('USB','SD','MMC'))}|ForEach-Object{
    [PSCustomObject]@{
        Number=[int]$_.Number
        FriendlyName=[string]$_.FriendlyName
        SerialNumber=[string]$_.SerialNumber
        UniqueId=[string]$_.UniqueId
        BusType=[string]$_.BusType
        Size=[Int64]$_.Size
        LargestFreeExtent=[Int64]$_.LargestFreeExtent
        LogicalSectorSize=[int]$_.LogicalSectorSize
        PhysicalSectorSize=[int]$_.PhysicalSectorSize
        PartitionStyle=[string]$_.PartitionStyle
        NumberOfPartitions=[int]$_.NumberOfPartitions
        IsBoot=[bool]$_.IsBoot
        IsSystem=[bool]$_.IsSystem
        IsOffline=[bool]$_.IsOffline
        IsReadOnly=[bool]$_.IsReadOnly
        OperationalStatus=[string]($_.OperationalStatus -join ', ')
        HealthStatus=[string]$_.HealthStatus
    }
}
@($items)|ConvertTo-Json -Compress''')


def get_disk(number):
    vals = ps_json(rf'''$ErrorActionPreference='Stop'
$d=Get-Disk -Number {int(number)}
[PSCustomObject]@{{
    Number=[int]$d.Number
    FriendlyName=[string]$d.FriendlyName
    SerialNumber=[string]$d.SerialNumber
    UniqueId=[string]$d.UniqueId
    BusType=[string]$d.BusType
    Size=[Int64]$d.Size
    LargestFreeExtent=[Int64]$d.LargestFreeExtent
    LogicalSectorSize=[int]$d.LogicalSectorSize
    PhysicalSectorSize=[int]$d.PhysicalSectorSize
    PartitionStyle=[string]$d.PartitionStyle
    NumberOfPartitions=[int]$d.NumberOfPartitions
    IsBoot=[bool]$d.IsBoot
    IsSystem=[bool]$d.IsSystem
    IsOffline=[bool]$d.IsOffline
    IsReadOnly=[bool]$d.IsReadOnly
    OperationalStatus=[string]($d.OperationalStatus -join ', ')
    HealthStatus=[string]$d.HealthStatus
}}|ConvertTo-Json -Compress''')
    if not vals:
        raise RuntimeError("Selected disk no longer exists.")
    return vals[0]


def safe_removable_disk(number, expected=None):
    d = get_disk(int(number))
    if d.get("IsBoot") or d.get("IsSystem"):
        raise RuntimeError("Refusing Windows boot/system disk.")
    if str(d.get("BusType") or "").upper() not in {"USB", "SD", "MMC"}:
        raise RuntimeError("Refusing non-removable target. Internal SATA/NVMe disks are not exposed.")
    if int(d.get("Number", -1)) != int(number) or int(d.get("Size") or 0) <= 0:
        raise RuntimeError("Invalid or changed device geometry.")
    if expected:
        if not any(str(expected.get(k) or "").strip() for k in ("UniqueId", "SerialNumber")):
            raise RuntimeError("Saved target has no stable identity; destructive/identity-bound operation refused.")
        if int(d["Size"]) != int(expected.get("Size", -1)):
            raise RuntimeError("Target media size changed. Refresh and reselect the USB.")
        for key in ("SerialNumber", "UniqueId"):
            old = str(expected.get(key) or "").strip().casefold()
            new = str(d.get(key) or "").strip().casefold()
            if old and new != old:
                raise RuntimeError(f"Target {key} changed or disappeared. Refusing this device.")
        if str(d.get("BusType") or "").upper() != str(expected.get("BusType") or "").upper():
            raise RuntimeError("Target bus changed. Refresh and reselect the USB.")
    return d


def _media_identity_strength(expected, candidate):
    if not expected or not candidate:
        return 0
    if int(expected.get("Size") or -1) != int(candidate.get("Size") or -2):
        return 0
    if candidate.get("IsBoot") or candidate.get("IsSystem"):
        return 0
    if str(candidate.get("BusType") or "").upper() not in {"USB", "SD", "MMC"}:
        return 0
    score=1
    for key,weight in (("UniqueId",8),("SerialNumber",6)):
        old=str(expected.get(key) or "").strip().casefold();new=str(candidate.get(key) or "").strip().casefold()
        if old:
            if new!=old:return 0
            score+=weight
    if str(expected.get("BusType") or "").upper()!=str(candidate.get("BusType") or "").upper():
        return 0
    return score


def resolve_target_disk(expected, preferred_number=None):
    if preferred_number is not None:
        try:
            current=safe_removable_disk(int(preferred_number),expected)
            return current
        except Exception:
            pass
    matches=[d for d in enumerate_usb_disks() if _media_identity_strength(expected,d)>=7]
    if len(matches)!=1:
        raise RuntimeError("Original removable media is unavailable or ambiguously identified; no automatic target chosen.")
    return safe_removable_disk(int(matches[0]["Number"]),expected)


def wait_for_target_media(expected, preferred_number=None, timeout=12.0, log=None):
    deadline = time.time() + max(1.0, float(timeout))
    last = None
    while time.time() < deadline:
        try:
            d = resolve_target_disk(expected, preferred_number)
            if log:
                log(f"MEDIA RE-ACQUIRE: target confirmed as PhysicalDrive{int(d['Number'])} / {d.get('FriendlyName') or 'removable media'}.")
            return d
        except Exception as e:
            last = e
            refresh_storage_cache()
            time.sleep(0.35)
    raise RuntimeError(f"Timed out waiting for the selected removable media to reappear safely: {last}")


def is_recoverable_media_error(exc):
    text=str(exc).lower()
    return bool(re.search(r"\bwindows error (2|5|21|1117)\b",text) or any(x in text for x in (
        "device is not ready", "selected disk no longer exists", "access is denied", "i/o device error")))


def get_letters(number):
    try:
        vals = ps_json(rf'''$ErrorActionPreference='SilentlyContinue'
@(Get-Partition -DiskNumber {int(number)}|Where-Object{{$_.DriveLetter}}|ForEach-Object{{[string]$_.DriveLetter}})|ConvertTo-Json -Compress''')
    except Exception:
        return []
    return [str(x).strip().upper() for x in vals if len(str(x).strip()) == 1]


def get_volume_access_paths(number):
    try:
        vals = ps_json(rf'''$ErrorActionPreference='SilentlyContinue'
@((Get-Partition -DiskNumber {int(number)} | ForEach-Object {{ $_.AccessPaths }} | Where-Object {{ $_ }} | Sort-Object -Unique)) | ConvertTo-Json -Compress''')
    except Exception:
        return []
    out = []
    for x in vals:
        s = str(x or "").strip()
        if s and s not in out:
            out.append(s)
    return out


def volume_device_path(access_path):
    p = str(access_path or "").strip()
    if re.match(r"^[A-Za-z]:\\?$", p):
        return rf"\\.\{p[0].upper()}:"
    if p.startswith(r"\\?\Volume{"):
        return p.rstrip("\\")
    return None


def dismount_target_volumes(number, log=None):
    """Best-effort lock+dismount every mounted volume belonging to the target disk, including GUID-only EFI volumes."""
    paths = get_volume_access_paths(number)
    for access_path in paths:
        dev = volume_device_path(access_path)
        if not dev:
            continue
        h = None
        try:
            h = open_handle(dev, GENERIC_READ | GENERIC_WRITE, FILE_SHARE_READ | FILE_SHARE_WRITE)
            locked = False
            for _ in range(16):
                if ioctl(h.h, FSCTL_LOCK_VOLUME):
                    locked = True
                    break
                time.sleep(0.12)
            # Dismount even when the lock could not be acquired; Clean-Disk/DiskPart
            # will immediately remove the partition map afterward.
            dismounted = ioctl(h.h, FSCTL_DISMOUNT_VOLUME)
            if log:
                log(f"VOLUME: {access_path} — lock={'yes' if locked else 'no'} dismount={'yes' if dismounted else 'no'}")
        except Exception as e:
            if log:
                log(f"VOLUME WARNING: could not pre-dismount {access_path}: {e}")
        finally:
            if h:
                try:
                    if h.valid():
                        ioctl(h.h, FSCTL_UNLOCK_VOLUME)
                except Exception:
                    pass
                h.close()


def make_disk_writable(number):
    number = int(number)
    expected = safe_removable_disk(number)
    if not expected.get('IsOffline') and not expected.get('IsReadOnly'):
        return expected
    try:
        run_ps(ps_target_guard(number, expected) + f"\nif($d.IsOffline){{Set-Disk -Number {number} -IsOffline $false}}\nif($d.IsReadOnly){{Set-Disk -Number {number} -IsReadOnly $false}}")
    except Exception as exc:
        log_file('ATTRIBUTE NORMALIZATION: ' + str(exc))
        safe_removable_disk(number, expected)
        run_diskpart([f'select disk {number}', 'attributes disk clear readonly noerr', 'online disk noerr'],
                     preflight=lambda: safe_removable_disk(number, expected))
    d = safe_removable_disk(number, expected)
    if d.get('IsReadOnly'):
        raise MediaOperationError('WRITE_PROTECTED',
            'Target remains read-only after attribute clearing. Check a physical lock switch or controller write protection.')
    if d.get('IsOffline'):
        raise MediaOperationError('MEDIA_IO', 'Target remains offline after online normalization.')
    return d


def set_disk_offline(number, offline=True):
    try:
        run_ps(rf'''$ErrorActionPreference='Stop'
Set-Disk -Number {int(number)} -IsOffline ${str(bool(offline)).lower()}
Update-HostStorageCache''')
        return True
    except Exception:
        try:
            run_diskpart([
                f"select disk {int(number)}",
                "offline disk noerr" if offline else "online disk noerr",
            ], timeout=90)
            return True
        except Exception:
            return False


def set_disk_offline_strict(number, offline=True, log=None):
    requested = bool(offline)
    ok = set_disk_offline(number, requested)
    for _ in range(20):
        try:
            d = get_disk(int(number))
            if bool(d.get("IsOffline")) == requested:
                if log:
                    log(f"DISK STATE: {'offline/exclusive raw mode' if requested else 'online'} confirmed.")
                return True
        except Exception:
            pass
        time.sleep(0.15)
    if log:
        log(f"DISK STATE WARNING: Windows did not confirm IsOffline={requested}; operation will fail closed.")
    raise RuntimeError(f"Windows did not confirm the requested disk state IsOffline={requested}; operation not certified.")


def refresh_storage_cache():
    try:
        run_ps("$ErrorActionPreference='SilentlyContinue'; Update-HostStorageCache", timeout=60)
    except Exception:
        pass


def ensure_disk_online_writable(number, log=None):
    d = make_disk_writable(number)
    if log:
        log('DISK STATE: online and writable confirmed.')
    return d


def get_automount_disabled():
    vals = ps_json(r"""$ErrorActionPreference='SilentlyContinue'
$v=(Get-ItemProperty -Path 'HKLM:\SYSTEM\CurrentControlSet\Services\mountmgr' -Name 'NoAutoMount' -ErrorAction SilentlyContinue).NoAutoMount
[PSCustomObject]@{Disabled=[bool]([int]($v -as [int]) -eq 1)}|ConvertTo-Json -Compress""", timeout=60)
    return bool(vals and vals[0].get('Disabled'))


def set_automount_disabled(disabled=True, log=None):
    disabled = bool(disabled)
    cmd = ['/N'] if disabled else ['/E']
    p = subprocess.run(['mountvol.exe', *cmd], capture_output=True, text=True, encoding='utf-8', errors='replace', timeout=60, creationflags=CREATE_NO_WINDOW)
    if p.returncode:
        raise RuntimeError((p.stderr or p.stdout or 'mountvol failed').strip())
    refresh_storage_cache()
    if log:
        log('AUTOMOUNT: ' + ('disabled to shield raw access from mount-manager claims.' if disabled else 'restored to the normal Windows state.'))
    return True


def refresh_target_layout(number, expected):
    """Invalidate the kernel partition view AND refresh the Storage provider."""
    safe_removable_disk(number, expected)
    update_disk_properties(number)
    run_ps(f"$ErrorActionPreference='Stop'; Update-Disk -Number {int(number)}; Update-HostStorageCache", timeout=30)


def wait_for_no_partitions(number, timeout=12.0, expected=None, checkpoint=None, log=None):
    # Never infer an empty map from missing/null NumberOfPartitions.
    expected = expected or safe_removable_disk(number)
    deadline = time.monotonic() + max(0.0, float(timeout))
    last = None
    last_error = None
    while True:
        if checkpoint:
            checkpoint()
        safe_removable_disk(number, expected)
        try:
            refresh_target_layout(number, expected)
            last_error = None
        except Exception as exc:
            last_error = str(exc)
        last = safe_removable_disk(number, expected)
        count = last.get('NumberOfPartitions')
        if count is not None and int(count) == 0 and last_error is None:
            # Query on the disk object: an empty association is valid; provider
            # errors are terminating and must not be converted to an empty list.
            rows = ps_json(f"$ErrorActionPreference='Stop'; "
                           f"@(Get-CimInstance -Namespace root/Microsoft/Windows/Storage -ClassName MSFT_Partition -Filter 'DiskNumber = {int(number)}' -ErrorAction Stop | Select-Object PartitionNumber) | ConvertTo-Json -Compress", timeout=30)
            if not rows:
                if last.get('IsReadOnly'):
                    raise MediaOperationError('WRITE_PROTECTED', 'Target remains read-only after reclaim.')
                return last
        if time.monotonic() >= deadline:
            detail = (f"Disk {number}: map={last.get('PartitionStyle')}, "
                      f"partitions={count}, online={not bool(last.get('IsOffline'))}.")
            if last_error:
                detail += ' Layout refresh: ' + last_error
            raise MediaOperationError('RECLAIM_INCOMPLETE',
                'Windows still reports target partitions after reclaim, or an empty layout could not be verified. ' + detail)
        time.sleep(0.35)


def native_delete_layout(number, expected, log=None):
    """Last bounded fallback; hold every discoverable volume lock throughout.

    No direct sector overwrite is permitted while old partitions remain.
    Un-lockable or unenumerated partitions cause a refusal, not a lock bypass.
    """
    d = safe_removable_disk(number, expected)
    guard_runtime_outside_target(number)
    handles = lock_target_volumes(number)
    try:
        safe_removable_disk(number, expected)
        device = rf'\\.\PhysicalDrive{int(number)}'
        with open_handle(device, GENERIC_READ | GENERIC_WRITE,
                         FILE_SHARE_READ | FILE_SHARE_WRITE,
                         FILE_ATTRIBUTE_NORMAL | FILE_FLAG_WRITE_THROUGH) as h:
            _assert_open_disk_geometry(h.h, number, int(d['Size']))
            if not ioctl(h.h, IOCTL_DISK_DELETE_DRIVE_LAYOUT):
                raise win_error('Native partition-layout removal failed')
            if not kernel32.FlushFileBuffers(h.h):
                raise win_error('Native partition-layout flush failed')
        if log:
            log('RECLAIM: native layout removal completed; verifying the partition map.')
    finally:
        unlock_volumes(handles)


def force_clean_disk(number, expected=None, log=None, checkpoint=None):
    """Destructive; called only within an explicitly confirmed erase operation.

    A successful command is NOT successful reclaim. Each backend must pass the
    empty-layout check. Silent/no-op successes proceed to the next backend too.
    """
    number = int(number)
    guard_runtime_outside_target(number)
    expected = dict(expected or safe_removable_disk(number))
    errors = []
    for backend in ('Storage Clear-Disk', 'DiskPart CLEAN', 'Native layout removal'):
        if checkpoint:
            checkpoint()
        safe_removable_disk(number, expected)
        make_disk_writable(number)
        safe_removable_disk(number, expected)
        if log:
            log(f'RECLAIM: attempting {backend}; target identity confirmed.')
        try:
            if backend == 'Storage Clear-Disk':
                run_ps(ps_target_guard(number, expected) + f"\nClear-Disk -Number {number} -RemoveData -RemoveOEM -Confirm:$false -ErrorAction Stop", timeout=180)
            elif backend == 'DiskPart CLEAN':
                dismount_target_volumes(number, log=log)
                run_diskpart([f'select disk {number}', 'clean'], timeout=180,
                             preflight=lambda: safe_removable_disk(number, expected))
            else:
                native_delete_layout(number, expected, log=log)
        except InterruptedError:
            raise
        except Exception as exc:
            errors.append(f'{backend}: {exc}')
            if log:
                log(f'RECLAIM BACKEND NOTE: {backend}: {exc}')
        # A command may complete its mutation but fail during its own refresh.
        # Verify the state even in that case; never needlessly erase twice.
        try:
            d = wait_for_no_partitions(number, timeout=8.0, expected=expected,
                                       checkpoint=checkpoint, log=log)
            if log:
                log(f'RECLAIM PASS: zero partitions confirmed after {backend}.')
            return d
        except MediaOperationError as exc:
            if exc.code != 'RECLAIM_INCOMPLETE':
                raise
            errors.append(f'{backend} verification: {exc}')
            if log:
                log(f'RECLAIM: {backend} did not produce a verified empty map.')
    raise MediaOperationError('RECLAIM_INCOMPLETE',
        'All three cleanup paths finished without a verified empty partition map. '
        'No image write was started. Export the log; close programs using the USB, '
        'reconnect it and reselect it.\n\n' + '\n\n'.join(errors))


def ps_target_guard(number, expected):
    """Recheck immutable selection facts inside destructive PowerShell scripts."""
    def quote(value):
        return "'" + str(value).replace("'", "''") + "'"
    lines = ["$ErrorActionPreference='Stop'", f'$d=Get-Disk -Number {int(number)}',
             "if($d.IsBoot -or $d.IsSystem){throw 'Refusing Boot/System disk'}",
             "if($d.BusType -notin @('USB','SD','MMC')){throw 'Refusing non-removable target'}",
             f"if([Int64]$d.Size -ne {int(expected['Size'])}){{throw 'Target capacity changed'}}"]
    for key in ('SerialNumber', 'UniqueId', 'BusType'):
        if str(expected.get(key) or '').strip():
            lines.append(f"if(([string]$d.{key}).Trim() -ine {quote(str(expected[key]).strip())}){{throw 'Target {key} changed'}}")
    return '\n'.join(lines)


def restore_disk_windows(number, label="NEXUS_USB", scheme="GPT", filesystem="exFAT", full=False, expected=None, log=None):
    number = int(number)
    guard_runtime_outside_target(number)
    d = safe_removable_disk(number, expected)
    label = sanitize_label(label)
    scheme = "MBR" if str(scheme).upper().startswith("MBR") else "GPT"
    filesystem = str(filesystem).upper()
    fs_ps = {"EXFAT": "exFAT", "NTFS": "NTFS", "FAT32": "FAT32"}.get(filesystem)
    if not fs_ps:
        raise RuntimeError("Unsupported filesystem selection.")
    if fs_ps == "FAT32" and int(d["Size"]) > 32 * 1024**3:
        raise RuntimeError(
            "Windows' built-in FAT32 formatter is limited to 32 GB. Use exFAT for a full-size factory reset, "
            "or flash an OS image that contains its own FAT32 EFI partition."
        )

    expected = dict(expected or d)
    dismount_target_volumes(number, log=log)
    force_clean_disk(number, expected, log=log)
    # Keep the disk online during the signature wipe. For some removable-media
    # controllers, forcing the disk offline causes raw I/O to fail with
    # ERROR_NOT_READY even though the physical drive handle opens successfully.
    wipe_disk_edges(number, int(d["Size"]), int(d.get("LogicalSectorSize") or 512), expected=expected)
    refresh_storage_cache()
    full_arg = " -Full" if full else ""
    out = ps_json(ps_target_guard(number, expected) + rf'''
$d=Get-Disk -Number {number}
if($d.IsBoot -or $d.IsSystem){{throw 'Refusing Boot/System disk'}}
if($d.BusType -notin @('USB','SD','MMC')){{throw 'Refusing non-removable target'}}
if($d.IsOffline){{Set-Disk -Number {number} -IsOffline $false}}
if($d.IsReadOnly){{Set-Disk -Number {number} -IsReadOnly $false}}
Initialize-Disk -Number {number} -PartitionStyle {scheme}
$p=New-Partition -DiskNumber {number} -UseMaximumSize -AssignDriveLetter
$v=Format-Volume -Partition $p -FileSystem {fs_ps} -NewFileSystemLabel '{label.replace("'", "''")}' -Confirm:$false -Force{full_arg}
Update-HostStorageCache
[PSCustomObject]@{{DriveLetter=[string]$v.DriveLetter;FileSystem=[string]$v.FileSystem;Label=[string]$v.FileSystemLabel;Size=[Int64]$v.Size}}|ConvertTo-Json -Compress''', timeout=7200 if full else 300)
    if not out or str(out[0].get("FileSystem", "")).casefold() != fs_ps.casefold() or int(out[0].get("Size") or 0) <= 0:
        raise MediaOperationError("FORMAT_FAILURE", "Windows did not return a verified formatted volume. Inspect Disk Manager before retrying.")
    safe_removable_disk(number, expected)
    return out[0]


def enumerate_partitions(number):
    number = int(number)
    return ps_json(rf'''$ErrorActionPreference='Stop'
$items = @(Get-Partition -DiskNumber {number} -ErrorAction SilentlyContinue | ForEach-Object {{
    $p = $_
    $v = $null
    try {{ $v = Get-Volume -Partition $p -ErrorAction Stop }} catch {{}}
    [PSCustomObject]@{{
        PartitionNumber=[int]$p.PartitionNumber
        DriveLetter=[string]$p.DriveLetter
        Type=[string]$p.Type
        GptType=[string]$p.GptType
        MbrType=[int]$p.MbrType
        Size=[Int64]$p.Size
        Offset=[Int64]$p.Offset
        IsActive=[bool]$p.IsActive
        IsHidden=[bool]$p.IsHidden
        IsReadOnly=[bool]$p.IsReadOnly
        AccessPaths=[string]($p.AccessPaths -join ';')
        FileSystem=[string]$(if($v){{$v.FileSystem}}else{{''}})
        FileSystemLabel=[string]$(if($v){{$v.FileSystemLabel}}else{{''}})
        HealthStatus=[string]$(if($v){{$v.HealthStatus}}else{{''}})
    }}
}})
@($items)|ConvertTo-Json -Compress''')


def partition_is_protected(part):
    if not part:
        return True
    gpt = str(part.get("GptType") or "").strip().lower().strip("{}")
    typ = str(part.get("Type") or "").lower()
    if gpt == str(ESP_GUID).lower():
        return True
    protected_guids = {
        "e3c9e316-0b5c-4db8-817d-f92df00215ae",
        "de94bba4-06d1-4d40-a16a-bfd50179d6ac",
    }
    if gpt in protected_guids:
        return True
    return any(word in typ for word in ("system", "reserved", "recovery"))


def relocate_gpt_backup_to_disk_end(number, disk_size, sector_size=512, log=None):
    """Relocate a small image's GPT backup structures to the physical end of a larger USB.

    This runs only after image verification. It preserves all partition entries, expands
    the GPT usable-LBA ceiling, writes a valid backup table/header at the true media end,
    updates the protective MBR span, and clears the obsolete backup metadata location.
    """
    number = int(number)
    guard_runtime_outside_target(number)
    disk_size = int(disk_size)
    sector = max(512, int(sector_size or 512))
    if disk_size < sector * 100:
        return {"changed": False, "reason": "disk too small"}
    actual = safe_removable_disk(number)
    if int(actual["Size"]) != disk_size:
        raise RuntimeError("GPT relocation target capacity changed.")
    with open_physical_retry(number, GENERIC_READ | GENERIC_WRITE, exclusive=True) as h:
        allow_extended_dasd_io(h.h)
        _assert_open_disk_geometry(h.h, number, disk_size)
        raw_seek(h.h, sector)
        hdr = raw_read_exact(h.h, sector)
        if len(hdr) < 92 or hdr[:8] != b"EFI PART":
            return {"changed": False, "reason": "not GPT"}
        _gpt_snapshot(RawHandleReader(h.h, disk_size), sector)
        hsize = struct.unpack_from("<I", hdr, 12)[0]
        if hsize < 92 or hsize > sector:
            raise RuntimeError("Invalid GPT header size while expanding media.")
        old_backup = struct.unpack_from("<Q", hdr, 32)[0]
        entries_lba = struct.unpack_from("<Q", hdr, 72)[0]
        count = struct.unpack_from("<I", hdr, 80)[0]
        esize = struct.unpack_from("<I", hdr, 84)[0]
        if count <= 0 or count > 4096 or esize < 128:
            raise RuntimeError("Invalid GPT entry geometry while expanding media.")
        entries_bytes = count * esize
        entries_span = align_up(entries_bytes, sector)
        entries_sectors = entries_span // sector
        raw_seek(h.h, entries_lba * sector)
        entries_padded = raw_read_exact(h.h, entries_span)
        if len(entries_padded) < entries_span:
            raise RuntimeError("GPT partition entry array could not be read during expansion.")
        entries = entries_padded[:entries_bytes]
        entry_crc = crc32(entries)
        last_lba = disk_size // sector - 1
        backup_entries_lba = last_lba - entries_sectors
        new_last_usable = backup_entries_lba - 1
        max_partition_lba = 0
        for i in range(count):
            e = entries[i*esize:(i+1)*esize]
            if len(e) < 48 or e[:16] == b"\x00" * 16:
                continue
            last = struct.unpack_from("<Q", e, 40)[0]
            max_partition_lba = max(max_partition_lba, int(last))
        if max_partition_lba > new_last_usable:
            raise RuntimeError("Existing partitions leave no safe room for a relocated GPT backup table.")
        if old_backup == last_lba:
            return {"changed": False, "reason": "GPT already spans physical media", "last_usable": new_last_usable}

        primary = bytearray(hdr)
        struct.pack_into("<Q", primary, 32, last_lba)
        struct.pack_into("<Q", primary, 48, new_last_usable)
        struct.pack_into("<I", primary, 88, entry_crc)
        struct.pack_into("<I", primary, 16, 0)
        struct.pack_into("<I", primary, 16, crc32(primary[:hsize]))

        backup = bytearray(primary)
        struct.pack_into("<Q", backup, 24, last_lba)
        struct.pack_into("<Q", backup, 32, 1)
        struct.pack_into("<Q", backup, 72, backup_entries_lba)
        struct.pack_into("<I", backup, 16, 0)
        struct.pack_into("<I", backup, 16, crc32(backup[:hsize]))

        # Update protective MBR length when one exists.
        raw_seek(h.h, 0)
        mbr = bytearray(raw_read_exact(h.h, sector))
        if len(mbr) >= 512 and mbr[510:512] == b"\x55\xAA":
            for i in range(4):
                off = 446 + i * 16
                if mbr[off + 4] == 0xEE:
                    struct.pack_into("<I", mbr, off + 12, min(last_lba, 0xFFFFFFFF))
                    break
            raw_seek(h.h, 0)
            raw_write(h.h, bytes(mbr))

        raw_seek(h.h, backup_entries_lba * sector)
        raw_write(h.h, entries + b"\x00" * (entries_span - entries_bytes))
        raw_seek(h.h, last_lba * sector)
        raw_write(h.h, bytes(backup))
        if not kernel32.FlushFileBuffers(h.h):
            raise win_error("GPT backup expansion flush failed")
        _gpt_header(RawHandleReader(h.h, disk_size), last_lba, sector)
        raw_seek(h.h, sector)
        raw_write(h.h, bytes(primary))
        if not kernel32.FlushFileBuffers(h.h):
            raise win_error("GPT primary expansion flush failed")
        _gpt_snapshot(RawHandleReader(h.h, disk_size), sector)
        # The obsolete backup lies beyond the previous usable range. Leave it
        # inert; the new authoritative primary/backup pair now points elsewhere.
    if log:
        log(f"GPT EXPANSION PASS: backup GPT relocated from LBA {old_backup} to {last_lba}; last usable LBA is now {new_last_usable}.")
    return {"changed": True, "old_backup_lba": old_backup, "new_backup_lba": last_lba, "last_usable": new_last_usable}


def provision_remainder_partition(number, filesystem="exFAT", label="NEXUS_DATA", min_free=64 * 1024 * 1024):
    number = int(number)
    guard_runtime_outside_target(number)
    safe_removable_disk(number)
    filesystem = str(filesystem or "exFAT").upper()
    fs_ps = {"EXFAT": "exFAT", "NTFS": "NTFS", "FAT32": "FAT32"}.get(filesystem)
    if not fs_ps:
        raise RuntimeError("Unsupported data-partition filesystem.")
    label = sanitize_label(label or "NEXUS_DATA")
    set_disk_offline_strict(number, False)
    make_disk_writable(number)
    refresh_storage_cache()
    time.sleep(0.35)
    d = get_disk(number)
    free = int(d.get("LargestFreeExtent") or 0)
    if free < int(min_free):
        return {"created": False, "reason": "No substantial unallocated space remains.", "free": free}
    if fs_ps == "FAT32" and free > 32 * 1024**3:
        fs_ps = "exFAT"
    safe_label = label.replace("'", "''")
    vals = ps_json(rf'''$ErrorActionPreference='Stop'
$d=Get-Disk -Number {number}
if($d.IsBoot -or $d.IsSystem){{throw 'Refusing Boot/System disk'}}
if($d.BusType -notin @('USB','SD','MMC')){{throw 'Refusing non-removable target'}}
if($d.IsOffline){{Set-Disk -Number {number} -IsOffline $false}}
if($d.IsReadOnly){{Set-Disk -Number {number} -IsReadOnly $false}}
Update-HostStorageCache
$d=Get-Disk -Number {number}
if([Int64]$d.LargestFreeExtent -lt {int(min_free)}){{
  [PSCustomObject]@{{Created=$false;Reason='No substantial unallocated space remains.';Free=[Int64]$d.LargestFreeExtent}} | ConvertTo-Json -Compress
  exit 0
}}
$p=New-Partition -DiskNumber {number} -UseMaximumSize -AssignDriveLetter
$v=Format-Volume -Partition $p -FileSystem {fs_ps} -NewFileSystemLabel '{safe_label}' -Confirm:$false -Force
Update-HostStorageCache
[PSCustomObject]@{{Created=$true;PartitionNumber=[int]$p.PartitionNumber;DriveLetter=[string]$v.DriveLetter;FileSystem=[string]$v.FileSystem;Label=[string]$v.FileSystemLabel;Size=[Int64]$p.Size}} | ConvertTo-Json -Compress''', timeout=600)
    if not vals:
        raise RuntimeError("Windows did not return a result while provisioning the remainder partition.")
    result = vals[0]
    result["created"] = bool(result.get("Created"))
    return result


def format_partition(number, partition_number, filesystem="exFAT", label="NEXUS_DATA", full=False):
    number, partition_number = int(number), int(partition_number)
    safe_removable_disk(number)
    parts = enumerate_partitions(number)
    part = next((p for p in parts if int(p.get("PartitionNumber", -1)) == partition_number), None)
    if not part:
        raise RuntimeError("Partition no longer exists.")
    if partition_is_protected(part):
        raise RuntimeError("Protected EFI/System/Recovery partitions cannot be formatted from Disk Manager.")
    filesystem = str(filesystem or "exFAT").upper()
    fs_ps = {"EXFAT": "exFAT", "NTFS": "NTFS", "FAT32": "FAT32"}.get(filesystem)
    if not fs_ps:
        raise RuntimeError("Unsupported filesystem.")
    if fs_ps == "FAT32" and int(part.get("Size") or 0) > 32 * 1024**3:
        raise RuntimeError("Windows FAT32 formatting is limited to 32 GB. Choose exFAT or NTFS.")
    label = sanitize_label(label)
    safe_label = label.replace("'", "''")
    full_arg = " -Full" if full else ""
    run_ps(rf'''$ErrorActionPreference='Stop'
$d=Get-Disk -Number {number}
if($d.IsOffline){{Set-Disk -Number {number} -IsOffline $false}}
if($d.IsReadOnly){{Set-Disk -Number {number} -IsReadOnly $false}}
$p=Get-Partition -DiskNumber {number} -PartitionNumber {partition_number}
Format-Volume -Partition $p -FileSystem {fs_ps} -NewFileSystemLabel '{safe_label}' -Force -Confirm:$false{full_arg} | Out-Null
Update-HostStorageCache''', timeout=7200 if full else 600)
    return True


def delete_partition(number, partition_number):
    number, partition_number = int(number), int(partition_number)
    safe_removable_disk(number)
    parts = enumerate_partitions(number)
    part = next((p for p in parts if int(p.get("PartitionNumber", -1)) == partition_number), None)
    if not part:
        raise RuntimeError("Partition no longer exists.")
    if partition_is_protected(part):
        raise RuntimeError("Protected EFI/System/Recovery partitions cannot be deleted from Disk Manager. Use Factory Reset / Reclaim when you intentionally want to erase the whole removable disk.")
    run_ps(rf'''$ErrorActionPreference='Stop'
Remove-Partition -DiskNumber {number} -PartitionNumber {partition_number} -Confirm:$false
Update-HostStorageCache''')
    return True


def assign_partition_letter(number, partition_number):
    number, partition_number = int(number), int(partition_number)
    safe_removable_disk(number)
    vals = ps_json(rf'''$ErrorActionPreference='Stop'
$p=Get-Partition -DiskNumber {number} -PartitionNumber {partition_number}
if(-not $p.DriveLetter){{ Add-PartitionAccessPath -DiskNumber {number} -PartitionNumber {partition_number} -AssignDriveLetter }}
$p=Get-Partition -DiskNumber {number} -PartitionNumber {partition_number}
[PSCustomObject]@{{DriveLetter=[string]$p.DriveLetter}} | ConvertTo-Json -Compress''')
    return str(vals[0].get("DriveLetter") or "") if vals else ""


def remove_partition_letter(number, partition_number):
    number, partition_number = int(number), int(partition_number)
    safe_removable_disk(number)
    run_ps(rf'''$ErrorActionPreference='Stop'
$p=Get-Partition -DiskNumber {number} -PartitionNumber {partition_number}
if($p.DriveLetter){{ Remove-PartitionAccessPath -DiskNumber {number} -PartitionNumber {partition_number} -AccessPath ($p.DriveLetter + ':\') }}
Update-HostStorageCache''')
    return True


def extend_partition_to_max(number, partition_number):
    number, partition_number = int(number), int(partition_number)
    safe_removable_disk(number)
    parts = enumerate_partitions(number)
    part = next((p for p in parts if int(p.get("PartitionNumber", -1)) == partition_number), None)
    if not part or partition_is_protected(part):
        raise RuntimeError("Only normal data partitions can be extended from Disk Manager.")
    vals = ps_json(rf'''$ErrorActionPreference='Stop'
$s=Get-PartitionSupportedSize -DiskNumber {number} -PartitionNumber {partition_number}
$p=Get-Partition -DiskNumber {number} -PartitionNumber {partition_number}
if([Int64]$s.SizeMax -gt [Int64]$p.Size){{ Resize-Partition -DiskNumber {number} -PartitionNumber {partition_number} -Size $s.SizeMax }}
$p=Get-Partition -DiskNumber {number} -PartitionNumber {partition_number}
[PSCustomObject]@{{Size=[Int64]$p.Size}} | ConvertTo-Json -Compress''')
    return int(vals[0].get("Size") or 0) if vals else 0


def get_disk_pnp_id(number):
    vals = ps_json(rf'''$ErrorActionPreference='SilentlyContinue'
$d=Get-CimInstance Win32_DiskDrive | Where-Object {{ [int]$_.Index -eq {int(number)} }} | Select-Object -First 1
if($d){{[PSCustomObject]@{{PNPDeviceID=[string]$d.PNPDeviceID;Model=[string]$d.Model}}|ConvertTo-Json -Compress}}''')
    return vals[0] if vals else {}


def backup_disk_to_image(number, output_path, checkpoint=None, progress=None):
    number=int(number);d=safe_removable_disk(number);total=int(d["Size"])
    out=Path(output_path).resolve(strict=False)
    guard_runtime_outside_target(number,out)
    if out.exists():raise RuntimeError("Backup output already exists. Choose a new filename; existing images are never overwritten.")
    if not out.parent.is_dir():raise RuntimeError("Backup output directory does not exist.")
    if shutil.disk_usage(out.parent).free<total+1024**2:raise RuntimeError("Insufficient destination capacity for a full raw image.")
    digest=hashlib.sha256();done=0;started=time.time();part=Path(str(out)+".partial")
    if part.exists():raise RuntimeError("A partial backup already uses that name. Choose a different destination filename.")
    # Application reads only. Live Windows volumes can still change underneath the scan.
    # Use a hardware write blocker for evidence-sensitive work; prefer offline evidence images.
    with open_physical_retry(number,GENERIC_READ,retries=1) as h,part.open("xb",buffering=0) as f:
        _assert_open_disk_geometry(h.h,number,total);safe_removable_disk(number,d);raw_seek(h.h,0)
        while done<total:
            _rec_check(checkpoint);want=min(CHUNK,total-done);data=raw_read_exact(h.h,want)
            if len(data)!=want:raise RuntimeError(f"Backup read ended early at {human_size(done)}. Partial image retained.")
            if f.write(data)!=want:raise OSError("Short backup destination write.")
            digest.update(data);done+=want
            if progress:progress(done,total,started)
        f.flush();os.fsync(f.fileno())
    os.replace(part,out)
    result={"path":str(out),"size":total,"sha256":digest.hexdigest(),"source_device":d,
            "consistency":"Live-source consistency is not guaranteed. Application used read-only physical I/O.",
            "hardware_write_blocker_verified":False}
    if not save_json_file(Path(str(out)+".acquisition.json"),result):
        raise OSError("Image saved, but acquisition manifest could not be written.")
    return result


def safe_eject_disk(number, log=None):
    number=int(number);expected=safe_removable_disk(number)
    if log:log("SAFE EJECT: flushing and locking all target volumes; Windows hardware confirmation is required.")
    handles=lock_target_volumes(number)
    try:
        safe_removable_disk(number,expected)
        info=get_disk_pnp_id(number);pnp_id=str(info.get("PNPDeviceID") or "").strip()
    finally:
        # Our own handles must not veto the hardware removal request.
        unlock_volumes(handles)
    if cfgmgr32 and pnp_id:
        devinst=wintypes.DWORD()
        cr=int(cfgmgr32.CM_Locate_DevNodeW(ctypes.byref(devinst),pnp_id,0))
        if cr==0:
            veto=ctypes.c_int(0);veto_name=ctypes.create_unicode_buffer(260)
            cr=int(cfgmgr32.CM_Request_Device_EjectW(devinst.value,ctypes.byref(veto),veto_name,len(veto_name),0))
            if cr==0:
                return {"ejected":True,"safe":True,"message":"Windows confirmed hardware eject. It is safe to remove the device."}
            if log:log(f"Hardware eject refused: CONFIGRET {cr}, veto {veto.value}, {veto_name.value}")
    return {"ejected":False,"safe":False,"message":"Windows did not confirm hardware eject. Do not remove the device yet. Close applications using it and retry, or use Windows Safely Remove Hardware."}


# ---------------------------------------------------------------------------
# Raw Win32 disk I/O
# ---------------------------------------------------------------------------

class Handle:
    def __init__(self, h=None):
        self.h = h

    def valid(self):
        return self.h not in (None, 0, INVALID_HANDLE_VALUE)

    def close(self):
        if self.valid():
            kernel32.CloseHandle(self.h)
        self.h = None

    def __enter__(self):
        return self

    def __exit__(self, *_):
        self.close()


def open_handle(path, access, share, flags=FILE_ATTRIBUTE_NORMAL):
    h = kernel32.CreateFileW(path, access, share, None, OPEN_EXISTING, flags, None)
    if h == INVALID_HANDLE_VALUE:
        raise win_error(f"Could not open {path}")
    return Handle(h)


def open_physical_retry(number, access, retries=16, exclusive=False):
    device = r"\\.\PhysicalDrive{}".format(int(number))
    last = None
    # Prefer an exclusive write handle first, but do not force the removable disk
    # offline here. Some controllers surface ERROR_NOT_READY when taken offline
    # even though the physical drive handle opens. Instead, normalize the disk to
    # online/writable state and fall back to the documented shared mode if needed.
    shares = [0, FILE_SHARE_READ | FILE_SHARE_WRITE] if exclusive else [FILE_SHARE_READ | FILE_SHARE_WRITE]
    flags = FILE_ATTRIBUTE_NORMAL | (FILE_FLAG_WRITE_THROUGH if (access & GENERIC_WRITE) else 0)
    for share in shares:
        attempts = max(3, retries // len(shares))
        for attempt in range(attempts):
            try:
                if access & GENERIC_WRITE:
                    ensure_disk_online_writable(number)
                return open_handle(device, access, share, flags)
            except Exception as e:
                last = e
                if access & GENERIC_WRITE:
                    refresh_storage_cache()
                time.sleep(0.16 + min(0.24, attempt * 0.03))
    raise last or RuntimeError(f"Could not open {device}")


class CertificationHandle(Handle):
    """Own the physical handle and keep volume locks alive through readback."""
    def __init__(self, raw, volumes, mode):
        super().__init__(raw.h)
        raw.h = None
        self.volumes = volumes
        self.mode = mode

    def close(self):
        try:
            super().close()
        finally:
            volumes, self.volumes = self.volumes, []
            unlock_volumes(volumes)


def open_physical_certification_handle(number, retries=24):
    """Try no-share access, then Windows-compatible sharing with volume locks.

    FILE_SHARE flags govern handle compatibility, not filesystem dismounts.
    Retain all volume locks and the same raw handle through write/readback.
    Shared access cannot exclude another administrator's raw-disk writer.
    No storage refresh or online transition is made inside the barrier.
    """
    number = int(number)
    device = rf"\\.\PhysicalDrive{number}"
    flags = FILE_ATTRIBUTE_NORMAL | FILE_FLAG_WRITE_THROUGH
    expected = safe_removable_disk(number)
    ensure_disk_online_writable(number)
    volumes = lock_target_volumes(number)
    last = None
    try:
        for share in (0, FILE_SHARE_READ | FILE_SHARE_WRITE):
            for attempt in range(max(1, min(6, int(retries) // 2))):
                safe_removable_disk(number, expected)
                try:
                    raw = open_handle(device, GENERIC_READ | GENERIC_WRITE, share, flags)
                except Exception as exc:
                    last = exc
                    code = getattr(exc, "winerror", None)
                    if code not in (5, 32, 33):
                        raise
                    log_file(f"RAW OPEN: share={share} attempt={attempt+1}: {exc}")
                    time.sleep(0.15)
                    continue
                try:
                    _assert_open_disk_geometry(raw.h, number, int(expected["Size"]))
                    mode = "exclusive" if share == 0 else "shared-with-volume-locks"
                    log_file(f"RAW ACCESS: {mode}; retained volume locks={len(volumes)}. "
                             "No disk refresh until readback completes.")
                    return CertificationHandle(raw, volumes, mode)
                except BaseException:
                    raw.close()
                    raise
        raise last or RuntimeError("Raw handle acquisition failed without a Windows error.")
    except BaseException:
        unlock_volumes(volumes)
        raise


def ioctl(h, code):
    out = wintypes.DWORD()
    return bool(kernel32.DeviceIoControl(h, code, None, 0, None, 0, ctypes.byref(out), None))


def allow_extended_dasd_io(h):
    try:
        return ioctl(h, FSCTL_ALLOW_EXTENDED_DASD_IO)
    except Exception:
        return False


def update_disk_properties(number):
    try:
        with open_physical_retry(number, GENERIC_READ, retries=8) as h:
            return ioctl(h.h, IOCTL_DISK_UPDATE_PROPERTIES)
    except Exception:
        return False


def lock_volumes(letters):
    # Kept for compatibility and diagnostic use. v2.1 normally removes all
    # partitions before raw flashing, eliminating hidden EFI-volume lock races.
    hs = []
    try:
        for letter in letters:
            h = open_handle(rf"\\.\{letter}:", GENERIC_READ | GENERIC_WRITE, FILE_SHARE_READ | FILE_SHARE_WRITE)
            ok = False
            for _ in range(20):
                if ioctl(h.h, FSCTL_LOCK_VOLUME):
                    ok = True
                    break
                time.sleep(0.25)
            if not ok:
                h.close()
                raise win_error(f"Could not lock {letter}:; close Explorer/programs using USB")
            if not ioctl(h.h, FSCTL_DISMOUNT_VOLUME):
                h.close()
                raise win_error(f"Could not dismount {letter}:")
            hs.append(h)
        return hs
    except Exception:
        unlock_volumes(hs)
        raise


def unlock_volumes(hs):
    for h in hs:
        try:
            if h.valid():
                ioctl(h.h, FSCTL_UNLOCK_VOLUME)
        except Exception:
            pass
        h.close()


def raw_seek(h, offset):
    newpos = ctypes.c_longlong()
    if not kernel32.SetFilePointerEx(h, ctypes.c_longlong(int(offset)), ctypes.byref(newpos), 0):
        raise win_error("Could not seek raw disk")


def raw_write(h, data):
    if not data:
        return
    buf = ctypes.create_string_buffer(data)
    done = wintypes.DWORD()
    if not kernel32.WriteFile(h, buf, len(data), ctypes.byref(done), None):
        raise win_error("Raw write failed")
    if done.value != len(data):
        raise RuntimeError(f"Short raw write {done.value}/{len(data)}")


def is_windows_error_not_ready(exc):
    text = str(exc or "")
    lower = text.lower()
    return ("windows error 21" in lower) or ("device is not ready" in lower)


def raw_read(h, n):
    if n <= 0:
        return b""
    buf = ctypes.create_string_buffer(n)
    got = wintypes.DWORD()
    if not kernel32.ReadFile(h, buf, n, ctypes.byref(got), None):
        raise win_error("Raw read failed")
    return bytes(buf.raw[:got.value])


def raw_read_exact(h, n):
    chunks = []
    remaining = int(n)
    while remaining > 0:
        part = raw_read(h, remaining)
        if not part:
            break
        chunks.append(part)
        remaining -= len(part)
    return b"".join(chunks)


def short_hex(data, limit=32):
    if not data:
        return ""
    return " ".join(f"{b:02X}" for b in bytes(data[:limit]))


def verify_image_against_open_handle(image_path, raw_handle, total, sector, checkpoint=None, progress=None):
    """Exact readback against an already-open physical-drive handle.

    v3.2 uses this during the same raw-write transaction, before this application requests Windows storage
    discovery to refresh/normalize GPT metadata on a larger target.
    That removes false strict-verification failures at GPT header bytes such as
    offset 528 (sector 1 + GPT header CRC field) while still failing closed on
    any mismatch actually observed under the certification handle.
    """
    src_hash = hashlib.sha256()
    dst_hash = hashlib.sha256()
    checked = 0
    mismatch = None
    image_path = Path(image_path)
    raw_seek(raw_handle, 0)
    with image_path.open("rb", buffering=0) as src:
        while checked < total:
            if checkpoint:
                checkpoint()
            chunk = src.read(min(CHUNK, total - checked))
            if not chunk:
                raise RuntimeError("Source image ended unexpectedly during verification.")
            want = len(chunk)
            read_n = align_up(want, sector) if (checked + want == total and want % sector) else want
            target = raw_read_exact(raw_handle, read_n)
            if len(target) < read_n:
                raise RuntimeError("Verification read ended early.")
            target = target[:want]
            src_hash.update(chunk)
            dst_hash.update(target)
            if mismatch is None and chunk != target:
                for idx, (sb, tb) in enumerate(zip(chunk, target)):
                    if sb != tb:
                        mismatch = {
                            "offset": checked + idx,
                            "source_sample": chunk[idx:idx+32],
                            "target_sample": target[idx:idx+32],
                        }
                        break
                if mismatch is None and len(chunk) != len(target):
                    mismatch = {
                        "offset": checked + min(len(chunk), len(target)),
                        "source_sample": chunk[min(len(chunk), len(target)):min(len(chunk), len(target))+32],
                        "target_sample": target[min(len(chunk), len(target)):min(len(chunk), len(target))+32],
                    }
            checked += want
            if progress:
                progress(checked, total)
    return {
        "match": mismatch is None,
        "source_hash": src_hash.hexdigest(),
        "target_hash": dst_hash.hexdigest(),
        "mismatch_offset": mismatch["offset"] if mismatch else None,
        "source_sample_hex": short_hex(mismatch["source_sample"]) if mismatch else "",
        "target_sample_hex": short_hex(mismatch["target_sample"]) if mismatch else "",
    }


def verify_image_against_target(image_path, disk_number, total, sector, checkpoint=None, progress=None):
    with open_physical_retry(int(disk_number), GENERIC_READ) as h:
        allow_extended_dasd_io(h.h)
        return verify_image_against_open_handle(
            image_path, h.h, total, sector, checkpoint=checkpoint, progress=progress
        )


def parse_gpt_geometry(reader):
    try:
        g=_gpt_header(reader,1,512)
        return {"header_size":g["header_size"],"current_lba":g["current"],"backup_lba":g["backup"],
                "entries_lba":g["entries_lba"],"count":g["count"],"esize":g["esize"],"entries_bytes":len(g["entries"])}
    except (ValueError,struct.error):
        return None


def merge_ranges(ranges):
    cleaned = []
    for start, end in sorted((max(0, int(a)), max(0, int(b))) for a, b in ranges if b > a):
        if not cleaned or start > cleaned[-1][1]:
            cleaned.append([start, end])
        else:
            cleaned[-1][1] = max(cleaned[-1][1], end)
    return [(a, b) for a, b in cleaned]


def gpt_metadata_ignore_ranges(reader):
    g = parse_gpt_geometry(reader)
    if not g:
        return []
    sector = 512
    entries_span = align_up(g["entries_bytes"], sector)
    primary_header_start = g["current_lba"] * sector
    primary_entries_start = g["entries_lba"] * sector
    backup_header_start = g["backup_lba"] * sector
    backup_entries_start = max(0, backup_header_start - entries_span)
    return merge_ranges([
        (primary_header_start, primary_header_start + sector),
        (primary_entries_start, primary_entries_start + entries_span),
        (backup_entries_start, backup_entries_start + entries_span),
        (backup_header_start, backup_header_start + sector),
    ])



def _partition_byte_ranges_512(reader):
    """Return bounded partition byte ranges for the source image's 512-byte MBR/GPT map."""
    mbr = parse_mbr(reader)
    if not mbr.get("valid"):
        return []
    parts = []
    if mbr.get("protective_gpt"):
        gpt = parse_gpt(reader)
        if not gpt.get("valid"):
            return []
        for p in gpt.get("partitions", []):
            start = int(p["first_lba"]) * 512
            end = (int(p["last_lba"]) + 1) * 512
            if 0 <= start < end <= reader.size:
                parts.append((start, end))
    else:
        for p in mbr.get("partitions", []):
            start = int(p["first_lba"]) * 512
            end = start + int(p["sectors"]) * 512
            if 0 <= start < end <= reader.size:
                parts.append((start, end))
    return parts


def _fat32_fsinfo_signature_valid(data):
    """Validate the fixed FAT32 FSInfo signatures without trusting its advisory counters."""
    return (
        len(data) >= 512
        and data[0:4] == b"RRaA"
        and data[484:488] == b"rrAa"
        and data[508:512] == b"\x00\x00\x55\xAA"
    )


def fat32_fsinfo_host_mutable_state(reader):
    """Locate only FAT32 FSInfo advisory fields Windows may update after media discovery.

    FAT32 BPB_FSInfo identifies a reserved-sector FSInfo structure. Its Free_Count
    (offset 488) and Next_Free (offset 492) values are advisory. Windows may
    recalculate them after the exact raw-write handle is released even though no
    payload file was modified.

    The returned ranges are deliberately limited to 8 bytes per valid FSInfo copy.
    """
    states = []
    for part_start, part_end in _partition_byte_ranges_512(reader):
        bs = reader.read_at(part_start, 512)
        if len(bs) != 512 or bs[510:512] != b"\x55\xAA":
            continue
        try:
            bps = struct.unpack_from("<H", bs, 11)[0]
            spc = int(bs[13])
            reserved = struct.unpack_from("<H", bs, 14)[0]
            fats = int(bs[16])
            root_entries = struct.unpack_from("<H", bs, 17)[0]
            total16 = struct.unpack_from("<H", bs, 19)[0]
            fat16 = struct.unpack_from("<H", bs, 22)[0]
            total32 = struct.unpack_from("<I", bs, 32)[0]
            fat32 = struct.unpack_from("<I", bs, 36)[0]
            fsinfo_sector = struct.unpack_from("<H", bs, 48)[0]
            backup_boot = struct.unpack_from("<H", bs, 50)[0]
        except (struct.error, IndexError):
            continue

        if (
            bps not in (512, 1024, 2048, 4096)
            or spc == 0 or (spc & (spc - 1))
            or reserved == 0 or fats == 0
            or root_entries != 0 or fat16 != 0 or fat32 == 0
        ):
            continue

        total_sectors = int(total16 or total32)
        data_sectors = total_sectors - (reserved + fats * fat32)
        if total_sectors <= 0 or data_sectors <= 0:
            continue
        cluster_count = data_sectors // spc
        if cluster_count <= 0:
            continue

        candidates = []
        if 0 < fsinfo_sector < reserved:
            candidates.append(("primary", fsinfo_sector))
        backup_fsinfo = int(backup_boot) + int(fsinfo_sector)
        if backup_boot and 0 < backup_fsinfo < reserved:
            candidates.append(("backup", backup_fsinfo))

        seen = set()
        for kind, rel_sector in candidates:
            info_off = part_start + rel_sector * bps
            if info_off in seen or info_off + bps > min(part_end, reader.size):
                continue
            seen.add(info_off)
            data = reader.read_at(info_off, bps)
            if not _fat32_fsinfo_signature_valid(data):
                continue
            states.append({
                "kind": kind,
                "partition_start": part_start,
                "fsinfo_offset": info_off,
                "mutable_range": (info_off + 488, info_off + 496),
                "cluster_count": int(cluster_count),
                "source_free_count": int(struct.unpack_from("<I", data, 488)[0]),
                "source_next_free": int(struct.unpack_from("<I", data, 492)[0]),
            })
    return states


def _fat32_fsinfo_target_values_valid(target, states):
    """Require target FSInfo signatures and advisory values to remain structurally sane."""
    for state in states:
        off = int(state["fsinfo_offset"])
        sector = target.read_at(off, 512)
        if not _fat32_fsinfo_signature_valid(sector):
            return False
        free_count = struct.unpack_from("<I", sector, 488)[0]
        next_free = struct.unpack_from("<I", sector, 492)[0]
        clusters = int(state["cluster_count"])
        if free_count != 0xFFFFFFFF and free_count > clusters:
            return False
        if next_free != 0xFFFFFFFF and not (2 <= next_free <= clusters + 1):
            return False
    return True


def _offset_in_ranges(offset, ranges):
    try:
        off = int(offset)
    except (TypeError, ValueError):
        return False
    return any(int(a) <= off < int(b) for a, b in ranges)



def compare_image_target_except_ranges(image_path, disk_number, total, ignore_ranges, checkpoint=None, progress=None):
    src_hash = hashlib.sha256()
    dst_hash = hashlib.sha256()
    checked = 0
    mismatch = None
    ignore_ranges = merge_ranges(ignore_ranges)
    range_index = 0
    image_path = Path(image_path)
    with image_path.open("rb", buffering=0) as src, open_physical_retry(int(disk_number), GENERIC_READ) as h:
        allow_extended_dasd_io(h.h)
        raw_seek(h.h, 0)
        while checked < total:
            if checkpoint:
                checkpoint()
            want = min(CHUNK, total - checked)
            source = src.read(want)
            if not source:
                raise RuntimeError("Source image ended unexpectedly during comparison.")
            target = raw_read_exact(h.h, want)
            if len(target) < want:
                raise RuntimeError("Verification read ended early.")
            cursor = 0
            while cursor < want:
                absolute = checked + cursor
                while range_index < len(ignore_ranges) and ignore_ranges[range_index][1] <= absolute:
                    range_index += 1
                next_stop = want
                if range_index < len(ignore_ranges):
                    r0, r1 = ignore_ranges[range_index]
                    if absolute >= r0:
                        skip = min(want - cursor, r1 - absolute)
                        cursor += max(0, skip)
                        continue
                    next_stop = min(next_stop, r0 - checked)
                if next_stop > cursor:
                    s_part = source[cursor:next_stop]
                    t_part = target[cursor:next_stop]
                    src_hash.update(s_part)
                    dst_hash.update(t_part)
                    if mismatch is None and s_part != t_part:
                        for idx, (sb, tb) in enumerate(zip(s_part, t_part)):
                            if sb != tb:
                                mismatch = {
                                    "offset": absolute + idx,
                                    "source_sample": s_part[idx:idx+32],
                                    "target_sample": t_part[idx:idx+32],
                                }
                                break
                    cursor = next_stop
                else:
                    cursor += 1
            checked += want
            if progress:
                progress(checked, total)
    return {
        "match": mismatch is None,
        "source_hash": src_hash.hexdigest(),
        "target_hash": dst_hash.hexdigest(),
        "mismatch_offset": mismatch["offset"] if mismatch else None,
        "source_sample_hex": short_hex(mismatch["source_sample"]) if mismatch else "",
        "target_sample_hex": short_hex(mismatch["target_sample"]) if mismatch else "",
    }


def smart_verify_image(image_path,disk_number,total,sector,checkpoint=None,progress=None):
    strict=verify_image_against_target(image_path,disk_number,total,sector,checkpoint=checkpoint,progress=progress)
    strict["mode"]="strict"
    if strict["match"]:
        strict["message"]="Byte-for-byte verification passed."
        return strict
    strict["message"]="Byte mismatch not proven to be safe GPT relocation. Verification failed."
    if sector!=512:return strict
    try:
        d=get_disk(int(disk_number))
        with ImageReader(image_path) as source,open_physical_retry(int(disk_number),GENERIC_READ) as handle:
            target=RawHandleReader(handle.h,int(d["Size"]))
            s,sb=_gpt_snapshot(source,sector);t,tb=_gpt_snapshot(target,sector)
            if s["entries"]!=t["entries"]:
                return strict
            if t["backup"]!=target.size//sector-1 or t["last"]<s["last"]:
                return strict
            # All primary header bytes must match except CRC, backup-LBA and last-usable-LBA.
            allowed=[(16,20),(32,40),(48,56)]
            hs,ht=bytearray(s["header"]),bytearray(t["header"])
            for a,b in allowed:hs[a:b]=b"\0"*(b-a);ht[a:b]=b"\0"*(b-a)
            if hs!=ht:return strict
            ignore=[(sector+a,sector+b) for a,b in allowed]
            # An old backup may be left intact or explicitly zeroed, never silently accepted as arbitrary data.
            if t["backup"]!=s["backup"]:
                a=sb["entries_lba"]*sector;b=(s["backup"]+1)*sector
                old=source.read_at(a,b-a);now=target.read_at(a,b-a)
                if now!=old and now!=b"\0"*len(old):return strict
                ignore.append((a,b))
            sm=source.read_at(0,512);tm=target.read_at(0,512)
            for i in range(4):
                p=446+i*16
                if sm[p+4]==0xEE and tm[p+4]==0xEE:
                    if struct.unpack_from("<I",tm,p+12)[0] not in (struct.unpack_from("<I",sm,p+12)[0],min(target.size//sector-1,0xFFFFFFFF)):
                        return strict
                    ignore.append((p+12,p+16))
            if not validate_boot_reader(target,".img").get("valid"):return strict
        result=compare_image_target_except_ranges(image_path,disk_number,total,ignore,checkpoint=checkpoint,progress=progress)
        result["mode"]="gpt-normalized"
        result["message"]="Only checked GPT relocation fields changed; primary/backup CRCs, identical partition entries and all remaining image bytes were validated."
        return result
    except InterruptedError:
        raise
    except Exception:
        return strict


def post_cert_payload_audit(image_path, disk_number, total, sector, checkpoint=None, progress=None):
    """Audit host-visible media after an exact locked write certification.

    Strict certification still occurs under the unreleased raw handle. This later
    audit permits only two bounded host-side normalization classes:

      1. Validated GPT relocation/header bookkeeping.
      2. The 8 advisory bytes in each valid FAT32 FSInfo copy:
         Free_Count (offset 488) and Next_Free (offset 492).

    No file data, directory entry, FAT allocation entry, boot code, partition entry,
    or other payload byte is excused.
    """
    exact = verify_image_against_target(
        image_path, disk_number, total, sector, checkpoint=checkpoint, progress=progress
    )
    exact["mode"] = "exact"
    exact["message"] = "Host-visible image region is byte-identical."
    if exact.get("match") or sector != 512:
        return exact

    try:
        with ImageReader(image_path) as source, open_physical_retry(int(disk_number), GENERIC_READ) as h:
            d = get_disk(int(disk_number))
            target = RawHandleReader(h.h, int(d["Size"]))

            sg, sb = _gpt_snapshot(source, sector)
            tg, tb = _gpt_snapshot(target, sector)
            if sg["entries"] != tg["entries"]:
                return exact
            if sg["header"][56:72] != tg["header"][56:72]:
                return exact
            if tg["first"] != sg["first"] or tg["last"] < sg["last"]:
                return exact
            target_last_lba = target.size // sector - 1
            if tg["backup"] not in (sg["backup"], target_last_lba):
                return exact

            allowed = [(16, 20), (32, 40), (48, 56)]
            sh, th = bytearray(sg["header"]), bytearray(tg["header"])
            for a, b in allowed:
                sh[a:b] = b"\0" * (b - a)
                th[a:b] = b"\0" * (b - a)
            if sh != th:
                return exact

            if not validate_boot_reader(target, ".img").get("valid"):
                return exact

            ignore = list(gpt_metadata_ignore_ranges(source))

            mbr = source.read_at(0, 512)
            if len(mbr) == 512 and mbr[510:512] == b"\x55\xAA":
                for i in range(4):
                    pos = 446 + i * 16
                    if mbr[pos + 4] == 0xEE:
                        ignore.append((pos + 12, pos + 16))

            fsinfo_states = fat32_fsinfo_host_mutable_state(source)
            fsinfo_ranges = [s["mutable_range"] for s in fsinfo_states]
            if fsinfo_states and not _fat32_fsinfo_target_values_valid(target, fsinfo_states):
                exact["mode"] = "filesystem-metadata-invalid"
                exact["message"] = "FAT32 FSInfo changed to structurally invalid values after certification."
                return exact

            ignore.extend(fsinfo_ranges)
            ignore = merge_ranges(ignore)

        result = compare_image_target_except_ranges(
            image_path, disk_number, total, ignore,
            checkpoint=checkpoint, progress=progress
        )
        if not result.get("match"):
            result["mode"] = "payload-mismatch"
            result["message"] = (
                "A byte outside validated GPT relocation fields and FAT32 FSInfo "
                "advisory counters changed after locked certification."
            )
            return result

        first_off = exact.get("mismatch_offset")
        if _offset_in_ranges(first_off, fsinfo_ranges):
            result["mode"] = "post-cert-fat32-fsinfo-adjusted"
            result["message"] = (
                "Exact locked certification passed earlier; Windows later updated only "
                "validated FAT32 FSInfo Free_Count/Next_Free advisory metadata. All other "
                "image bytes in the source region remain certified."
            )
        else:
            result["mode"] = "post-cert-gpt-host-adjusted"
            result["message"] = (
                "Exact locked certification passed earlier; after host refresh, all "
                "non-mutable payload bytes still match and only validated GPT host-layout "
                "metadata differs."
            )
        return result
    except InterruptedError:
        raise
    except Exception:
        return exact


def wipe_disk_edges(number, disk_size, sector_size=512, expected=None, checkpoint=None):
    """Clear and read back stale edge signatures only AFTER verified reclaim."""
    number, disk_size = int(number), int(disk_size)
    guard_runtime_outside_target(number)
    expected = expected or safe_removable_disk(number)
    d = wait_for_no_partitions(number, timeout=4, expected=expected, checkpoint=checkpoint)
    if disk_size != int(d['Size']):
        raise RuntimeError('Signature wipe target capacity changed.')
    sector = int(sector_size or 512)
    if sector not in (512, 1024, 2048, 4096) or disk_size % sector:
        raise RuntimeError('Unsupported or unaligned signature-wipe geometry.')
    span = min(EDGE_WIPE, max(sector, disk_size // 8)) // sector * sector
    tail = disk_size - span
    zero = b'\x00' * min(CHUNK, span)
    safe_removable_disk(number, expected)
    with open_physical_certification_handle(number) as h:
        _assert_open_disk_geometry(h.h, number, disk_size)
        allow_extended_dasd_io(h.h)
        for base in sorted(set((0, tail))):
            raw_seek(h.h, base)
            left = span
            while left:
                if checkpoint:
                    checkpoint()
                block = zero[:min(left, len(zero))]
                raw_write(h.h, block)
                left -= len(block)
        if not kernel32.FlushFileBuffers(h.h):
            raise win_error('Signature wipe flush failed')
        for base in sorted(set((0, tail))):
            raw_seek(h.h, base)
            left = span
            while left:
                if checkpoint:
                    checkpoint()
                block = zero[:min(left, len(zero))]
                if raw_read_exact(h.h, len(block)) != block:
                    raise MediaOperationError('MEDIA_IO', 'Signature wipe readback failed; no image write started.')
                left -= len(block)


def prepare_disk_for_flash(number, expected, log=None, checkpoint=None):
    d = safe_removable_disk(number, expected)
    if log:
        log("RAW ACCESS: enabling elevated volume-management privileges…")
    privs = enable_raw_disk_privileges()
    if log:
        log("PRIVILEGES: " + ", ".join(f"{k}={'on' if v else 'not available'}" for k, v in privs.items()))
        log("RECLAIM: locking/dismounting all target volumes, including hidden EFI volume GUIDs…")
    dismount_target_volumes(number, log=log)
    if log:
        log("RECLAIM: clearing read-only/offline state and deleting EFI/OEM/recovery partitions…")
    force_clean_disk(number, expected, log=log, checkpoint=checkpoint)

    # Some Windows storage stacks report ERROR_NOT_READY during WriteFile() when a
    # removable disk is forced offline before raw I/O. After all partitions are
    # removed, keep the disk online. The raw acquisition helper retains any
    # remaining volume locks and supports Windows-compatible handle sharing.
    if log:
        log("RAW ACCESS: preparing guarded raw-disk access with the target kept online for compatibility…")

    if log:
        log("RECLAIM: zeroing stale primary/backup GPT and boot signatures…")
    wipe_disk_edges(number, int(d["Size"]), int(d.get("LogicalSectorSize") or 512), expected=expected, checkpoint=checkpoint)
    update_disk_properties(number)
    refresh_storage_cache()
    return safe_removable_disk(number, expected)



# ---------------------------------------------------------------------------
# AEGIS FORENSIC RECOVERY / DATA LIFECYCLE SERVICES
# ---------------------------------------------------------------------------

def forensic_recovery_capabilities():
    return {"image_sources": ["IMG", "RAW", "BIN", "uncompressed sector images"],
            "metadata_undelete": ["NTFS (base-record resident / uncompressed data runs)",
                                  "FAT32 (free contiguous clusters, inferred layout)",
                                  "exFAT (intact deleted entry sets and surviving allocation)"] ,
            "carving": ["PNG", "JPEG", "PDF", "ZIP / Office Open XML", "RIFF / WAV / AVI / WebP"],
            "source_writes": False, "extraction_sha256": True,
            "unsupported": ["BitLocker / encrypted volumes", "NTFS compressed or EFS data",
                            "NTFS attribute-list extensions", "RAID reconstruction", "APFS", "ext4 metadata",
                            "TRIMmed / overwritten contents", "guaranteed recovery of arbitrary fragmented files"],
            "limits": dict(RECOVERY_LIMITS)}


def forensic_delete_capabilities():
    return {"implemented_method":"One zero overwrite of all host-addressable bytes, followed by full readback",
            "target_scope":"Non-system USB / SD / MMC disks only",
            "typed_disk_bound_confirmation":True,"retained_volume_locks":True,"audit_report":True,
            "full_readback_verification":True,"multipass_profiles":False,
            "firmware_sanitize":False,"cryptographic_erase":False,"purge_certification":False,
            "limitation":"No assurance for remapped sectors, SSD over-provisioning, hidden areas or controller-managed flash."}


# v3.2 implementations and bounded defaults

RECOVERY_LIMITS = {"max_files": 10000, "max_file_bytes": 256 * 1024**2,
                   "max_mft_records": 2000000, "max_directories": 10000,
                   "max_directory_bytes": 32 * 1024**2}

class RecoveryImage:
    """Bounded, read-only random access to an ordinary local image file."""
    def __init__(self, path):
        self.path = Path(path).resolve(strict=True)
        if not self.path.is_file():
            raise ValueError("Recovery requires an existing ordinary image file.")
        self.f = self.path.open("rb")
        self.size = os.fstat(self.f.fileno()).st_size
        self.initial = self.stamp()
        self._cache = {}

    def stamp(self):
        st = os.fstat(self.f.fileno())
        return (st.st_size, st.st_mtime_ns)

    def read_at(self, off, count):
        off, count = int(off), int(count)
        if off < 0 or count < 0 or off + count > self.size or count > 64 * 1024**2:
            raise ValueError("Recovery read outside image bounds or above bounded read size.")
        self.f.seek(off)
        data = self.f.read(count)
        if len(data) != count:
            raise OSError(f"Short image read at byte {off}; scan stopped, not certified.")
        return data

    def cached(self, off, count):
        # Small metadata reads use bounded pages; bulk source hashing bypasses this cache.
        if count > 65536 or off // 65536 != (off + max(0, count-1)) // 65536:
            return self.read_at(off, count)
        page = off // 65536 * 65536
        if page not in self._cache:
            if len(self._cache) >= 64:
                self._cache.pop(next(iter(self._cache)))
            self._cache[page] = self.read_at(page, min(65536, self.size-page))
        data = self._cache[page][off-page:off-page+count]
        if len(data) != count:
            raise ValueError("Truncated metadata page.")
        return data

    def unchanged(self):
        if self.stamp() != self.initial:
            raise RuntimeError("Source image changed while being read. Discard this scan and use an immutable copy.")

    def close(self):
        self.f.close()

    def __enter__(self):
        return self

    def __exit__(self, *_):
        self.close()

def _rec_check(checkpoint):
    if checkpoint:
        checkpoint()

def _rec_u16(b, off):
    return struct.unpack_from("<H", b, off)[0]

def _rec_u32(b, off):
    return struct.unpack_from("<I", b, off)[0]

def _rec_u64(b, off):
    return struct.unpack_from("<Q", b, off)[0]

def recovery_volumes(reader, notes):
    """Locate ordinary MBR primary/GPT partitions or a partition-only image."""
    candidates = [(0, reader.size)]
    if reader.size < 512:
        return []
    mbr = reader.read_at(0, 512)
    if mbr[510:512] == b"\x55\xaa":
        for index in range(4):
            e = mbr[446+index*16:462+index*16]
            first, sectors = _rec_u32(e, 8), _rec_u32(e, 12)
            if e[4] in (5, 15, 0x85):
                notes.append("MBR extended partition traversal is not implemented; signature carving still scans the whole image.")
            if e[4] not in (0, 0xEE, 5, 15, 0x85) and sectors:
                start, length = first*512, sectors*512
                if start >= 512 and start+length <= reader.size:
                    candidates.append((start, length))
    # GPT sector size is discovered independently; recovery does not use the 512-byte boot validator.
    for sector in (512, 4096):
        if reader.size < 2*sector:
            continue
        hdr = reader.read_at(sector, sector)
        if hdr[:8] != b"EFI PART":
            continue
        hs, count, es = _rec_u32(hdr,12), _rec_u32(hdr,80), _rec_u32(hdr,84)
        if not (92 <= hs <= sector and 0 < count <= 4096 and 128 <= es <= 1024 and es % 8 == 0):
            notes.append("Rejected invalid GPT geometry in recovery source."); continue
        hc = bytearray(hdr[:hs]); struct.pack_into("<I", hc, 16, 0)
        if crc32(hc) != _rec_u32(hdr,16):
            notes.append("Rejected GPT header with invalid CRC; carving remains available."); continue
        arr_off, arr_len = _rec_u64(hdr,72)*sector, count*es
        if arr_off+arr_len > reader.size:
            notes.append("Rejected out-of-bounds GPT entry array."); continue
        arr = reader.read_at(arr_off, arr_len)
        if crc32(arr) != _rec_u32(hdr,88):
            notes.append("Rejected GPT entry array with invalid CRC."); continue
        for i in range(count):
            e = arr[i*es:(i+1)*es]
            if e[:16] == b"\0"*16:
                continue
            first, last = _rec_u64(e,32), _rec_u64(e,40)
            if first >= 2 and last >= first and (last+1)*sector <= reader.size:
                candidates.append((first*sector, (last-first+1)*sector))
    volumes, seen = [], set()
    for start,length in candidates:
        if start in seen or length < 512:
            continue
        seen.add(start)
        boot = reader.read_at(start,512)
        typ = "NTFS" if boot[3:11] == b"NTFS    " else "exFAT" if boot[3:11] == b"EXFAT   " else "FAT32" if boot[82:90] == b"FAT32   " else ""
        if typ:
            volumes.append({"offset": start, "length": length, "fs": typ})
    return volumes

def _rec_runs(raw, total_clusters):
    """Decode signed NTFS mapping pairs, including sparse runs, with strict bounds."""
    out, pos, lcn, logical = [], 0, 0, 0
    while pos < len(raw):
        code = raw[pos]; pos += 1
        if code == 0:
            return out
        nl, no = code & 15, code >> 4
        if not (1 <= nl <= 8 and 0 <= no <= 8) or pos+nl+no > len(raw):
            raise ValueError("Malformed NTFS run list.")
        count = int.from_bytes(raw[pos:pos+nl], "little"); pos += nl
        if count <= 0 or logical+count > total_clusters:
            raise ValueError("Invalid NTFS run length.")
        if no:
            lcn += int.from_bytes(raw[pos:pos+no], "little", signed=True)
            if lcn < 0 or lcn+count > total_clusters:
                raise ValueError("NTFS run is outside its volume.")
            physical = lcn
        else:
            physical = None
        pos += no
        out.append((logical, physical, count)); logical += count
        if len(out) > 4096:
            raise ValueError("Run-list safety limit exceeded.")
    raise ValueError("Unterminated NTFS run list.")

def _rec_fixup(raw, sector):
    if raw[:4] != b"FILE" or len(raw) < 48:
        raise ValueError("Not an NTFS FILE record.")
    usa, count = _rec_u16(raw,4), _rec_u16(raw,6)
    if len(raw) % sector or count != len(raw)//sector+1 or usa < 8 or usa+count*2 > len(raw):
        raise ValueError("Invalid NTFS update-sequence geometry.")
    result = bytearray(raw); sig = raw[usa:usa+2]
    for i in range(1,count):
        end = i*sector
        if raw[end-2:end] != sig:
            raise ValueError("Torn NTFS record (update-sequence mismatch).")
        result[end-2:end] = raw[usa+2*i:usa+2*i+2]
    return bytes(result)

def _rec_attrs(record):
    used, pos = _rec_u32(record,24), _rec_u16(record,20)
    if used > len(record) or used < 48 or pos < 48 or pos >= used:
        raise ValueError("Invalid NTFS attribute area.")
    attrs = []
    while pos+4 <= used:
        kind = _rec_u32(record,pos)
        if kind == 0xFFFFFFFF:
            return attrs
        if pos+16 > used:
            break
        length = _rec_u32(record,pos+4)
        if length < 24 or length % 8 or pos+length > used:
            raise ValueError("Invalid NTFS attribute length.")
        a = record[pos:pos+length]
        if a[8] not in (0,1):
            raise ValueError("Invalid NTFS residency flag.")
        attrs.append((kind, a)); pos += length
        if len(attrs) > 128:
            raise ValueError("Too many NTFS attributes.")
    raise ValueError("Unterminated NTFS attribute area.")

def _rec_resident(a):
    if a[8] != 0:
        raise ValueError("Resident attribute expected.")
    n, off = _rec_u32(a,16), _rec_u16(a,20)
    if off < 24 or off+n > len(a):
        raise ValueError("Invalid resident attribute value.")
    return a[off:off+n]

def _rec_stream(a, volume, cluster, total_clusters):
    if a[8] == 0:
        data = _rec_resident(a)
        return {"size":len(data), "resident_hex":data.hex(), "spans":[]}
    if len(a) < 64 or _rec_u16(a,12) & 0x4001 or _rec_u64(a,16) != 0 or _rec_u16(a,34) != 0:
        raise ValueError("Compressed, encrypted or extension-based NTFS data is unsupported.")
    off, size, initialized = _rec_u16(a,32), _rec_u64(a,48), _rec_u64(a,56)
    if off < 64 or off >= len(a) or initialized > size:
        raise ValueError("Invalid NTFS stream geometry.")
    runs = _rec_runs(a[off:],total_clusters)
    if sum(n for _,_,n in runs)*cluster < size or _rec_u64(a,24)+1 != sum(n for _,_,n in runs):
        raise ValueError("NTFS data requires missing extension runs.")
    spans, remaining, init_left = [],size,initialized
    for _, physical,count in runs:
        n = min(remaining,count*cluster)
        if not n:
            break
        live_n = min(n,init_left)
        if live_n:
            spans.append([None if physical is None else volume+physical*cluster,live_n])
        if n > live_n:
            spans.append([None,n-live_n])
        remaining -= n; init_left -= live_n
    return {"size":size,"spans":spans,"resident_hex":None}

def _rec_stream_read(reader, stream, offset, count):
    if offset < 0 or count < 0 or offset+count > stream["size"]:
        raise ValueError("Read outside reconstructed stream.")
    if stream.get("resident_hex") is not None:
        return bytes.fromhex(stream["resident_hex"])[offset:offset+count]
    pieces, cursor = [],0
    for physical,n in stream["spans"]:
        a,b = max(offset,cursor),min(offset+count,cursor+n)
        if b > a:
            pieces.append(b"\0"*(b-a) if physical is None else reader.cached(physical+a-cursor,b-a))
        cursor += n
        if cursor >= offset+count:
            break
    data = b"".join(pieces)
    if len(data) != count:
        raise ValueError("Incomplete reconstructed stream.")
    return data

def _rec_candidate(name,method,stream,note,metadata_offset):
    return dict(stream, name=name, method=method, note=note, metadata_offset=metadata_offset,
                deletion_status="deleted metadata" if method != "CARVE" else "unknown (signature scan)")

def recover_ntfs_candidates(reader,volume,limits,checkpoint,notes):
    base,length = volume["offset"],volume["length"]
    boot = reader.read_at(base,512); sector,spc = _rec_u16(boot,11),boot[13]
    if sector not in (512,1024,2048,4096) or not spc or spc & (spc-1):
        raise ValueError("Unsupported NTFS sector/cluster geometry.")
    cluster = sector*spc; total = _rec_u64(boot,40)*sector
    if total <= 0 or total > length or cluster > 2*1024**2:
        raise ValueError("NTFS volume size is outside source bounds.")
    clusters = total//cluster
    rec_code = struct.unpack_from("b",boot,64)[0]
    rec_size = (1 << -rec_code) if -16 <= rec_code < 0 else rec_code*cluster if 0 < rec_code < 128 else 0
    if not (sector <= rec_size <= 65536 and rec_size % sector == 0):
        raise ValueError("Unsupported NTFS MFT record size.")
    mft_lcn = _rec_u64(boot,48)
    if mft_lcn*cluster+rec_size > total:
        raise ValueError("MFT is outside the NTFS volume.")
    first = _rec_fixup(reader.read_at(base+mft_lcn*cluster,rec_size),sector)
    attrs = _rec_attrs(first)
    if any(k==0x20 for k,_ in attrs):
        raise ValueError("MFT has attribute-list extensions; metadata recovery is not supported for this layout.")
    mft_data = [a for k,a in attrs if k==0x80 and a[9]==0]
    if len(mft_data)!=1:
        raise ValueError("A single base MFT data stream is required.")
    mft = _rec_stream(mft_data[0],base,cluster,clusters)
    bitmap = None
    try:
        rec6 = _rec_fixup(_rec_stream_read(reader,mft,6*rec_size,rec_size),sector)
        battrs = _rec_attrs(rec6)
        ba = [a for k,a in battrs if k==0x80 and a[9]==0]
        if len(ba)==1 and not any(k==0x20 for k,_ in battrs):
            bitmap = _rec_stream(ba[0],base,cluster,clusters)
            if bitmap["size"]*8 < clusters:
                bitmap = None
    except (ValueError,struct.error):
        bitmap = None
    result,skipped,torn = [],0,0
    total_records = mft["size"]//rec_size
    if total_records > limits["max_mft_records"]:
        notes.append("MFT scan capped by max_mft_records; metadata scan is partial.")
    for index in range(16,min(total_records,limits["max_mft_records"])):
        _rec_check(checkpoint)
        try:
            rec = _rec_fixup(_rec_stream_read(reader,mft,index*rec_size,rec_size),sector)
            if _rec_u16(rec,22) & 3 or _rec_u64(rec,32):
                continue
            attrs = _rec_attrs(rec)
            if any(k==0x20 for k,_ in attrs):
                skipped+=1;continue
            names=[]
            for k,a in attrs:
                if k==0x30 and a[8]==0:
                    value=_rec_resident(a)
                    if len(value)>=66 and 66+value[64]*2 <= len(value):
                        names.append((value[65]!=2,value[66:66+value[64]*2].decode("utf-16le","replace")))
            dataattrs=[a for k,a in attrs if k==0x80 and a[9]==0]
            if not names or len(dataattrs)!=1:
                continue
            stream=_rec_stream(dataattrs[0],base,cluster,clusters)
            if stream["size"] > limits["max_file_bytes"]:
                skipped+=1;continue
            reused=False
            if bitmap and stream.get("resident_hex") is None:
                for physical,n in stream["spans"]:
                    if physical is None:
                        continue
                    first_c=(physical-base)//cluster; last_c=(physical-base+n-1)//cluster
                    bytes_=_rec_stream_read(reader,bitmap,first_c//8,last_c//8-first_c//8+1)
                    if any(bytes_[c//8-first_c//8] & (1<<(c%8)) for c in range(first_c,last_c+1)):
                        reused=True;break
            if reused:
                skipped+=1;continue
            name=sorted(names,reverse=True)[0][1]
            note="Resident bytes retained in an unused MFT record." if stream.get("resident_hex") is not None else "Run list reconstructed; current clusters are free." if bitmap else "Run list reconstructed; allocation bitmap unavailable. Original content is unverified."
            result.append(_rec_candidate(name,"NTFS",stream,note,index))
            if len(result)>=limits["max_files"]:
                notes.append("NTFS candidate cap reached; metadata scan is partial.");break
        except (ValueError,struct.error):
            torn+=1
    if skipped or torn:
        notes.append(f"NTFS: {skipped} oversized/reused/unsupported candidates skipped; {torn} invalid/unused records skipped.")
    return result

def _rec_fat_chain(reader, fat, cluster, max_cluster, checkpoint, max_count=1048576, exfat=False):
    chain,seen=[],set()
    while 2 <= cluster <= max_cluster:
        _rec_check(checkpoint)
        if cluster in seen or len(chain)>=max_count:
            raise ValueError("Cyclic or over-limit FAT chain.")
        seen.add(cluster);chain.append(cluster)
        nxt=_rec_u32(reader.cached(fat+cluster*4,4),0) & (0xFFFFFFFF if exfat else 0x0FFFFFFF)
        if nxt >= (0xFFFFFFF8 if exfat else 0x0FFFFFF8):
            return chain
        if nxt<2 or nxt==(0xFFFFFFF7 if exfat else 0x0FFFFFF7):
            raise ValueError("Missing or damaged FAT chain.")
        cluster=nxt
    raise ValueError("FAT chain outside volume.")

def recover_fat32_candidates(reader,volume,limits,checkpoint,notes):
    base,length=volume["offset"],volume["length"];b=reader.read_at(base,512)
    sector,spc,reserved,fats=_rec_u16(b,11),b[13],_rec_u16(b,14),b[16]
    nf,ns,root=_rec_u32(b,36),_rec_u32(b,32),_rec_u32(b,44)
    if sector not in (512,1024,2048,4096) or not spc or spc&(spc-1) or not reserved or fats not in (1,2) or not nf:
        raise ValueError("Invalid FAT32 geometry.")
    data_sector=reserved+fats*nf;cluster=sector*spc
    if ns*sector>length or ns<=data_sector or cluster>1024**2:
        raise ValueError("FAT32 volume outside image bounds.")
    clusters=(ns-data_sector)//spc
    if (clusters+2)*4>nf*sector or not 2<=root<=clusters+1:
        raise ValueError("FAT32 allocation geometry is inconsistent.")
    flags=_rec_u16(b,40);active=(flags&15) if flags&0x80 else 0
    if active>=fats:
        raise ValueError("Invalid active FAT.")
    fat=base+(reserved+active*nf)*sector;heap=base+data_sector*sector
    pending=[root];visited=set();out=[];skipped=0
    while pending and len(visited)<limits["max_directories"]:
        _rec_check(checkpoint);d=pending.pop()
        if d in visited:
            continue
        visited.add(d)
        try:chain=_rec_fat_chain(reader,fat,d,clusters+1,checkpoint,max_count=limits["max_directory_bytes"]//cluster)
        except ValueError:
            skipped+=1;continue
        end=False
        for c in chain:
            buf=reader.read_at(heap+(c-2)*cluster,cluster)
            for pos in range(0,len(buf),32):
                e=buf[pos:pos+32]
                if e[0]==0:
                    end=True;break
                if e[11]==0x0F or e[11]&0x08:
                    continue
                first=(_rec_u16(e,20)<<16)|_rec_u16(e,26)
                if e[0]!=0xE5:
                    if e[11]&0x10 and e[0]!=46 and 2<=first<=clusters+1:
                        pending.append(first)
                    continue
                if e[11]&0x10:
                    continue
                size=_rec_u32(e,28);count=(size+cluster-1)//cluster
                if size>limits["max_file_bytes"] or size==0 or first<2 or first+count>clusters+2:
                    skipped+=1;continue
                # Deleted FAT32 chains are normally cleared. Do not fabricate fragment links.
                free=True
                for n in range(first,first+count):
                    _rec_check(checkpoint)
                    if _rec_u32(reader.cached(fat+n*4,4),0)&0x0FFFFFFF:
                        free=False;break
                if not free:
                    skipped+=1;continue
                short=b"_"+e[1:11];name=fat_name(short)
                stream={"size":size,"spans":[[heap+(first-2)*cluster,size]],"resident_hex":None}
                out.append(_rec_candidate(name,"FAT32",stream,"Contiguous layout ASSUMED; first filename character lost. Fragmentation/overwriting cannot be ruled out.",heap+(c-2)*cluster+pos))
                if len(out)>=limits["max_files"]:
                    notes.append("FAT32 candidate cap reached; metadata scan is partial.");return out
            if end:break
    if pending:notes.append("FAT32 directory limit reached; metadata scan is partial.")
    if skipped:notes.append(f"FAT32: {skipped} invalid, allocated or unsupported entries/chains skipped.")
    return out

def _exfat_checksum(entries):
    value=0
    for i,b in enumerate(entries):
        if i not in (2,3):
            value=(((value&1)<<15)+(value>>1)+b)&0xFFFF
    return value

def recover_exfat_candidates(reader,volume,limits,checkpoint,notes):
    base,length=volume["offset"],volume["length"];b=reader.read_at(base,512)
    ss,cs=b[108],b[109]
    if not (9<=ss<=12 and cs<=25-ss) or b[110] not in (1,2):
        raise ValueError("Invalid exFAT sector/cluster geometry.")
    sector,cluster=1<<ss,1<<(ss+cs)
    total,fo,fl,ho,cc,root=_rec_u64(b,72),_rec_u32(b,80),_rec_u32(b,84),_rec_u32(b,88),_rec_u32(b,92),_rec_u32(b,96)
    if total*sector>length or ho*sector+cc*cluster>total*sector or not cc or fo<24 or fo+fl*b[110]>ho or (cc+2)*4>fl*sector or not 2<=root<=cc+1:
        raise ValueError("exFAT allocation geometry outside volume bounds.")
    active=(_rec_u16(b,106)&1) if b[110]==2 else 0
    fat=base+(fo+active*fl)*sector;heap=base+ho*sector
    def chain(first):
        return _rec_fat_chain(reader,fat,first,cc+1,checkpoint,max_count=max(1,limits["max_directory_bytes"]//cluster),exfat=True)
    def stream(first,size,contiguous):
        if size<0 or first<2 or first>cc+1:
            raise ValueError("Invalid exFAT stream.")
        count=(size+cluster-1)//cluster
        if contiguous:
            if first+count>cc+2:raise ValueError("exFAT stream outside heap.")
            return {"size":size,"spans":[[heap+(first-2)*cluster,size]],"resident_hex":None}
        clusters=chain(first)
        if len(clusters)*cluster<size:raise ValueError("Incomplete exFAT cluster chain.")
        spans=[];remaining=size
        for c in clusters:
            n=min(cluster,remaining)
            if not n:break
            spans.append([heap+(c-2)*cluster,n]);remaining-=n
        return {"size":size,"spans":spans,"resident_hex":None}
    rootchain=chain(root)
    rootstream={"size":len(rootchain)*cluster,"spans":[[heap+(c-2)*cluster,cluster] for c in rootchain],"resident_hex":None}
    rootbuf=_rec_stream_read(reader,rootstream,0,rootstream["size"])
    bitmap=None
    for pos in range(0,len(rootbuf),32):
        e=rootbuf[pos:pos+32]
        if e[0]==0:break
        if e[0]==0x81 and (e[1]&1)==active:
            try:
                bitmap=stream(_rec_u32(e,20),_rec_u64(e,24),False)
                if bitmap["size"]*8<cc:bitmap=None
            except ValueError:bitmap=None
            break
    if bitmap is None:
        raise ValueError("exFAT allocation bitmap unavailable; refusing uncertain metadata extraction. Use carving instead.")
    pending=[rootstream];visited=set();out=[];skipped=0
    while pending and len(visited)<limits["max_directories"]:
        _rec_check(checkpoint);ds=pending.pop();key=tuple(tuple(x) for x in ds["spans"])
        if key in visited:continue
        visited.add(key)
        if ds["size"]>limits["max_directory_bytes"]:
            notes.append("exFAT oversized directory skipped.");continue
        data=_rec_stream_read(reader,ds,0,ds["size"]);pos=0
        while pos+32<=len(data):
            _rec_check(checkpoint);e=data[pos:pos+32]
            if e[0]==0:break
            if e[0] not in (0x85,0x05):pos+=32;continue
            count=e[1];span=(count+1)*32;deleted=e[0]==0x05
            if count<2 or count>18 or pos+span>len(data):pos+=32;continue
            group=bytearray(data[pos:pos+span]);old_pos=pos;pos+=span
            expected_stream=0x40 if deleted else 0xC0;expected_name=0x41 if deleted else 0xC1
            if group[32]!=expected_stream or any(group[j]!=expected_name for j in range(64,span,32)):
                skipped+=1;continue
            # A normal delete clears InUse. Restoring only that bit must reproduce the saved checksum.
            for j in range(0,span,32):group[j]|=0x80
            if _exfat_checksum(group)!=_rec_u16(group,2):skipped+=1;continue
            s=group[32:64];namelen=s[3];first=_rec_u32(s,20);size=_rec_u64(s,24);initialized=_rec_u64(s,8)
            if namelen==0 or namelen>15*(count-1) or initialized>size:skipped+=1;continue
            name=b"".join(bytes(group[j+2:j+32]) for j in range(64,span,32))[:namelen*2].decode("utf-16le","replace")
            directory=bool(_rec_u16(group,4)&0x10)
            if not deleted and not directory:continue
            if size==0 or size>(limits["max_directory_bytes"] if directory else limits["max_file_bytes"]):skipped+=1;continue
            try:st=stream(first,size,bool(s[1]&2))
            except ValueError:skipped+=1;continue
            if not deleted and directory:pending.append(st);continue
            if directory:continue
            allocated=False
            for physical,n in st["spans"]:
                firstc=(physical-heap)//cluster;lastc=(physical-heap+n-1)//cluster
                bm=_rec_stream_read(reader,bitmap,firstc//8,lastc//8-firstc//8+1)
                if any(bm[c//8-firstc//8]&(1<<(c%8)) for c in range(firstc,lastc+1)):
                    allocated=True;break
            if allocated:skipped+=1;continue
            # Initialized length is authoritative; do not expose unrelated uninitialized slack.
            if initialized<size:
                trimmed=[];remaining=initialized
                for physical,n in st["spans"]:
                    take=min(remaining,n)
                    if take:trimmed.append([physical,take]);remaining-=take
                trimmed.append([None,size-initialized]);st["spans"]=trimmed
            out.append(_rec_candidate(name,"exFAT",st,"Deleted entry checksum validated; current allocation bitmap is free. Original bytes remain unverified.",str(key)+":"+str(old_pos)))
            if len(out)>=limits["max_files"]:
                notes.append("exFAT candidate cap reached; metadata scan is partial.");return out
    if pending:notes.append("exFAT directory limit reached; metadata scan is partial.")
    if skipped:notes.append(f"exFAT: {skipped} invalid, allocated or unsupported entry sets skipped.")
    return out

def _rec_find_end(reader,start,limit,marker,checkpoint):
    off=start;carry=b""
    while off<limit:
        _rec_check(checkpoint);n=min(1024**2,limit-off);data=carry+reader.read_at(off,n)
        where=data.find(marker)
        if where>=0:return off-len(carry)+where+len(marker)
        carry=data[-(len(marker)-1):] if len(marker)>1 else b"";off+=n
    return None

def _rec_carve_extent(reader,start,kind,cap,checkpoint):
    limit=min(reader.size,start+cap)
    if kind=="PNG":
        pos=start+8;first=True
        while pos+12<=limit:
            _rec_check(checkpoint);hdr=reader.read_at(pos,8);n=int.from_bytes(hdr[:4],"big");typ=hdr[4:8]
            if not all(65<=x<=90 or 97<=x<=122 for x in typ) or pos+12+n>limit or (first and (typ!=b"IHDR" or n!=13)):
                return None
            check=binascii.crc32(typ);p=pos+8;left=n
            while left:
                _rec_check(checkpoint);take=min(left,1024**2);check=binascii.crc32(reader.read_at(p,take),check);p+=take;left-=take
            if (check&0xFFFFFFFF)!=int.from_bytes(reader.read_at(p,4),"big"):return None
            pos+=n+12;first=False
            if typ==b"IEND":return (pos-start,"png","PNG chunk CRCs validated") if n==0 else None
        return None
    if kind=="JPEG":
        # Parse marker segment lengths to avoid an embedded EXIF thumbnail ending the outer JPEG.
        pos=start+2;seen_scan=False
        while pos+2<=limit:
            _rec_check(checkpoint)
            if reader.read_at(pos,1)!=b"\xff":return None
            while pos<limit and reader.read_at(pos,1)==b"\xff":pos+=1
            if pos>=limit:return None
            marker=reader.read_at(pos,1)[0];pos+=1
            if marker==0xD9:return (pos-start,"jpg","JPEG marker structure delimited; decoded pixels not validated") if seen_scan else None
            if marker in (0,0xD8):return None
            if marker==1 or 0xD0<=marker<=0xD7:continue
            if pos+2>limit:return None
            n=int.from_bytes(reader.read_at(pos,2),"big")
            if n<2 or pos+n>limit:return None
            pos+=n
            if marker==0xDA:
                seen_scan=True
                # Entropy-coded data: ignore stuffed FF00 and restart markers.
                while pos<limit:
                    _rec_check(checkpoint);data=reader.read_at(pos,min(1024**2,limit-pos));i=0;found=False
                    while True:
                        j=data.find(b"\xff",i)
                        if j<0:pos+=len(data);break
                        if j+1>=len(data):
                            if pos+j+1>=limit:return None
                            pos+=j;found=True;break
                        nxt=data[j+1]
                        if nxt==0 or 0xD0<=nxt<=0xD7:i=j+2;continue
                        pos+=j;found=True;break
                    if found:
                        peek=reader.read_at(pos,min(2,limit-pos))
                        if len(peek)<2:return None
                        if peek[1]==0 or 0xD0<=peek[1]<=0xD7:pos+=2;continue
                        break
        return None
    if kind=="PDF":
        end=_rec_find_end(reader,start+8,limit,b"%%EOF",checkpoint)
        return (end-start,"pdf","Header/first EOF delimited; incremental updates, fragmentation and PDF validity not verified") if end else None
    if kind=="ZIP":
        search=start+4
        for _ in range(128):
            end=_rec_find_end(reader,search,limit,b"PK\x05\x06",checkpoint)
            if not end or end+18>limit:return None
            e=reader.read_at(end-4,22);comment=_rec_u16(e,20);cdsize=_rec_u32(e,12);cdoff=_rec_u32(e,16);entries=_rec_u16(e,10)
            if (_rec_u16(e,4)==_rec_u16(e,6)==0 and _rec_u16(e,8)==entries and entries not in (0,65535)
                    and end+18+comment<=limit and start+cdoff+cdsize==end-4 and cdsize>=46 and reader.read_at(start+cdoff,4)==b"PK\x01\x02"):
                return (end+18+comment-start,"zip","ZIP central-directory bounds checked; content CRCs and ZIP64 not validated")
            search=end
        return None
    if kind=="RIFF":
        if start+12>limit:return None
        h=reader.read_at(start,12);n=_rec_u32(h,4)+8;typ=h[8:12]
        ext={b"WAVE":"wav",b"AVI ":"avi",b"WEBP":"webp"}.get(typ)
        return (n,ext,"RIFF declared length checked; media decoding not validated") if ext and 12<=n<=limit-start else None
    return None

def scan_recovery_image(path, mode="Combined", limits=None, checkpoint=None, progress=None):
    limits=dict(RECOVERY_LIMITS,**(limits or {}))
    if not (1<=int(limits["max_files"])<=100000 and 1024<=int(limits["max_file_bytes"])<=4*1024**3):
        raise ValueError("Recovery limits out of supported range.")
    if mode not in ("Combined","Metadata only","Signature carving"):
        raise ValueError("Unknown recovery mode.")
    notes=[];found=[];volumes=[];digest=hashlib.sha256()
    with RecoveryImage(path) as reader:
        if mode!="Signature carving":
            volumes=recovery_volumes(reader,notes)
            funcs={"NTFS":recover_ntfs_candidates,"FAT32":recover_fat32_candidates,"exFAT":recover_exfat_candidates}
            for v in volumes:
                _rec_check(checkpoint)
                if progress:progress("METADATA",0,reader.size)
                try:found.extend(funcs[v["fs"]](reader,v,limits,checkpoint,notes))
                except (ValueError,struct.error) as exc:notes.append(f"{v['fs']} at {v['offset']}: {exc}")
                if len(found)>=limits["max_files"]:
                    found=found[:limits["max_files"]];notes.append("Global candidate cap reached; scan is partial.");break
            if not volumes:notes.append("No supported filesystem metadata found; carving does not require a surviving partition map.")
        signatures=re.compile(b"\x89PNG\r\n\x1a\n|\xff\xd8\xff|%PDF-[12]\\.[0-9]|PK\x03\x04|RIFF")
        off=0;carry=b"";seen=set();attempts=0;capped=False
        while off<reader.size:
            _rec_check(checkpoint);n=min(CHUNK,reader.size-off);block=reader.read_at(off,n);digest.update(block)
            if mode!="Metadata only" and len(found)<limits["max_files"] and not capped:
                data=carry+block;origin=off-len(carry)
                for match in signatures.finditer(data):
                    _rec_check(checkpoint);start=origin+match.start()
                    if start in seen:continue
                    seen.add(start);attempts+=1
                    if attempts>limits["max_files"]*20:
                        capped=True;notes.append("Signature-attempt safety cap reached; carving is partial.");break
                    sig=match.group();kind="PNG" if sig.startswith(b"\x89") else "JPEG" if sig.startswith(b"\xff") else "PDF" if sig.startswith(b"%") else "ZIP" if sig.startswith(b"PK") else "RIFF"
                    try:
                        result=_rec_carve_extent(reader,start,kind,limits["max_file_bytes"],checkpoint)
                    except (ValueError, struct.error, OverflowError):
                        result=None
                    if result:
                        size,ext,note=result
                        found.append(_rec_candidate(f"carved_{start:016x}.{ext}","CARVE",{"size":size,"spans":[[start,size]],"resident_hex":None},note,start))
                        if len(found)>=limits["max_files"]:
                            notes.append("Global candidate cap reached; carving is partial.");break
                carry=data[-32:]
            off+=n
            if progress:progress("SCAN / SHA-256" if mode!="Metadata only" else "SOURCE SHA-256",off,reader.size)
        reader.unchanged()
        for i,c in enumerate(found):c["id"]=i+1
        return {"schema":1,"application":APP_NAME,"source":str(reader.path),"source_size":reader.size,
                "source_sha256":digest.hexdigest(),"source_mtime_ns":reader.initial[1],"mode":mode,"limits":limits,
                "volumes":volumes,"candidates":found,"notes":notes,"source_modified_by_application":False,
                "warning":"Candidates are not proof of intact original files. Carving can include live files. No source repair is performed."}

def recovery_safe_name(name):
    name=re.sub(r'[\x00-\x1f<>:"/\\|?*]',"_",str(name)).strip(" .")
    name=name[:150] or "unnamed.bin"
    if name.split(".")[0].upper() in {"CON","PRN","AUX","NUL",*(f"COM{i}" for i in range(1,10)),*(f"LPT{i}" for i in range(1,10))}:
        name="_"+name
    return name

def extract_recovery_candidates(scan, selected_ids, output_dir, checkpoint=None, progress=None):
    source=Path(scan["source"]).resolve(strict=True);dest=Path(output_dir).resolve(strict=True)
    if not dest.is_dir():raise ValueError("Choose an existing output folder.")
    if source==dest:raise ValueError("Source and destination must be different.")
    selected=set(int(x) for x in selected_ids);items=[c for c in scan["candidates"] if c["id"] in selected]
    if not items:raise ValueError("Select at least one candidate.")
    total=sum(int(c["size"]) for c in items)
    if shutil.disk_usage(dest).free<total+1024**2:raise OSError("Insufficient free space for selected recovered files.")
    # Re-hash the entire image before extraction; refuse a stale scan.
    with RecoveryImage(source) as reader:
        digest=hashlib.sha256();off=0
        while off<reader.size:
            _rec_check(checkpoint);n=min(CHUNK,reader.size-off);digest.update(reader.read_at(off,n));off+=n
            if progress:progress("SOURCE RECHECK",off,reader.size)
        if reader.size!=scan["source_size"] or digest.hexdigest()!=scan["source_sha256"]:
            raise RuntimeError("Source image no longer matches the scanned SHA-256. Extraction refused.")
        folder=dest/("NEXUS_Recovered_"+time.strftime("%Y%m%d_%H%M%S")+"_"+uuid.uuid4().hex[:8])
        folder.mkdir(exist_ok=False)
        report={"schema":1,"application":APP_NAME,"source":str(source),"source_sha256":scan["source_sha256"],
                "status":"INCOMPLETE","files":[],"notes":scan["notes"],"warning":scan["warning"]}
        manifest=folder/"recovery_manifest.json";written=0
        try:
            for c in items:
                _rec_check(checkpoint)
                # Only engine-generated byte ranges are accepted; never create an output from an untrusted source path.
                n=int(c["size"])
                if n<0 or n>scan["limits"]["max_file_bytes"]:raise ValueError("Candidate size exceeds scan bounds.")
                dst=folder/(f"{int(c['id']):06d}_"+recovery_safe_name(c["name"]))
                part=Path(str(dst)+".partial");h=hashlib.sha256();cursor=0
                with part.open("xb") as out:
                    while cursor<n:
                        _rec_check(checkpoint);take=min(CHUNK,n-cursor)
                        data=_rec_stream_read(reader,c,cursor,take)
                        out.write(data);h.update(data);cursor+=take;written+=take
                        if progress:progress("EXTRACT",written,total)
                    out.flush();os.fsync(out.fileno())
                os.replace(part,dst)
                report["files"].append({"name":dst.name,"size":n,"sha256":h.hexdigest(),"method":c["method"],"note":c["note"],"spans":c["spans"],"metadata_offset":c["metadata_offset"]})
            reader.unchanged();report["status"]="EXTRACTED / ORIGINAL CONTENT NOT GUARANTEED"
        except BaseException as exc:
            report["error"]=str(exc)
            raise
        finally:
            if not save_json_file(manifest,report):
                raise OSError(f"Could not save recovery manifest to {manifest}")
        return {"folder":str(folder),"manifest":str(manifest),"count":len(report["files"]),"bytes":written}

def _nearest_existing_path(path):
    p=Path(path).expanduser().resolve(strict=False)
    while not p.exists() and p!=p.parent:
        p=p.parent
    if not p.exists():raise RuntimeError("Could not resolve the storage location of a safety-critical path.")
    return p

def path_disk_numbers(path):
    """Resolve actual volume extents, including mount folders and multi-extent volumes.

    No fallback to drive-letter comparison: unknown mappings fail closed.
    """
    if os.name!="nt" or kernel32 is None:
        raise RuntimeError("Windows volume-to-physical-disk resolution is unavailable on this platform.")
    p=str(_nearest_existing_path(path))
    if p.startswith("\\\\"):
        raise RuntimeError("Network/device namespace paths cannot be used for this local-disk safety check.")
    k=kernel32
    k.GetVolumePathNameW.argtypes=[wintypes.LPCWSTR,wintypes.LPWSTR,wintypes.DWORD]
    k.GetVolumePathNameW.restype=wintypes.BOOL
    k.GetVolumeNameForVolumeMountPointW.argtypes=[wintypes.LPCWSTR,wintypes.LPWSTR,wintypes.DWORD]
    k.GetVolumeNameForVolumeMountPointW.restype=wintypes.BOOL
    root=ctypes.create_unicode_buffer(32768);volume=ctypes.create_unicode_buffer(1024)
    if not k.GetVolumePathNameW(p,root,len(root)):
        raise win_error("Could not resolve volume root for safety check")
    if not k.GetVolumeNameForVolumeMountPointW(root.value,volume,len(volume)):
        raise win_error("Could not resolve volume GUID for safety check")
    with open_handle(volume.value.rstrip("\\"),GENERIC_READ,FILE_SHARE_READ|FILE_SHARE_WRITE) as h:
        buf=ctypes.create_string_buffer(65536);got=wintypes.DWORD()
        if not k.DeviceIoControl(h.h,0x00560000,None,0,buf,len(buf),ctypes.byref(got),None):
            raise win_error("Could not query physical volume extents")
        if got.value<8:raise RuntimeError("Truncated volume extents result.")
        count=struct.unpack_from("<I",buf.raw,0)[0]
        if not (1<=count<=1024) or 8+24*count>got.value:
            raise RuntimeError("Invalid volume extents geometry.")
        return {struct.unpack_from("<I",buf.raw,8+24*i)[0] for i in range(count)}

def guard_paths_outside_target(number, *paths):
    for p in paths:
        if int(number) in path_disk_numbers(p):
            raise RuntimeError(f"Safety guard: this path is on the target physical disk: {p}. Choose a different physical device.")

def guard_runtime_outside_target(number, *extra):
    guard_paths_outside_target(number, __file__, sys.executable, APP_STATE_DIR, LOG_PATH, *extra)

def _assert_open_disk_geometry(handle, number, size):
    """Confirm the already-open handle refers to the selected disk number/capacity."""
    for code,minimum in ((0x002D1080,12),(0x0007405C,8)):
        data=ctypes.create_string_buffer(64);got=wintypes.DWORD()
        if not kernel32.DeviceIoControl(handle,code,None,0,data,len(data),ctypes.byref(got),None):
            raise win_error("Could not verify open physical-drive handle")
        if got.value<minimum:raise RuntimeError("Short physical-drive identity response.")
        if code==0x002D1080 and struct.unpack_from("<I",data.raw,4)[0]!=int(number):
            raise RuntimeError("Open handle disk number differs from confirmed device.")
        if code==0x0007405C and struct.unpack_from("<q",data.raw,0)[0]!=int(size):
            raise RuntimeError("Open handle capacity differs from confirmed device.")

def strict_target_volume_paths(number):
    d=safe_removable_disk(number)
    if int(d.get("NumberOfPartitions") or 0)==0:
        return []
    vals=ps_json(rf'''$ErrorActionPreference='Stop'
@(Get-Partition -DiskNumber {int(number)} -ErrorAction Stop | ForEach-Object {{
 [PSCustomObject]@{{Number=[int]$_.PartitionNumber;Paths=@($_.AccessPaths)}}
}}) | ConvertTo-Json -Depth 5 -Compress''')
    if len(vals)!=int(d.get("NumberOfPartitions") or 0):
        raise RuntimeError("Cannot prove that all target partitions were enumerated; operation refused.")
    paths=[]
    for row in vals:
        options=row.get("Paths") or []
        if isinstance(options,str):options=[options]
        valid=[volume_device_path(x) for x in options if volume_device_path(x)]
        guids=[v for v in valid if v.startswith("\\\\?\\Volume{")]
        if not valid:raise RuntimeError(f"Partition {row.get('Number')} has no lockable volume path. No destructive write started.")
        chosen=(guids or valid)[0]
        if chosen.casefold() not in [x.casefold() for x in paths]:paths.append(chosen)
    return paths

def lock_target_volumes(number):
    """Keep all lock handles alive until the caller explicitly releases them."""
    handles=[]
    try:
        for path in strict_target_volume_paths(number):
            h=open_handle(path,GENERIC_READ|GENERIC_WRITE,FILE_SHARE_READ|FILE_SHARE_WRITE)
            handles.append(h)
            if not ioctl(h.h,FSCTL_LOCK_VOLUME):
                raise win_error("Could not lock target volume; close applications using the device")
            if not kernel32.FlushFileBuffers(h.h):raise win_error("Target volume cache flush failed")
            if not ioctl(h.h,FSCTL_DISMOUNT_VOLUME):raise win_error("Target volume dismount failed")
        return handles
    except BaseException:
        unlock_volumes(handles)
        raise

def overwrite_and_verify(read_at,write_at,flush,total,checkpoint=None,progress=None,block_size=CHUNK):
    """Media-independent logical overwrite core, tested only on disposable file/memory fixtures.

    Caller must enforce authorization, physical identity, exclusive volume locks,
    sector alignment and a report destination outside the target before entering.
    """
    total=int(total);block_size=int(block_size)
    if total<=0 or not 1<=block_size<=64*1024**2:raise ValueError("Invalid overwrite geometry.")
    zero=b"\0"*min(total,block_size);done=0;expected=hashlib.sha256()
    while done<total:
        _rec_check(checkpoint);n=min(len(zero),total-done);data=zero[:n]
        result=write_at(done,data)
        if result is not None and result!=n:raise OSError(f"Short overwrite at byte {done}.")
        expected.update(data);done+=n
        if progress:progress("OVERWRITE",done,total)
    _rec_check(checkpoint)
    if flush() is False:raise OSError("Overwrite cache flush failed.")
    verified=0;actual=hashlib.sha256()
    while verified<total:
        _rec_check(checkpoint);n=min(len(zero),total-verified);data=read_at(verified,n)
        if len(data)!=n:raise OSError(f"Readback ended early at byte {verified}.")
        if data!=zero[:n]:
            offset=verified+next(i for i,b in enumerate(data) if b)
            raise OSError(f"Logical erase verification failed at byte {offset}. No successful erase result issued.")
        actual.update(data);verified+=n
        if progress:progress("READBACK",verified,total)
    return {"written_bytes":done,"verified_bytes":verified,"readback_sha256":actual.hexdigest(),
            "expected_sha256":expected.hexdigest(),"logical_verification_passed":True}

def logical_erase_disk(expected,report_path,checkpoint=None,progress=None):
    """Destructive. GUI has already required a typed disk-bound erase phrase.

    There is no unattended command-line erase entry point and no automatic retry
    onto another disk. All failures and cancellations produce INCOMPLETE reports.
    """
    number=int(expected["Number"]);report_path=Path(report_path).resolve(strict=False)
    if os.name!="nt":raise RuntimeError("Physical-drive erase requires Windows; it cannot run on this platform.")
    current=safe_removable_disk(number,expected)
    if not any(str(current.get(k) or "").strip() for k in ("UniqueId","SerialNumber")):
        raise RuntimeError("Verified erase requires a stable device UniqueId or serial number.")
    if current.get("IsReadOnly") or current.get("IsOffline"):
        raise RuntimeError("Target must already be online and writable. Erase does not silently change media attributes.")
    total=int(current["Size"]);sector=int(current.get("LogicalSectorSize") or 512)
    if sector not in (512,1024,2048,4096) or total%sector or CHUNK%sector:
        raise RuntimeError("Unsupported or unaligned target geometry.")
    guard_runtime_outside_target(number,report_path)
    if not report_path.parent.is_dir() or report_path.exists():
        raise RuntimeError("Choose a new report filename in an existing folder outside the target disk.")
    report={"schema":1,"application":APP_NAME,"operation":"VERIFIED LOGICAL OVERWRITE",
            "status":"INCOMPLETE","device":current,"start_utc":time.strftime("%Y-%m-%dT%H:%M:%SZ",time.gmtime()),
            "written_bytes":0,"verified_bytes":0,"scope":forensic_delete_capabilities(),
            "hardware_purge_claimed":False,"certificate":False}
    # Refuse writes if the audit destination cannot be opened and committed first.
    with report_path.open("x",encoding="utf-8") as f:
        json.dump(report,f,indent=2);f.flush();os.fsync(f.fileno())
    handles=[];raw=None;last_save=[0.0]
    try:
        _rec_check(checkpoint);safe_removable_disk(number,expected)
        handles=lock_target_volumes(number)
        raw=open_handle(r"\\.\PhysicalDrive{}".format(number),GENERIC_READ|GENERIC_WRITE,
                        FILE_SHARE_READ|FILE_SHARE_WRITE,FILE_ATTRIBUTE_NORMAL|FILE_FLAG_WRITE_THROUGH)
        _assert_open_disk_geometry(raw.h,number,total)
        safe_removable_disk(number,expected)
        def read_at(off,n):raw_seek(raw.h,off);return raw_read_exact(raw.h,n)
        def write_at(off,data):raw_seek(raw.h,off);raw_write(raw.h,data);return len(data)
        def flush():
            if not kernel32.FlushFileBuffers(raw.h):raise win_error("Erase flush failed")
            return True
        def tick(phase,done,n):
            report["written_bytes" if phase=="OVERWRITE" else "verified_bytes"]=done
            if time.monotonic()-last_save[0]>=1:
                if not save_json_file(report_path,report):raise OSError("Audit checkpoint could not be saved; stopping erase.")
                last_save[0]=time.monotonic()
            if progress:progress(phase,done,n)
        result=overwrite_and_verify(read_at,write_at,flush,total,checkpoint,tick)
        _assert_open_disk_geometry(raw.h,number,total)
        report.update(result);report["status"]="VERIFIED LOGICAL OVERWRITE COMPLETE / NOT A HARDWARE PURGE"
    except BaseException as exc:
        report["error"]=str(exc)
        if raw:
            try:kernel32.FlushFileBuffers(raw.h)
            except Exception:pass
        raise
    finally:
        if raw:raw.close()
        unlock_volumes(handles)
        report["end_utc"]=time.strftime("%Y-%m-%dT%H:%M:%SZ",time.gmtime())
        if not save_json_file(report_path,report):raise OSError("Final erase audit report could not be saved; do not treat this operation as certified.")
    # Do not initialize, format or mount the erased device; that would alter the verified zero result.
    return {"report":str(report_path),**report}

def _gpt_header(reader,lba,sector=512):
    if sector not in (512,4096) or lba<1 or (lba+1)*sector>reader.size:
        raise ValueError("GPT header outside device bounds.")
    hdr=reader.read_at(lba*sector,sector)
    if len(hdr)!=sector or hdr[:8]!=b"EFI PART":raise ValueError("GPT signature missing.")
    hs=struct.unpack_from("<I",hdr,12)[0]
    if not 92<=hs<=sector:raise ValueError("Invalid GPT header size.")
    h=bytearray(hdr[:hs]);stored=struct.unpack_from("<I",h,16)[0];struct.pack_into("<I",h,16,0)
    if crc32(h)!=stored:raise ValueError("GPT header CRC mismatch.")
    current,backup,first,last=struct.unpack_from("<QQQQ",hdr,24)
    entries_lba,count,esize,ecrc=struct.unpack_from("<QIII",hdr,72)
    if current!=lba or backup==current or backup<1 or (backup+1)*sector>reader.size:
        raise ValueError("Invalid GPT current/backup LBA.")
    if not (0<count<=4096 and 128<=esize<=1024 and esize%8==0):raise ValueError("Invalid GPT entry geometry.")
    length=count*esize;span=align_up(length,sector)
    if entries_lba<2 or (entries_lba*sector+span)>reader.size or first>last or first<2 or (last+1)*sector>reader.size:
        raise ValueError("GPT geometry exceeds image/device bounds.")
    entries=reader.read_at(entries_lba*sector,length)
    if len(entries)!=length or crc32(entries)!=ecrc:raise ValueError("GPT entry array CRC mismatch.")
    return {"header":hdr,"header_size":hs,"current":current,"backup":backup,"first":first,"last":last,
            "entries_lba":entries_lba,"count":count,"esize":esize,"entries":entries,"entries_span":span}

def _gpt_snapshot(reader,sector=512):
    p=_gpt_header(reader,1,sector);b=_gpt_header(reader,p["backup"],sector)
    if b["backup"]!=1 or p["entries"]!=b["entries"] or p["first"]!=b["first"] or p["last"]!=b["last"] or p["header"][56:72]!=b["header"][56:72]:
        raise ValueError("Primary/backup GPT disagree.")
    if p["last"]>=b["entries_lba"] or b["entries_lba"]*sector+b["entries_span"]>b["current"]*sector:
        raise ValueError("GPT backup overlaps usable sectors.")
    if sector==512 and not parse_gpt(reader).get("valid"):
        raise ValueError("GPT partitions are invalid.")
    return p,b

def _chrome_surface(master,width,height,accent="#28CCFF",disabled=False,pressed=False,hover=False,neutral=False):
    root=master.winfo_toplevel();cache=getattr(root,"_chrome_image_cache",None)
    if cache is None:cache={};root._chrome_image_cache=cache
    bg=master._parent_bg if hasattr(master,"_parent_bg") else master.cget("bg")
    key=(width,height,accent,disabled,pressed,hover,neutral,bg)
    if key in cache:return cache[key]
    requested_width=max(16,int(width));height=max(16,int(height))
    textures=getattr(root,"_chrome_texture_cache",None)
    if textures is None:textures={};root._chrome_texture_cache=textures
    texture_key=(height,accent,disabled,pressed,hover,neutral,bg)
    if texture_key not in textures:
        width=96; pixels=bytearray(width*height*3)
        back=hex_rgb(bg);light=hex_rgb(accent)
        stops=[(0,(72,81,89)),(.045,(242,249,255)),(.13,(166,179,190)),(.47,(70,78,88)),(.64,(40,44,50)),(.86,(165,181,194)),(1,(48,55,65))]
        def mix(a,b,t):return tuple(int(a[i]+(b[i]-a[i])*max(0,min(1,t))) for i in range(3))
        def gradient(t):
            for (a,c),(b,d) in zip(stops,stops[1:]):
                if t<=b:return mix(c,d,(t-a)/(b-a))
            return stops[-1][1]
        x1,y1,x2,y2=2,2,width-3,height-5
        cx,cy=(x1+x2)/2,(y1+y2)/2;hx,hy=(x2-x1)/2,(y2-y1)/2;radius=min(hy*.85,25)
        for y in range(height):
            t=max(0,min(1,(y-y1)/max(1,y2-y1)));metal=gradient(t)
            for x in range(width):
                qx=abs(x-cx)-(hx-radius);qy=abs(y-cy)-(hy-radius)
                distance=math.hypot(max(qx,0),max(qy,0))+min(max(qx,qy),0)-radius
                depth=-distance
                if depth<0:
                    col=mix(back,(0,0,0),.7*max(0,1-(distance-1)/4)) if y>cy else back
                elif depth<1.2:col=(36,42,49)
                elif depth<4.1:
                    col=metal
                    if x<width*.76 and y<7:col=mix(col,(255,255,255),.25)
                    if width*.79<x<width*.82 and y<10:col=(215,227,237)
                elif depth<5.5:col=(4,8,13)
                elif depth<7:
                    col=mix((3,63,90),light,.68 if hover else .40)
                else:
                    blue=mix((8,116,166),(1,37,65),t)
                    row=int(round((y-9)/7));xx=x-9-(row%2)*4;colnum=round(xx/8)
                    dx=abs(xx-colnum*8);dy=abs(y-9-row*7)
                    inside=max(dx*.866+dy*.5,dy)<3.25
                    if inside:blue=mix(blue,(42,171,218),.20 if y<height*.55 else .10)
                    else:blue=mix(blue,(0,18,35),.23)
                    # Broad sloping highlight and a darker central reading bed, like the reference.
                    if y<height*.33:blue=mix(blue,(188,240,255),.17)
                    if height*.36<y<height*.78:blue=mix(blue,(0,20,38),.16)
                    if y>height*.73 and depth<8.1:blue=mix(blue,(240,251,255),.68)
                    if hover:blue=mix(blue,light,.10)
                    if neutral:blue=mix(blue,(45,51,57),.77)
                    col=blue
                if disabled:
                    grey=int(col[0]*.21+col[1]*.72+col[2]*.07);col=mix(col,(grey,grey,grey),.9);col=mix(col,back,.35)
                if pressed:col=mix(col,(0,0,0),.20)
                if -1<distance<1:col=mix(col,back,(distance+1)*.35)
                idx=(y*width+x)*3;pixels[idx:idx+3]=bytes(max(0,min(255,int(v))) for v in col)
        if len(textures)>=128:textures.pop(next(iter(textures)))
        textures[texture_key]=bytes(pixels)
    texture=textures[texture_key];width=requested_width
    rows=[];side=min(32,width//2);middle=max(0,width-2*side)
    for row in range(height):
        line=texture[row*96*3:(row+1)*96*3]
        center=line[32*3:64*3]
        rows.append(line[:side*3]+(center*((middle+31)//32))[:middle*3]+line[(96-side)*3:])
    pixels=b"".join(rows)
    img=tk.PhotoImage(master=master,data=f"P6\n{width} {height}\n255\n".encode()+bytes(pixels),format="PPM")
    if len(cache)>=384:cache.pop(next(iter(cache)))
    cache[key]=img
    return img

def _chrome_icon(canvas,kind,x,y,size,color):
    """Small vector pictograms; no platform-dependent emoji font required."""
    s=size/24
    def xy(points):return [v for p in points for v in (x+(p[0]-12)*s,y+(p[1]-12)*s)]
    def line(points,**kw):return canvas.create_line(*xy(points),fill=color,width=max(1.4,1.7*s),capstyle="round",joinstyle="round",**kw)
    def poly(points,**kw):return canvas.create_polygon(*xy(points),fill="#031925",outline=color,width=max(1.2,1.4*s),**kw)
    if kind=="flash":poly([(14,2),(4,14),(11,14),(9,22),(21,9),(13,9)])
    elif kind=="eject":
        poly([(3,14),(12,3),(21,14)]);line([(4,19),(20,19)])
    elif kind=="pause":line([(8,4),(8,20)]);line([(16,4),(16,20)])
    elif kind=="resume":poly([(6,3),(21,12),(6,21)])
    elif kind=="stop":poly([(5,5),(19,5),(19,19),(5,19)])
    elif kind=="search":
        canvas.create_oval(x-9*s,y-9*s,x+4*s,y+4*s,outline=color,width=max(1.4,2*s));line([(16,16),(22,22)])
    elif kind=="gear":
        pts=[]
        for n in range(48):
            a=n*math.pi/24;r=10 if n%6 in (1,2,3,4) else 7
            pts.append((12+r*math.cos(a),12+r*math.sin(a)))
        poly(pts);canvas.create_oval(x-4*s,y-4*s,x+4*s,y+4*s,outline=color,width=1.7*s)
    elif kind=="lock":
        poly([(5,10),(19,10),(19,22),(5,22)])
        canvas.create_arc(x-5*s,y-11*s,x+5*s,y+2*s,start=0,extent=180,style="arc",outline=color,width=1.8*s)
        line([(12,14),(12,18)])
    elif kind=="erase":
        poly([(12,2),(23,21),(1,21)]);line([(12,8),(12,14)]);line([(12,17),(12,18)])
    elif kind=="refresh":
        canvas.create_arc(x-9*s,y-9*s,x+9*s,y+9*s,start=40,extent=285,style="arc",outline=color,width=1.8*s)
        poly([(19,2),(21,10),(13,7)])
    elif kind=="folder":poly([(2,6),(9,6),(12,9),(23,9),(20,21),(2,21)])
    elif kind=="disk":
        poly([(3,4),(21,4),(21,21),(3,21)]);line([(4,15),(20,15)]);line([(7,18),(9,18)])
    elif kind=="check":line([(3,12),(9,19),(21,5)])
    elif kind=="help":
        canvas.create_text(x,y,text="?",font=("Arial",max(8,int(size*.65)),"bold"),fill=color)
    else:
        poly([(5,2),(15,2),(20,7),(20,22),(5,22)]);line([(15,2),(15,8),(20,8)]);line([(8,13),(16,13)]);line([(8,17),(15,17)])

def _button_icon(text):
    text=text.lower()
    if "undelete" in text or "recover selected" in text or "recover all" in text: return "search"
    for keys,kind in [(("resume",),"resume"),(("pause",),"pause"),(("stop","cancel"),"stop"),
                      (("erase","overwrite","delete","sanitize"),"erase"),(("eject",),"eject"),
                      (("settings","themes"),"gear"),(("flash","clone"),"flash"),
                      (("rescan","refresh","reclaim","reset"),"refresh"),
                      (("scan","diagnostic","undelete","recover"),"search"),
                      (("open","folder","select image","browse"),"folder"),
                      (("disk","partition","data","mount","letter","online","writable"),"disk"),
                      (("verify","test","continue"),"check"),(("help",),"help")]:
        if any(k in text for k in keys):return kind
    return "file"

class ChromeToggle(tk.Frame):
    """Keyboard-operable glass switch that shares its BooleanVar with all views."""
    def __init__(self,parent,text,variable,command=None,style=None,**kwargs):
        super().__init__(parent,bg=parent.cget("bg"),**kwargs)
        self.variable=variable;self.command=command;self._state="normal";self._parent_bg=self.cget("bg")
        self.knob=tk.Canvas(self,width=54,height=31,bg=self.cget("bg"),highlightthickness=0,takefocus=1,cursor="hand2")
        self.knob.pack(side="left");self.label=tk.Label(self,text=text,bg=self.cget("bg"),fg="#DCEAF4",font=("Segoe UI",9))
        self.label.pack(side="left",padx=(3,0))
        for widget in (self.knob,self.label):widget.bind("<ButtonRelease-1>",self.invoke)
        self.knob.bind("<KeyRelease-space>",self.invoke);self.knob.bind("<KeyRelease-Return>",self.invoke)
        self.knob.bind("<FocusIn>",self._draw);self.knob.bind("<FocusOut>",self._draw)
        self.trace=variable.trace_add("write",lambda *_:self._draw());self.bind("<Destroy>",self._cleanup,add="+");self._draw()
    def _draw(self,*_):
        self.knob.delete("all");on=bool(self.variable.get());disabled=self._state=="disabled"
        _rounded_rect(self.knob,2,4,52,28,12,fill="#161C22",outline="#A1ABB4",width=2)
        if on:_rounded_rect(self.knob,5,7,49,25,9,fill="#027FB0" if not disabled else "#454F59",outline="")
        x=39 if on else 15
        self.knob.create_oval(x-10,6,x+10,26,fill="#0677A9" if on else "#454E56",outline="#AEEBFF" if not disabled else "#66717C",width=2)
        self.knob.create_line(x-4,10,x+4,10,fill="#D3F6FF",width=2)
        if self.knob.focus_get() is self.knob and not disabled:
            self.knob.create_rectangle(0,1,53,30,outline="#45DCFF")
        self.label.configure(fg="#81909A" if disabled else "#DCEAF4")
    def invoke(self,_=None):
        if self._state!="disabled":
            self.variable.set(not self.variable.get())
            if self.command:self.command()
        return "break"
    def configure(self,cnf=None,**kwargs):
        if isinstance(cnf,dict):kwargs.update(cnf)
        if "state" in kwargs:
            self._state=kwargs.pop("state");self.knob.configure(takefocus=0 if self._state=="disabled" else 1);self._draw()
        if kwargs:return super().configure(**kwargs)
    config=configure
    def cget(self,key):
        if key=="state":return self._state
        return super().cget(key)
    def _cleanup(self,event=None):
        if event is not None and event.widget is not self:return
        try:self.variable.trace_remove("write",self.trace)
        except Exception:pass

# ---------------------------------------------------------------------------
# NEXUS UI
# ---------------------------------------------------------------------------

def _rounded_rect(canvas, x1, y1, x2, y2, radius=14, **kwargs):
    r = max(2, min(int(radius), int((x2-x1)/2), int((y2-y1)/2)))
    points = [
        x1+r, y1, x2-r, y1, x2, y1, x2, y1+r,
        x2, y2-r, x2, y2, x2-r, y2, x1+r, y2,
        x1, y2, x1, y2-r, x1, y1+r, x1, y1,
    ]
    return canvas.create_polygon(points, smooth=True, splinesteps=24, **kwargs)


class RoundedButton(tk.Canvas):
    """Chrome capsule with honeycomb glass, explicit states and single-shot keyboard activation."""
    def __init__(self,parent,text,command,bg,hover,fg,width_chars=None,height=50,radius=20,
                 disabled_fg="#9BA5AD",accent=None,font=None):
        self._parent_bg=parent.cget("bg");self._text=str(text);self._command=command
        self._bg=bg;self._hover=hover;self._fg=fg;self._accent=accent or "#2AD5FF"
        self._font=font or ("Segoe UI",9,"bold");self._disabled_fg=disabled_fg
        self._state="normal";self._radius=radius;self._hovered=False;self._pressed=False;self._key_down=False
        self._nexus_normal_bg=bg;self._nexus_hover_bg=hover;self._selected=False
        self._font_obj=tkfont.Font(root=parent,font=self._font)
        px=max(96,self._font_obj.measure(self._text)+76,(width_chars or 0)*6+48)
        h=max(height,self._font_obj.metrics("linespace")+27)
        super().__init__(parent,width=px,height=h,bg=self._parent_bg,highlightthickness=0,bd=0,cursor="hand2",takefocus=1)
        self.bind("<Configure>",self._draw);self.bind("<Enter>",self._enter);self.bind("<Leave>",self._leave)
        self.bind("<ButtonPress-1>",self._press);self.bind("<ButtonRelease-1>",self._release)
        for key in ("space","Return"):
            self.bind("<KeyPress-"+key+">",self._keyboard_press)
            self.bind("<KeyRelease-"+key+">",self._keyboard_release)
        self.bind("<FocusIn>",self._draw);self.bind("<FocusOut>",self._focus_out)
        self._draw()

    def _draw(self,*_):
        if not self.winfo_exists():return
        self.delete("all")
        w=self.winfo_width();h=self.winfo_height()
        if w<=1:w=int(tk.Canvas.cget(self,"width"))
        if h<=1:h=int(tk.Canvas.cget(self,"height"))
        disabled=self._state=="disabled"
        self._surface=_chrome_surface(self,w,h,self._accent,disabled,self._pressed,self._hovered,
                                      neutral=getattr(self,"_is_nav",False) and not self._selected)
        self.create_image(0,0,image=self._surface,anchor="nw")
        color=self._disabled_fg if disabled else "#F4FCFF"
        iconcolor=self._disabled_fg if disabled else self._accent
        icon=_button_icon(self._text);size=min(25,h*.47);shift=1 if self._pressed else 0
        _chrome_icon(self,icon,26,h/2-1+shift,size,iconcolor)
        label=self._text.strip();available=max(1,w-64)
        while label and self._font_obj.measure(label)>available:
            label=label[:-2]+"…" if not label.endswith("…") else label[:-2]+"…"
            if len(label)<=1:break
        self.create_text(48,h/2+shift,text=label,anchor="w",fill="#00131E",font=self._font)
        self.create_text(47,h/2-1+shift,text=label,anchor="w",fill=color,font=self._font,tags="label")
        if self.focus_get() is self and not disabled:
            _rounded_rect(self,0,0,w-1,h-3,min(22,h/2-2),fill="",outline="#81E9FF",width=1)

    def _enter(self,_=None):
        if self._state!="disabled":self._hovered=True;self._draw()
    def _leave(self,_=None):
        self._hovered=False;self._pressed=False;self._draw()
    def _focus_out(self,_=None):
        self._pressed=False;self._key_down=False;self._draw()
    def _press(self,_=None):
        if self._state!="disabled":self.focus_set();self._pressed=True;self._draw()
    def _release(self,event=None):
        was=self._pressed;self._pressed=False;self._draw()
        if was and (event is None or 0<=event.x<self.winfo_width() and 0<=event.y<self.winfo_height()):
            return self.invoke()
    def _keyboard_press(self,_=None):
        if self._state!="disabled" and not self._key_down:self._key_down=True;self._pressed=True;self._draw()
        return "break"
    def _keyboard_release(self,_=None):
        was=self._key_down;self._key_down=False;self._pressed=False;self._draw()
        if was:self.invoke()
        return "break"
    def _keyboard_activate(self,_=None):
        return self.invoke()
    def invoke(self):
        if self._state!="disabled" and callable(self._command):return self._command()
    def configure(self,cnf=None,**kwargs):
        if isinstance(cnf,dict):kwargs={**cnf,**kwargs}
        if not kwargs and cnf is None:return super().configure()
        if isinstance(cnf,str):return super().configure(cnf)
        for key in ("state","text","bg","fg","command","font","selected"):
            if key not in kwargs:continue
            value=kwargs.pop(key)
            if key=="selected":self._selected=bool(value)
            else:setattr(self,"_"+key,value)
            if key=="bg":self._nexus_normal_bg=value
            if key=="font":self._font_obj.configure(**tkfont.Font(root=self,font=value).actual())
            if key=="state":
                self._pressed=False;self._key_down=False
                super().configure(cursor="arrow" if value=="disabled" else "hand2",takefocus=0 if value=="disabled" else 1)
        if kwargs:super().configure(**kwargs)
        self._draw()
    config=configure
    def cget(self,key):
        if key in ("state","text","bg","fg","command","font","selected"):return getattr(self,"_"+key)
        return super().cget(key)
    __getitem__=cget


class RoundedPanel(tk.Canvas):
    """Hyperglass card surface with brighter edges, richer depth and a cleaner glass sheen."""
    def __init__(self, parent, fill, border, radius=20, padding=1):
        parent_bg = parent.cget("bg") if hasattr(parent, "cget") else "#000000"
        super().__init__(parent, bg=parent_bg, highlightthickness=0, bd=0, height=100)
        self.fill = fill
        self.border = border
        self.radius = radius
        self.padding = padding
        self.content = tk.Frame(self, bg=fill)
        self._window = self.create_window((18, 16), window=self.content, anchor="nw")
        self.bind("<Configure>", self._resize)
        self.content.bind("<Configure>", self._content_resize)

    def _content_resize(self, _event=None):
        req = max(48, self.content.winfo_reqheight() + 32)
        try:
            if abs(int(float(self.cget("height"))) - req) > 2:
                self.configure(height=req)
        except Exception:
            pass
        self._draw()

    def _resize(self, event=None):
        w = event.width if event else self.winfo_width()
        try:
            self.itemconfigure(self._window, width=max(20, w-36))
        except Exception:
            pass
        self._draw()

    def _draw(self):
        self.delete("panelbg")
        w = max(4, self.winfo_width())
        h = max(4, self.winfo_height())
        shadow = _rounded_rect(self, 8, 11, w-1, h-1, self.radius+2, fill=blend_hex(self.fill, "#000000", 0.64), outline="", tags="panelbg")
        glow = _rounded_rect(self, 5, 7, w-4, h-4, self.radius+1, fill=blend_hex(self.border, self.fill, 0.66), outline="", tags="panelbg")
        base = _rounded_rect(self, 1, 1, w-7, h-7, self.radius, fill=self.fill, outline=blend_hex(self.border, "#FFFFFF", 0.07), width=1, tags="panelbg")
        inner = _rounded_rect(self, 3, 3, w-9, h-9, max(6, self.radius-2), fill="", outline=blend_hex(self.border, "#FFFFFF", 0.16), width=1, tags="panelbg")
        sheen = _rounded_rect(self, 5, 5, w-11, max(20, int(h*0.22)), max(6, self.radius-8), fill=blend_hex(self.fill, "#FFFFFF", 0.045), outline="", tags="panelbg")
        accent = self.create_line(self.radius+8, 6, max(self.radius+8, w-self.radius-14), 6, fill=blend_hex(self.border, "#FFFFFF", 0.28), width=1, tags="panelbg")
        for item in (shadow, glow, base, inner, sheen, accent):
            self.tag_lower(item)
        self.tag_raise(self._window)


class GradientBar(tk.Canvas):
    def __init__(self, parent, start, end, height=3):
        parent_bg = parent.cget("bg") if hasattr(parent, "cget") else "#000000"
        super().__init__(parent, height=height, bg=parent_bg, highlightthickness=0, bd=0)
        self.start, self.end = start, end
        self.bind("<Configure>", self._paint)

    def _paint(self, event=None):
        self.delete("all")
        w = max(1, event.width if event else self.winfo_width())
        h = max(1, event.height if event else self.winfo_height())
        steps = min(320, w)
        for i in range(steps):
            x1 = int(i*w/steps); x2 = int((i+1)*w/steps)+1
            self.create_rectangle(x1, 0, x2, h, outline="", fill=blend_hex(self.start, self.end, i/max(1, steps-1)))


class HudProgressBar(tk.Canvas):
    def __init__(self, parent, variable, start, end, trough, height=18, radius=9):
        parent_bg = parent.cget("bg") if hasattr(parent, "cget") else "#000000"
        super().__init__(parent, height=height, bg=parent_bg, highlightthickness=0, bd=0)
        self.variable = variable; self.start = start; self.end = end; self.trough = trough; self.radius = radius
        self.bind("<Configure>", lambda _e: self._paint())
        self._trace_id = None
        try: self._trace_id = self.variable.trace_add("write", lambda *_: self._paint())
        except Exception: pass
        self.bind("<Destroy>", self._cleanup, add="+")
        self._paint()

    def _cleanup(self, _event=None):
        if self._trace_id:
            try: self.variable.trace_remove("write", self._trace_id)
            except Exception: pass
            self._trace_id = None

    def _paint(self):
        self.delete("all")
        w = max(8, self.winfo_width()); h = max(8, self.winfo_height())
        _rounded_rect(self, 1, 2, w-1, h-1, self.radius, fill=blend_hex(self.trough, "#000000", 0.12), outline=blend_hex(self.trough, "#FFFFFF", 0.11), width=1)
        _rounded_rect(self, 3, 4, w-3, h-3, max(4, self.radius-2), fill=self.trough, outline="")
        try: pct = max(0.0, min(100.0, float(self.variable.get())))
        except Exception: pct = 0.0
        fill_w = int((w-8) * pct / 100.0)
        if fill_w > 3:
            steps = max(8, min(160, fill_w//2))
            for i in range(steps):
                x1 = 4 + int(i*fill_w/steps); x2 = 4 + int((i+1)*fill_w/steps)+1
                c = blend_hex(self.start, self.end, i/max(1, steps-1))
                self.create_rectangle(x1, 5, min(w-4, x2), h-4, outline="", fill=c)
            right = min(w-4, 4+fill_w)
            self.create_line(9, 6, max(9, right-8), 6, fill=blend_hex(self.start, "#FFFFFF", 0.62), width=1)
            self.create_oval(max(4, right-5), max(4, h/2-5), min(w-3, right+5), min(h-3, h/2+5), outline="", fill=blend_hex(self.end, "#FFFFFF", 0.15))
            self.create_oval(max(4, right-2), max(4, h/2-2), min(w-3, right+2), min(h-3, h/2+2), outline="", fill="#FFFFFF")


class HudDial(tk.Canvas):
    def __init__(self, parent, variable, accent, bg, text="AEGIS", size=76, ui_font="Segoe UI", mono_font="Consolas"):
        super().__init__(parent, width=size, height=size, bg=bg, highlightthickness=0, bd=0)
        self.variable=variable; self.accent=accent; self.bg=bg; self.label=text; self.size=size
        self.ui_font=ui_font; self.mono_font=mono_font
        self._trace_id = None
        try: self._trace_id = self.variable.trace_add("write", lambda *_: self._draw())
        except Exception: pass
        self.bind("<Configure>", lambda _e: self._draw())
        self.bind("<Destroy>", self._cleanup, add="+")
        self._draw()

    def _cleanup(self, _event=None):
        if self._trace_id:
            try: self.variable.trace_remove("write", self._trace_id)
            except Exception: pass
            self._trace_id = None

    def _draw(self):
        self.delete("all"); s=self.size; c=s/2; pad=7
        self.create_oval(pad+2, pad+3, s-pad+2, s-pad+3, outline=blend_hex(self.bg, "#000000", 0.66), width=4)
        self.create_oval(pad, pad, s-pad, s-pad, outline=blend_hex(self.accent, self.bg, 0.52), width=2)
        self.create_oval(pad+4, pad+4, s-pad-4, s-pad-4, outline=blend_hex(self.accent, self.bg, 0.76), width=1)
        self.create_oval(pad+9, pad+9, s-pad-9, s-pad-9, outline=blend_hex(self.accent, "#FFFFFF", 0.08), width=1)
        try: pct=max(0.0,min(100.0,float(self.variable.get())))
        except Exception: pct=0.0
        self.create_arc(pad, pad, s-pad, s-pad, start=90, extent=-max(2.5, 3.6*pct), style="arc", outline=self.accent, width=4)
        for a in range(0,360,30):
            r=math.radians(a); r1=s*0.405; r2=s*0.435
            self.create_line(c+math.cos(r)*r1,c+math.sin(r)*r1,c+math.cos(r)*r2,c+math.sin(r)*r2,
                             fill=blend_hex(self.accent,self.bg,0.48),width=1)
        self.create_text(c, c-5, text=f"{pct:03.0f}", fill=blend_hex("#FFFFFF", self.accent, 0.08), font=(self.mono_font, 11, "bold"))
        self.create_text(c, c+12, text=self.label, fill=blend_hex(self.accent, "#FFFFFF", 0.08), font=(self.ui_font, 6, "bold"))



def centered_dialog_bounds(width, height, work_area):
    """Absolute desktop coordinates; work areas may have negative origins."""
    left, top, right, bottom = (int(v) for v in work_area)
    width = min(max(1, int(width)), max(1, right-left))
    height = min(max(1, int(height)), max(1, bottom-top))
    return width, height, left + (right-left-width)//2, top + (bottom-top-height)//2


def show_centered_dialog(dialog, parent):
    """Center on the parent's monitor work area, after measuring content/DPI."""
    dialog.update_idletasks()
    work = (0, 0, parent.winfo_screenwidth(), parent.winfo_screenheight())
    user32 = None
    hwnd = None
    try:
        if os.name == 'nt':
            user32 = ctypes.WinDLL('user32', use_last_error=True)
            user32.GetAncestor.argtypes = [wintypes.HWND, wintypes.UINT]
            user32.GetAncestor.restype = wintypes.HWND
            user32.MonitorFromWindow.argtypes = [wintypes.HWND, wintypes.DWORD]
            user32.MonitorFromWindow.restype = wintypes.HANDLE
            class MONITORINFO(ctypes.Structure):
                _fields_ = [('cbSize', wintypes.DWORD), ('rcMonitor', wintypes.RECT),
                            ('rcWork', wintypes.RECT), ('dwFlags', wintypes.DWORD)]
            user32.GetMonitorInfoW.argtypes = [wintypes.HANDLE, ctypes.POINTER(MONITORINFO)]
            user32.GetMonitorInfoW.restype = wintypes.BOOL
            user32.SetWindowPos.argtypes = [wintypes.HWND, wintypes.HWND, ctypes.c_int,
                                           ctypes.c_int, ctypes.c_int, ctypes.c_int, wintypes.UINT]
            user32.SetWindowPos.restype = wintypes.BOOL
            parent_hwnd = user32.GetAncestor(parent.winfo_id(), 2) or parent.winfo_id()
            hwnd = user32.GetAncestor(dialog.winfo_id(), 2) or dialog.winfo_id()
            monitor = user32.MonitorFromWindow(parent_hwnd, 2)  # nearest monitor
            info = MONITORINFO()
            info.cbSize = ctypes.sizeof(info)
            if user32.GetMonitorInfoW(monitor, ctypes.byref(info)):
                r = info.rcWork
                work = (r.left, r.top, r.right, r.bottom)
    except (OSError, AttributeError, tk.TclError):
        user32 = None
    w, h, x, y = centered_dialog_bounds(dialog.winfo_reqwidth(), dialog.winfo_reqheight(), work)
    dialog.geometry(f'{w}x{h}{x:+d}{y:+d}')
    dialog.deiconify()
    dialog.update_idletasks()
    if user32 is not None and hwnd:
        # Tk negative geometry offsets are edge-relative. Win32 coordinates are
        # absolute, so monitors left/above the primary screen work correctly.
        user32.SetWindowPos(hwnd, None, x, y, 0, 0, 0x0015)
    dialog.lift(parent)


class App(tk.Tk):
    BG = "#071018"
    PANEL = "#0C1721"
    PANEL_2 = "#101F2B"
    BORDER = "#183348"
    TEXT = "#EAF7FF"
    MUTED = "#8AA6B8"
    CYAN = "#32D6FF"
    CYAN_2 = "#0FA8D8"
    GREEN = "#35D58A"
    AMBER = "#FFB454"
    RED = "#FF667A"
    PURPLE = "#A58CFF"

    def __init__(self):
        super().__init__()
        self._configure_ultra_visual_system()
        self.settings = load_json_file(SETTINGS_PATH, {})
        if not isinstance(self.settings, dict):
            self.settings = {}
        theme_name = self.settings.get("theme", "NEXUS Chrome Honeycomb")
        if not self.settings.get("v31_chrome_migrated"):
            theme_name = "NEXUS Chrome Honeycomb"
            self.settings["theme"] = theme_name
            self.settings["v31_chrome_migrated"] = True
            save_json_file(SETTINGS_PATH, self.settings)
        if theme_name not in THEMES:
            theme_name = "NEXUS Chrome Honeycomb"
        self._apply_theme_values(theme_name)

        self.title(APP_NAME)
        self.geometry(self.settings.get("geometry", "1440x980"))
        self.minsize(1020, 720)
        self.configure(bg=self.BG)
        self.theme_var = tk.StringVar(value=theme_name)
        self.opacity_var = tk.DoubleVar(value=float(self.settings.get("opacity", THEMES[theme_name].get("ALPHA", 0.975))) * 100.0)
        try:
            self.attributes("-alpha", max(0.90, min(1.0, self.opacity_var.get()/100.0)))
        except Exception:
            pass

        self.image_var = tk.StringVar()
        self.disk_var = tk.StringVar()
        self.status = tk.StringVar(value="Ready. Select removable media and a NEXUS image.")
        self.stage = tk.StringVar(value="IDLE")
        self.progress = tk.DoubleVar()
        self.verify = tk.BooleanVar(value=True)
        requested_verify = verification_display_name(self.settings.get("verify_mode", "AEGIS Adaptive (recommended)"))
        self.verify_mode = tk.StringVar(value=requested_verify)
        self.verify_guard_status = tk.StringVar(value="AEGIS certification guard: adaptive GPT-aware verification armed")
        self.force_raw = tk.BooleanVar(value=False)
        self.fs_var = tk.StringVar(value="exFAT")
        self.scheme_var = tk.StringVar(value="GPT")
        self.label_var = tk.StringVar(value="NEXUS_USB")
        self.full_format = tk.BooleanVar(value=False)
        self.provision_remainder = tk.BooleanVar(value=bool(self.settings.get("provision_remainder", True)))
        self.auto_open_data = tk.BooleanVar(value=bool(self.settings.get("auto_open_data", True)))
        self.data_fs_var = tk.StringVar(value=self.settings.get("data_fs", "exFAT"))
        self.data_label_var = tk.StringVar(value=self.settings.get("data_label", "NEXUS_DATA"))
        self.self_heal_var = tk.BooleanVar(value=bool(self.settings.get("self_heal", True)))
        self.dm_fs_var = tk.StringVar(value="exFAT")
        self.dm_label_var = tk.StringVar(value="NEXUS_DATA")
        self.disk_summary = tk.StringVar(value="No removable device selected.")
        self.image_summary = tk.StringVar(value="No image selected.")
        self.telemetry = tk.StringVar(value="Speed —   •   ETA —   •   Written —")
        self.policy_summary = tk.StringVar(value="Write policy: checking…")
        self.access_summary = tk.StringVar(value="MEDIA ACCESS / idle")
        self.diskmap_summary = tk.StringVar(value="Disk Manager: select media to inspect its partition map.")

        self.recovery = RecoveryEngine(path=RECOVERY_PATH)
        self.recovery_status = tk.StringVar(value=self.recovery.summary())
        self.adaptive_profile = self.recovery.adaptive_profile()
        self.verify_guard_status.set("Exact bytes are certified under the raw-disk lock. After handoff, Windows may update filesystem metadata; post-certification checks validate boot/GPT health, not byte identity.")

        self.disks = []
        self.validated_image = None
        self.events = queue.Queue()
        self.busy = False
        self.paused = False
        self.current_page = "flash"
        self.pause_event = threading.Event()
        self.pause_event.set()
        self.cancel_event = threading.Event()

        self._build_style()
        self._build()
        self.protocol("WM_DELETE_WINDOW", self.on_close)
        self.after(60, self.apply_native_chrome)
        self.after(120, self.pump)
        self.after(250, self.refresh)

    def _pick_font(self, *candidates):
        try:
            available = {name.lower(): name for name in tkfont.families(self)}
            for candidate in candidates:
                found = available.get(str(candidate).lower())
                if found:
                    return found
        except Exception:
            pass
        return str(candidates[-1] if candidates else "Segoe UI")

    def _configure_ultra_visual_system(self):
        # Tk is vector based, but explicit per-monitor scaling keeps text, curves and
        # Canvas controls crisp on 1440p/4K/5K Windows displays.
        dpi = 96
        if os.name == "nt":
            try:
                dpi = int(ctypes.windll.user32.GetDpiForWindow(self.winfo_id()) or 96)
            except Exception:
                dpi = 96
        self.ui_dpi = max(96, dpi)
        try:
            self.tk.call("tk", "scaling", max(1.0, min(4.0, self.ui_dpi / 72.0)))
        except Exception:
            pass
        self.FONT_UI = self._pick_font("Segoe UI Variable Text", "Segoe UI", "Arial")
        self.FONT_DISPLAY = self._pick_font("Segoe UI Variable Display", "Segoe UI Semibold", "Segoe UI", "Arial")
        self.FONT_MONO = self._pick_font("Cascadia Code", "Cascadia Mono", "Consolas", "Courier New")
        try:
            self.option_add("*Font", (self.FONT_UI, 9))
            self.option_add("*Menu.Font", (self.FONT_UI, 9))
        except Exception:
            pass

    def _apply_theme_values(self, theme_name):
        theme = THEMES.get(theme_name, THEMES["NEXUS Quantum Glass"])
        for key in ("BG", "PANEL", "PANEL_2", "BORDER", "TEXT", "MUTED", "CYAN", "CYAN_2", "GREEN", "AMBER", "RED", "PURPLE"):
            setattr(self, key, theme[key])
        self.SIDEBAR = theme["SIDEBAR"]
        self.NAV_ACTIVE = theme["NAV_ACTIVE"]
        self.GLASS = theme["GLASS"]
        self.GRAD_A = theme["GRAD_A"]
        self.GRAD_B = theme["GRAD_B"]

    def apply_native_chrome(self):
        apply_windows_dark_chrome(self, self.BG, self.TEXT, self.BORDER)

    def save_settings(self):
        try:
            self.settings.update({
                "theme": self.theme_var.get(),
                "opacity": max(0.90, min(1.0, self.opacity_var.get()/100.0)),
                "provision_remainder": bool(self.provision_remainder.get()),
                "auto_open_data": bool(self.auto_open_data.get()),
                "data_fs": self.data_fs_var.get(),
                "data_label": sanitize_label(self.data_label_var.get()),
                "self_heal": bool(self.self_heal_var.get()),
                "verify_mode": verification_display_name(self.verify_mode.get()),
                "geometry": self.geometry(),
            })
            save_json_file(SETTINGS_PATH, self.settings)
        except Exception:
            pass

    def apply_opacity(self, value=None):
        try:
            if value is not None:
                self.opacity_var.set(float(value))
            alpha = max(0.90, min(1.0, float(self.opacity_var.get()) / 100.0))
            self.attributes("-alpha", alpha)
            self.save_settings()
        except Exception:
            pass

    def change_theme(self, _event=None):
        if self.busy:
            messagebox.showwarning(APP_NAME, "Theme changes are disabled while a media operation is running.")
            return
        name = self.theme_var.get()
        if name not in THEMES:
            return
        self._apply_theme_values(name)
        self.save_settings()
        self.rebuild_ui()

    def rebuild_ui(self):
        page = getattr(self, "current_page", "flash")
        log_text = ""
        try:
            log_text = self.log.get("1.0", "end-1c")
        except Exception:
            pass
        try:
            self.unbind_all("<MouseWheel>")
            self.unbind_all("<Button-4>")
            self.unbind_all("<Button-5>")
        except Exception:
            pass
        for child in list(self.winfo_children()):
            child.destroy()
        self.configure(bg=self.BG)
        self._build_style()
        self._build()
        if self.disks:
            self.set_disks(self.disks)
        self.show_page(page if page in self.pages else "flash")
        if log_text:
            self.log.configure(state="normal")
            self.log.insert("end", log_text + "\n")
            self.log.configure(state="disabled")
        self.after(40, self.apply_native_chrome)
        self.logline(f"THEME: {self.theme_var.get()} applied.")

    def reset_recovery_knowledge(self):
        if self.busy:
            return
        if messagebox.askyesno(APP_NAME, "Reset AEGIS recovery memory?\n\nThis clears remembered error fingerprints and adaptive recovery history."):
            self.recovery.reset()
            self.adaptive_profile = self.recovery.adaptive_profile()
            self.recovery_status.set(self.recovery.summary())
            self.logline("AEGIS SELF-HEAL: recovery memory reset by operator.")

    def show_recovery_memory(self):
        data = json.dumps(self.recovery.data, indent=2)
        messagebox.showinfo(APP_NAME + " — AEGIS Recovery Memory", data[:7000] or "No recovery history.")

    def run_application_self_test(self):
        if self.busy:
            messagebox.showwarning(APP_NAME,"Wait for the active operation before running self-tests.");return
        results=[]
        def add(name,ok,detail):results.append((name,"PASS" if ok else "FAIL",detail))
        add("Python / Tk",True,f"Python {sys.version_info.major}.{sys.version_info.minor}; Tk {tk.TkVersion}")
        add("Chrome button renderer",isinstance(self.start,RoundedButton),"Live control exists")
        add("Forensic workspaces",all(p in self.pages for p in ("undelete","erase")),"Image recovery and verified logical erase pages")
        add("Verification-mode normalization",normalize_verify_mode("Strict forensic byte-for-byte")=="Strict byte-for-byte","Strict remains strict")
        add("Source recovery engine",callable(scan_recovery_image) and callable(extract_recovery_candidates),"Function availability; not a media-recovery guarantee")
        try:
            data=bytearray(b"sensitive"*2048)
            def write(off,chunk):data[off:off+len(chunk)]=chunk;return len(chunk)
            r=overwrite_and_verify(lambda off,n:bytes(data[off:off+n]),write,lambda:True,len(data),block_size=1024)
            add("Logical erase core / memory fixture",r["logical_verification_passed"] and not any(data),"RAM only; no device opened")
        except Exception as exc:add("Logical erase core / memory fixture",False,str(exc))
        if os.name=="nt":
            add("Administrator access",is_admin(),"Runtime permission only")
            add("PowerShell availability",bool(shutil.which("powershell.exe")),"Executable discovery only")
            add("DiskPart availability",bool(shutil.which("diskpart.exe")),"Executable discovery only")
            add("Win32 I/O / eject API availability",bool(kernel32 and cfgmgr32),"DLL loading only; physical I/O not exercised")
        else:
            results.append(("Windows APIs / physical-device I/O","SKIP","Not available on this operating system"))
        results.append(("Actual USB write, readback, erase, eject and UEFI boot","NOT TESTED","Requires your Windows PC and sacrificial removable media"))
        lines=[f"{status}  {name} — {detail}" for name,status,detail in results]
        for line in lines:self.logline("SELF-TEST: "+line)
        messagebox.showinfo(APP_NAME+" — Non-destructive self-test","\n".join(lines)+"\n\nA software self-test is not a hardware qualification or sanitization certificate.")
        return results

    def on_close(self):
        if self.busy:
            messagebox.showwarning(APP_NAME,"An operation is still active. Use STOP and wait for cleanup/reporting to finish before closing. Abrupt termination could leave the device or Windows storage state incomplete.")
            return
        self.save_settings()
        for job in self.tk.call("after","info"):
            try:self.after_cancel(job)
            except tk.TclError:pass
        self.destroy()

    # ----- visual helpers -------------------------------------------------
    def _build_style(self):
        style = ttk.Style(self)
        try:
            style.theme_use("clam")
        except Exception:
            pass
        field = blend_hex(self.PANEL_2, self.CYAN, 0.025)
        style.configure(
            "Nexus.Horizontal.TProgressbar",
            troughcolor=blend_hex(self.PANEL, "#000000", 0.30), background=self.CYAN, bordercolor=self.PANEL,
            lightcolor=self.CYAN, darkcolor=self.GRAD_B, thickness=12,
        )
        style.configure(
            "Nexus.TCombobox", fieldbackground=field, background=field, foreground=self.TEXT,
            arrowcolor=blend_hex(self.CYAN, "#FFFFFF", 0.10), bordercolor=blend_hex(self.BORDER, "#FFFFFF", 0.05),
            lightcolor=self.BORDER, darkcolor=self.BORDER, padding=(11, 9), font=(self.FONT_UI, 9),
        )
        style.map(
            "Nexus.TCombobox",
            fieldbackground=[("readonly", field), ("focus", blend_hex(field, self.CYAN, 0.035))],
            foreground=[("readonly", self.TEXT)],
            bordercolor=[("focus", blend_hex(self.CYAN_2, "#FFFFFF", 0.08))],
        )
        style.configure("Nexus.TCheckbutton", background=self.PANEL, foreground=self.TEXT, font=(self.FONT_UI, 9), padding=2)
        style.map("Nexus.TCheckbutton", background=[("active", self.PANEL)], foreground=[("active", self.TEXT)])
        style.configure("Nexus.Vertical.TScrollbar", troughcolor=self.BG, background=blend_hex(self.PANEL_2, self.CYAN, 0.02), bordercolor=self.BG, arrowcolor=self.CYAN)
        style.configure("Nexus.Treeview", background=self.PANEL_2, fieldbackground=self.PANEL_2, foreground=self.TEXT, rowheight=32, borderwidth=0, font=(self.FONT_MONO, 8))
        style.configure("Nexus.Treeview.Heading", background=blend_hex(self.PANEL_2, self.CYAN, 0.055), foreground=blend_hex(self.CYAN, "#FFFFFF", 0.12), relief="flat", font=(self.FONT_UI, 8, "bold"), padding=(6, 7))
        style.map("Nexus.Treeview", background=[("selected", self.NAV_ACTIVE)], foreground=[("selected", self.TEXT)])

    def _card(self, parent, title, subtitle=None):
        panel = RoundedPanel(parent, fill=self.PANEL, border=self.BORDER, radius=20)
        inner = panel.content
        head = tk.Frame(inner, bg=self.PANEL)
        head.pack(fill="x", padx=4, pady=(3, 7))
        tk.Label(head, text=title, bg=self.PANEL, fg=self.TEXT, font=(self.FONT_DISPLAY, 11, "bold")).pack(anchor="w")
        if subtitle:
            tk.Label(head, text=subtitle, bg=self.PANEL, fg=self.MUTED, font=(self.FONT_UI, 8), wraplength=980, justify="left").pack(anchor="w", pady=(2, 0))
        body = tk.Frame(inner, bg=self.PANEL)
        body.pack(fill="both", expand=True, padx=4, pady=(2, 4))
        return panel, body

    def _button(self,parent,text,command,accent="cyan",width=None):
        rail=self.RED if accent=="red" else self.AMBER if accent=="amber" else self.CYAN
        button=RoundedButton(parent,text,command,bg=self.CYAN_2,hover=self.CYAN,fg=self.TEXT,
                             width_chars=width,height=50,radius=20,accent=rail,font=(self.FONT_UI,9,"bold"))
        button._is_nav=accent=="nav"
        return button

    def _entry(self, parent, variable):
        return tk.Entry(
            parent, textvariable=variable, bg=blend_hex(self.PANEL_2, self.CYAN, 0.025), fg=self.TEXT,
            insertbackground=self.CYAN, selectbackground=blend_hex(self.CYAN_2, self.BG, 0.28), selectforeground=self.TEXT,
            relief="flat", bd=0, highlightthickness=1, highlightbackground=self.BORDER,
            highlightcolor=self.CYAN_2, font=(self.FONT_UI, 9),
        )

    def _build_hud_command_bar(self, parent):
        try:
            self.tk.call(self._w, "configure", "-menu", "")
        except Exception:
            pass
        bar = tk.Frame(parent, bg=blend_hex(self.SIDEBAR, self.CYAN, 0.018), height=56)
        bar.pack(fill="x", side="top")
        bar.pack_propagate(False)
        left = tk.Frame(bar, bg=bar.cget("bg")); left.pack(side="left", padx=12, pady=2)

        def popup_menu(items):
            m = tk.Menu(self, tearoff=False, bg=self.PANEL, fg=self.TEXT, activebackground=self.NAV_ACTIVE, activeforeground=self.TEXT, bd=0, relief="flat", font=(self.FONT_UI, 9), activeborderwidth=0)
            for item in items:
                if item is None:
                    m.add_separator()
                else:
                    label, cmd = item; m.add_command(label=label, command=cmd)
            return m

        file_menu = popup_menu([
            ("Select image…", self.choose_image),
            ("Create image backup from selected media…", self.backup_selected_to_image),
            ("Export operation log…", self.export_operation_log), None,
            ("Exit", self.on_close),
        ])
        action_menu = popup_menu([
            ("Flash image", self.start_write),
            ("Factory reset / reclaim", self.restore_usb),
            ("Safe eject selected media", self.safe_eject_selected), None,
            ("Media diagnostics", self.run_diagnostics),
            ("Rescan devices", self.refresh),
        ])
        view_menu = popup_menu([
            ("Flash / Clone", lambda: self.show_page("flash")),
            ("Recovery / Reset", lambda: self.show_page("reset")),
            ("Disk Manager", lambda: self.show_page("disk")),
            ("Undelete Lab", lambda: self.show_page("undelete")),
            ("Verified Logical Erase", lambda: self.show_page("erase")),
            ("Settings / Themes", lambda: self.show_page("settings")),
        ])
        view_menu.add_separator()
        for name in THEMES:
            view_menu.add_command(label=f"Theme: {name}", command=lambda n=name: (self.theme_var.set(n), self.change_theme()))
        help_menu = popup_menu([
            ("Run non-destructive application self-test", self.run_application_self_test),
            ("AEGIS recovery memory", self.show_recovery_memory),
            ("Open runtime log folder", lambda: os.startfile(str(LOG_PATH.parent)) if os.name == "nt" else None), None,
            ("About NEXUS Imaging Studio", lambda: messagebox.showinfo(APP_NAME, APP_NAME + "\n\nAEGIS enterprise removable-media imaging, adaptive verification, recovery and disk-management utility.")),
        ])

        def add_menu_button(label, menu):
            holder = {"button": None}
            def show():
                b = holder["button"]
                try:
                    menu.tk_popup(b.winfo_rootx(), b.winfo_rooty()+b.winfo_height()+3)
                finally:
                    try: menu.grab_release()
                    except Exception: pass
            b = self._button(left, label, show, "ghost", width=max(5, len(label)+1))
            holder["button"] = b
            b.pack(side="left", padx=(0,5))

        add_menu_button("FILE", file_menu)
        add_menu_button("ACTION", action_menu)
        add_menu_button("VIEW", view_menu)
        add_menu_button("HELP", help_menu)

        right = tk.Frame(bar, bg=bar.cget("bg")); right.pack(side="right", padx=12)
        tk.Label(right, text="NEXUS / CHROME HONEYCOMB", bg=bar.cget("bg"), fg=self.CYAN, font=(self.FONT_MONO, 8, "bold")).pack(side="left", pady=12)
        tk.Label(right, text="  •  ADMIN" if is_admin() else "  •  PREVIEW / NOT ELEVATED", bg=bar.cget("bg"), fg=self.GREEN, font=(self.FONT_MONO, 7)).pack(side="left", pady=12)
        GradientBar(parent, self.GRAD_A, self.GRAD_B, height=2).pack(fill="x", side="top")

    def show_page(self, name):
        if name not in self.pages:
            return
        self.current_page = name
        for frame in self.pages.values():
            frame.pack_forget()
        self.pages[name].pack(fill="both", expand=True)
        for key, btn in self.nav_buttons.items():
            active = key == name
            btn._nexus_normal_bg = self.NAV_ACTIVE if active else self.SIDEBAR
            btn.configure(bg=btn._nexus_normal_bg, fg=self.CYAN if active else self.MUTED, selected=active)
        titles = {
            "flash": "FLASH / CLONE IMAGE",
            "reset": "FACTORY RESET / RECLAIM",
            "undelete": "UNDELETE LAB",
            "erase": "VERIFIED LOGICAL ERASE",
            "disk": "DISK MANAGER",
            "settings": "SETTINGS / AEGIS",
        }
        self.workspace_title.configure(text=titles.get(name, "NEXUS IMAGING STUDIO"))
        if name == "disk":
            self.refresh_partition_view()

    def _build(self):
        shell = tk.Frame(self, bg=self.BG)
        shell.pack(fill="both", expand=True)
        self._build_hud_command_bar(shell)
        root = tk.Frame(shell, bg=self.BG)
        root.pack(fill="both", expand=True)

        sidebar = tk.Frame(root, bg=self.SIDEBAR, width=224)
        sidebar.pack(side="left", fill="y")
        sidebar.pack_propagate(False)
        GradientBar(sidebar, self.GRAD_A, self.GRAD_B, height=3).pack(fill="x", side="top")

        content_shell = tk.Frame(root, bg=self.BG)
        content_shell.pack(side="left", fill="both", expand=True)
        self.main_xscroll = ttk.Scrollbar(content_shell, orient="horizontal")
        self.main_xscroll.pack(side="bottom", fill="x")
        self.main_canvas = tk.Canvas(content_shell, bg=self.BG, bd=0, highlightthickness=0)
        self.main_scroll = ttk.Scrollbar(content_shell, orient="vertical", command=self.main_canvas.yview, style="Nexus.Vertical.TScrollbar")
        self.main_canvas.configure(yscrollcommand=self.main_scroll.set, xscrollcommand=self.main_xscroll.set)
        self.main_xscroll.configure(command=self.main_canvas.xview)
        self.main_scroll.pack(side="right", fill="y")
        self.main_canvas.pack(side="left", fill="both", expand=True)
        main = tk.Frame(self.main_canvas, bg=self.BG)
        self._main_canvas_window = self.main_canvas.create_window((0, 0), window=main, anchor="nw")

        def _sync_scroll_region(_event=None):
            try: self.main_canvas.configure(scrollregion=self.main_canvas.bbox("all"))
            except Exception: pass

        def _sync_canvas_width(event):
            try: self.main_canvas.itemconfigure(self._main_canvas_window, width=max(1136,event.width))
            except Exception: pass

        def _wheel(event):
            try:
                if event.delta:
                    step = -1 * int(event.delta / 120)
                else:
                    step = -1 if getattr(event, "num", None) == 4 else 1
                self.main_canvas.yview_scroll(step, "units")
            except Exception:
                pass

        main.bind("<Configure>", _sync_scroll_region)
        self.main_canvas.bind("<Configure>", _sync_canvas_width)
        self.bind_all("<MouseWheel>", _wheel)
        self.bind_all("<Button-4>", _wheel)
        self.bind_all("<Button-5>", _wheel)

        # Brand rail
        brand = tk.Frame(sidebar, bg=self.SIDEBAR)
        brand.pack(fill="x", padx=18, pady=(22, 24))
        emblem = tk.Canvas(brand, width=46, height=46, bg=self.SIDEBAR, highlightthickness=0)
        emblem.pack(side="left")
        _rounded_rect(emblem, 2, 3, 44, 45, 13, fill=blend_hex(self.SIDEBAR, "#000000", 0.55), outline="")
        _rounded_rect(emblem, 1, 1, 43, 43, 13, fill=blend_hex(self.CYAN, self.GRAD_B, 0.20), outline=blend_hex(self.CYAN, "#FFFFFF", 0.18), width=1)
        _rounded_rect(emblem, 4, 4, 40, 21, 10, fill=blend_hex(self.CYAN, "#FFFFFF", 0.18), outline="")
        emblem.create_text(22, 22, text="N", fill="#031015", font=(self.FONT_DISPLAY, 18, "bold"))
        brand_text = tk.Frame(brand, bg=self.SIDEBAR)
        brand_text.pack(side="left", padx=(10, 0))
        tk.Label(brand_text, text="NEXUS", bg=self.SIDEBAR, fg=self.TEXT, font=(self.FONT_DISPLAY, 14, "bold")).pack(anchor="w")
        tk.Label(brand_text, text="IMAGING STUDIO / AEGIS", bg=self.SIDEBAR, fg=self.CYAN, font=(self.FONT_UI, 7)).pack(anchor="w")

        tk.Label(sidebar, text="WORKSPACE", bg=self.SIDEBAR, fg=blend_hex(self.MUTED, self.BG, 0.30), font=(self.FONT_UI, 8, "bold")).pack(anchor="w", padx=20, pady=(0, 7))
        self.nav_buttons = {}
        nav_items = [
            ("flash", "Flash / clone"),
            ("reset", "Factory reset"),
            ("undelete", "Undelete lab"),
            ("erase", "Verified erase"),
            ("disk", "Disk manager"),
            ("settings", "Settings / themes"),
        ]
        for key, label in nav_items:
            btn = self._button(sidebar, label, lambda k=key: self.show_page(k), "nav")
            btn.pack(fill="x", padx=10, pady=3)
            self.nav_buttons[key] = btn

        side_info = tk.Frame(sidebar, bg=blend_hex(self.SIDEBAR, self.CYAN, 0.035))
        side_info.pack(side="bottom", fill="x", padx=12, pady=14)
        tk.Label(side_info, text="AEGIS / ADMIN MODE" if is_admin() else "PREVIEW / NO DISK ACCESS", bg=side_info.cget("bg"), fg=self.GREEN, font=(self.FONT_MONO, 8, "bold")).pack(anchor="w", padx=12, pady=(10, 2))
        tk.Label(side_info, text="Physical disk writes\nGPT / MBR / UEFI\nAdaptive recovery\nSafe eject + disk tools", bg=side_info.cget("bg"), fg=self.MUTED, font=(self.FONT_UI, 8), justify="left").pack(anchor="w", padx=12, pady=(0, 10))

        # Header
        header = tk.Frame(main, bg=self.BG)
        header.pack(fill="x", padx=26, pady=(18, 8))
        hleft = tk.Frame(header, bg=self.BG)
        hleft.pack(side="left", fill="x", expand=True)
        tk.Label(hleft, text="NEXUS / REMOVABLE MEDIA OPERATIONS", bg=self.BG, fg=self.CYAN, font=("Segoe UI Semibold", 8)).pack(anchor="w")
        self.workspace_title = tk.Label(hleft, text="FLASH / CLONE IMAGE", bg=self.BG, fg=self.TEXT, font=(self.FONT_DISPLAY, 23, "bold"))
        self.workspace_title.pack(anchor="w", pady=(2, 0))
        tk.Label(hleft, text=APP_SUBTITLE, bg=self.BG, fg=self.MUTED, font=(self.FONT_UI, 8), wraplength=630, justify="left").pack(anchor="w", pady=(2, 0))
        hright = tk.Frame(header, bg=self.BG)
        hright.pack(side="right", anchor="n")
        self.hud_dial = HudDial(hright, self.progress, self.CYAN, self.BG, text="CORE", size=84, ui_font=self.FONT_UI, mono_font=self.FONT_MONO)
        self.hud_dial.pack(side="right", padx=(10, 0))
        badge_stack = tk.Frame(hright, bg=self.BG)
        badge_stack.pack(side="right", pady=5)
        self.access_badge = tk.Label(badge_stack, textvariable=self.access_summary, bg=blend_hex(self.PANEL_2, self.CYAN, 0.08), fg=self.CYAN, font=(self.FONT_MONO, 8, "bold"), padx=12, pady=7)
        self.access_badge.pack(anchor="e")
        tk.Label(badge_stack, text="GPT / UEFI / RAW I/O / ADAPTIVE CERT", bg=self.BG, fg=self.MUTED, font=(self.FONT_MONO, 7)).pack(anchor="e", pady=(5,0))
        GradientBar(main, self.GRAD_A, self.GRAD_B, height=3).pack(fill="x", padx=26, pady=(0, 12))

        # Target media
        dev_card, dev = self._card(main, "TARGET DEVICE / MEDIA", "Removable USB / SD / MMC only — Windows boot and system disks are excluded by the software target guard")
        dev_card.pack(fill="x", padx=24, pady=(0, 10))
        row = tk.Frame(dev, bg=self.PANEL)
        row.pack(fill="x")
        self.combo = ttk.Combobox(row, textvariable=self.disk_var, state="readonly", style="Nexus.TCombobox")
        self.combo.pack(side="left", fill="x", expand=True)
        self.combo.bind("<<ComboboxSelected>>", lambda _e: self.on_disk_selected())
        self.refresh_btn = self._button(row, "RESCAN", self.refresh, "ghost", width=10)
        self.refresh_btn.pack(side="left", padx=(8, 0))
        self.diag_btn = self._button(row, "DIAGNOSTICS", self.run_diagnostics, "ghost", width=12)
        self.diag_btn.pack(side="left", padx=(8, 0))
        self.eject_btn = self._button(row, "SAFE EJECT", self.safe_eject_selected, "purple", width=12)
        self.eject_btn.pack(side="left", padx=(8, 0))
        summary_row = tk.Frame(dev, bg=self.PANEL)
        summary_row.pack(fill="x", pady=(9, 0))
        tk.Label(summary_row, textvariable=self.disk_summary, bg=self.PANEL, fg=blend_hex(self.TEXT, self.MUTED, 0.35), font=(self.FONT_MONO, 8), justify="left").pack(side="left", anchor="w", fill="x", expand=True)
        tk.Label(summary_row, textvariable=self.policy_summary, bg=blend_hex(self.PANEL_2, self.CYAN, 0.025), fg=self.MUTED, font=(self.FONT_MONO, 8), padx=10, pady=6).pack(side="right", anchor="n")

        host = tk.Frame(main, bg=self.BG)
        host.pack(fill="both", expand=True, padx=24)
        flash_page = tk.Frame(host, bg=self.BG)
        reset_page = tk.Frame(host, bg=self.BG)
        disk_page = tk.Frame(host, bg=self.BG)
        settings_page = tk.Frame(host, bg=self.BG)
        self.pages = {"flash": flash_page, "reset": reset_page, "disk": disk_page, "settings": settings_page}

        # FLASH PAGE
        img_card, img_body = self._card(flash_page, "SOURCE IMAGE / ARTIFACT", "Hybrid ISO / IMG / RAW / BIN — boot structure is validated before destructive write")
        img_card.pack(fill="x", pady=(0, 10))
        row = tk.Frame(img_body, bg=self.PANEL); row.pack(fill="x")
        image_entry = self._entry(row, self.image_var); image_entry.configure(state="readonly", readonlybackground=self.PANEL_2); image_entry.pack(side="left", fill="x", expand=True, ipady=8)
        self.select_image_btn = self._button(row, "SELECT IMAGE", self.choose_image, "ghost", width=14); self.select_image_btn.pack(side="left", padx=(8, 0))
        tk.Label(img_body, textvariable=self.image_summary, bg=self.PANEL, fg=self.MUTED, font=(self.FONT_MONO, 8), justify="left").pack(anchor="w", pady=(8, 0))
        opts = tk.Frame(img_body, bg=self.PANEL); opts.pack(fill="x", pady=(8, 0))
        ChromeToggle(opts, text="Verification enabled", variable=self.verify, style="Nexus.TCheckbutton").pack(side="left")
        tk.Label(opts, text="Verification", bg=self.PANEL, fg=self.MUTED, font=(self.FONT_UI, 8)).pack(side="left", padx=(16, 8))
        ttk.Combobox(opts, textvariable=self.verify_mode, values=["AEGIS Adaptive (recommended)", "Strict forensic byte-for-byte", "Structure only"], state="readonly", style="Nexus.TCombobox", width=29).pack(side="left")
        advanced_row = tk.Frame(img_body, bg=self.PANEL); advanced_row.pack(fill="x", pady=(4,0))
        ChromeToggle(advanced_row, text="Advanced raw / bypass boot validator", variable=self.force_raw, command=self.update_start_state, style="Nexus.TCheckbutton").pack(side="left", padx=(18, 0))
        tk.Label(img_body, textvariable=self.verify_guard_status, bg=self.PANEL, fg=self.CYAN, font=(self.FONT_MONO, 7), justify="left").pack(anchor="w", pady=(7,0))

        data_card, data_body = self._card(flash_page, "POST-FLASH STORAGE", "After the requested image checks, AEGIS can use the remaining unallocated USB capacity as a normal mounted data drive")
        data_card.pack(fill="x", pady=(0, 10))
        drow = tk.Frame(data_body, bg=self.PANEL); drow.pack(fill="x")
        ChromeToggle(drow, text="Create and mount a data partition from remaining space", variable=self.provision_remainder, style="Nexus.TCheckbutton", command=self.save_settings).pack(side="left")
        ChromeToggle(drow, text="Open when complete", variable=self.auto_open_data, style="Nexus.TCheckbutton", command=self.save_settings).pack(side="left", padx=(14, 0))
        drow = tk.Frame(data_body, bg=self.PANEL); drow.pack(fill="x", pady=(5,0))
        tk.Label(drow, text="Filesystem", bg=self.PANEL, fg=self.MUTED, font=(self.FONT_UI, 8)).pack(side="left", padx=(18, 7))
        ttk.Combobox(drow, textvariable=self.data_fs_var, values=["exFAT", "NTFS", "FAT32"], state="readonly", style="Nexus.TCombobox", width=10).pack(side="left")
        tk.Label(drow, text="Label", bg=self.PANEL, fg=self.MUTED, font=(self.FONT_UI, 8)).pack(side="left", padx=(18, 7))
        self._entry(drow, self.data_label_var).pack(side="left", fill="x", expand=True, ipady=7)

        action_card, action = self._card(flash_page, "AEGIS FLASH PIPELINE", "Identity guard → hidden-volume dismount → protected-partition reclaim → guarded raw write → exact byte verification → host-health handoff → optional remainder partition")
        action_card.pack(fill="x", pady=(0, 10))
        actions = tk.Frame(action, bg=self.PANEL); actions.pack(fill="x")
        self.start = self._button(actions, "FLASH IMAGE", self.start_write, "green", width=18); self.start.configure(state="disabled"); self.start.pack(side="left")
        self.pause = self._button(actions, "PAUSE", self.toggle_pause, "amber", width=11); self.pause.configure(state="disabled"); self.pause.pack(side="left", padx=(8, 0))
        self.stop = self._button(actions, "STOP", self.request_stop, "red", width=10); self.stop.configure(state="disabled"); self.stop.pack(side="left", padx=(8, 0))
        self.flash_eject_btn = self._button(actions, "SAFE EJECT", self.safe_eject_selected, "purple", width=12); self.flash_eject_btn.pack(side="right")

        # RECOVERY PAGE
        reset_card, reset = self._card(reset_page, "FACTORY RESET + MEDIA RECLAIM", "Removes EFI/OEM/recovery partitions and rebuilds one normal Windows-readable volume")
        reset_card.pack(fill="x", pady=(0, 10))
        grid = tk.Frame(reset, bg=self.PANEL); grid.pack(fill="x")
        for col in range(6): grid.grid_columnconfigure(col, weight=1 if col in (1, 3, 5) else 0)
        tk.Label(grid, text="Partition map", bg=self.PANEL, fg=self.MUTED, font=(self.FONT_UI, 8)).grid(row=0, column=0, sticky="w", padx=(0, 8), pady=5)
        ttk.Combobox(grid, textvariable=self.scheme_var, values=["GPT", "MBR"], state="readonly", style="Nexus.TCombobox", width=11).grid(row=0, column=1, sticky="ew", padx=(0, 18), pady=5)
        tk.Label(grid, text="Filesystem", bg=self.PANEL, fg=self.MUTED, font=(self.FONT_UI, 8)).grid(row=0, column=2, sticky="w", padx=(0, 8), pady=5)
        ttk.Combobox(grid, textvariable=self.fs_var, values=["exFAT", "NTFS", "FAT32"], state="readonly", style="Nexus.TCombobox", width=11).grid(row=0, column=3, sticky="ew", padx=(0, 18), pady=5)
        tk.Label(grid, text="Volume label", bg=self.PANEL, fg=self.MUTED, font=(self.FONT_UI, 8)).grid(row=0, column=4, sticky="w", padx=(0, 8), pady=5)
        label_entry = self._entry(grid, self.label_var); label_entry.grid(row=0, column=5, sticky="ew", ipady=7, pady=5)
        ChromeToggle(reset, text="Full format / media surface check (slow)", variable=self.full_format, style="Nexus.TCheckbutton").pack(anchor="w", pady=(9, 4))
        ractions = tk.Frame(reset, bg=self.PANEL); ractions.pack(fill="x", pady=(7, 0))
        self.restore = self._button(ractions, "RECLAIM + FACTORY RESET", self.restore_usb, "cyan", width=26); self.restore.pack(side="left")
        self.diag_btn_reset = self._button(ractions, "MEDIA DIAGNOSTICS", self.run_diagnostics, "ghost", width=19); self.diag_btn_reset.pack(side="left", padx=(8, 0))
        self.reset_eject_btn = self._button(ractions, "SAFE EJECT", self.safe_eject_selected, "purple", width=12); self.reset_eject_btn.pack(side="left", padx=(8, 0))

        # DISK MANAGER PAGE
        map_card, map_body = self._card(disk_page, "DISK MAP / PARTITIONS", "Integrated removable-media partition management. Protected EFI/System/Recovery partitions are guarded from accidental format/delete operations.")
        map_card.pack(fill="x", pady=(0, 10))
        tk.Label(map_body, textvariable=self.diskmap_summary, bg=self.PANEL, fg=self.MUTED, font=(self.FONT_MONO, 8), justify="left").pack(anchor="w", pady=(0, 7))
        tree_shell = tk.Frame(map_body, bg=self.PANEL); tree_shell.pack(fill="both", expand=True)
        cols = ("part", "letter", "type", "fs", "label", "size", "offset", "health")
        self.partition_tree = ttk.Treeview(tree_shell, columns=cols, show="headings", height=8, style="Nexus.Treeview")
        headings = {"part":"#", "letter":"Mount", "type":"Type", "fs":"FS", "label":"Label", "size":"Size", "offset":"Offset", "health":"Health"}
        widths = {"part":45, "letter":65, "type":150, "fs":80, "label":150, "size":90, "offset":100, "health":90}
        for c in cols:
            self.partition_tree.heading(c, text=headings[c]); self.partition_tree.column(c, width=widths[c], anchor="w", stretch=(c in ("type","label")))
        tvs = ttk.Scrollbar(tree_shell, orient="vertical", command=self.partition_tree.yview, style="Nexus.Vertical.TScrollbar")
        self.partition_tree.configure(yscrollcommand=tvs.set)
        tvs.pack(side="right", fill="y"); self.partition_tree.pack(side="left", fill="both", expand=True)

        dm_card, dm = self._card(disk_page, "DISK MANAGEMENT ACTIONS", "Create, mount, format, delete and extend normal data partitions without leaving NEXUS Imaging Studio")
        dm_card.pack(fill="x", pady=(0, 10))
        dm_top = tk.Frame(dm, bg=self.PANEL); dm_top.pack(fill="x")
        tk.Label(dm_top, text="Filesystem", bg=self.PANEL, fg=self.MUTED, font=(self.FONT_UI, 8)).pack(side="left")
        ttk.Combobox(dm_top, textvariable=self.dm_fs_var, values=["exFAT", "NTFS", "FAT32"], state="readonly", style="Nexus.TCombobox", width=10).pack(side="left", padx=(7, 14))
        tk.Label(dm_top, text="Label", bg=self.PANEL, fg=self.MUTED, font=(self.FONT_UI, 8)).pack(side="left")
        self._entry(dm_top, self.dm_label_var).pack(side="left", fill="x", expand=True, padx=(7, 12), ipady=7)
        self._button(dm_top, "REFRESH MAP", self.refresh_partition_view, "ghost", width=13).pack(side="right")
        dm_actions = tk.Frame(dm, bg=self.PANEL); dm_actions.pack(fill="x", pady=(9, 0))
        for text, cmd, accent, width in [
            ("CREATE DATA", self.disk_create_data, "green", 13),
            ("FORMAT", self.disk_format_selected, "cyan", 10),
            ("EXTEND", self.disk_extend_selected, "ghost", 10),
            ("ASSIGN LETTER", self.disk_assign_letter, "ghost", 14),
            ("REMOVE LETTER", self.disk_remove_letter, "ghost", 14),
        ]:
            self._button(dm_actions, text, cmd, accent, width=width).pack(side="left", padx=(0, 7), pady=3)
        dm_actions2 = tk.Frame(dm, bg=self.PANEL); dm_actions2.pack(fill="x", pady=(6, 0))
        for text, cmd, accent, width in [
            ("OPEN MOUNT", self.disk_open_mount, "ghost", 12),
            ("MAKE WRITABLE", self.disk_make_writable, "ghost", 14),
            ("ONLINE / OFFLINE", self.disk_toggle_online, "ghost", 16),
        ]:
            self._button(dm_actions2, text, cmd, accent, width=width).pack(side="left", padx=(0, 7), pady=3)
        dm_actions3 = tk.Frame(dm, bg=self.PANEL); dm_actions3.pack(fill="x", pady=(6, 0))
        for text, cmd, accent, width in [
            ("CREATE IMAGE BACKUP", self.backup_selected_to_image, "purple", 19),
            ("DELETE PARTITION", self.disk_delete_selected, "red", 16),
            ("SAFE EJECT", self.safe_eject_selected, "purple", 12),
        ]:
            self._button(dm_actions3, text, cmd, accent, width=width).pack(side="left", padx=(0, 7), pady=3)

        # SETTINGS PAGE
        theme_card, theme_body = self._card(settings_page, "CHROME / HONEYCOMB APPEARANCE", "Per-monitor DPI rendering, precision typography, quantum-glass surfaces, brighter vector controls, luminous progress telemetry and dark Windows chrome. Theme settings persist between launches.")
        theme_card.pack(fill="x", pady=(0, 10))
        trow = tk.Frame(theme_body, bg=self.PANEL); trow.pack(fill="x")
        tk.Label(trow, text="Theme", bg=self.PANEL, fg=self.MUTED, font=(self.FONT_UI, 8)).pack(side="left")
        theme_combo = ttk.Combobox(trow, textvariable=self.theme_var, values=list(THEMES.keys()), state="readonly", style="Nexus.TCombobox", width=20)
        theme_combo.pack(side="left", padx=(8, 20)); theme_combo.bind("<<ComboboxSelected>>", self.change_theme)
        tk.Label(trow, text="Window transparency", bg=self.PANEL, fg=self.MUTED, font=(self.FONT_UI, 8)).pack(side="left")
        opacity = tk.Scale(trow, from_=90, to=100, orient="horizontal", variable=self.opacity_var, command=self.apply_opacity, bg=self.PANEL, fg=self.TEXT, troughcolor=self.PANEL_2, activebackground=self.CYAN, highlightthickness=0, bd=0, length=220, resolution=1)
        opacity.pack(side="left", padx=(8, 0))

        heal_card, heal_body = self._card(settings_page, "AEGIS SELF-HEAL / ADAPTIVE RECOVERY", "Bounded recovery memory fingerprints known failures and escalates deterministic recovery recipes on future operations; it never self-grants permissions or rewrites itself.")
        heal_card.pack(fill="x", pady=(0, 10))
        ChromeToggle(heal_body, text="Enable AEGIS adaptive recovery memory", variable=self.self_heal_var, style="Nexus.TCheckbutton", command=self.save_settings).pack(anchor="w")
        tk.Label(heal_body, textvariable=self.recovery_status, bg=self.PANEL, fg=self.CYAN, font=(self.FONT_MONO, 8), wraplength=900, justify="left").pack(anchor="w", pady=(8, 7))
        hbtn = tk.Frame(heal_body, bg=self.PANEL); hbtn.pack(fill="x")
        self._button(hbtn, "VIEW RECOVERY MEMORY", self.show_recovery_memory, "ghost", width=21).pack(side="left")
        self._button(hbtn, "RESET RECOVERY MEMORY", self.reset_recovery_knowledge, "red", width=21).pack(side="left", padx=(8, 0))
        self._button(hbtn, "RUN SELF-TEST", self.run_application_self_test, "cyan", width=14).pack(side="left", padx=(8, 0))

        defaults_card, defaults_body = self._card(settings_page, "POST-FLASH DEFAULTS", "Control whether unused capacity becomes a mounted data drive after the boot image has been verified")
        defaults_card.pack(fill="x", pady=(0, 10))
        df = tk.Frame(defaults_body, bg=self.PANEL); df.pack(fill="x")
        ChromeToggle(df, text="Auto-provision remaining capacity", variable=self.provision_remainder, style="Nexus.TCheckbutton", command=self.save_settings).pack(side="left")
        ChromeToggle(df, text="Open data volume after flash", variable=self.auto_open_data, style="Nexus.TCheckbutton", command=self.save_settings).pack(side="left", padx=(14, 0))
        ttk.Combobox(df, textvariable=self.data_fs_var, values=["exFAT", "NTFS", "FAT32"], state="readonly", style="Nexus.TCombobox", width=10).pack(side="left", padx=(16, 8))
        self._entry(df, self.data_label_var).pack(side="left", fill="x", expand=True, ipady=7)

        self._build_forensic_pages(host)

        # Persistent telemetry
        status_card, st = self._card(main, "ENTERPRISE TELEMETRY / AEGIS EVENT STREAM", "Raw-disk state, progress, throughput, verification, partition provisioning and adaptive-recovery diagnostics")
        status_card.pack(fill="x", padx=24, pady=(10, 18))
        top = tk.Frame(st, bg=self.PANEL); top.pack(fill="x")
        self.stage_label = tk.Label(top, textvariable=self.stage, bg=blend_hex(self.PANEL_2, self.CYAN, 0.08), fg=self.CYAN, font=("Consolas", 8, "bold"), padx=10, pady=5)
        self.stage_label.pack(side="left")
        tk.Label(top, textvariable=self.status, bg=self.PANEL, fg=self.TEXT, font=(self.FONT_UI, 9, "bold")).pack(side="left", padx=(10, 0))
        self.export_btn = self._button(top, "EXPORT LOG", self.export_operation_log, "ghost", width=12); self.export_btn.pack(side="right")
        self.hud_progress = HudProgressBar(st, self.progress, self.GRAD_A, self.GRAD_B, blend_hex(self.PANEL_2, "#000000", 0.28), height=18, radius=9)
        self.hud_progress.pack(fill="x", pady=(10, 5))
        tk.Label(st, textvariable=self.telemetry, bg=self.PANEL, fg=self.MUTED, font=(self.FONT_MONO, 8)).pack(anchor="w", pady=(0, 7))
        self.log = tk.Text(st, height=10, state="disabled", font=(self.FONT_MONO, 8), wrap="word", bg=blend_hex(self.BG, "#000000", 0.34), fg=blend_hex(self.TEXT, self.MUTED, 0.25), insertbackground=self.CYAN, relief="flat", bd=0, highlightthickness=1, highlightbackground=self.BORDER)
        self.log.pack(fill="both", expand=True)

        self.show_page(getattr(self, "current_page", "flash"))

    # ----- state / events -------------------------------------------------
    def logline(self, s):
        s = str(s)
        log_file(s)
        self.log.configure(state="normal")
        self.log.insert("end", s.rstrip() + "\n")
        self.log.see("end")
        self.log.configure(state="disabled")

    def export_operation_log(self):
        try:
            default_name = f"NEXUS_Imaging_Studio_Log_{time.strftime('%Y%m%d_%H%M%S')}.txt"
            path = filedialog.asksaveasfilename(
                title="Export operation log",
                defaultextension=".txt",
                initialfile=default_name,
                filetypes=[("Text log", "*.txt"), ("All files", "*.*")],
            )
            if not path:
                return
            text = self.log.get("1.0", "end-1c")
            with open(path, "w", encoding="utf-8") as f:
                f.write(text)
            messagebox.showinfo(APP_NAME, f"Operation log exported to:\n\n{path}")
        except Exception as e:
            messagebox.showerror(APP_NAME, f"Could not export log: {e}")

    def run_diagnostics(self):
        if self.busy:
            return
        sel = self.selected()
        number = int(sel["Number"]) if sel else None
        lines = raw_access_diagnostics(number)
        for line in lines:
            self.logline("DIAGNOSTIC: " + line)
        self.logline("DIAGNOSTIC: " + self.recovery.summary())
        policies = storage_write_policy_diagnostics()
        self.policy_summary.set("WRITE POLICY / BLOCKED" if policies else "WRITE POLICY / CLEAR")
        self.access_summary.set("MEDIA ACCESS / POLICY BLOCK" if policies else "MEDIA READY / ELEVATED")
        messagebox.showinfo(APP_NAME, "NEXUS write-access diagnostic\n\n" + "\n".join(lines))

    def choose_image(self):
        if self.busy:
            return
        p = filedialog.askopenfilename(
            title="Select NEXUS USB image",
            filetypes=[
                ("Boot / raw images", "*.img *.iso *.raw *.bin"),
                ("IMG", "*.img"),
                ("ISO", "*.iso"),
                ("Raw", "*.raw *.bin"),
                ("All files", "*.*"),
            ],
        )
        if not p:
            return
        self.image_var.set(p)
        self.validated_image = None
        self.start.configure(state="disabled")
        size = Path(p).stat().st_size
        self.image_summary.set(f"{Path(p).name}  •  {human_size(size)}  •  validation running…")
        self.stage.set("VALIDATE")
        self.status.set("Inspecting MBR/GPT, EFI partition, FAT32 structure, and BOOTX64.EFI…")
        threading.Thread(
            target=lambda: self.events.put(("image_validation", (p, validate_boot_image(p)))),
            daemon=True,
        ).start()

    def refresh(self):
        if self.busy:
            return
        self.refresh_btn.configure(state="disabled")
        threading.Thread(target=self._refresh_worker, daemon=True).start()

    def _refresh_worker(self):
        try:
            self.events.put(("disks", enumerate_usb_disks()))
        except Exception as e:
            self.events.put(("scan_error", f"USB scan failed: {e}"))

    def set_disks(self,ds):
        previous=self.selected();self.disks=list(ds)
        vals=[f"Disk {d['Number']}  •  {d.get('FriendlyName') or 'USB'}  •  {human_size(int(d['Size']))}  •  {d.get('BusType','USB')}" for d in self.disks]
        self.combo["values"]=vals;self.disk_var.set("")
        if previous:
            matches=[i for i,d in enumerate(self.disks) if int(d["Number"])==int(previous["Number"]) and _media_identity_strength(previous,d)>=7]
            if len(matches)==1:self.combo.current(matches[0])
        self.partition_rows={}
        if hasattr(self,"partition_tree"):
            for row in self.partition_tree.get_children():self.partition_tree.delete(row)
        self.refresh_btn.configure(state="disabled" if self.busy else "normal")
        self.on_disk_selected();self.update_start_state()

    def selected(self):
        i = self.combo.current()
        return self.disks[i] if 0 <= i < len(self.disks) else None

    def on_disk_selected(self):
        self.partition_rows = {}
        if hasattr(self, "partition_tree"):
            for row in self.partition_tree.get_children(): self.partition_tree.delete(row)
        d = self.selected()
        if not d:
            self.disk_summary.set("Select a device explicitly; no automatic target is armed.")
            self.access_summary.set("NO TARGET / DISARMED")
            self.diskmap_summary.set("Select media to inspect partitions.")
            self.update_start_state()
            return
        serial = str(d.get("SerialNumber") or "").strip() or "n/a"
        if len(serial) > 36:
            serial = serial[:33] + "…"
        flags = []
        if d.get("IsReadOnly"):
            flags.append("READ-ONLY")
        if d.get("IsOffline"):
            flags.append("OFFLINE")
        flags.append(str(d.get("HealthStatus") or "Health n/a"))
        self.disk_summary.set(
            f"Disk {d['Number']}  |  {d.get('FriendlyName') or 'Removable media'}  |  {human_size(int(d['Size']))}\n"
            f"Bus {d.get('BusType')}  |  Map {d.get('PartitionStyle')}  |  Partitions {d.get('NumberOfPartitions')}  |  "
            f"Logical sector {d.get('LogicalSectorSize') or 512} B  |  Free {human_size(int(d.get('LargestFreeExtent') or 0))}  |  {' / '.join(flags)}\n"
            f"Serial {serial}"
        )
        policies = storage_write_policy_diagnostics()
        self.policy_summary.set("WRITE POLICY / BLOCKED" if policies else "WRITE POLICY / CLEAR")
        if d.get("IsReadOnly"):
            self.access_summary.set("RAW ACCESS / READ-ONLY")
        elif policies:
            self.access_summary.set("RAW ACCESS / POLICY BLOCK")
        else:
            self.access_summary.set("MEDIA READY / ELEVATED" if is_admin() else "MEDIA / NOT ELEVATED")
        self.update_start_state()
        if getattr(self, "current_page", "") == "disk":
            self.refresh_partition_view()

    def update_start_state(self):
        info=self.validated_image or {};path=self.image_var.get()
        image_ok=bool(info.get("valid") and info.get("_path")==path)
        try:
            st=Path(path).stat();stamp=(st.st_size,st.st_mtime_ns)
            image_ok=image_ok and tuple(info.get("_stamp",()))==stamp
            exists=Path(path).is_file()
        except (OSError,ValueError):exists=False;image_ok=False
        can=not self.busy and bool(self.selected()) and exists and (image_ok or self.force_raw.get())
        self.start.configure(state="normal" if can else "disabled")

    def set_running(self,running):
        running=bool(running)
        if running and not self.busy:
            self._frozen_controls=[]
            for w in self._walk_widgets():
                if isinstance(w,RoundedButton):
                    if getattr(w,"_is_nav",False) or w in (self.pause,self.stop,self.export_btn):continue
                    if getattr(w,"_lab_control",False):continue
                elif not isinstance(w,(ttk.Combobox,ttk.Checkbutton,tk.Entry,tk.Scale,ChromeToggle)):
                    continue
                try:
                    state=w.cget("state");self._frozen_controls.append((w,state));w.configure(state="disabled")
                except tk.TclError:pass
        self.busy=running
        if not running:
            for w,state in getattr(self,"_frozen_controls",[]):
                try:
                    if w.winfo_exists():w.configure(state=state)
                except tk.TclError:pass
            self._frozen_controls=[];self.paused=False;self.pause_event.set()
        self.start.configure(state="disabled")
        self.pause.configure(state="normal" if running else "disabled",text="PAUSE")
        self.stop.configure(state="normal" if running else "disabled")
        self.export_btn.configure(state="normal")
        for w in getattr(self,"_lab_pause_buttons",[]):w.configure(state="normal" if running and getattr(self,"_lab_job",None) else "disabled",text="PAUSE")
        for w in getattr(self,"_lab_stop_buttons",[]):w.configure(state="normal" if running and getattr(self,"_lab_job",None) else "disabled")
        if not running:self.update_start_state()

    def toggle_pause(self):
        if not self.busy or self.pause.cget("state")=="disabled":return
        self.paused=not self.paused
        if self.paused:self.pause_event.clear()
        else:self.pause_event.set()
        text="RESUME" if self.paused else "PAUSE"
        self.pause.configure(text=text)
        for b in getattr(self,"_lab_pause_buttons",[]):b.configure(text=text)
        self.stage.set("PAUSE REQUESTED" if self.paused else "RESUME")
        self.status.set("Pause requested; the worker will wait at its next checkpoint." if self.paused else "Resuming operation…")

    def request_stop(self):
        if not self.busy or self.stop.cget("state")=="disabled":return
        kind=getattr(self,"_lab_job",None)
        detail=("Bytes already overwritten cannot be recovered. An interrupted erase is INCOMPLETE and will not receive a successful verification result." if kind=="ERASE" else
                "The source image will not be modified. Any partial extraction is retained with an incomplete manifest." if kind in ("SCAN","EXTRACT") else
                "A partially written image may not boot. A partial image backup will remain marked .partial. No rollback is possible for bytes already written.")
        if messagebox.askyesno(APP_NAME,"Stop at the next checkpoint?\n\n"+detail,icon="warning"):
            self.cancel_event.set();self.pause_event.set();self.stage.set("STOPPING")
            self.status.set("Waiting for the next checkpoint, cleanup and final report…")

    def checkpoint(self):
        if self.cancel_event.is_set():raise InterruptedError("Stopped by user.")
        while not self.pause_event.wait(.15):
            if self.cancel_event.is_set():raise InterruptedError("Stopped by user.")
        if self.cancel_event.is_set():raise InterruptedError("Stopped by user.")

    def confirm_word(self, word, title, detail=None):
        d = tk.Toplevel(self)
        d.withdraw()  # measure and position before the first visible frame
        d.title(title)
        d.configure(bg=self.BG)
        d.transient(self)
        d.resizable(False, False)
        f = tk.Frame(d, bg=self.PANEL, padx=20, pady=18)
        f.pack(fill="both", expand=True, padx=1, pady=1)
        tk.Label(f, text=title.upper(), bg=self.PANEL, fg=self.CYAN, font=(self.FONT_DISPLAY, 10, "bold")).pack(anchor="w")
        if detail:
            tk.Label(f, text=detail, bg=self.PANEL, fg=self.MUTED, font=(self.FONT_UI, 9), justify="left", wraplength=460).pack(anchor="w", pady=(8, 6))
        tk.Label(f, text=f"Type {word} to continue:", bg=self.PANEL, fg=self.TEXT, font=(self.FONT_DISPLAY, 10, "bold")).pack(anchor="w", pady=(6, 4))
        v = tk.StringVar()
        e = self._entry(f, v)
        e.pack(fill="x", ipady=7, pady=(0, 8))
        hint = tk.StringVar()
        tk.Label(f, textvariable=hint, bg=self.PANEL, fg=self.RED, font=(self.FONT_UI, 9)).pack(anchor="w", pady=(0, 8))
        ans = {"ok": False}
        previous_focus = self.focus_get()

        def close():
            try:
                d.grab_release()
            except tk.TclError:
                pass
            d.destroy()

        def ok():
            if v.get().strip() != word:
                hint.set(f"Enter {word} exactly to confirm, or choose Cancel.")
                e.focus_set()
                e.selection_range(0, "end")
                return
            ans["ok"] = True
            close()

        row = tk.Frame(f, bg=self.PANEL)
        row.pack(fill="x")
        self._button(row, "CANCEL", close, "ghost", width=10).pack(side="right")
        self._button(row, "CONTINUE", ok, "red", width=10).pack(side="right", padx=(0, 8))
        d.protocol("WM_DELETE_WINDOW", close)
        d.bind("<Escape>", lambda _e: close())
        d.bind("<Return>", lambda _e: ok())
        show_centered_dialog(d, self)
        if not d.winfo_viewable():
            d.wait_visibility()
        d.grab_set()
        e.focus_set()
        self.wait_window(d)
        try:
            (previous_focus or self).focus_set()
        except tk.TclError:
            pass
        return ans["ok"]

    # ----- disk manager / eject / adaptive recovery ----------------------
    def selected_partition(self):
        try:
            chosen = self.partition_tree.selection()
            if not chosen:
                return None
            values = self.partition_tree.item(chosen[0], "values")
            if not values:
                return None
            pnum = int(values[0])
            return getattr(self, "partition_rows", {}).get(pnum)
        except Exception:
            return None

    def refresh_partition_view(self):
        if self.busy:
            return
        if not hasattr(self, "partition_tree"):
            return
        sel = self.selected()
        if not sel:
            self.diskmap_summary.set("Disk Manager: no removable media selected.")
            for item in self.partition_tree.get_children():
                self.partition_tree.delete(item)
            return
        number = int(sel["Number"])
        self.diskmap_summary.set(f"Disk {number}: reading partition map…")

        def worker():
            try:
                d = get_disk(number)
                parts = enumerate_partitions(number)
                self.events.put(("partition_data", (d, parts)))
            except Exception as e:
                self.events.put(("log", f"DISK MANAGER ERROR: {e}"))
        threading.Thread(target=worker, daemon=True).start()

    def _run_disk_action(self, stage, description, func):
        if self.busy:
            return
        sel = self.selected()
        if not sel: return
        expected = dict(sel)
        try:
            safe_removable_disk(int(sel["Number"]), expected)
            guard_runtime_outside_target(int(sel["Number"]))
        except Exception as exc:
            messagebox.showerror(APP_NAME, str(exc))
            return
        self.stage.set(stage)
        self.status.set(description)
        self.set_running(True)
        self.pause.configure(state="disabled")
        self.stop.configure(state="disabled")

        def worker():
            try:
                safe_removable_disk(int(expected["Number"]), expected)
                result = func()
                self.events.put(("disk_action_done", (stage, result)))
            except Exception as e:
                self.events.put(("error", f"Disk Manager: {e}"))
        threading.Thread(target=worker, daemon=True).start()

    def disk_create_data(self):
        sel = self.selected()
        if not sel or self.busy:
            return
        fs = self.dm_fs_var.get(); label = sanitize_label(self.dm_label_var.get())
        if not messagebox.askyesno(APP_NAME, f"Create a new {fs} data partition from all available unallocated space on Disk {sel['Number']}?\n\nExisting partitions will not be deleted."):
            return
        self._run_disk_action("CREATE PARTITION", "Creating and mounting a data partition…", lambda: provision_remainder_partition(int(sel["Number"]), fs, label))

    def disk_format_selected(self):
        sel = self.selected(); part = self.selected_partition()
        if not sel or not part or self.busy:
            messagebox.showwarning(APP_NAME, "Select a normal data partition first.")
            return
        if partition_is_protected(part):
            messagebox.showerror(APP_NAME, "AEGIS protection: EFI/System/Recovery partitions cannot be formatted here.")
            return
        fs = self.dm_fs_var.get(); label = sanitize_label(self.dm_label_var.get())
        detail = f"Disk {sel['Number']} partition {part['PartitionNumber']} — {human_size(int(part.get('Size') or 0))}\nFormat as {fs} / {label}\n\nALL FILES ON THIS PARTITION WILL BE ERASED."
        if not self.confirm_word("FORMAT", "Format partition", detail):
            return
        self._run_disk_action("FORMAT", "Formatting selected data partition…", lambda: format_partition(int(sel["Number"]), int(part["PartitionNumber"]), fs, label, False))

    def disk_delete_selected(self):
        sel = self.selected(); part = self.selected_partition()
        if not sel or not part or self.busy:
            messagebox.showwarning(APP_NAME, "Select a normal data partition first.")
            return
        if partition_is_protected(part):
            messagebox.showerror(APP_NAME, "AEGIS protection: protected boot/system partitions cannot be deleted individually. Use Recovery / Reset to intentionally reclaim the entire USB.")
            return
        detail = f"Delete Disk {sel['Number']} partition {part['PartitionNumber']} ({human_size(int(part.get('Size') or 0))})?\n\nThe partition and all of its files will be permanently removed."
        if not self.confirm_word("DELETE", "Delete partition", detail):
            return
        self._run_disk_action("DELETE", "Deleting selected data partition…", lambda: delete_partition(int(sel["Number"]), int(part["PartitionNumber"])))

    def disk_assign_letter(self):
        sel = self.selected(); part = self.selected_partition()
        if not sel or not part or self.busy:
            return
        if partition_is_protected(part):
            messagebox.showerror(APP_NAME, "AEGIS protection: boot/system partitions are not exposed with a drive letter.")
            return
        self._run_disk_action("MOUNT", "Assigning a Windows drive letter…", lambda: assign_partition_letter(int(sel["Number"]), int(part["PartitionNumber"])))

    def disk_remove_letter(self):
        sel = self.selected(); part = self.selected_partition()
        if not sel or not part or self.busy:
            return
        self._run_disk_action("UNMOUNT", "Removing the Windows drive letter…", lambda: remove_partition_letter(int(sel["Number"]), int(part["PartitionNumber"])))

    def disk_extend_selected(self):
        sel = self.selected(); part = self.selected_partition()
        if not sel or not part or self.busy:
            return
        if partition_is_protected(part):
            messagebox.showerror(APP_NAME, "AEGIS protection: only normal data partitions can be extended.")
            return
        self._run_disk_action("EXTEND", "Extending the selected partition into adjacent free space…", lambda: extend_partition_to_max(int(sel["Number"]), int(part["PartitionNumber"])))

    def disk_make_writable(self):
        sel = self.selected()
        if not sel or self.busy:
            return
        self._run_disk_action("WRITABLE", "Clearing removable-media read-only/offline attributes…", lambda: make_disk_writable(int(sel["Number"])))

    def disk_toggle_online(self):
        sel = self.selected()
        if not sel or self.busy:
            return
        number = int(sel["Number"]); desired = not bool(sel.get("IsOffline"))
        label = "OFFLINE" if desired else "ONLINE"
        self._run_disk_action(label, f"Setting Disk {number} {label.lower()}…", lambda: set_disk_offline_strict(number, desired))

    def disk_open_mount(self):
        part = self.selected_partition()
        if not part:
            return
        letter = str(part.get("DriveLetter") or "").strip()
        if not letter:
            messagebox.showwarning(APP_NAME, "The selected partition has no Windows drive letter. Use ASSIGN LETTER first.")
            return
        if os.name == "nt":
            subprocess.Popen(["explorer.exe", f"{letter}:\\"])

    def backup_selected_to_image(self):
        if self.busy:
            return
        sel = self.selected()
        if not sel:
            messagebox.showwarning(APP_NAME, "Select removable media to back up.")
            return
        output = filedialog.asksaveasfilename(
            title="Create raw image backup from selected media",
            defaultextension=".img",
            initialfile=f"NEXUS_Disk{sel['Number']}_backup.img",
            filetypes=[("Raw disk image", "*.img"), ("All files", "*.*")],
        )
        if not output:
            return
        number = int(sel["Number"])
        self.cancel_event.clear(); self.pause_event.set(); self.progress.set(0)
        self._backup_active = True
        self.stage.set("IMAGE BACKUP"); self.status.set("Reading the full physical device into a raw image…")
        self.set_running(True)

        def worker():
            try:
                def prog(done, total, started):
                    elapsed = max(time.time()-started, 0.01)
                    speed = done/elapsed; eta = (total-done)/speed if speed else float("inf")
                    self.events.put(("progress", done*100/max(total,1)))
                    self.events.put(("status", f"Creating image backup — {done*100/max(total,1):.1f}%"))
                    self.events.put(("telemetry", f"Read {human_size(int(speed))}/s   •   ETA {human_time(eta)}   •   Saved {human_size(done)} / {human_size(total)}"))
                result = backup_disk_to_image(number, output, checkpoint=self.checkpoint, progress=prog)
                self.events.put(("backup_done", result))
            except InterruptedError as e:
                self.events.put(("cancelled", str(e)))
            except Exception as e:
                self.events.put(("error", f"Image backup failed: {e}"))
        threading.Thread(target=worker, daemon=True).start()

    def safe_eject_selected(self):
        if self.busy:
            messagebox.showwarning(APP_NAME, "Wait for the current media operation to finish before ejecting.")
            return
        sel = self.selected()
        if not sel:
            messagebox.showwarning(APP_NAME, "Select removable media to eject.")
            return
        number = int(sel["Number"])
        if not messagebox.askyesno(APP_NAME, f"Safely eject Disk {number} — {sel.get('FriendlyName') or 'removable media'}?\n\nAEGIS will flush caches, dismount filesystems and request hardware removal from Windows."):
            return
        self.stage.set("SAFE EJECT")
        self.status.set("Flushing, dismounting and requesting safe hardware removal…")
        self.set_running(True)
        self.pause.configure(state="disabled"); self.stop.configure(state="disabled")

        def worker():
            try:
                result = safe_eject_disk(number, log=lambda t: self.events.put(("log", t)))
                self.events.put(("ejected", result))
            except Exception as e:
                self.events.put(("error", f"Safe eject failed: {e}"))
        threading.Thread(target=worker, daemon=True).start()

    def apply_recovery_preflight(self):
        self.adaptive_profile=self.recovery.adaptive_profile();self.recovery_status.set(self.recovery.summary())
        self._adaptive_delay=float(self.adaptive_profile.get("mount_manager_delay",.25)) if self.self_heal_var.get() else .25
        if self.self_heal_var.get() and self.adaptive_profile.get("aggressive_reclaim"):
            self.logline("AEGIS: prior access contention recorded; extended settle time armed. Verification mode will not be downgraded.")
        if self.self_heal_var.get() and self.recovery.count("GPT_VERIFY_NORMALIZATION") > 0:
            self.logline("AEGIS v3.2: prior GPT-normalization mismatches recorded; atomic raw write/certification barrier is armed before Windows storage refresh. Verification mode is preserved.")
        current=normalize_verify_mode(self.verify_mode.get());self.verify_mode.set(verification_display_name(current))
        self.verify_guard_status.set("Effective verification: "+verification_display_name(current)+" — strict mode never silently falls back")

    # ----- flash workflow -------------------------------------------------
    def start_write(self):
        if self.busy:
            return
        img = Path(self.image_var.get())
        if not img.is_file():
            messagebox.showerror(APP_NAME, "Select a valid image file.")
            return
        sel = self.selected()
        if not sel:
            messagebox.showerror(APP_NAME, "Select a removable target device.")
            return
        try:
            cur = safe_removable_disk(int(sel["Number"]), sel)
        except Exception as e:
            messagebox.showerror(APP_NAME, str(e))
            return
        if img.stat().st_size > int(cur["Size"]):
            messagebox.showerror(APP_NAME, "Image is larger than the target USB.")
            return
        try:
            guard_runtime_outside_target(int(cur["Number"]), img)
            confirmed_source_stamp = image_stamp(img)
            fresh_validation = validate_boot_image(img)
            if image_stamp(img) != confirmed_source_stamp:
                raise MediaOperationError("SOURCE_CHANGED", "Source changed while validating. Reselect the image.")
        except Exception as exc:
            messagebox.showerror(APP_NAME, str(exc))
            return
        strict_valid = bool(fresh_validation.get("valid"))
        if strict_valid and int(cur.get("LogicalSectorSize") or 512) != 512:
            messagebox.showerror(APP_NAME, "This boot-image validator supports 512-byte logical-sector targets only. A 4Kn image conversion has NOT been implemented.")
            return
        if not strict_valid and not self.force_raw.get():
            messagebox.showerror(APP_NAME, "Image validation failed. Use a valid hybrid USB image or explicitly enable Advanced raw mode.")
            return

        mode = "STRICT UEFI" if strict_valid else "ADVANCED RAW / UNVALIDATED"
        warning = (
            f"Disk {cur['Number']} — {cur.get('FriendlyName')} — {human_size(int(cur['Size']))}\n"
            f"Image: {img.name} — {human_size(img.stat().st_size)}\n"
            f"Mode: {mode}\n\n"
            "NEXUS will forcibly remove ALL existing partitions, including EFI/OEM/hidden partitions, then overwrite the physical disk from sector 0."
        )
        if not messagebox.askyesno(APP_NAME, "ERASE and flash this removable device?\n\n" + warning, icon="warning"):
            return
        if not self.confirm_word("ERASE", "Final flash confirmation", warning):
            return

        try:
            cur = safe_removable_disk(int(cur["Number"]), cur)
            guard_runtime_outside_target(int(cur["Number"]), img)
        except Exception as exc:
            messagebox.showerror(APP_NAME, str(exc))
            return
        self.apply_recovery_preflight()
        self.save_settings()
        verify_mode = normalize_verify_mode(self.verify_mode.get())
        self.verify_mode.set(verification_display_name(verify_mode))
        self.verify_guard_status.set(f"AEGIS effective verification: {verification_display_name(verify_mode)}")
        provision_cfg = {
            "_source_stamp": confirmed_source_stamp,
            "enabled": bool(self.provision_remainder.get()),
            "open_after": bool(self.auto_open_data.get()),
            "filesystem": self.data_fs_var.get(),
            "label": sanitize_label(self.data_label_var.get()),
        }
        self.cancel_event.clear()
        self.pause_event.set()
        self.progress.set(0)
        self.telemetry.set("Speed —   •   ETA —   •   Written —")
        self.set_running(True)
        threading.Thread(
            target=self._write_worker,
            args=(img, dict(cur), bool(self.verify.get()), strict_valid, verify_mode, provision_cfg, bool(self.self_heal_var.get())),
            daemon=True,
        ).start()

    def _write_worker(self, img, disk, verify, strict_valid, verify_mode, provision_cfg, adaptive_enabled=True):
        num = int(disk["Number"])
        automount_changed = False
        terminal = None
        source_guard = None
        try:
            source_guard = SourceImageGuard(img, provision_cfg.get("_source_stamp"))
            total = source_guard.stamp[2]
            sector = int(disk.get("LogicalSectorSize") or 512)
            if sector not in (512, 1024, 2048, 4096):
                raise RuntimeError("Unsupported target logical-sector size.")
            if align_up(total, sector) > int(disk["Size"]):
                raise RuntimeError("Aligned image write would exceed target media size.")
            resolved = wait_for_target_media(disk, num, timeout=6.0, log=lambda s: self.events.put(("log", s)))
            num = int(resolved["Number"])
            guard_runtime_outside_target(num, img)
            self.checkpoint()
            if not get_automount_disabled():
                automount_changed = True
                set_automount_disabled(True, log=lambda text: self.events.put(("log", text)))

            self.events.put(("stage", "RECLAIM"))
            self.events.put(("status", "Dismounting EFI volumes and preparing guarded raw-disk access…"))
            prepare_disk_for_flash(num, disk, log=lambda s: self.events.put(("log", s)), checkpoint=self.checkpoint)
            settle = float(getattr(self, "_adaptive_delay", 0.25))
            if settle > 0.25:
                self.events.put(("log", f"AEGIS SELF-HEAL: applying {settle:.2f}s adaptive mount-manager settle delay from prior recovery history."))
                time.sleep(settle)
            self.checkpoint()

            source_guard.check()
            sector = max(512, int(disk.get("LogicalSectorSize") or 512))
            padded_total = align_up(total, sector)
            if padded_total > int(disk["Size"]):
                raise RuntimeError("Aligned image write would exceed target media size.")
            if padded_total != total:
                self.events.put(("log", f"ALIGNMENT: final write padded by {padded_total-total} zero byte(s) to {sector}-byte sector boundary."))

            src_hash = None
            locked_verify = None
            locked_post = None
            mode_name = verify_mode
            verify_started = time.time()

            def verify_progress(checked, total_bytes):
                elapsed = max(time.time() - verify_started, 0.01)
                speed = checked / elapsed
                eta = (total_bytes - checked) / speed if speed > 0 else float("inf")
                pct = checked * 100 / max(total_bytes, 1)
                self.events.put(("progress", pct))
                self.events.put(("status", f"Verification — {pct:.1f}%"))
                self.events.put(("telemetry", f"Read {human_size(int(speed))}/s   •   ETA {human_time(eta)}   •   Verified {human_size(checked)} / {human_size(total_bytes)}"))

            def log_verify_mismatch(prefix, result):
                off = int(result.get("mismatch_offset") or 0)
                self.events.put(("log", f"{prefix}: first differing byte at offset {off} (0x{off:08X})."))
                if result.get("source_sample_hex"):
                    self.events.put(("log", f"{prefix} EXPECTED: " + result["source_sample_hex"]))
                if result.get("target_sample_hex"):
                    self.events.put(("log", f"{prefix} ACTUAL:   " + result["target_sample_hex"]))
                return off

            for write_attempt in (1, 2, 3):
                safe_removable_disk(num, disk)
                started = time.time()
                self.events.put(("stage", "WRITE" if write_attempt == 1 else f"RAW RETRY {write_attempt-1}"))
                self.events.put(("status", "Writing image from physical sector 0…" if write_attempt == 1 else f"Re-acquired target — raw retry {write_attempt-1}/2 from sector 0…"))
                try:
                    with img.open("rb", buffering=0) as f, open_physical_certification_handle(num) as h:
                        self.events.put(("log", f"RAW ACCESS MODE: {h.mode}; volume locks retained through readback."))
                        allow_extended_dasd_io(h.h)
                        _assert_open_disk_geometry(h.h, num, int(disk["Size"]))
                        source_guard.check()
                        def write_progress(written, total_bytes):
                            elapsed = max(time.time() - started, 0.01)
                            speed = written / elapsed
                            eta = (total_bytes - written) / speed if speed > 0 else float("inf")
                            pct = written * 100 / max(total_bytes, 1)
                            self.events.put(("progress", pct))
                            self.events.put(("status", f"Writing image — {pct:.1f}%"))
                            self.events.put(("telemetry", f"Speed {human_size(int(speed))}/s   •   ETA {human_time(eta)}   •   Written {human_size(written)} / {human_size(total_bytes)}"))
                        written_hash = copy_image_stream(f, h.h, total, sector, self.checkpoint, write_progress)
                        source_guard.check()
                        if not kernel32.FlushFileBuffers(h.h):
                            raise win_error("Flush failed")
                        _assert_open_disk_geometry(h.h, num, int(disk["Size"]))

                        # v3.2 certification barrier: do not release the raw write handle and
                        # do not call Update-HostStorageCache / IOCTL_DISK_UPDATE_PROPERTIES
                        # until structure checks and exact requested readback have completed.
                        # Windows can legitimately relocate/repair a small image's backup GPT
                        # on a larger USB after discovery; doing that before strict readback is
                        # what produced the repeat mismatch at byte 528 in v3.1.
                        self.events.put(("stage", "VALIDATE-LOCKED"))
                        self.events.put(("status", "Validating UEFI structure before requesting Windows storage refresh…"))
                        locked_post = validate_boot_reader(RawHandleReader(h.h, int(disk["Size"])), ".img")
                        if strict_valid and not locked_post.get("valid"):
                            raise RuntimeError("USB STRUCTURE VALIDATION FAILED UNDER RAW LOCK: " + "; ".join(locked_post.get("errors", [])))

                        if verify and mode_name != "Structure only":
                            self.events.put(("stage", "VERIFY-LOCKED"))
                            self.events.put(("status", "Certifying exact image bytes under the raw-media barrier…"))
                            self.events.put(("log", "AEGIS v3.2 CERTIFICATION BARRIER: exact readback is occurring before any Windows disk-property refresh or post-flash GPT expansion."))
                            verify_started = time.time()
                            locked_verify = verify_image_against_open_handle(
                                img, h.h, total, sector, checkpoint=self.checkpoint, progress=verify_progress
                            )
                            locked_verify["mode"] = "strict-locked"
                            self.events.put(("log", f"LOCKED SOURCE SHA-256: {locked_verify['source_hash']}"))
                            self.events.put(("log", f"LOCKED TARGET SHA-256: {locked_verify['target_hash']}"))
                            if not locked_verify["match"]:
                                first_off = log_verify_mismatch("LOCKED VERIFY MISMATCH", locked_verify)
                                self.events.put(("stage", "RE-VERIFY-LOCKED"))
                                self.events.put(("status", "Mismatch under certification barrier — performing a second raw read before releasing the device…"))
                                time.sleep(0.20)
                                verify_started = time.time()
                                second = verify_image_against_open_handle(
                                    img, h.h, total, sector, checkpoint=self.checkpoint, progress=verify_progress
                                )
                                second["mode"] = "strict-locked"
                                self.events.put(("log", f"LOCKED RE-VERIFY SOURCE SHA-256: {second['source_hash']}"))
                                self.events.put(("log", f"LOCKED RE-VERIFY TARGET SHA-256: {second['target_hash']}"))
                                if not second["match"]:
                                    off2 = log_verify_mismatch("LOCKED RE-VERIFY MISMATCH", second)
                                    in_gpt = mismatch_is_gpt_metadata(img, off2)
                                    detail = (
                                        "The mismatch is inside source GPT metadata, but it persisted while the v3.2 raw certification barrier was still held; "
                                        "it is therefore not being excused as Windows post-write GPT normalization."
                                        if in_gpt else
                                        "The mismatch is outside the source GPT metadata ranges and is treated as a genuine write/readback failure."
                                    )
                                    raise RuntimeError(
                                        "VERIFICATION FAILED INSIDE THE RAW CERTIFICATION BARRIER.\n\n"
                                        f"First persistent mismatch at byte offset {off2} (0x{off2:08X}).\n\n"
                                        + detail
                                        + "\n\nAEGIS will not certify this write. Reclaim and retry; if the same media repeats the locked mismatch, use different media or a different USB port/controller."
                                    )
                                locked_verify = second
                                self.events.put(("log", f"LOCKED RE-VERIFY PASS: the first read mismatch at 0x{first_off:08X} was transient and did not persist."))
                            self.events.put(("log", "LOCKED BYTE VERIFY PASS: source and target image bytes are identical before host GPT normalization is permitted."))

                    source_guard.check()
                    src_hash = written_hash
                    break
                except Exception as e:
                    is_access_denied = "Windows error 5" in str(e) or "Access is denied" in str(e)
                    is_not_ready = is_windows_error_not_ready(e)
                    recoverable = is_recoverable_media_error(e)
                    if write_attempt < 3 and recoverable:
                        self.events.put(("stage", "MEDIA HEAL"))
                        self.events.put(("log", f"AEGIS MEDIA HEAL: raw attempt {write_attempt} failed with a recoverable storage error: {e}"))
                        self.events.put(("status", "Storage controller changed state — re-identifying the selected media and rebuilding guarded raw access…"))
                        refresh_storage_cache()
                        time.sleep(0.45 * write_attempt)
                        rebound = wait_for_target_media(disk, num, timeout=10.0, log=lambda s: self.events.put(("log", s)))
                        old_num = num
                        num = int(rebound["Number"])
                        if num != old_num:
                            self.events.put(("log", f"AEGIS MEDIA HEAL: Windows renumbered the target from PhysicalDrive{old_num} to PhysicalDrive{num}; stable identity match confirmed."))
                        guard_runtime_outside_target(num, img)
                        source_guard.check()
                        self.checkpoint()
                        prepare_disk_for_flash(num, disk, log=lambda s: self.events.put(("log", s)), checkpoint=self.checkpoint)
                        self.events.put(("progress", 0))
                        continue
                    if is_access_denied:
                        diag = raw_access_diagnostics(num)
                        for line in diag:
                            self.events.put(("log", "ACCESS DIAGNOSTIC: " + line))
                        policies = storage_write_policy_diagnostics()
                        if policies:
                            raise RuntimeError(
                                "RAW WRITE BLOCKED BY WINDOWS POLICY. The device was cleaned and reclaimed, but Windows still denied sector writes.\n\n"
                                + "\n".join(policies)
                                + "\n\nThis is an OS policy block, not an EFI partition lock."
                            )
                        raise RuntimeError(
                            "RAW WRITE ACCESS IS STILL DENIED AFTER EFI/OEM RECLAIM, VOLUME DISMOUNT, PRIVILEGE ENABLEMENT, AUTOMOUNT SHIELDING, AND EXCLUSIVE-ACCESS RETRY.\n\n"
                            "Windows still refused access. This message alone cannot establish whether the cause is a volume lock, security policy, another application, or hardware write protection.\n\n"
                            "Use RUN MEDIA DIAGNOSTICS and export the operation log.\n\n"
                            f"Original failure: {e}"
                        ) from e
                    if is_not_ready:
                        raise RuntimeError(
                            "RAW WRITE FAILED: the removable device reported 'device is not ready' during sector-level I/O even after the compatibility retry.\n\n"
                            "This usually indicates unstable media, a USB bridge/controller reset, a flaky port/hub, or the flash controller entering a fault state. Try a direct motherboard USB port and a different USB device."
                        ) from e
                    raise

            if not src_hash:
                raise RuntimeError("Raw write did not complete.")

            self.events.put(("log", f"SOURCE SHA-256: {src_hash}"))
            if verify and mode_name != "Structure only" and locked_verify and not locked_verify.get("match"):
                raise RuntimeError("Internal certification state is inconsistent: locked verification did not pass.")

            # Only now expose the newly written partition table to the Windows storage
            # manager. Any subsequent GPT relocation is a post-certification host/layout
            # change and cannot retroactively invalidate the exact locked readback.
            self.events.put(("log", "CERTIFICATION BARRIER RELEASED: Windows disk-property refresh is now permitted."))
            safe_removable_disk(num, disk)
            update_disk_properties(num)
            refresh_storage_cache()
            time.sleep(0.20)

            self.events.put(("stage", "VALIDATE"))
            self.events.put(("status", "Validating the host-visible written media after certification…"))
            with open_physical_retry(num, GENERIC_READ) as h:
                post = validate_boot_reader(RawHandleReader(h.h, int(disk["Size"])), ".img")
            if strict_valid:
                if not post.get("valid"):
                    raise RuntimeError("USB STRUCTURE VALIDATION FAILED AFTER HOST REFRESH: " + "; ".join(post.get("errors", [])))
                self.events.put(("log", f"USB STRUCTURE PASS: {post['format']} / EFI loader {post['loader_size']} bytes"))
            else:
                if post.get("valid"):
                    self.events.put(("log", f"RAW IMAGE ALSO PASSED UEFI CHECK: {post['format']} / EFI loader {post['loader_size']} bytes"))
                else:
                    self.events.put(("log", "RAW MODE NOTE: post-write UEFI validation not enforced: " + "; ".join(post.get("errors", []))))

            if verify:
                if mode_name == "Structure only":
                    self.events.put(("log", "VERIFY MODE: structure-only validation selected; byte-for-byte verification skipped."))
                else:
                    # v3.2.2 certification boundary:
                    #
                    # The exact byte-for-byte certification already completed while the
                    # raw handle and any volume locks were still held. Once that handle is
                    # released, Windows storage/filesystem services may legitimately update
                    # host-managed filesystem metadata (for example FAT32 FSInfo counters,
                    # FAT allocation state, or other mount bookkeeping). A second bytewise
                    # comparison after host discovery is therefore not a valid test of the
                    # original raw write and previously caused false failures at 0x090003E8
                    # and 0x0900400C.
                    #
                    # Do NOT broaden ignore ranges to the FAT or filesystem. Instead, keep
                    # the locked exact certification authoritative and use the post-handoff
                    # phase only as a structural/boot-health gate.
                    if not locked_verify or not locked_verify.get("match"):
                        raise RuntimeError(
                            "Internal certification state is inconsistent: exact locked "
                            "byte-for-byte verification was not proven before host handoff."
                        )

                    self.events.put(("stage", "POST-CERT HEALTH"))
                    self.events.put(("status", "Validating host-visible boot/GPT health after the certified raw-media handoff…"))
                    self.events.put(("log", "READBACK PASS: source and target were byte-identical while the same raw handle and volume locks were held."))
                    self.events.put(("log", "POST-CERT POLICY: host-visible byte changes after raw-handle release are not used to retroactively invalidate the locked certification; Windows may update filesystem bookkeeping during device discovery."))

                    if strict_valid and not post.get("valid"):
                        raise RuntimeError(
                            "POST-CERTIFICATION BOOT/GPT HEALTH CHECK FAILED.\n\n"
                            + "; ".join(post.get("errors", []))
                            + "\n\nThe raw write had certified exactly under lock, but the host-visible "
                              "boot structure is no longer valid. AEGIS will not continue to provisioning."
                        )

                    if post.get("valid"):
                        self.events.put((
                            "log",
                            f"POST-CERT HOST HEALTH PASS: {post.get('format')} / EFI loader "
                            f"{post.get('loader_size')} bytes. Locked byte certification remains authoritative."
                        ))
                    elif not strict_valid:
                        self.events.put((
                            "log",
                            "POST-CERT HOST HEALTH NOTE: advanced raw mode does not require UEFI structure validation. "
                            "Locked byte certification remains the only payload-certification result."
                        ))

                    if mode_name == "Smart verify (recommended)":
                        self.events.put(("log", "SMART VERIFY RESULT: exact locked payload certification PASS + post-handoff structural health PASS. No post-mount byte-for-byte re-certification was attempted."))
                    else:
                        self.events.put(("log", "STRICT VERIFY RESULT: exact locked byte-for-byte certification PASS. Post-handoff Windows filesystem mutations are outside the sealed certification instant and do not downgrade that result."))

            done_message = ("UEFI STRUCTURE VALIDATED / IMAGE WRITTEN" if strict_valid else "RAW IMAGE WRITTEN / BOOTABILITY NOT CERTIFIED")
            done_message += (" / LOCKED PAYLOAD READBACK CERTIFIED" if verify and verify_mode != "Structure only" else " / PAYLOAD READBACK NOT PERFORMED")
            if provision_cfg.get("enabled"):
                self.events.put(("stage", "PROVISION"))
                self.events.put(("status", "Expanding the partition map and creating a mounted data volume from remaining USB capacity…"))
                self.events.put(("log", "POST-FLASH STORAGE: preparing the certified image to use the full physical media capacity."))
                safe_removable_disk(num, disk)
                try:
                    relocate_gpt_backup_to_disk_end(
                        num, int(disk["Size"]), int(disk.get("LogicalSectorSize") or 512),
                        log=lambda t: self.events.put(("log", t)),
                    )
                except Exception as gpt_error:
                    raise MediaOperationError("FORMAT_FAILURE", "Image write completed, but GPT expansion failed. No data partition was created. Inspect the log before retrying: " + str(gpt_error)) from gpt_error
                update_disk_properties(num)
                set_disk_offline_strict(num, False)
                update_disk_properties(num)
                refresh_storage_cache()
                time.sleep(0.5)
                try:
                    data_result = provision_remainder_partition(
                        num,
                        provision_cfg.get("filesystem") or "exFAT",
                        provision_cfg.get("label") or "NEXUS_DATA",
                    )
                except Exception as first_error:
                    # A timed-out/failed Format-Volume may already have created a
                    # partition. Repeating New-Partition is not idempotent.
                    raise MediaOperationError("FORMAT_FAILURE",
                        "The image write completed, but the optional data volume is incomplete. "
                        "No automatic partition-creation retry was made. Inspect the new partition "
                        "in Disk Manager and format that data partition if needed. " + str(first_error)) from first_error
                if data_result.get("created"):
                    letter = str(data_result.get("DriveLetter") or "").strip()
                    mount_text = f"{letter}:" if letter else "mounted volume"
                    self.events.put(("log", f"POST-FLASH STORAGE PASS: partition {data_result.get('PartitionNumber')} / {data_result.get('FileSystem')} / {human_size(int(data_result.get('Size') or 0))} / {mount_text}."))
                    # Confirm that adding a data partition did not damage the boot path.
                    with open_physical_retry(num, GENERIC_READ) as h:
                        final_boot = validate_boot_reader(RawHandleReader(h.h, int(disk["Size"])), ".img")
                    if strict_valid and not final_boot.get("valid"):
                        raise RuntimeError("Post-provision boot validation failed: " + "; ".join(final_boot.get("errors", [])))
                    if final_boot.get("valid"):
                        self.events.put(("log", f"POST-PROVISION BOOT PASS: {final_boot.get('format')} / EFI loader {final_boot.get('loader_size')} bytes."))
                    if letter and provision_cfg.get("open_after"):
                        self.events.put(("open_mount", letter))
                    done_message += f" — DATA VOLUME {mount_text}"
                else:
                    self.events.put(("log", "POST-FLASH STORAGE: " + str(data_result.get("reason") or "No substantial unallocated space remained.")))

            terminal = ("done", done_message)
        except InterruptedError as e:
            terminal = ("cancelled", str(e))
        except Exception as e:
            terminal = ("error", str(e))
        finally:
            if source_guard is not None:
                source_guard.close()
            if automount_changed:
                try:
                    set_automount_disabled(False, log=lambda s: self.events.put(("log", s)))
                except Exception as e:
                    self.events.put(("log", f"AUTOMOUNT RESTORE WARNING: {e}"))
                    terminal = ("error", "Media operation ended, but Windows automount restoration failed. Do not automatically reflash; inspect the runtime log and restore the original automount setting. " + str(e))
            try:
                safe_removable_disk(num, disk)
                update_disk_properties(num)
                set_disk_offline_strict(num, False)
                refresh_storage_cache()
            except Exception as cleanup_error:
                self.events.put(("log", f"Cleanup did not touch an unverified target: {cleanup_error}"))
            if terminal is not None:
                self.events.put(terminal)

    # ----- factory reset --------------------------------------------------
    def restore_usb(self):
        if self.busy:
            return
        sel = self.selected()
        if not sel:
            messagebox.showerror(APP_NAME, "Select the USB / SD media to reclaim.")
            return
        try:
            cur = safe_removable_disk(int(sel["Number"]), sel)
        except Exception as e:
            messagebox.showerror(APP_NAME, str(e))
            return
        fs = self.fs_var.get()
        scheme = self.scheme_var.get()
        label = sanitize_label(self.label_var.get())
        full = bool(self.full_format.get())
        if fs.upper() == "FAT32" and int(cur["Size"]) > 32 * 1024**3:
            messagebox.showerror(APP_NAME, "Windows FAT32 formatting is limited to 32 GB. Select exFAT or NTFS for this device.")
            return
        detail = (
            f"Disk {cur['Number']} — {cur.get('FriendlyName')} — {human_size(int(cur['Size']))}\n"
            f"New map: {scheme}   •   Filesystem: {fs}   •   Label: {label}\n"
            f"Format: {'FULL media check' if full else 'QUICK'}\n\n"
            "All EFI/OEM/hidden partitions and all existing data will be removed."
        )
        if not messagebox.askyesno(APP_NAME, "Factory reset this removable device?\n\n" + detail, icon="warning"):
            return
        if not self.confirm_word("RESTORE", "Factory reset confirmation", detail):
            return
        try:
            safe_removable_disk(int(cur["Number"]), cur)
            guard_runtime_outside_target(int(cur["Number"]))
        except Exception as exc:
            messagebox.showerror(APP_NAME, str(exc))
            return

        self.cancel_event.clear()
        self.progress.set(0)
        self.stage.set("RECLAIM")
        self.status.set("Reclaiming protected media and rebuilding the partition map…")
        self.telemetry.set("Factory reset in progress…")
        self.set_running(True)
        self.pause.configure(state="disabled")
        self.stop.configure(state="disabled")

        def worker():
            try:
                self.events.put(("log", "FACTORY RESET: clearing read-only/offline state, EFI/OEM partitions, and partition metadata."))
                result = restore_disk_windows(int(cur["Number"]), label, scheme, fs, full, expected=cur, log=lambda s: self.events.put(("log", s)))
                letter = str(result.get("DriveLetter") or "").strip()
                suffix = f" ({letter}:)" if letter else ""
                self.events.put(("restored", f"USB factory reset complete{suffix} — {scheme} / {fs} / {label}"))
            except Exception as e:
                self.events.put(("error", f"Factory reset failed: {e}"))

        threading.Thread(target=worker, daemon=True).start()

    # ----- UI event pump --------------------------------------------------
    def pump(self):
        try:
            while True:
                k, p = self.events.get_nowait()
                if k == "lab_done":
                    self._handle_lab_done(p)
                elif k == "scan_error":
                    self.logline(str(p))
                    if not self.busy:
                        self.refresh_btn.configure(state="normal")
                        self.status.set(str(p))
                elif k == "disks":
                    if not self.busy: self.set_disks(p)
                elif k == "partition_data":
                    disk, parts = p
                    selected = self.selected()
                    if self.busy or not selected or int(selected["Number"]) != int(disk["Number"]) or _media_identity_strength(selected, disk) < 7:
                        continue
                    self.partition_rows = {}
                    if hasattr(self, "partition_tree"):
                        for item in self.partition_tree.get_children():
                            self.partition_tree.delete(item)
                        for part in parts:
                            pnum = int(part.get("PartitionNumber") or 0)
                            self.partition_rows[pnum] = part
                            letter = (str(part.get("DriveLetter") or "") + ":") if part.get("DriveLetter") else "—"
                            typ = str(part.get("Type") or "") or ("GPT " + str(part.get("GptType") or "")[:8])
                            self.partition_tree.insert("", "end", values=(
                                pnum, letter, typ, str(part.get("FileSystem") or ""), str(part.get("FileSystemLabel") or ""),
                                human_size(int(part.get("Size") or 0)), human_size(int(part.get("Offset") or 0)), str(part.get("HealthStatus") or ""),
                            ))
                    self.diskmap_summary.set(
                        f"Disk {disk.get('Number')} — {disk.get('FriendlyName') or 'removable media'} — {human_size(int(disk.get('Size') or 0))} — "
                        f"{disk.get('PartitionStyle')} — {len(parts)} partition(s) — unallocated {human_size(int(disk.get('LargestFreeExtent') or 0))}"
                    )
                elif k == "disk_action_done":
                    stage_name, result = p
                    self.set_running(False)
                    self.stage.set("READY")
                    self.status.set(f"Disk Manager action complete: {stage_name}.")
                    self.logline(f"DISK MANAGER {stage_name} PASS: {result}")
                    self.refresh()
                    self.after(700, self.refresh_partition_view)
                elif k == "ejected":
                    self.set_running(False)
                    self.stage.set("EJECTED" if p.get("ejected") else "EJECT NOT CONFIRMED")
                    self.status.set(str(p.get("message") or "Media is safe to remove."))
                    self.telemetry.set("Hardware removal confirmed." if p.get("ejected") else "Do not remove media: hardware eject not confirmed.")
                    self.logline(("SAFE EJECT PASS: " if p.get("ejected") else "SAFE EJECT INCOMPLETE: ") + str(p))
                    (messagebox.showinfo if p.get("ejected") else messagebox.showwarning)(APP_NAME, str(p.get("message")))
                    self.refresh()
                elif k == "open_mount":
                    if os.name == "nt" and p:
                        try:
                            subprocess.Popen(["explorer.exe", f"{str(p).strip()}:\\"])
                            self.logline(f"POST-FLASH STORAGE: opened {str(p).strip()}: in File Explorer.")
                        except Exception as e:
                            self.logline(f"POST-FLASH STORAGE WARNING: could not open mounted data volume: {e}")
                elif k == "backup_done":
                    self._backup_active = False
                    self.set_running(False)
                    self.progress.set(100)
                    self.stage.set("BACKUP COMPLETE")
                    self.status.set("Raw device image backup created successfully.")
                    self.telemetry.set(f"Backup {human_size(int(p.get('size') or 0))} — SHA-256 {p.get('sha256')}")
                    self.logline("IMAGE BACKUP PASS: " + json.dumps(p))
                    self.recovery.record_success("image_backup")
                    if getattr(self, "_recovery_acquire", False):
                        self.recovery_image_var.set(p["path"])
                        self._recovery_scan = None
                        self._recovery_acquire = False
                        self.recovery_info_var.set("Acquisition complete. Run a read-only image scan.")
                        self.show_page("undelete")
                    messagebox.showinfo(APP_NAME, f"Raw image backup created.\n\n{p.get('path')}\n\nSHA-256: {p.get('sha256')}")
                elif k == "image_validation":
                    if self.busy: continue
                    path, res = p
                    if path != self.image_var.get():
                        continue
                    try:
                        st = Path(path).stat()
                    except OSError:
                        self.validated_image = None
                        self.status.set("Source disappeared during validation. Select the image again.")
                        self.update_start_state()
                        continue
                    if res.get("valid") and tuple(res.get("_stamp", ())) != (st.st_size, st.st_mtime_ns):
                        res["valid"] = False
                        res["errors"] = ["Image changed after asynchronous validation."]
                    res["_path"] = path
                    self.validated_image = res
                    name = Path(path).name
                    size = human_size(st.st_size)
                    if res.get("valid"):
                        warn = f"  •  {res['warnings'][0]}" if res.get("warnings") else ""
                        self.image_summary.set(f"{name}  •  {size}  •  PASS {res['format']}  •  EFI loader {res['loader_size']} B{warn}")
                        self.stage.set("READY")
                        self.status.set("Image validation passed. Ready for protected-media reclaim and raw flash.")
                        self.logline("IMAGE VALIDATION PASS: " + json.dumps(res))
                    else:
                        self.image_summary.set(f"{name}  •  {size}  •  validation rejected for strict UEFI mode")
                        self.stage.set("ATTENTION")
                        self.status.set("Strict boot validation failed. Use a hybrid USB image or Advanced raw mode.")
                        self.logline("IMAGE VALIDATION REJECTED: " + "; ".join(res.get("errors", [])))
                    self.update_start_state()
                elif k == "stage":
                    self.stage.set(str(p))
                elif k == "status":
                    self.status.set(str(p))
                elif k == "progress":
                    self.progress.set(float(p))
                elif k == "telemetry":
                    self.telemetry.set(str(p))
                elif k == "log":
                    self.logline(str(p))
                elif k == "done":
                    self.set_running(False)
                    self.progress.set(100)
                    self.stage.set("COMPLETE")
                    self.status.set(str(p))
                    self.telemetry.set("Requested operations complete. See the mode and log for actual verification and provisioning results.")
                    self.logline(str(p))
                    self.recovery.record_success("flash")
                    self.recovery_status.set(self.recovery.summary())
                    messagebox.showinfo(
                        APP_NAME,
                        str(p) + "\n\nReview the verification mode and operation log. When enabled and available, remaining capacity was provisioned as a data volume. "
                        "Use SAFE EJECT before removing the media, or Recovery / Reset to return the whole device to ordinary storage.",
                    )
                    self.refresh()
                elif k == "cancelled":
                    was_backup = bool(getattr(self, "_backup_active", False))
                    self._backup_active = False
                    self._recovery_acquire = False
                    self.set_running(False)
                    self.stage.set("STOPPED")
                    if was_backup:
                        self.status.set("Image acquisition stopped — the output image is incomplete.")
                        self.telemetry.set("The acquisition engine opened the source read-only; no source repair was attempted.")
                        messagebox.showwarning(APP_NAME, "Image acquisition stopped. Keep the source unchanged; do not format, flash or reclaim it to recover files. Partial output is not a complete backup.")
                    else:
                        self.status.set("Write stopped — target image is incomplete.")
                        self.telemetry.set("Do not rely on the interrupted target as bootable media.")
                        messagebox.showwarning(APP_NAME, "Write stopped. The partially overwritten target may not boot. Original overwritten bytes cannot be recovered by a factory reset.")
                    self.refresh()
                elif k == "restored":
                    self.set_running(False)
                    self.progress.set(100)
                    self.stage.set("READY")
                    self.status.set(str(p))
                    self.telemetry.set("Protected partition metadata removed; one normal volume created.")
                    self.logline(str(p))
                    self.recovery.record_success("factory_reset")
                    self.recovery_status.set(self.recovery.summary())
                    messagebox.showinfo(APP_NAME, str(p))
                    self.refresh()
                elif k == "error":
                    self._backup_active = False
                    self._recovery_acquire = False
                    self.set_running(False)
                    self.stage.set("ERROR")
                    self.status.set("Operation failed. AEGIS captured and classified the failure.")
                    self.telemetry.set("No further write is in progress.")
                    self.logline("ERROR: " + str(p))
                    if self.self_heal_var.get():
                        key, entry = self.recovery.record_failure(str(p))
                        self.adaptive_profile = self.recovery.adaptive_profile()
                        self.recovery_status.set(self.recovery.summary())
                        remedy = str(entry.get("remedy") or "Capture diagnostics and fail closed.")
                        if key == "SOFTWARE_REGRESSION":
                            self.logline(f"AEGIS INTERNAL DEFECT CLASSIFIED: occurrence {entry.get('count')} — {remedy}")
                        else:
                            self.logline(f"AEGIS RECOVERY DIAGNOSIS: {key} occurrence {entry.get('count')} — {remedy}")
                    messagebox.showerror(APP_NAME, str(p))
        except queue.Empty:
            pass
        finally:
            self.after(120, self.pump)

    def _walk_widgets(self,parent=None):
        for child in (parent or self).winfo_children():
            yield child
            yield from self._walk_widgets(child)

    def report_callback_exception(self,exc_type,exc_value,tb):
        detail="".join(traceback.format_exception(exc_type,exc_value,tb))
        log_file("UI CALLBACK ERROR: "+detail)
        messagebox.showerror(APP_NAME,"A user-interface error occurred. No automatic repair or disk retry was started.\n\n"+str(exc_value)+"\n\nSee the runtime log for details.")

    def _build_forensic_pages(self,host):
        self._lab_pause_buttons=[];self._lab_stop_buttons=[]
        for key in ("undelete","erase"):self.pages[key]=tk.Frame(host,bg=self.BG)
        if not hasattr(self,"recovery_image_var"):
            self.recovery_image_var=tk.StringVar();self.recovery_output_var=tk.StringVar()
            self.recovery_mode_var=tk.StringVar(value="Combined");self.recovery_max_var=tk.StringVar(value="256")
            self.recovery_info_var=tk.StringVar(value="No source scan. Select an image, or acquire one from the selected removable disk.")
            self._recovery_scan=None;self._lab_job=None;self._last_lab_output=None
        card,body=self._card(self.pages["undelete"],"UNDELETE LAB / READ-ONLY SOURCE","Native NTFS, FAT32 and exFAT metadata analysis + PNG/JPEG/PDF/ZIP/RIFF signature carving. Recover to copies; never repair the source in place.")
        card.pack(fill="x",pady=(0,10))
        tk.Label(body,text="Do not flash, format or reclaim a drive containing files you want to recover. For evidence-sensitive acquisition, use a hardware write blocker. This application is not a certified forensic suite.",bg=self.PANEL,fg=self.AMBER,wraplength=1030,justify="left",font=(self.FONT_UI,9)).pack(anchor="w",pady=(0,9))
        row=tk.Frame(body,bg=self.PANEL);row.pack(fill="x")
        entry=self._entry(row,self.recovery_image_var);entry.configure(state="readonly",readonlybackground=self.PANEL_2)
        entry.pack(side="left",fill="x",expand=True,ipady=8)
        self._button(row,"BROWSE IMAGE",self._choose_recovery_image,"cyan",17).pack(side="left",padx=(8,0))
        self._button(row,"ACQUIRE IMAGE",self._acquire_recovery_image,"ghost",18).pack(side="left",padx=(8,0))
        row=tk.Frame(body,bg=self.PANEL);row.pack(fill="x",pady=(8,0))
        tk.Label(row,text="Scan mode",bg=self.PANEL,fg=self.MUTED).pack(side="left")
        ttk.Combobox(row,textvariable=self.recovery_mode_var,values=["Combined","Metadata only","Signature carving"],state="readonly",style="Nexus.TCombobox",width=19).pack(side="left",padx=8)
        tk.Label(row,text="Maximum file size (MiB)",bg=self.PANEL,fg=self.MUTED).pack(side="left",padx=(10,8))
        limit=self._entry(row,self.recovery_max_var);limit.configure(width=8);limit.pack(side="left",ipady=7)
        self._button(row,"SCAN SOURCE",self._start_recovery_scan,"cyan",18).pack(side="right")
        results,body=self._card(self.pages["undelete"],"RECOVERY CANDIDATES / EXTRACTION","A candidate is not proof of an intact original. FAT32 layout may be inferred; carving cannot distinguish deleted from live files. Unsupported metadata is reported, not silently declared recovered.")
        results.pack(fill="x",pady=(0,10))
        tk.Label(body,textvariable=self.recovery_info_var,bg=self.PANEL,fg=self.CYAN,wraplength=1020,justify="left").pack(anchor="w",pady=(0,6))
        shell=tk.Frame(body,bg=self.PANEL);shell.pack(fill="x")
        cols=("id","method","name","size","note")
        self.recovery_tree=ttk.Treeview(shell,columns=cols,show="headings",height=9,selectmode="extended",style="Nexus.Treeview")
        for c,w in zip(cols,(55,90,240,100,480)):
            self.recovery_tree.heading(c,text=c.upper());self.recovery_tree.column(c,width=w,minwidth=40,stretch=c in ("name","note"))
        y=ttk.Scrollbar(shell,orient="vertical",command=self.recovery_tree.yview,style="Nexus.Vertical.TScrollbar");y.pack(side="right",fill="y")
        self.recovery_tree.configure(yscrollcommand=y.set);self.recovery_tree.pack(fill="x",expand=True)
        row=tk.Frame(body,bg=self.PANEL);row.pack(fill="x",pady=(10,0))
        ent=self._entry(row,self.recovery_output_var);ent.configure(state="readonly",readonlybackground=self.PANEL_2);ent.pack(side="left",fill="x",expand=True,ipady=7)
        self._button(row,"OUTPUT FOLDER",self._choose_recovery_output,"ghost",18).pack(side="left",padx=(8,0))
        row=tk.Frame(body,bg=self.PANEL);row.pack(fill="x",pady=(8,0))
        self._button(row,"RECOVER SELECTED",lambda:self._extract_recovery(False),"cyan",21).pack(side="left")
        self._button(row,"RECOVER ALL",lambda:self._extract_recovery(True),"ghost",17).pack(side="left",padx=8)
        self._button(row,"OPEN OUTPUT",self._open_lab_output,"ghost",17).pack(side="left")
        self._lab_controls(body)
        card,body=self._card(self.pages["erase"],"VERIFIED LOGICAL ERASE / DESTRUCTIVE","One complete zero overwrite of the selected physical device's host-addressable range, followed by a complete readback comparison. The device is left unformatted.")
        card.pack(fill="x",pady=(0,10))
        tk.Label(body,text="THIS PERMANENTLY DESTROYS ADDRESSABLE DATA, INCLUDING THE PARTITION TABLE.\nRecovery and erase are mutually exclusive goals: recover needed files before erasing.",bg=self.PANEL,fg=self.RED,font=(self.FONT_UI,11,"bold"),wraplength=1030,justify="left").pack(anchor="w",pady=(0,12))
        tk.Label(body,text="Scope: non-system USB / SD / MMC media only. A stable serial or UniqueId is required. All volumes must lock successfully. The program, logs and report must be on a different physical disk. Failed I/O, cancellation or a readback mismatch leaves an INCOMPLETE report; no automatic disk rebinding or destructive retry is performed.",bg=self.PANEL,fg=self.TEXT,wraplength=1030,justify="left").pack(anchor="w",pady=(0,12))
        tk.Label(body,text="LIMITATION: This is a verified logical overwrite, NOT firmware sanitize, cryptographic erase, hardware Purge or a guarantee against laboratory recovery. SSD/USB wear-leveling, remapped sectors, spare capacity and hidden storage are outside the host-visible range. No NIST/DoD certification is claimed.",bg=self.PANEL,fg=self.AMBER,wraplength=1030,justify="left").pack(anchor="w",pady=(0,12))
        self._button(body,"ERASE ENTIRE SELECTED DEVICE",self._begin_logical_erase,"red",38).pack(anchor="w")
        self._lab_controls(body)
        if self._recovery_scan:self._populate_recovery_tree()

    def _lab_controls(self,parent):
        row=tk.Frame(parent,bg=self.PANEL);row.pack(fill="x",pady=(10,0))
        p=self._button(row,"PAUSE",self.toggle_pause,"amber",12);p._lab_control=True;p.configure(state="disabled");p.pack(side="left")
        s=self._button(row,"STOP",self.request_stop,"red",12);s._lab_control=True;s.configure(state="disabled");s.pack(side="left",padx=8)
        self._lab_pause_buttons.append(p);self._lab_stop_buttons.append(s)
        HudProgressBar(parent,self.progress,self.GRAD_A,self.GRAD_B,self.PANEL_2,height=22,radius=11).pack(fill="x",pady=8)
        tk.Label(parent,textvariable=self.status,bg=self.PANEL,fg=self.TEXT,wraplength=1030,justify="left").pack(anchor="w")

    def _choose_recovery_image(self):
        if self.busy:return
        path=filedialog.askopenfilename(title="Select read-only sector image",filetypes=[("Raw sector images","*.img *.raw *.bin *.dd *.iso"),("All files","*.*")])
        if path:self.recovery_image_var.set(path);self._recovery_scan=None;self.recovery_info_var.set("Source changed. Run a new scan.");self._populate_recovery_tree()

    def _choose_recovery_output(self):
        if self.busy:return
        path=filedialog.askdirectory(title="Choose a folder for recovered copies",mustexist=True)
        if path:self.recovery_output_var.set(path)

    def _acquire_recovery_image(self):
        if self.busy:return
        self._recovery_acquire=True
        self.backup_selected_to_image()
        if not self.busy:self._recovery_acquire=False

    def _lab_start(self,kind,func):
        if self.busy:return
        self._lab_job=kind;self.cancel_event.clear();self.pause_event.set();self.progress.set(0)
        self._lab_last_tick=0;self._lab_phase="";self._lab_phase_start=time.monotonic()
        self.set_running(True);self.stage.set(kind);self.status.set("Starting "+kind.lower()+"…")
        def worker():
            payload={"kind":kind,"status":"complete"}
            try:payload["result"]=func()
            except InterruptedError as exc:payload.update(status="cancelled",error=str(exc))
            except Exception as exc:
                payload.update(status="error",error=str(exc));log_file("LAB ERROR: "+traceback.format_exc())
            self.events.put(("lab_done",payload))
        self._active_lab_worker=threading.Thread(target=worker,daemon=True);self._active_lab_worker.start()

    def _lab_progress(self,phase,done,total):
        now=time.monotonic()
        changed=phase!=self._lab_phase
        if changed:self._lab_phase=phase;self._lab_phase_start=now
        if not changed and now-self._lab_last_tick<.12 and done!=total:return
        self._lab_last_tick=now;pct=100*done/max(1,total)
        if self._lab_job=="ERASE":pct=(50 if phase=="READBACK" else 0)+pct*.5
        elapsed=max(.01,now-self._lab_phase_start);speed=done/elapsed;eta=(total-done)/speed if speed else float("inf")
        self.events.put(("stage",phase));self.events.put(("progress",min(100,pct)))
        self.events.put(("status",f"{phase} — {human_size(done)} / {human_size(total)}"))
        self.events.put(("telemetry",f"{human_size(int(speed))}/s  •  Phase ETA {human_time(eta)}  •  {'Destructive overwrite' if self._lab_job=='ERASE' else 'Source opened read-only'}"))

    def _start_recovery_scan(self):
        if self.busy:return
        try:
            path=Path(self.recovery_image_var.get()).resolve(strict=True)
            if not path.is_file():raise ValueError("Select an existing source image.")
            maximum=int(self.recovery_max_var.get())
            if not 1<=maximum<=4096:raise ValueError("Maximum recovered file size must be 1–4096 MiB.")
            mode=self.recovery_mode_var.get()
        except (OSError,ValueError) as exc:messagebox.showerror(APP_NAME,str(exc));return
        self._recovery_scan=None;self._populate_recovery_tree()
        self._lab_start("SCAN",lambda:scan_recovery_image(path,mode,{"max_file_bytes":maximum*1024**2},self.checkpoint,self._lab_progress))

    def _populate_recovery_tree(self):
        for row in self.recovery_tree.get_children():self.recovery_tree.delete(row)
        if not self._recovery_scan:return
        for c in self._recovery_scan["candidates"]:
            self.recovery_tree.insert("","end",iid=str(c["id"]),values=(c["id"],c["method"],c["name"],human_size(c["size"]),c["note"]))

    def _extract_recovery(self,all_files=False):
        if self.busy:return
        if not self._recovery_scan:messagebox.showwarning(APP_NAME,"Run a source-image scan first.");return
        ids=[c["id"] for c in self._recovery_scan["candidates"]] if all_files else [int(i) for i in self.recovery_tree.selection()]
        if not ids:messagebox.showwarning(APP_NAME,"Select one or more candidate rows.");return
        dest=self.recovery_output_var.get()
        if not dest or not Path(dest).is_dir():messagebox.showwarning(APP_NAME,"Choose an existing output folder first.");return
        if not messagebox.askyesno(APP_NAME,f"Extract {len(ids)} candidate(s) to a new folder?\n\nSource image stays read-only. Integrity/originality of deleted contents is not guaranteed. An extraction manifest will record file hashes and limitations."):return
        scan=self._recovery_scan
        self._lab_start("EXTRACT",lambda:extract_recovery_candidates(scan,ids,dest,self.checkpoint,self._lab_progress))

    def _begin_logical_erase(self):
        if self.busy:return
        sel=self.selected()
        if not sel:messagebox.showwarning(APP_NAME,"Explicitly select a removable device first.");return
        try:
            current=safe_removable_disk(int(sel["Number"]),sel)
            if not any(str(current.get(k) or "").strip() for k in ("UniqueId","SerialNumber")):
                raise RuntimeError("This device has no stable identity. Verified erase is unavailable.")
            guard_runtime_outside_target(int(current["Number"]))
        except Exception as exc:messagebox.showerror(APP_NAME,str(exc));return
        path=filedialog.asksaveasfilename(title="Save logical erase audit report on another physical device",defaultextension=".json",initialfile=f"NEXUS_Erase_Disk{current['Number']}_{time.strftime('%Y%m%d_%H%M%S')}.json",filetypes=[("JSON audit report","*.json")])
        if not path:return
        try:
            guard_paths_outside_target(int(current["Number"]),path)
            if Path(path).exists():raise RuntimeError("Choose a new report filename, not an existing report.")
        except Exception as exc:messagebox.showerror(APP_NAME,str(exc));return
        token=str(current.get("SerialNumber") or current.get("UniqueId")).strip()[-8:]
        phrase=f"ERASE DISK {current['Number']} {token}"
        detail=(f"Disk {current['Number']} — {current.get('FriendlyName')} — {human_size(int(current['Size']))}\n"
                f"Serial: {current.get('SerialNumber') or 'not provided'}\nUniqueId: {current.get('UniqueId') or 'not provided'}\n\n"
                "ALL ADDRESSABLE DATA WILL BE OVERWRITTEN AND LOST.\nThe full range will be read back; no format is performed.\nThis does NOT guarantee SSD/flash hardware sanitization.\n\nReport: "+path)
        if not self.confirm_word(phrase,"Permanent whole-device logical erase",detail):return
        self._lab_start("ERASE",lambda:logical_erase_disk(dict(current),path,self.checkpoint,self._lab_progress))

    def _handle_lab_done(self,payload):
        kind=payload["kind"];self._lab_job=None;self.set_running(False)
        if payload["status"]!="complete":
            self.stage.set("STOPPED" if payload["status"]=="cancelled" else "ERROR")
            message=payload.get("error","Operation did not complete.")
            self.status.set(message)
            self.telemetry.set("INCOMPLETE — no successful erase/recovery certification issued.")
            self.logline(f"{kind} {payload['status'].upper()}: {message}")
            messagebox.showwarning(APP_NAME,message+"\n\n"+("Erase report remains INCOMPLETE. Already overwritten bytes cannot be restored." if kind=="ERASE" else "Source image was not modified by the recovery engine."))
            return
        result=payload["result"];self.progress.set(100);self.stage.set("COMPLETE")
        if kind=="SCAN":
            self._recovery_scan=result;self._populate_recovery_tree()
            self.recovery_info_var.set(f"{len(result['candidates'])} candidate(s). Source SHA-256: {result['source_sha256']}")
            self.status.set("Scan complete. Review candidates and limitations before extracting copies.")
            self.logline(self.recovery_info_var.get())
            for note in result["notes"]:self.logline("RECOVERY NOTE: "+note)
            self.telemetry.set("Source read-only. Candidates may be partial, inferred or still-live files.")
        elif kind=="EXTRACT":
            self._last_lab_output=result["folder"];self.status.set(f"Extracted {result['count']} candidate(s); manifest saved.")
            self.logline("RECOVERY EXTRACTION: "+json.dumps(result));self.telemetry.set("Extracted-file SHA-256 values recorded; original content not guaranteed.")
            messagebox.showinfo(APP_NAME,self.status.get()+"\n\n"+result["folder"])
        elif kind=="ERASE":
            self._last_lab_output=str(Path(result["report"]).parent);self.status.set("Complete addressable range overwritten and readback verified. Hardware Purge is NOT claimed.")
            self.telemetry.set(f"Verified {human_size(result['verified_bytes'])}; report: {result['report']}")
            self.logline("LOGICAL ERASE: "+json.dumps(result));messagebox.showinfo(APP_NAME,self.status.get()+"\n\n"+result["report"])
            self.refresh()

    def _open_lab_output(self):
        folder=self._last_lab_output or self.recovery_output_var.get()
        if folder and Path(folder).is_dir() and os.name=="nt":os.startfile(folder)
        elif not folder:messagebox.showinfo(APP_NAME,"No output folder has been selected or created.")


def show_fatal_startup_error(exc):
    """Make .pyw startup failures visible instead of silently exiting."""
    message = (
        f"{APP_NAME} could not start.\n\n{type(exc).__name__}: {exc}\n\n"
        f"A diagnostic log was written to:\n{LOG_PATH}"
    )
    log_file("FATAL STARTUP ERROR: " + repr(exc))
    try:
        if os.name == "nt":
            ctypes.windll.user32.MessageBoxW(None, message, APP_NAME + " — Startup Error", 0x10)
        else:
            print(message, file=sys.stderr)
    except Exception:
        try:
            print(message, file=sys.stderr)
        except Exception:
            pass


def main():
    enable_uhd_dpi_awareness()
    if "--preview" in sys.argv:
        class PreviewApp(App):
            def refresh(self):
                self.status.set("UI PREVIEW — no physical disks enumerated; hardware operations unavailable.")
                self.stage.set("PREVIEW")
                self.update_start_state()
        PreviewApp().mainloop()
        return
    if os.name != "nt":
        raise RuntimeError("Windows physical-media operations only. Use --preview for the non-destructive interface.")
    if not is_admin():
        if relaunch_as_admin(): return
        raise RuntimeError("Administrator access required. Accept the Windows UAC prompt.")
    log_file("=" * 78)
    log_file(APP_NAME + " starting; physical media functions require local qualification.")
    log_file("Raw-disk privileges: " + json.dumps(enable_raw_disk_privileges()))
    App().mainloop()


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        show_fatal_startup_error(exc)
