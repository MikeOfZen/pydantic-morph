from typing import Any, Callable, Dict, Iterable, Type, Union, get_args, get_origin

from pydantic.fields import FieldInfo

from pydantic_variants.core import DecomposedModel, ModelTransformer, VariantContext
from pydantic_variants.field_ops import modify_fieldinfo


class DefaultFactoryTag:
    """Wrapper for default factory values"""

    def __init__(self, factory: Callable[[], Any]):
        self.factory = factory


class MakeOptional(ModelTransformer):
    """
    Makes fields optional by adding None to their type union and setting defaults.

    Supports four mutually exclusive modes:
    - all: Make all fields optional with None default
    - exclude: Make all fields optional except specified ones
    - include_only: Make only specified fields optional
    - callable: Use function to determine which fields to make optional and their defaults

    Args:
        all: Boolean - make all fields optional with None default
        exclude: Iterable of field names to exclude from making optional
        include_only: Iterable of field names to make optional (all others unchanged)
        callable: Function(name: str, field: FieldInfo) -> (bool, Any) that returns
                 (should_make_optional, default_value)
        defaults: Dict mapping field names to default values (works with all modes)

    Raises:
        ValueError: If more than one mode option is provided

    Example:
        # Make all fields optional
        Optional(all=True)

        # Make all except specific fields optional
        Optional(exclude=['id', 'created_at'], defaults={'name': 'Anonymous'})

        # Make only specific fields optional
        Optional(include_only=['name', 'email'])

        # Custom logic with function returning (should_make_optional, default_value)
        Optional(callable=lambda name, field: (not name.endswith('_id'), f'default_{name}'))
    """

    def __init__(
        self,
        all: bool | None = None,
        exclude: Iterable[str] | None = None,
        include_only: Iterable[str] | None = None,
        optional_func: Callable[[str, FieldInfo], tuple[bool, Any]] | None = None,
        defaults: Dict[str, Any] | None = None,
    ):
        if sum(x is not None for x in [all, exclude, include_only, optional_func]) != 1:
            raise ValueError("Must provide one of: all, exclude, include_only, or callable")

        self.defaults = defaults or {}

        # Build the appropriate logic
        if all:
            self._get_optional_info = lambda name, field: (
                True,
                self.defaults.get(name),
            )
        elif exclude is not None:
            exclude_set = set(exclude)
            self._get_optional_info = lambda name, field: (
                name not in exclude_set,
                self.defaults.get(name),
            )
        elif include_only is not None:
            include_set = set(include_only)
            self._get_optional_info = lambda name, field: (
                name in include_set,
                self.defaults.get(name),
            )
        elif optional_func is not None:  # callable
            self._get_optional_info = optional_func  # type: ignore
        else:
            raise ValueError("Must provide one of: all, exclude, include_only, or callable")

    def __call__(self, context: VariantContext) -> VariantContext:
        if not isinstance(context.current_variant, DecomposedModel):
            raise ValueError("Build transformer requires DecomposedModel, got built model")
        new_fields = {}
        for field_name, field_info in context.current_variant.model_fields.items():
            make_opt, default_value = self._get_optional_info(field_name, field_info)
            if field_info.is_required() and make_opt:
                new_fields[field_name] = self._make_optional(field_info, default_value)
            else:
                new_fields[field_name] = field_info
        context.current_variant.model_fields = new_fields
        return context

    @staticmethod
    def _make_optional(field_info: FieldInfo, default_value: Any) -> FieldInfo:
        ann = field_info.annotation

        # Case 1: Factory - no need to add None to annotation
        if isinstance(default_value, DefaultFactoryTag):
            return modify_fieldinfo(field_info, default_factory=default_value.factory)

        # Case 2: None default - add None to annotation if not already there
        elif default_value is None:
            annotation = ann if MakeOptional._none_in_annotation(ann) else Union[ann, None]
            return modify_fieldinfo(field_info, annotation=annotation, default=None)

        # Case 3: Other value - keep original annotation
        else:
            return modify_fieldinfo(field_info, default=default_value)

    @staticmethod
    def _none_in_annotation(annotation: Any) -> bool:
        if annotation is None or annotation is Any:
            return True
        origin = get_origin(annotation)
        if origin is Union:
            args = get_args(annotation)
            if type(None) in args or Any in args:
                return True

        return False
