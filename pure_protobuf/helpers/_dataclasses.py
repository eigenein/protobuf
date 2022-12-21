from sys import version_info

DATACLASS_OPTIONS = {"frozen": True}  # ensures that I don't modify attributes
"""Used for the internal dataclasses."""

if version_info >= (3, 10):
    DATACLASS_OPTIONS["slots"] = True  # optimizes the storage
    # FIXME: DATACLASS_OPTIONS["kw_only"] = True  # prevents me from confusing the parameters
