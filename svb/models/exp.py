"""
Multi-exponential models
"""
import tensorflow as tf

from svb import __version__
from svb.model import Model
from svb.parameter import Parameter
import svb.dist as dist

class MultiExpModel(Model):
    """
    Exponential decay with multiple independent decay rates and amplitudes
    """

    def __init__(self, **options):
        Model.__init__(self, **options)
        self._num_exps = options.get("num_exps", 1)
        for idx in range(self._num_exps):
            self.params += [
                Parameter("amp%i" % (idx+1),
                          prior=dist.LogNormal(1.0, 1e6),
                          post=dist.LogNormal(1.0, 1.5),
                          initialise=self._init_amp,
                          **options),
                Parameter("r%i" % (idx+1),
                          prior=dist.LogNormal(1.0, 1e6),
                          post=dist.LogNormal(1.0, 1.5),
                          **options),
            ]

    def _init_amp(self, _param, _t, data):
        return tf.reduce_max(data, axis=1) / self._num_exps, None

    def evaluate(self, params, tpts):
        ret = None
        for idx in range(self._num_exps):
            amp = params[2*idx]
            r = params[2*idx+1]
            contrib = amp * tf.exp(-r * tpts)
            if ret is None:
                ret = contrib
            else:
                ret += contrib
        return ret

    def __str__(self):
        return "Multi exponential model with %i exponentials: %s" % (self._num_exps, __version__)

class ExpModel(MultiExpModel):
    """
    Simple exponential decay model
    """
    def __init__(self, **options):
        MultiExpModel.__init__(self, num_exps=1, **options)

    def __str__(self):
        return "Exponential model: %s" % __version__

class BiExpModel(MultiExpModel):
    """
    Exponential decay with two independent decay rates and amplitudes
    """
    def __init__(self, **options):
        MultiExpModel.__init__(self, num_exps=2, **options)

    def __str__(self):
        return "Bi-Exponential model: %s" % __version__
