from sklearn.ensemble import RandomForestClassifier
from sklearn.datasets import load_iris
from sklearn.model_selection import cross_val_score
iris = load_iris()
clf = RandomForestClassifier(
    max_depth={{ "max_depth" | randint(1, 100)}},
    n_estimators={{ "n_estimators" | randint(1, 100)  }}
)
scores = cross_val_score(clf, iris.data, iris.target, cv=5)
result = scores.mean()
