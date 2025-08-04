from typing import Dict

from pydantic.fields import FieldInfo

from pydantic_variants.core import DecomposedModel, ModelTransformer, VariantContext


class SetFields(ModelTransformer):
    """
    Sets or updates specific fields in a DecomposedModel with new field definitions.

    This transformer allows adding new fields or overriding existing ones with
    custom FieldInfo configurations.

    Args:
        fields: Dict mapping field names to FieldInfo instances

    Raises:
        ValueError: If not operating on a DecomposedModel

    Example:
        # Add new fields
        SetFields({
            'created_by': FieldInfo(annotation=str, default='system'),
            'version': FieldInfo(annotation=int, default=1)
        })

        # Override existing field
        SetFields({
            'id': FieldInfo(annotation=str, default_factory=lambda: str(uuid4()))
        })
    """

    def __init__(self, fields: Dict[str, FieldInfo]):
        self.fields = fields

    def __call__(self, context: VariantContext) -> VariantContext:
        if not isinstance(context.current_variant, DecomposedModel):
            raise ValueError(
                "SetFields transformer requires DecomposedModel, got built model"
            )

        # Update existing fields with new ones
        context.current_variant.model_fields.update(self.fields)

        return context
