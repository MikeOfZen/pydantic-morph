"""
Pydantic variants library

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

from pydantic_variants.core import VariantContext, VariantPipe
from pydantic_variants.decorators import basic_variant_pipeline, variants

__all__ = [
    "VariantContext",
    "VariantPipe",
    "basic_variant_pipeline",
    "variants",
]
