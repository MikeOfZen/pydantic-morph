from core import DecomposedModel, ModelTransformer, VariantContext


class ConnectVariant(ModelTransformer):
    """
    Attaches a built variant model to the original model class.
    and also connects base model to the vairant.

    Requires the variant to already be built (type[BaseModel]).
    Always stores variants in the ._variants dict using the context name as key.
    Optionally can also attach directly as an attribute on the class.

    Args:
        attach_directly: If True, also attaches the variant as ._{name} attribute
        attach_base: If True, attaches the original model as _root_model on the variant.
    Raises:
        ValueError: If not operating on a built model.
    """

    def __init__(self, attach_directly: bool = True, attach_base: bool = True):
        self.attach_directly = attach_directly
        self.attach_base = attach_base

    def __call__(self, context: VariantContext) -> VariantContext:
        # Assert we have a built model
        if isinstance(context.current_variant, DecomposedModel):
            raise ValueError(
                "Attach transformer requires built model, got DecomposedModel"
            )

        variant_model = context.current_variant

        # Ensure ._variants dict exists
        if not hasattr(context.original_model, "_variants"):
            context.original_model._variants = {}  # type: ignore

        # Always store in _variants dict
        context.original_model._variants[context.name] = variant_model  # type: ignore

        # Optionally attach directly as attribute
        if self.attach_directly:
            setattr(context.original_model, f"_{context.name}", variant_model)
        if self.attach_base:
            setattr(variant_model, "_root_model", context.original_model)

        return context
