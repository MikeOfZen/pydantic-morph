from typing import Any, Dict
from copy import copy

from ..core import DecomposedModel, VariantContext, ModelTransformer
from ..field_ops import modify_fieldinfo


class ModifyFields(ModelTransformer):
    """
    Modifies specific fields in a DecomposedModel using field_ops.modify_fieldinfo.

    Allows updating field attributes like annotation, default, validation_alias, etc.
    Special 'metadata_callback' key gets unpacked as a parameter to modify_fieldinfo.

    Args:
        field_modifications: Dict mapping field names to modification dicts.
                           Each modification dict contains field attributes to change.
                           Special key 'metadata_callback' gets passed separately.

    Raises:
        ValueError: If not operating on a DecomposedModel or invalid field attributes or addressing non-existent fields.

    Example:
        ```python
        # Modify field defaults and annotations
        ModifyFields({
            'name': {'default': 'Anonymous', 'annotation': str},
            'apt': {'default': '0', 'annotation': int, 'alias': 'apartment_number'},
        })

        # Modify metadata with callback
        ModifyFields({
            'email': {
                'validation_alias': 'email_address',
                'metadata_callback': lambda meta: meta + your_metadata_list
            }
        })
        ```
    """

    def __init__(self, field_modifications: Dict[str, Dict[str, Any]]):
        self.field_modifications = field_modifications

    def __call__(self, context: VariantContext) -> VariantContext:
        if not isinstance(context.current_variant, DecomposedModel):
            raise ValueError(
                "ModifyFields transformer requires DecomposedModel, got built model"
            )

        new_fields = copy(context.current_variant.model_fields)

        for field_name, modifications in self.field_modifications.items():
            if field_name not in new_fields:
                raise ValueError(f"Field '{field_name}' not found in model fields")

            # Extract metadata_callback if present
            mod_copy = modifications.copy()
            metadata_callback = mod_copy.pop("metadata_callback", None)

            # Apply modifications
            new_fields[field_name] = modify_fieldinfo(
                new_fields[field_name], metadata_callback=metadata_callback, **mod_copy
            )

        context.current_variant.model_fields = new_fields
        return context
