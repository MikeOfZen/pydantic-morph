from typing import Callable, Iterable

from pydantic.fields import FieldInfo

from pydantic_variants.core import DecomposedModel, ModelTransformer, VariantContext


class FilterFields(ModelTransformer):
    """
    Filters fields from a DecomposedModel based on field names or custom logic.

    Supports three mutually exclusive filtering modes:
    - exclude: Remove specific fields by name
    - include_only: Keep only specific fields by name
    - filter_func: Custom function that returns True for fields to REMOVE

    Args:
        exclude: Iterable of field names to exclude from the model
        include_only: Iterable of field names to keep (all others removed)
        filter_func: Function(name: str, field: FieldInfo) -> bool that returns
                    True for fields that should be REMOVED

    Raises:
        ValueError: If more than one filtering option is provided

    Example:
        # Remove specific fields
        Filter(exclude=['id', 'created_at'])

        # Keep only specific fields
        Filter(include_only=['name', 'email'])

        # Custom filter logic
        Filter(filter_func=lambda name, field: field.is_required() == False)
    """

    def __init__(
        self,
        exclude: Iterable[str] | None = None,
        include_only: Iterable[str] | None = None,
        filter_func: Callable[[str, FieldInfo], bool] | None = None,
    ):
        if sum(x is not None for x in [exclude, include_only, filter_func]) != 1:
            raise ValueError(
                "Must provide one of: exclude, include_only, or filter_func"
            )

        # Build the appropriate filter lambda
        if exclude is not None:
            exclude_set = set(exclude)
            self._filter_func = lambda name, field: name in exclude_set
        elif include_only is not None:
            include_set = set(include_only)
            self._filter_func = lambda name, field: name not in include_set
        else:
            self._filter_func = filter_func

    def __call__(self, context: VariantContext) -> VariantContext:
        # Build a new dict with fields that should be kept
        if not isinstance(context.current_variant, DecomposedModel):
            raise ValueError(
                "Filter transformer requires DecomposedModel, got built model"
            )

        new_fields = {}
        for name, field in context.current_variant.model_fields.items():
            if not self._filter_func(name, field):  # type: ignore
                new_fields[name] = field

        context.current_variant.model_fields = new_fields
        return context
