from clize import run
import os
import hashlib
import json

from .parser import parse_file

def sample_and_run(filename, folder_prefix='.', result_var='result'):
    """
    codeopt is a simple tool to run optimization of combination of
    parameters that affect a python code and gathe the results.
    """
    content, variables = parse_file(filename)
    global_vars = {}
    local_vars = {}
    exec(content, global_vars, local_vars)
    all_vars = global_vars
    all_vars.update(local_vars)
    if result_var in all_vars:
        result = all_vars[result_var]
    else:
        result = 'undefined'
    content ='#result:{}\n'.format(result) + content

    key = dict_hash(variables)
    folder = os.path.join(folder_prefix, key)
    mkdir_path(folder)
    with open(os.path.join(folder, os.path.basename(filename)), 'w') as fd:
        fd.write(content)
    with open(os.path.join(folder, 'result.json'), 'w') as fd:
        d = {'params': variables, 'result': result}
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
