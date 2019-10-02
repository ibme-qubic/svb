"""
Distributions that can be applied to a model parameter
"""
import math

import tensorflow as tf

from .posterior import NormalPosterior
from .utils import LogBase

def get_dist(prefix, **kwargs):
    """
    Factory method to return a distribution from options
    """
    dist = kwargs.get("%s_dist" % prefix, kwargs.get("dist", "Normal"))
    mean = kwargs.get("%s_mean" % prefix, kwargs.get("mean", 0.0))
    var = kwargs.get("%s_var" % prefix, kwargs.get("var", 1.0))

    dist_class = globals().get(dist, None)
    if dist_class is None:
        raise ValueError("Unrecognized distribution: %s" % dist)
    else:
        return dist_class(mean, var)

class Identity:
    """
    Base class for variable transformations which defines just a
    simple identity transformation
    """

    def int_values(self, ext_values):
        """
        Convert internal (inferred) values to external
        (model-visible) values
        """
        return ext_values

    def int_moments(self, ext_mean, ext_var):
        """
        Convert internal (inferred) mean/variance to external
        (model-visible) mean/variance
        """
        return ext_mean, ext_var

    def ext_values(self, int_values):
        """
        Convert external (model) values to internal
        (inferred) values
        """
        return int_values

    def ext_moments(self, int_mean, int_var):
        """
        Convert the external (model) mean/variance to internal
        (inferred) mean/variance
        """
        return int_mean, int_var

class Log(Identity):
    """
    Log-transform used for log-normal distribution
    """
    def __init__(self, geom=True):
        self._geom = geom

    def int_values(self, ext_values):
        return tf.log(ext_values)

    def int_moments(self, ext_mean, ext_var):
        if self._geom:
            return math.log(ext_mean), math.log(ext_var)
        else:
            # See https://uk.mathworks.com/help/stats/lognstat.html
            return math.log(ext_mean**2/math.sqrt(ext_var + ext_mean**2)), math.log(ext_var/ext_mean**2 + 1)

    def ext_values(self, int_values):
        return tf.exp(int_values)

    def ext_moments(self, int_mean, int_var):
        if self._geom:
            return math.exp(int_mean), math.exp(int_var)
        else:
            raise NotImplementedError()

class Abs(Identity):
    """
    Absolute value transform used for folded normal distribution
    """
    def ext_values(self, int_values):
        return tf.abs(int_values)

    def ext_moments(self, int_mean, int_var):
        raise NotImplementedError()

class Dist(LogBase):
    """
    A parameter distribution
    """
    pass

class Normal(Dist):
    """
    Gaussian-based distribution

    The distribution of a parameter has an *underlying* Gaussian
    distribution but may apply a transformation on top of this
    to form the *model* distribution.

    We force subclasses to implement the required methods rather
    than providing a default implementation
    """
    def __init__(self, ext_mean, ext_var, transform=Identity()):
        """
        Constructor.

        Sets the distribution mean, variance and std.dev.

        Note that these are the mean/variance of the *model*
        distribution, not the underlying Gaussian - the latter are
        returned by the ``int_mean`` and ``int_var`` methods
        """
        Dist.__init__(self)
        self.transform = transform
        self.ext_mean, self.ext_var = ext_mean, ext_var
        self.mean, self.var = self.transform.int_moments(ext_mean, ext_var)
        self.sd = math.sqrt(self.var)

    def __str__(self):
        return "Gaussian (%f, %f)" % (self.mean, self.var)

class LogNormal(Normal):
    """
    Log of the parameter is distributed as a Gaussian.

    This is one means of ensuring that a parameter is always > 0.
    """

    def __init__(self, mean, var, geom=True, **kwargs):
        Normal.__init__(self, mean, var, transform=Log(geom), **kwargs)

    def __str__(self):
        return "Log-Normal (%f, %f)" % (self.ext_mean, self.ext_var)

class FoldedNormal(Normal):
    """
    Distribution where the probability density
    is zero for negative values and the sum of Gaussian
    densities for the value and its negative otherwise

    This is a fancy way of saying we take the absolute
    value of the underlying distribution as the model
    distribution value.
    """

    def __init__(self, mean, var, **kwargs):
        Normal.__init__(self, mean, var, transform=Abs(), **kwargs)

    def __str__(self):
        return "Folded Normal (%f, %f)" % (self.ext_mean, self.ext_var)

