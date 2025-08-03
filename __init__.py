"""
Pydantic Variants

A library for creating model variants with transformation pipelines.

Basic Usage:
    ```python
    from pydantic_variants import variants, basic_variant_pipeline
    from pydantic_variants.transformers import FilterFields, MakeOptional

    @variants(
        basic_variant_pipeline('Input',
            FilterFields(exclude=['id']),
            MakeOptional(all=True)
        )
    )
    class User(BaseModel):
        id: int
        name: str
        email: str
    ```

Advanced Usage:
    ```python
    from pydantic_variants import VariantPipe, VariantContext
    from pydantic_variants.transformers import *

    custom_pipeline = VariantPipe(
        VariantContext('Custom'),
        FilterFields(exclude=['internal']),
        BuildVariant(),
        ConnectVariant()
    )
    ```
"""

# Core public API - most users will only need these
from .decorators import variants, basic_variant_pipeline

# Advanced API - for custom pipeline creation
from .core import VariantPipe, VariantContext

# Re-export transformers for convenience
from . import transformers

__version__ = "0.1.0"

__all__ = [
    # Main decorator and helper
    "variants",
    "basic_variant_pipeline",
    # Advanced pipeline building
    "VariantPipe",
    "VariantContext",
    # Transformers subpackage
    "transformers",
]
