from typing import Annotated, Any, Dict, Literal, Type, get_origin, Union, Optional, Protocol
from dataclasses import dataclass, field

from beanie import Document, PydanticObjectId
from pydantic import BaseModel, Field, create_model
from pydantic.fields import FieldInfo


class Filter:
    """Mark field for filtering from input/output models"""

    def __init__(self, exclude: Literal["in", "out", "any"]):
        self.exclude = exclude


@dataclass(frozen=True)
class FieldData:
    """Immutable field data"""

    name: str
    field_info: FieldInfo


class FieldTransformer(Protocol):
    """Protocol for field transformers"""

    def transform(self, field: FieldData) -> Optional[FieldData]: ...


class ExcludeByName(FieldTransformer):
    """Exclude fields by name"""

    def __init__(self, *names: str):
        self.names = frozenset(names)

    def transform(self, field: FieldData) -> Optional[FieldData]:
        return None if field.name in self.names else field


class ExcludeByFilter(FieldTransformer):
    """Exclude fields by Filter metadata"""

    def __init__(self, *filters: str):
        self.filters = frozenset(filters)

    def transform(self, field: FieldData) -> Optional[FieldData]:
        return (
            None
            if any(isinstance(m, Filter) and m.exclude in self.filters for m in field.field_info.metadata)
            else field
        )


class MakeOptional(FieldTransformer):
    """Make field optional, excluding discriminator fields"""

    def __init__(self, exclude_fields: tuple[str, ...] = ()):
        self.exclude_fields = frozenset(exclude_fields)

    def transform(self, field: FieldData) -> FieldData:
        # Don't make discriminator fields optional
        if field.name in self.exclude_fields:
            return field

        annotation = field.field_info.annotation
        metadata = field.field_info.metadata

        if not field.field_info.is_required():
            return field  # Already optional

        new_annotation = Annotated[Union[annotation, None], *metadata] if metadata else Union[annotation, None]
        new_default = None

        new_field_info = FieldInfo.from_annotated_attribute(
            annotation=new_annotation,  # type: ignore
            default=new_default,
        )

        return FieldData(field.name, new_field_info)


class CleanFilterMetadata(FieldTransformer):
    """Remove Filter instances from annotations"""

    def transform(self, field: FieldData) -> FieldData:
        annotation = field.field_info.annotation

        if get_origin(annotation) is not Annotated:
            return field

        metadata = field.field_info.metadata
        clean_metadata = tuple(m for m in metadata if not isinstance(m, Filter))
        clean_annotation = Annotated[annotation, *clean_metadata] if clean_metadata else annotation

        new_field_info = FieldInfo.from_annotated_attribute(
            annotation=clean_annotation,  # type: ignore
            default=field.field_info.default,
        )

        return FieldData(field.name, new_field_info)


class HandleSpecialId(FieldTransformer):
    """Handle special id field processing"""

    def transform(self, field: FieldData) -> FieldData:
        if field.name == "id":
            new_field_info = FieldInfo.from_annotated_attribute(
                annotation=Annotated[PydanticObjectId | None, Field()],  # type: ignore
                default=None,
            )
            return FieldData(field.name, new_field_info)

        return field


def make_output(self):
    """creates an OUTPUT object from base object"""
    return self.Output(**self.model_dump())


@dataclass
class ModelVariation:
    """Configuration for a model variation"""

    name: str
    field_transformers: tuple[FieldTransformer, ...]
    add_to_base: Optional[Dict[str, Any]] = field(default_factory=dict)


# Common transformers
COMMON_EXCLUDES = ExcludeByName("revision_id", "created_at", "updated_at")
CLEAN_FILTERS = CleanFilterMetadata()
HANDLE_ID = HandleSpecialId()

# Predefined variations
INPUT = ModelVariation(
    name="Input",
    field_transformers=(
        COMMON_EXCLUDES,
        ExcludeByName("_id", "id"),
        ExcludeByFilter("in", "any"),
        CLEAN_FILTERS,
    ),
)

OUTPUT = ModelVariation(
    name="Output",
    field_transformers=(
        COMMON_EXCLUDES,
        ExcludeByFilter("out", "any"),
        CLEAN_FILTERS,
        HANDLE_ID,
    ),
)

UPDATE = ModelVariation(
    name="Update",
    field_transformers=(
        COMMON_EXCLUDES,
        ExcludeByName("_id", "id"),
        ExcludeByFilter("in", "any"),
        CLEAN_FILTERS,
        MakeOptional(("service_type",)),
    ),
    add_to_base={"_make_output": make_output},
)


def schema_models(*variations: ModelVariation):
    """Decorator to generate model variations for BaseModel classes"""

    def decorator(cls: Type[Document]) -> Type[Document]:
        cls.model_variations = {}  # type: ignore

        # Create each variation
        for variation in variations:
            model = create_variation(cls, variation)
            cls.model_variations[variation.name] = model  # type: ignore
            setattr(cls, variation.name, model)
            if variation.add_to_base:
                for attr_name, attr in variation.add_to_base.items():
                    setattr(cls, attr_name, attr)

        cls._variations = variations  # type: ignore
        cls.rebuild_models = classmethod(_rebuild_models)  # type: ignore
        return cls

    return decorator


def _apply_transformers(field: FieldData, transformers: tuple[FieldTransformer, ...]) -> Optional[FieldData]:
    """Apply transformers sequentially to field"""
    current_field = field

    for transformer in transformers:
        if current_field is None:
            break
        current_field = transformer.transform(current_field)

    return current_field


def create_variation(model_class: Type[BaseModel], variation: ModelVariation) -> Type[BaseModel]:
    """Create a single model variation"""
    model_fields = {}

    # Process each field from the model class
    for field_name, field_info in model_class.model_fields.items():
        field_data = FieldData(field_name, field_info)
        transformed_field = _apply_transformers(field_data, variation.field_transformers)

        # Add field to model if not excluded
        if transformed_field is not None:
            model_fields[transformed_field.name] = (
                transformed_field.field_info.annotation,
                transformed_field.field_info,
            )

    # Create the model
    model = create_model(f"{model_class.__name__}_{variation.name}", __module__=model_class.__module__, **model_fields)
    model._source_document = model_class  # type: ignore

    return model


def _rebuild_models(cls):
    """Rebuild the main model and all its variations"""
    cls.model_rebuild()

    for variation in cls._variations:
        if variation.name in cls.model_variations:
            try:
                cls.model_variations[variation.name].model_rebuild()
            except AssertionError:
                # Sometimes it fails first time, try again
                cls.model_variations[variation.name].model_rebuild()
