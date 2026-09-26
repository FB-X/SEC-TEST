"""Hardened requests package — delegates to compiled alireq module.

The actual hardened runtime lives in alireq<EXT_SUFFIX> (compiled).
This file exists only to satisfy Python's package import machinery.
"""
from __future__ import annotations

# Import everything from the compiled alireq module
# (alireq<EXT_SUFFIX> is a sibling .so that Python will find first)
from .alireq import *                                  # noqa: F401,F403
from .alireq import __all__ as _alireq_all

# Re-export all names from alireq.so
__all__ = list(_alireq_all)

# Version tag for compatibility with tools that inspect it
__version__ = getattr(__import__("alireq"), "__version__", "1.0.0-hardened")
