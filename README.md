codeopt
=======

codeopt is a simple tool to run optimization of combination of
parameters that affect a python code and gather the results.

One application example is hyper-parameter optimization of machine
learning models.

The advantadge of codeopt lies in its simplicity.
The original code to be optimized have to be modified a little to adapt to
codeopt, so its readability (the original code) is not affected a lot.
Also, codeopt allows easyness of prototyping because the original is not
modified a lot.

How to install
==============

  :::bash
  pip install git+https://github.com/mehdidc/codeopt

How does it work
================

codeopt takes a python file, and use jinja <jinja.pocoo.org>, a well known template library
to detect parts of the code that need to be optimized.

Here is an example of a typical python code that optimizes a machine learning model:

  :::python
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

this code have two parameters to be optimize, "max_depth" and "n_estimators" and we specify that
both their prior is an integer between 1 and 100.
We can then launch codeopt on this file by using :

  :::bash
  codeopt filename.py

this will create a directory with a name based on the md5 hash of the parameters, the directory will contain
the python file with the variables max_depth and n_estimators replaced by the sampled values.
A comment will be added in the beginning to specifiy the result found.
A second file will be added in the direct, "result.json", which is a json file containing the parameters
used and the result found.
By default, codeopt tries to lookup the results in the "result" file, so be aware to assign the result
of the program in a variable called "result". The name of the variable can be changed, please check
the options of codeopt for more information.
