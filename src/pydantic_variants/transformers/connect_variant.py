from typing import ClassVar

from pydantic import BaseModel
from pydantic_variants.core import DecomposedModel, ModelTransformer, VariantContext


class ConnectVariant(ModelTransformer):
    """
    Attaches a built variant model to the original model class.
    and also connects root model to the variant.

    Requires the variant to already be built (type[BaseModel]).
    Always stores variants in the ._variants dict using the context name as key.
    Optionally can also attach directly as an attribute on the class.

    Args:
        attach_directly: If True, also attaches the variant as ._{name} attribute
        attach_root: If True, attaches the original model as _root_model on the variant.
    Raises:
        ValueError: If not operating on a built model.
    """

    def __init__(self, attach_directly: bool = True, attach_root: bool = True):
        self.attach_directly = attach_directly
        self.attach_root = attach_root

    def __call__(self, context: VariantContext) -> VariantContext:
        # Assert we have a built model
        if isinstance(context.current_variant, DecomposedModel):
            raise ValueError("Attach transformer requires built model, got DecomposedModel")

        variant_model = context.current_variant

        # Ensure ._variants dict exists
        if not hasattr(context.original_model, "_variants"):
            context.original_model.__annotations__["_variants"] = ClassVar[dict[str, type(BaseModel)]]  # this keeps the linters happy
            context.original_model._variants = {}  # type: ignore

        context.original_model._variants[context.name] = variant_model  # type: ignore

        if self.attach_directly:
            context.original_model.__annotations__[context.name] = ClassVar[type(BaseModel)]
            setattr(context.original_model, f"{context.name}", variant_model)
        if self.attach_root:
            variant_model.__annotations__["_root_model"] = ClassVar[type(BaseModel)]
            setattr(variant_model, "_root_model", context.original_model)

        return context
