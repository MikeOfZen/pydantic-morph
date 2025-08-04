from pydantic import BaseModel

from pydantic_variants.core import DecomposedModel, VariantContext


class ExtractVariant:
    """
    Extracts and returns the current variant model.

    This is a utility transformer that simply returns the built model
    from context.current_variant. Useful for getting the final model
    at the end of a pipeline.

    Raises:
        ValueError: If current_variant is not a built model

    Example:
        # At the end of a pipeline to get the final model
        pipeline = VariantPipeline(
            FilterFields(exclude=['internal_id']),
            BuildVariant(),
            ExtractVariant()
        )
        final_model = pipeline(context)
    """

    def __call__(self, context: VariantContext) -> type[BaseModel]:
        if isinstance(context.current_variant, DecomposedModel):
            raise ValueError(
                "ExtractVariant requires built model, got DecomposedModel. Use BuildVariant first."
            )

        return context.current_variant
