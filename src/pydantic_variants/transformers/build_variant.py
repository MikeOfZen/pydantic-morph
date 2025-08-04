from typing import Any

from pydantic_variants.core import DecomposedModel, ModelTransformer, VariantContext


class BuildVariant(ModelTransformer):
    """
    Builds the final Pydantic model from a DecomposedModel, changing the variant type.

    This transformer converts current_variant from DecomposedModel to type[BaseModel].
    After this transformer, no field-level transformers should be applied.

    Args:
        base: Base class to inherit from (defaults to None)
        name_suffix: Optional suffix to append to the model name
        doc: Custom docstring for the generated model

    Example:
        # Basic build
        Build()

        # Build with custom base class
        Build(base=MyCustomBase)

        # Build with name customization
        Build(name_suffix="V2", doc="Version 2 of the model")
    """

    def __init__(self, base: Any = None, name_suffix: str = "", doc: str | None = None):
        self.base = base
        self.name_suffix = name_suffix
        self.doc = doc

    def __call__(self, context: VariantContext) -> VariantContext:
        # Assert we have a decomposed model
        if not isinstance(context.current_variant, DecomposedModel):
            raise ValueError(
                "Build transformer requires DecomposedModel, got built model"
            )

        # Determine final name
        final_name = context.name + self.name_suffix

        # Build the model
        built_model = context.current_variant.build(final_name, self.base)

        # Set custom doc if provided
        if self.doc is not None:
            built_model.__doc__ = self.doc

        # Change the variant type - this is the key change!
        context.current_variant = built_model

        return context
