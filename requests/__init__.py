from __future__ import annotations
from .alireq import *
from .alireq import __all__ as _alireq_all
__all__ = list(_alireq_all)
__version__ = getattr(__import__("alireq"), "__version__", "1.0.0-hardened")
