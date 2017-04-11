import sys
import numpy as np
import random
import json
import glob
from datetime import datetime
import os
import hashlib
import json
import random
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import LinearRegression

from clize import run

from .parser import parse_file


def sample_and_run(filename, *, 
                   folder_prefix='.', 
                   bayesopt=False, 
                   optim='minimize',
                   trials=1000,
                   kappa=1.96,
                   test_only=False, 
                   seed=None,  
                   result_variable_name='result', 
                   argv='', verbose=0):
    """
    codeopt is a simple tool to run optimization of combination of
    parameters that affect a python code and gathe the results.

    --folder-prefix=STR
    
    prefix of the folder where to put the results, that is, the results
    will be put in folder_prefix/key where key is the hash of the parameters.

    --bayesopt=BOOL (default is False)

    if True, use UCB based random forest bayesian optimization to select the next parameters, otherwise
    use randonm sampling. if minimize is True, it will try the minimize "result", otherwise it will
    try to maximize it.

    --optim='minimize'/'maximize' (default is 'minimize')

    Only used if bayesopt is True. 
    Specifiy whether it is a minimization problem : 'minimize'
    or a maximization problem : 'maximize'.

    --trials=INT (default is 1000)

    for "bayesopt" only:  nb. of candidates to sample in order to find the next candidate.

    --kappa=float (default is 1.96)

    for "bayesopt" only : tradeoff between exploration and exploitation, higher kapp
    means more exploration.

    --test-only=BOOL (default is False)
    
    if True, don't create any folder, only execute the script
    
    --seed=INT (default is None)
    
    seed to use for generating the parameters. by default it the seed
    will depend on the current time. The same seed leads to the exact
    same parameters. However, it will not affect the behavior of the script
    (it will not change any global variable controling the seed).

    --result-variable-name=STR
    
    name of the variable that will appear in the json result.json filename
    for storing the result variable

    --argv=STR

    arguments separated by spaces to use when executing the code (it mocks sys.argv)

    --verbose=INT
    
    if verbose is 1, print some debug messages.

    """
    if optim not in ('minimize', 'maximize'):
        print('optim should either be "minimize" or "maximize"')
        return

    if bayesopt:
        X, y, cols = _collect_results(folder_prefix)
        if len(X) == 0:
            print('Needs at least one observation to do bayesopt, please launch codeopt without "bayeseopt" at least once.')
            return
        reg = RandomForestRegressor(
            n_estimators=100, 
            min_samples_leaf=5,
            oob_score=True)
        reg.fit(X, y)
        if verbose > 0:
            train_score = reg.score(X, y)
            oob_score = reg.oob_score_
            print('Train R2-score : {:.3f}, Out-of-bag R2-score : {:.3f}'.format(train_score, oob_score))
        # sample several combinations
        params = []
        seeds = []
        for v in range(1000):
            seed = random.randint(0, 4294967295)
            _, variables = parse_file(filename, folder='', random_state=seed)
            params.append([variables[c] for c in cols])
            seeds.append(seed)
        params = np.array(params)
        trees = reg.estimators_
        y = np.concatenate([tree.predict(X)[np.newaxis, :] for tree in trees], axis=0)
        pred_mean = y.mean(axis=0)
        pred_std = y.std(axis=0)
        kappa = 1.96 # tradoff between exploration and exploitation (higher = more exploitation)
        if optim == 'minimize':
            score = pred_mean - kappa * pred_std
            seed = seeds[np.argmin(score)]
        else:
            score = pred_mean + kappa * pred_std
            seed = seeds[np.argmax(score)]
        content, variables = parse_file(filename, folder='', random_state=seed)
    else:
        if seed is not None:
            seed = int(seed)
        else:
            # the below constant is the maximum seed that can be handled by numpy.
            # I use numpy pseudo-random sampling because I don't want to modify
            # the global state of the pseudo-random number generator, I only
            # create an object np.random.RandomState.
            seed = random.randint(0, 4294967295)
        # first pass to know the variables
        content, variables = parse_file(filename, folder='', random_state=seed)
    
    if verbose > 0:
        print('parameters :'.format(variables))
        for k, v in variables.items():
            print('{}={}, type={}'.format(k, v, type(v)))
    # second pass but with the folder, now that it is known
    key = dict_hash(variables)
    folder = os.path.join(folder_prefix, key)
    content, variables = parse_file(filename, random_state=seed, folder=folder)
    
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
            if verbose > 0:
                print(d)
            json.dump(d, fd)
        # write the script where variables are replaced by their values
        with open(os.path.join(folder, os.path.basename(filename)), 'w') as fd:
            fd.write(content)
    
    # mock argv
    old = sys.argv[:]
    sys.argv = [os.path.basename(filename)] + (argv.split(' ') if argv else [])
    # run the script
    exec(content, global_vars, global_vars)
    
    # unmock argv
    if argv:
        sys.argv = old

    end_time = str(datetime.now())

    # gather the result variable
    all_vars = global_vars
    if result_variable_name in all_vars:
        result = all_vars[result_variable_name]
        if verbose > 0 and bayesopt:
            print('New score : {}'.format(result))
            prev_best = np.min(y) if optim == 'minimize' else np.max(y)
            improvement = result < prev_best if optim == 'minimize' else result > prev_best
            if improvement:
                print('Improvement over previous best score : from {:.3f} to {:.3f}'.format(prev_best, result))
            else:
                print('No improvement over best previous score.')
    else:
        # if the result variable is not found, it is considered
        # as None (and appears in json as 'null')
        result = None

    if test_only is False:
        # add a comment on the top of the script with the result
        content ='#result:{}\n'.format(result) + content
        with open(os.path.join(folder, os.path.basename(filename)), 'w') as fd:
            fd.write(content)

        # update result.json with the result
        with open(os.path.join(folder, 'result.json'), 'w') as fd:
            d = {'params': variables, 'result': result, 'start_time': start_time, 'end_time': end_time, 'seed': seed}
            json.dump(d, fd)

def _collect_results(folder):
    hypers = []
    results = []
    for resfile in glob.glob(os.path.join(folder, '**', 'result.json')):
        with open(resfile, 'r') as fd:
            data = json.load(fd)
        if 'params' not in data:
            continue
        if 'result' not in data:
            continue
        hypers.append(data['params'])
        results.append(data['result'])
    if len(hypers) == 0:
        return [], [], []
    cols = list(hypers[0].keys())
    X = [[h[c] for c in cols] for h in hypers]
    X = np.array(X)
    y = np.array(results)
    return X, y, cols

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
