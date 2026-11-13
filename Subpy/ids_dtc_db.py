"""
IDS DTC Database - Unified DTC lookup from IDS pickle files
============================================================
Loads the 'dtc' pickle file from config/ and provides fast lookup
by DTC label and ECU name.

Usage:
    from Subpy.ids_dtc_db import lookup_dtc
    desc = lookup_dtc("P17BA_8B", "LHZCU")  # → "刹车信号无效"
"""

import os
import pickle
import atexit

_DTC_DB = None  # lazy load
_CONFIG_DIR = None


def _get_config_dir():
    """Resolve config/ directory relative to this file."""
    global _CONFIG_DIR
    if _CONFIG_DIR is None:
        # Subpy/ids_dtc_db.py → Subpy/ → ITS/ → ITS/config/
        _CONFIG_DIR = os.path.normpath(
            os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "config")
        )
    return _CONFIG_DIR


def _load_dtc_db():
    """Lazy-load the DTC pickle database (thread-safe enough for GUI use)."""
    global _DTC_DB
    if _DTC_DB is None:
        path = os.path.join(_get_config_dir(), "dtc")
        if not os.path.exists(path):
            raise FileNotFoundError(f"IDS DTC database not found: {path}")
        with open(path, "rb") as f:
            _DTC_DB = pickle.load(f)
    return _DTC_DB


def lookup_dtc(dtc_label: str, ecu_name: str = "") -> str:
    """
    Look up a DTC description from the IDS database.
    
    Args:
        dtc_label: DTC label in format like "P17BA_8B" or "C16B4_29"
        ecu_name: ECU name like "LHZCU", "RHZCU", "IAM", "ICB", etc.
                  If empty, returns the first available description.
    
    Returns:
        Chinese description string, or empty string if not found.
    """
    try:
        db = _load_dtc_db()
    except (FileNotFoundError, Exception):
        return ""
    
    entry = db.get(dtc_label)
    if not entry:
        # Fallback: try zero-padded format (e.g., "U404_81" -> "U0404_81")
        import re
        m = re.match(r'^([PCBUpcb])([0-9A-Fa-f]+)_([0-9A-Fa-f]+)$', dtc_label)
        if m:
            prefix = m.group(1).upper()
            num_part = m.group(2)
            ftb = m.group(3)
            # Pad the number part to 4 hex digits
            padded = f"{prefix}{num_part.zfill(4)}_{ftb}"
            entry = db.get(padded)
        if not entry:
            return ""
    
    # 1. Try exact ECU match
    if ecu_name and ecu_name in entry:
        return entry[ecu_name]
    
    # 2. Try case-insensitive match
    if ecu_name:
        ecu_upper = ecu_name.upper()
        for k, v in entry.items():
            if k.upper() == ecu_upper:
                return v
    
    # 3. Fallback: return the first non-empty description
    for v in entry.values():
        if v and v.strip():
            return v
    
    return ""


def lookup_dtc_en(dtc_label: str, ecu_name: str = "") -> str:
    """
    Same as lookup_dtc, but prefers English descriptions.
    Currently the IDS DB stores Chinese descriptions under the ECU name keys,
    so this returns the same as lookup_dtc for now.
    """
    return lookup_dtc(dtc_label, ecu_name)


def get_db_stats() -> dict:
    """Return basic stats about the loaded database."""
    db = _load_dtc_db()
    ecus = set()
    for entry in db.values():
        ecus.update(entry.keys())
    return {
        "total_dtcs": len(db),
        "total_ecus": len(ecus),
        "ecu_list": sorted(ecus),
        "db_path": os.path.join(_get_config_dir(), "dtc"),
    }


# Register a cache-friendly cleanup (not strictly needed, but good practice)
@atexit.register
def _cleanup():
    global _DTC_DB
    _DTC_DB = None