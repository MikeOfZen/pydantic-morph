from copy import copy
from typing import Any, Callable, Dict

from pydantic.fields import FieldInfo

from pydantic_variants.core import DecomposedModel, ModelTransformer, VariantContext
from pydantic_variants.field_ops import modify_fieldinfo
from pydantic_variants.transformers.filter_tag import Tag


class ModifyFields(ModelTransformer):
    """
    Modifies specific fields in a DecomposedModel using field_ops.modify_fieldinfo.

    Supports two modes:
    - field_modifications: Dict mapping field names to modification dicts
    - modify_func: Function that takes field name and FieldInfo, returns modification dict

    Allows updating field attributes like annotation, default, validation_alias, etc.
    Special 'metadata_callback' key gets unpacked as a parameter to modify_fieldinfo.

    Args:
        field_modifications: Dict mapping field names to modification dicts.
                           Each modification dict contains field attributes to change.
        modify_func: Function(name: str, field: FieldInfo) -> Dict[str, Any] that returns
                    modifications to apply to the field

    Raises:
        ValueError: If both or neither modification options are provided, or if not
                   operating on a DecomposedModel.

    Example:
        ```python
        # Dict-based modifications
        ModifyFields(field_modifications={
            'name': {'default': 'Anonymous', 'annotation': str},
            'apt': {'default': '0', 'annotation': int, 'alias': 'apartment_number'},
        })

        # Function-based modifications
        ModifyFields(modify_func=lambda name, field: {
            'description': f'Field {name} with type {field.annotation}'
        } if field.is_required() else {})
        ```
    """

    def __init__(
        self,
        field_modifications: Dict[str, Dict[str, Any]] | None = None,
        tag_modifications: Dict[Tag, Dict[str, Any]] | None = None,
        modify_func: Callable[[str, FieldInfo], Dict[str, Any] | None] | None = None,
    ):
        if sum(x is not None for x in [field_modifications, modify_func, tag_modifications]) != 1:
            raise ValueError("Must provide either field_modifications or modify_func or tag_modifications")

        # Convert dict to function if needed
        if field_modifications:
            self.modify_func = lambda name, field: field_modifications.get(name)
        elif tag_modifications:

            def get_tag_modifications(name, field):
                mods = {}
                for tag in tuple(tag_modifications.keys()):
                    if tag.in_field(field):
                        mods.update(tag_modifications[tag])
                return mods

            self.modify_func = get_tag_modifications
        else:
            self.modify_func = modify_func  # type: ignore

    def __call__(self, context: VariantContext) -> VariantContext:
        if not isinstance(context.current_variant, DecomposedModel):
            raise ValueError("ModifyFields transformer requires DecomposedModel, got built model")

        new_fields = copy(context.current_variant.model_fields)

        for field_name, field_info in new_fields.items():
            modifications = self.modify_func(field_name, field_info)  # type: ignore

            if modifications:  # Only modify if function returns non-empty dict
                # Extract metadata_callback if present
                metadata_callback = modifications.pop("metadata_callback", None)

                # Apply modifications
                new_fields[field_name] = modify_fieldinfo(field_info, metadata_callback=metadata_callback, **modifications)

        context.current_variant.model_fields = new_fields
        return context
