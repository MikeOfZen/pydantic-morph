from typing import Any, Callable

from pydantic.fields import FieldInfo


def modify_fieldinfo(
    original: FieldInfo,
    metadata_callback: Callable[[list], list] | None = None,
    **changes: Any,
) -> FieldInfo:
    """
    Create a modified copy of a FieldInfo instance.

    Args:
        original: Source FieldInfo to copy
        metadata_callback: Function to transform metadata list
        **changes: Field attributes to modify (must be valid __slots__)

    Raises:
        ValueError: When attempting to modify invalid attributes

    Example:
        modify_fieldinfo(field, annotation=int, default=42,
                        metadata_callback=lambda meta: meta + [{"custom": "value"}])
    """
    # Get valid attributes from the actual object's class hierarchy
    valid_attrs = set()
    for cls in original.__class__.__mro__:
        if hasattr(cls, "__slots__"):
            valid_attrs.update(cls.__slots__)

    # Check for invalid attributes
    invalid_attrs = set(changes.keys()) - valid_attrs
    if invalid_attrs:
        raise ValueError(
            f"Invalid FieldInfo attributes: {invalid_attrs}, not defined in __slots__"
        )

    field_copy = original._copy()

    for attr, value in changes.items():
        setattr(field_copy, attr, value)

    if metadata_callback:
        field_copy.metadata = metadata_callback(field_copy.metadata)

    return field_copy
