from typing import Iterable

from pydantic.fields import FieldInfo

from pydantic_variants.core import DecomposedModel, ModelTransformer, VariantContext


class Tag:
    """Tag class for marking fields with metadata keys"""

    def __init__(self, key: str):
        self.key = key

    def __eq__(self, other):
        return isinstance(other, Tag) and self.key == other.key

    def __hash__(self):
        return hash(self.key)

    def __repr__(self):
        return f"Tag('{self.key}')"

    def in_field(self, field: FieldInfo) -> bool:
        if not field.metadata:
            return False
        return any(isinstance(item, Tag) and item == self for item in field.metadata)


class FilterTag(ModelTransformer):
    """
    Filters out fields that have Tag instances in their metadata matching the specified keys.

    Searches through field metadata for Tag instances and removes fields where any
    Tag.key matches the provided filter keys.

    Args:
        keys: Single key string or iterable of key strings to filter out

    Raises:
        ValueError: If not operating on a DecomposedModel

    Example:
        # Filter fields tagged with 'internal'
        FilterByTags('internal')

        # Filter fields tagged with multiple keys
        FilterByTags(['internal', 'deprecated', 'admin_only'])

        # Usage with Field metadata
        class User(BaseModel):
            id: int = Field(metadata=[Tag('internal')])
            name: str
            email: str = Field(metadata=[Tag('admin_only')])
    """

    def __init__(self, keys: str | Iterable[str]):
        if isinstance(keys, str):
            self.filter_keys = {keys}
        else:
            self.filter_keys = set(keys)

    def __call__(self, context: VariantContext) -> VariantContext:
        if not isinstance(context.current_variant, DecomposedModel):
            raise ValueError("FilterByTags transformer requires DecomposedModel, got built model")

        new_fields = {}
        for name, field in context.current_variant.model_fields.items():
            if not self._has_matching_tag(field):
                new_fields[name] = field

        context.current_variant.model_fields = new_fields
        return context

    def _has_matching_tag(self, field: FieldInfo) -> bool:
        """Check if field has any Tag in metadata that matches our filter keys"""
        if not field.metadata:
            return False

        for metadata_item in field.metadata:
            if isinstance(metadata_item, Tag) and metadata_item.key in self.filter_keys:
                return True

        return False
