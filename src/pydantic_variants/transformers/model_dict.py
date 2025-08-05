from typing import Callable, Dict, Any

from pydantic_variants.core import DecomposedModel, ModelTransformer, VariantContext


class ModelDict(ModelTransformer):
    """
    Modifies the model configuration dict using a custom function.

    Takes a callable that receives the current model_config dict and returns
    a new dict to replace it. This allows flexible modification of Pydantic
    model configuration settings.

    Args:
        config_func: Function that takes current config dict and returns new config dict

    Raises:
        ValueError: If not operating on a DecomposedModel

    Example:
        ModelDict(lambda config: config.update({'strict': True}))

        # Clear all existing config and set new
        ModelDict(lambda config: {'frozen': True, 'validate_assignment': True})
    """

    def __init__(self, config_func: Callable[[Dict[str, Any]], Dict[str, Any]]):
        self.config_func = config_func

    def __call__(self, context: VariantContext) -> VariantContext:
        if not isinstance(context.current_variant, DecomposedModel):
            raise ValueError("ModelDict transformer requires DecomposedModel, got built model")

        # Apply the function to get new config
        new_config = self.config_func(context.current_variant.model_config)

        # Replace the config
        context.current_variant.model_config = new_config

        return context
