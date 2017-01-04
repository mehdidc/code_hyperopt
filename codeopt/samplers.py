import numpy as np

def sampler(f, random_state=None, env=None):
    rng = np.random.RandomState(random_state)
    def f_(x, *args, **kwargs):
        val = f(rng, *args, **kwargs)
        if env: env.variables[x] = val
        return val
    f_.__name__ = f.__name__
    return f_

def uniform(rng, low=0, high=1):
    return rng.uniform(low=low, high=high)

def randint(rng, low=0, high=1):
    return rng.randint(low=low, high=high)
