from typing import Callable, Protocol, TypeVar

from pydantic import BaseModel

from pydantic_variants.core import ModelTransformer, VariantContext, VariantPipe
from pydantic_variants.transformers import BuildVariant, ConnectVariant
from pydantic_variants.transformers.extract_variant import ExtractVariant

# Generic type variable to preserve the original model type
T = TypeVar("T", bound=BaseModel)


def basic_variant_pipeline(name: str, *transformers: ModelTransformer) -> VariantPipe:
    """
    Helper function to create a complete variant pipeline.

    Automatically adds VariantContext creation, BuildVariant, and ConnectVariant
    transformers to create a complete pipeline.

    Args:
        name: Name of the variant
        *transformers: Field and model transformers to apply

    Returns:
        Complete VariantPipe ready for use with @variants decorator
    """

    return VariantPipe(VariantContext(name), *transformers, BuildVariant(), ConnectVariant(), ExtractVariant())


def variants(*pipelines: VariantPipe, delayed_build: bool = False) -> Callable[[type[T]], type[T]]:
    """
    Decorator that generates model variants using VariantPipe pipelines.

    Args:
        *pipelines: VariantPipe instances defining transformation pipelines
        delayed_build: If True, attaches pipeline logic to _build_variants method
                      instead of executing immediately

    Returns:
        Decorated BaseModel class with variants attached or _build_variants method
    """

    def immediate_decorator(model_cls: type[T]) -> type[T]:
        for pipeline in pipelines:
            pipeline(model_cls)
        return model_cls

    def delayed_decorator(model_cls: type[T]) -> type[T]:
        def _build_variants():
            for pipeline in pipelines:
                pipeline(model_cls)

        model_cls._build_variants = _build_variants  # type: ignore
        return model_cls

    return delayed_decorator if delayed_build else immediate_decorator
