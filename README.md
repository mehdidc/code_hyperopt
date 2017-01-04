codeopt
=======

codeopt is a simple tool to run optimization of combination of
parameters that affect a python code and gather the results.

One application example is hyper-parameter optimization of machine
learning models.

The advantage of codeopt lies in its simplicity.
The original code to be optimized have to be modified a little to adapt to
codeopt, so its readability (the original code) is not affected a lot.
Also, codeopt allows easyness of prototyping because the original is not
modified a lot.

How to install
==============

```bash
pip install git+https://github.com/mehdidc/codeopt
```

How does it work
================

codeopt takes a python file and uses jinja ([http://jinja.pocoo.org](http://jinja.pocoo.org)), a well known python template library, to detect automatically parameters from the code that need to be optimized. Each time codeopt is launched on a python file, those parameters are replaced by some sampled values, then the python file is run and finally the results are gathered.

Here is an example of a typical python code that optimizes a machine learning model which is usable by codeopt:

```python
import numpy as np
from functools import partial
from sklearn.ensemble import RandomForestClassifier
from sklearn.datasets import load_iris
from sklearn.model_selection import cross_val_score
iris = load_iris()
clf = RandomForestClassifier(
    max_depth={{ "max_depth" | randint(1, 100)}},
    n_estimators={{ "n_estimators" | randint(1, 100)}}
)
scores = cross_val_score(clf, iris.data, iris.target, cv=5)
result = scores.mean()
```

this code have two parameters to be optimize, "max_depth" and "n_estimators" and we specify that
both their prior is an integer between 1 and 100.
We can then launch codeopt on this file by using :

```bash
codeopt filename.py
```

if the file is named "filename.py".

When the script finishes running, a directory with a name based on the md5 hash of the parameters will created, the directory will contain the python file with the variables "max_depth" and "n_estimators" replaced by the chosen values.
A comment will be added in the beginning to indicate the result found.
A second file will be added in the direct, "result.json", which is a json file containing the parameters
used and the result found.
By default, codeopt tries to lookup the results in the "result" variable, so be aware to assign the result
of the program in a variable called "result". The name of that variable can be changed, please check
the options of codeopt for more information :


```bash
codeopt --help
```
