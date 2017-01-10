import numpy as np

def sampler(f, random_state=None, env=None):
    """
    'filter' to use for jinja in order to sample
    values
    """
    rng = np.random.RandomState(random_state)
    def f_(x, *args, **kwargs):
        val = f(rng, *args, **kwargs)
        if env: env.variables[x] = val
        return val
    f_.__name__ = f.__name__
    return f_

# currently available samplers
# use in jinja as is, except you don't have to specify 
# the first argument (rng)
def uniform(rng, low=0, high=1):
    return rng.uniform(low=low, high=high)

def randint(rng, low=0, high=1):
    return rng.randint(low=low, high=high)

def loguniform(rng, low=0, high=1, base=10):
    return base ** rng.uniform(low=low, high=high)

def choice(rng, *vals):
    return np.asscalar(rng.choice(vals))
