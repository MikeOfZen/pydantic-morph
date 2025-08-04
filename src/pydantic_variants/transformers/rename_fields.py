from typing import Callable, Dict

from pydantic_variants.core import DecomposedModel, ModelTransformer, VariantContext


class RenameFields(ModelTransformer):
    """
    Renames fields in a DecomposedModel using a mapping dict or custom function.

    Supports two renaming modes:
    - mapping: Dictionary of old_name -> new_name mappings
    - rename_func: Function that takes field name and returns new name (or same name)

    Args:
        mapping: Dict mapping current field names to new field names
        rename_func: Function(name: str) -> str that returns the new field name

    Raises:
        ValueError: If both or neither renaming options are provided

    Example:
        # Simple field renaming
        Rename(mapping={'user_id': 'id', 'email_addr': 'email'})

        # Pattern-based renaming with regex
        Rename(rename_func=lambda name: re.sub(r'_id$', '', name))

        # Convert snake_case to camelCase
        Rename(rename_func=lambda name: re.sub(r'_([a-z])', lambda m: m.group(1).upper(), name))
    """

    def __init__(
        self,
        mapping: Dict[str, str] | None = None,
        rename_func: Callable[[str], str | None] | None = None,
    ):
        if sum(x is not None for x in [mapping, rename_func]) != 1:
            raise ValueError("Must provide either mapping or rename_func")

        self._rename_func = rename_func if rename_func else mapping.get  # type: ignore

    def __call__(self, context: VariantContext) -> VariantContext:
        if not isinstance(context.current_variant, DecomposedModel):
            raise ValueError(
                "Rename transformer requires DecomposedModel, got built model"
            )

        new_fields = {}
        for old_name, field in context.current_variant.model_fields.items():
            new_name = self._rename_func(old_name) or old_name
            new_fields[new_name] = field
        context.current_variant.model_fields = new_fields
        return context
