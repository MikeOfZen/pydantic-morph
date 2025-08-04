from typing import Any, Iterable, get_origin, get_args
from pydantic import BaseModel

from pydantic_variants.core import DecomposedModel, ModelTransformer, VariantContext
from pydantic_variants.field_ops import modify_fieldinfo


class SwitchVariant(ModelTransformer):
    """
    Switches nested BaseModel types to their variants in field annotations.
    this allows nested schema changes of any depth.
    the variants must be attached to the model (by calling Attach in their pipeline)

    Iterates through model fields and replaces BaseModel types that have the
    specified variant with their variant counterpart. Handles Union types and
    nested generics.

    Args:
        variant_name: Name of variant to switch to (defaults to context name if None)
        exclude: Field names to ignore during processing

    Example:
        # Switch all nested models to 'Input' variant
        SwitchNested('Input')

        # Use context name as variant name
        SwitchNested()

        # Exclude specific fields
        SwitchNested('Output', exclude=['metadata', 'audit'])
    """

    def __init__(
        self, variant_name: str | None = None, exclude: Iterable[str] | None = None
    ):
        self.variant_name = variant_name
        self.exclude = set(exclude) if exclude else set()

    def __call__(self, context: VariantContext) -> VariantContext:
        if not isinstance(context.current_variant, DecomposedModel):
            raise ValueError(
                "SwitchNested transformer requires DecomposedModel, got built model"
            )

        # Use context name if no variant name specified
        variant_name = self.variant_name or context.name

        # Process each field
        for field_name, field_info in context.current_variant.model_fields.items():
            if field_name not in self.exclude:
                new_annotation = self._switch_annotation(
                    field_info.annotation, variant_name
                )
                if new_annotation != field_info.annotation:
                    # Update the field with new annotation
                    context.current_variant.model_fields[field_name] = modify_fieldinfo(
                        field_info,
                        annotation=new_annotation,
                    )

        return context

    def _switch_annotation(self, annotation: Any, variant_name: str) -> Any:
        """Switch BaseModel types to variants in annotation"""
        origin = get_origin(annotation)

        # Handle other generic types (List, Dict, etc.)
        if origin is not None:
            args = get_args(annotation)
            new_args = tuple(self._switch_annotation(arg, variant_name) for arg in args)
            return origin[new_args]

        # Handle BaseModel types
        elif (
            isinstance(annotation, type)
            and issubclass(annotation, BaseModel)
            and hasattr(annotation, "_variants")
            and variant_name in annotation._variants  # type: ignore
        ):
            return annotation._variants[variant_name]  # type: ignore

        # Return unchanged
        return annotation
