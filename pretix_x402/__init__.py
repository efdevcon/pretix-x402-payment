__version__ = "0.1.0"

try:
    from .apps import X402App as PretixPluginMeta  # noqa: F401
except ImportError:
    pass
