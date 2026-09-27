"""Hardened requests package — delegates to compiled alireq module.

Rust engine (libalireq_engine.so) accessed via compiled rust_bridge.so
that uses direct FFI (no ctypes — avoids Android TBI crash).
"""
from __future__ import annotations

import os

from .alireq import *                                  # noqa: F401,F403
from .alireq import __all__ as _alireq_all

# ── Load compiled rust_bridge.so ──
try:
    from .rust_bridge import (
        rust_engine_init,
        rust_engine_version,
        rust_threat_scan,
        rust_harden_ram,
        load_rust_engine,
    )
    _RUST_BRIDGE_AVAILABLE = True
except ImportError as e:
    # Fallback stubs if .so not compiled
    def rust_engine_init(): return False
    def rust_engine_version(): return None
    def rust_threat_scan(): return -1
    def rust_harden_ram(): return False
    def load_rust_engine(): return False
    _RUST_BRIDGE_AVAILABLE = False

__all__ = list(_alireq_all) + [
    "rust_engine_init",
    "rust_engine_version",
    "rust_threat_scan",
    "rust_harden_ram",
    "load_rust_engine",
]

__version__ = getattr(__import__("alireq"), "__version__", "2.0.0-hybrid")
