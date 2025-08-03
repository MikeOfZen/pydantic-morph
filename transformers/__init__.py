"""
Pydantic Variants Transformers

This package provides transformers for modifying Pydantic models through pipelines.
All transformers can be imported directly from this package.
"""

# Field manipulation transformers
from .filter_fields import FilterFields
from .make_optional import MakeOptional, DefaultFactoryTag
from .modify_fields import ModifyFields
from .rename_fields import RenameFields
from .set_fields import SetFields

# Model manipulation transformers
from .build_variant import BuildVariant
from .connect_variant import ConnectVariant
from .set_attributes import SetAttribute
from .switch_variant import SwitchNested

# Utility transformers
from .extract_variant import ExtractVariant

__all__ = [
    # Field transformers
    "FilterFields",
    "MakeOptional",
    "DefaultFactoryTag",
    "ModifyFields",
    "RenameFields",
    "SetFields",
    # Model transformers
    "BuildVariant",
    "ConnectVariant",
    "SetAttribute",
    "SwitchNested",
    # Utilities
    "ExtractVariant",
]
