"""this containes useful functions to attach to model"""


def convert_to_variant(variant_name: str):
    """creates an OUTPUT object from base object"""

    def decorator(self):
        self._variants[variant_name](**self.model_dump())

    return decorator


def rebuild_models(cls):
    """Rebuild the root model and all its variations"""
    cls.model_rebuild()

    for variation in cls._variations:
        if variation.name in cls.model_variations:
            try:
                cls.model_variations[variation.name].model_rebuild()
            except AssertionError:
                # Sometimes it fails first time, try again
                cls.model_variations[variation.name].model_rebuild()
