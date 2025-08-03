from copy import copy
from pydantic import BaseModel, ConfigDict, create_model, Field
from typing import Any, Callable, Dict, Protocol, Tuple, Union
from pydantic.fields import FieldInfo


class VariantPipeline:
    """
    Immutable pipeline that holds an ordered tuple of operations (functions).
    Supports list-like operations but returns new instances for immutability.
    """

    def __init__(self, *operations: Callable):
        self._operations: Tuple[Callable, ...] = tuple(operations)

    def __call__(self, obj: Any) -> Any:
        """Execute all operations sequentially on the input object"""
        for operation in self._operations:
            obj = operation(obj)
        return obj

    def append(self, operation: Callable) -> "VariantPipeline":
        """Return a new pipeline with the operation appended"""
        return VariantPipeline(*self._operations, operation)

    def insert(self, index: int, operation: Callable) -> "VariantPipeline":
        """Return a new pipeline with the operation inserted at the given index"""
        ops = list(self._operations)
        ops.insert(index, operation)
        return VariantPipeline(*ops)

    def replace(self, index: int, operation: Callable) -> "VariantPipeline":
        """Return a new pipeline with the operation at index replaced"""
        ops = list(self._operations)
        ops[index] = operation
        return VariantPipeline(*ops)

    def __getitem__(self, key: Union[int, slice]) -> Union[Callable, "VariantPipeline"]:
        """Support indexing and slicing"""
        if isinstance(key, slice):
            return VariantPipeline(*self._operations[key])
        return self._operations[key]

    def __len__(self) -> int:
        """Return the number of operations in the pipeline"""
        return len(self._operations)

    def __iter__(self):
        """Allow iteration over operations"""
        return iter(self._operations)

    def __repr__(self) -> str:
        return f"VariantPipeline({', '.join(op.__name__ if hasattr(op, '__name__') else str(op) for op in self._operations)})"


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
            self.original_model_cls.__name__ + name,
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


class VariantContext:
    original_model: type[BaseModel]
    current_variant: DecomposedModel | type[BaseModel]
    metadata: Dict[str, Any]

    def __init__(self, name: str):
        self.name = name
        self.metadata = {}

    def __call__(self, model_cls: type[BaseModel]) -> "VariantContext":
        """Initialize with a BaseModel class"""
        self.original_model = model_cls
        self.current_variant = DecomposedModel(model_cls)
        return self


class ModelTransformer(Protocol):
    def __call__(self, context: VariantContext) -> VariantContext: ...
