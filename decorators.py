from typing import Callable
from pydantic import BaseModel
from .core import VariantPipe, VariantContext, ModelTransformer


def basic_variant_pipeline(name: str, *transformers: ModelTransformer) -> VariantPipe:
    """
    Helper function to create a complete variant pipeline.

    Automatically adds VariantContext creation, BuildVariant, and ConnectVariant
    transformers to create a complete pipeline.

    Args:
        name: Name of the variant
        *transformers: Field and model transformers to apply

    Returns:
        Complete VariantPipe ready for use with @variants decorator
    """
    # Import here to avoid circular imports
    from .transformers import BuildVariant, ConnectVariant

    return VariantPipe(
        VariantContext(name), *transformers, BuildVariant(), ConnectVariant()
    )


def variants(*pipelines: VariantPipe) -> Callable[[type[BaseModel]], type[BaseModel]]:
    """
    Decorator that generates model variants using VariantPipe pipelines.

    Each pipeline should be a complete transformation pipeline that includes
    VariantContext creation, field transformers, BuildVariant, and ConnectVariant.
    Use create_variant_pipeline() helper for easier pipeline creation.

    Args:
        *pipelines: Variable number of VariantPipe instances, each defining
                   a complete transformation pipeline for creating a variant

    Returns:
        Decorated BaseModel class with variants attached

    Example:
        ```python
        from pydantic_variants import variants, create_variant_pipeline
        from pydantic_variants.transformers import FilterFields, MakeOptional

        input_pipeline = create_variant_pipeline(
            'Input',
            FilterFields(exclude=['id', 'created_at']),
            MakeOptional(all=True)
        )

        output_pipeline = create_variant_pipeline(
            'Output',
            FilterFields(exclude=['internal_notes'])
        )

        @variants(input_pipeline, output_pipeline)
        class User(BaseModel):
            id: int
            name: str
            email: str
            internal_notes: str = ""
            created_at: datetime

        # Access variants
        user_input = User.Input(name="John", email="john@example.com")
        user_output = User.Output(**user.model_dump())
        ```
    """

    def decorator(model_cls: type[BaseModel]) -> type[BaseModel]:
        for pipeline in pipelines:
            pipeline(model_cls)
        return model_cls

    return decorator
