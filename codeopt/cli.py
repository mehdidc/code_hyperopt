import numpy as np
import random

from datetime import datetime
import os
import hashlib
import json

from clize import run

from .parser import parse_file

def sample_and_run(filename, *, folder_prefix='.', result_var='result', test_only=False, verbose=0, seed=None):
    """
    codeopt is a simple tool to run optimization of combination of
    parameters that affect a python code and gathe the results.
    """
    if seed is not None:
        seed = int(seed)
    # first pass to know the variables
    content, variables = parse_file(filename, folder='', random_state=seed)
    if verbose > 0:
        print('parameters :'.format(variables))
        for k, v in variables.items():
            print('{}={}, type={}'.format(k, v, type(v)))
    # second pass but with the folder, now that it is known
    key = dict_hash(variables)
    folder = os.path.join(folder_prefix, key)
    content, variables = parse_file(filename, folder=folder, random_state=seed)
    
    # set name to main to simulate that we run the script with python
    global_vars = globals().copy()
    global_vars['__name__'] = '__main__'

    start_time = str(datetime.now())
   
    if test_only is False:
        # create the folder and initialize 'result.json' with the params only (without result)
        mkdir_path(folder) # create the folder because the script might put files on it
        # write result.json which contains params only (before execution)
        with open(os.path.join(folder, 'result.json'), 'w') as fd:
            d = {'params': variables, 'start_time': start_time, 'seed': seed}
            json.dump(d, fd)
    
    # run the script
    exec(content, global_vars, global_vars)
    
    end_time = str(datetime.now())

    # gather the result variable
    all_vars = global_vars
    if result_var in all_vars:
        result = all_vars[result_var]
    else:
        # if the result variable is not found, it is considered
        # as 'undefined'
        result = 'undefined'

    if test_only is False:
        # add a comment on the top of the script with the result
        content ='#result:{}\n'.format(result) + content
        with open(os.path.join(folder, os.path.basename(filename)), 'w') as fd:
            fd.write(content)

        # update result.json with the result
        with open(os.path.join(folder, 'result.json'), 'w') as fd:
            d = {'params': variables, 'result': result, 'start_time': start_time, 'end_time': end_time, 'seed': seed}
            json.dump(d, fd)

def dict_hash(d, algo='md5'):
    # Source : http://stackoverflow.com/questions/5884066/hashing-a-python-dictionary
    m = getattr(hashlib, algo)()
    s = json.dumps(d, sort_keys=True)
    s = s.encode('utf-8')
    m.update(s)
    return m.hexdigest()

def mkdir_path(path):
    """
    Create folder in `path` silently: if it exists, ignore, if not
    create all necessary folders reaching `path`
    """
    if not os.access(path, os.F_OK):
        os.makedirs(path)

def main():
    run(sample_and_run)

if __name__ == '__main__':
    main()
