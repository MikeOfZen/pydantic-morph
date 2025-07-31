from copy import copy
from pydantic import BaseModel, ConfigDict, create_model
from typing import Any, Callable, Dict, Iterable, Protocol
from pydantic.fields import FieldInfo


class VariantPipe:
    """
    Simple recursive pipeline where each step can be a function or another Pipeline
    """

    def __init__(self, step=None):
        self.step = step
        self.next = None

    def then(self, step_or_pipe):
        """Add a step (function) or another pipeline to the chain"""
        if self.next is None:
            if callable(step_or_pipe):
                self.next = VariantPipe(step_or_pipe)
            else:
                self.next = step_or_pipe
        else:
            self.next.then(step_or_pipe)
        return self  # Always return root pipeline

    def process(self, obj):
        """Execute the pipeline on an object"""
        if self.step:
            obj = self.step(obj)
        if self.next:
            obj = self.next.process(obj)
        return obj


class DecomposedModel:
    model_fields: Dict[str, FieldInfo]
    model_config: dict
    original_model_cls: type[BaseModel]
    model_doc: str | None

    def __init__(self, model_cls: type[BaseModel]):
        self.model_fields = copy(model_cls.model_fields)
        self.model_config = copy(model_cls.model_config)  # type: ignore
        self.original_model_cls = model_cls
        self.model_doc = model_cls.__doc__ or None

    def build(self, name: str, base: Any = None) -> type[BaseModel]:
        return create_model(
            name,
            __config__=ConfigDict(self.model_config),  # type: ignore
            __doc__=self.model_doc,
            __base__=base,
            __module__=self.original_model_cls.__module__,
            **self._prep_fields(),  # type: ignore
            # TODO handle other fields
        )

    def _prep_fields(self) -> Dict[str, tuple[type, FieldInfo]]:
        model_fields = {}
        for field_name, field in self.model_fields.items():
            model_fields[field_name] = (
                field.annotation,
                field,
            )
        return model_fields


class ModelTransformer(Protocol):
    def __call__(self, decomposed_model: DecomposedModel) -> DecomposedModel: ...


class Filter(ModelTransformer):
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

    def __call__(self, decomposed_model: DecomposedModel) -> DecomposedModel:
        # Apply the filter function to the model fields

        for name, field in decomposed_model.model_fields.items():
            if self._filter_func(name, field):  # type: ignore
                decomposed_model.model_fields.pop(name, None)

        return decomposed_model


class Rename(ModelTransformer):
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
        rename_func: Callable[[str], str] | None = None,
    ):
        if sum(x is not None for x in [mapping, rename_func]) != 1:
            raise ValueError("Must provide either mapping or rename_func")

        self._rename_func = rename_func if rename_func else mapping.get  # type: ignore

    def __call__(self, decomposed_model: DecomposedModel) -> DecomposedModel:
        new_fields = {}

        for old_name, field in decomposed_model.model_fields.items():
            new_name = self._rename_func(old_name)
            new_fields[new_name] = field

        decomposed_model.model_fields = new_fields
        return decomposed_model
