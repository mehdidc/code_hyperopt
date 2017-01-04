from jinja2 import Environment

from .samplers import sampler
from .samplers import uniform
from .samplers import randint


def parse_file(filename, **kwargs):
    with open(filename, 'r') as fd:
        s = fd.read()
    return parse_str(s, **kwargs)

samplers = {
    'uniform': uniform,
    'randint': randint
}

def parse_str(s, samplers=samplers, **kwargs):
    env = Environment()
    for name, func in samplers.items():
        samplers[name] = sampler(func, env=env)
    env.filters.update(samplers)
    env.variables = {}
    t = env.from_string(s)
    return t.render(**kwargs), env.variables
