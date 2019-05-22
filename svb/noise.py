"""
Noise model
"""
import tensorflow as tf

from svb.parameter import Parameter
import svb.dist as dist

class NoiseParameter(Parameter):
    """
    Noise parameter providing Gaussian (white) noise
    """

    def __init__(self, **kwargs):
        Parameter.__init__(self, "noise",
                           prior=dist.Normal(0.0, 1.0e4),
                           post=dist.Normal(2.6, 0.02),
                           **kwargs)

    def log_likelihood(self, data, pred, noise, nt):
        """
        Calculate the log-likelihood of the data

        Note that we are using the log of the noise Gaussian variance as the noise parameter
        here.

        data has shape [NV, B] - needs to be tiled for each sample
        pred has shape [NV, D, B]
        noise has shape [NV, D]
        """
        nvoxels = tf.shape(data)[0]
        batch_size = tf.shape(data)[1]
        draw_size = tf.shape(pred)[1]

        log_noise = noise # for clarity
        #log_noise = tf.fill([nvoxels, draw_size], 0.0)
        data = self.log_tf(tf.tile(tf.reshape(data, [nvoxels, 1, batch_size]), [1, draw_size, 1], name="data"))
        pred = self.log_tf(pred)

        # Square_diff has shape [NV, D, B]
        square_diff = self.log_tf(tf.square(data - pred, name="square_diff"))

        # Since we are processing only a batch of the data at a time, we need to scale this term
        # correctly to the latent loss
        scale = self.log_tf(tf.divide(tf.to_float(nt), tf.to_float(batch_size), name="scale"))

        # Log likelihood has shape [NV, D]
        noise_var = self.log_tf(tf.exp(log_noise, name="noise_var"))
        log_likelihood = 0.5 * (log_noise * tf.to_float(nt) +
                                scale * tf.reduce_sum(square_diff, axis=-1) / noise_var)
        log_likelihood = self.log_tf(tf.identity(log_likelihood, name="log_likelihood"))

        # Mean over samples - reconstr_loss has shape [NV]
        return self.log_tf(tf.reduce_mean(log_likelihood, axis=1, name="mean_log_likelihood"))