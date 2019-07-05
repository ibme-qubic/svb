"""
Base classes and built in models for SVB inference
"""
from .asl import *
from .exp import *

def get_model_class(model_name):
    """
    Get a model class by name

    FIXME proper registration and lookup needed
    """
    if model_name == "aslrest":
        return AslRestModel
    elif model_name == "biexp":
        return BiExpModel
    else:
        raise ValueError("No such model: %s" % model_name)
        