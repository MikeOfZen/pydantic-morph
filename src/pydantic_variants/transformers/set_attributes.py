from typing import Any, Dict

from pydantic_variants.core import DecomposedModel, ModelTransformer, VariantContext


class SetAttribute(ModelTransformer):
    """
    Sets class attributes on the variant and/or root model.

    Allows attaching arbitrary attributes to models during the transformation pipeline.
    Accepts dictionaries of attributes to set on each target.

    Args:
        variant_attrs: Dict of attribute name -> value pairs to set on the variant model
        root_attrs: Dict of attribute name -> value pairs to set on the root model

    Raises:
        ValueError: If variant_attrs is provided but current_variant is not built

    Example:
        # Set attributes on both models
        SetAttribute(
            variant_attrs={'_schema_version': '2.1.0', 'random_func': lambda x: x * 2},
            root_attrs={'_has_rabies': False}
        )

        # Set only on root model
        SetAttribute(root_attrs={'_last_modified': datetime.now()})

        # Set only on variant model
        SetAttribute(variant_attrs={'make_output': lambda: self:self._Output(**self.model_dump)})
    """

    def __init__(
        self,
        variant_attrs: Dict[str, Any] | None = None,
        root_attrs: Dict[str, Any] | None = None,
    ):
        self.variant_attrs = variant_attrs or {}
        self.root_attrs = root_attrs or {}

    def __call__(self, context: VariantContext) -> VariantContext:
        # Set attributes on variant if provided
        if self.variant_attrs:
            if isinstance(context.current_variant, DecomposedModel):
                raise ValueError(
                    "SetAttribute with variant_attrs requires built model. Use BuildVariant first."
                )
            for name, value in self.variant_attrs.items():
                setattr(context.current_variant, name, value)

        # Set attributes on root model if provided
        if self.root_attrs:
            for name, value in self.root_attrs.items():
                setattr(context.original_model, name, value)

        return context
