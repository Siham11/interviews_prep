import os, sys
from sklearn.base import BaseEstimator
from sklearn.datasets import load_iris
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
import numpy as np


def test():
    print ("-- Classification Tree --")

    data = load_iris()
    X = data.data
    y = data.target

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.4)

    clf = DecisionTree()
    clf.fit(X_train, y_train)
    y_pred = clf.predict(X_test)

    #accuracy = accuracy_score(y_test, y_pred)


    #print ("Accuracy:", accuracy)

def exp_dim(arr):
    return np.expand_dims(arr, axis=-1)

def divide_on_features(Xy, features_i, thresold):
    left = []
    left_y = []
    right = []
    right_y = []
    for v, y in zip(Xy[:, features_i], Xy[:, -1]):
        if v <=thresold:
            left.append(v)
            left_y.append(y)
        else:
            right.append(v)
            right_y.append(y)
    return (exp_dim(left), exp_dim(left_y)), (exp_dim(right), exp_dim(right_y))

class DecisionNode:
    """Class that represents a decision node or leaf in the decision tree
    Parameters:
    -----------
    feature_i: int
        Feature index which we want to use as the threshold measure.
    threshold: float
        The value that we will compare feature values at feature_i against to
        determine the prediction.
    value: float
        The class prediction if classification tree, or float value if regression tree.
    true_branch: DecisionNode
        Next decision node for samples where features value met the threshold.
    false_branch: DecisionNode
        Next decision node for samples where features value did not meet the threshold.
    """

    def __init__(self, feature_i=None,
                       threshold=None,
                       value=None,
                       true_branch=None,
                       false_branch=None):

        self.feature_i = feature_i
        self.threshold = threshold
        self.value = value
        self.true_branch = true_branch
        self.false_branch = false_branch


class DecisionTree(BaseEstimator):
    """Super class of RegressionTree and ClassificationTree.
    Parameters:
    -----------
    min_samples_split: int
        The minimum number of samples needed to make a split when building a tree.
    min_impurity: float
        The minimum impurity required to split the tree further.
    max_depth: int
        The maximum depth of a tree.
    loss: function
        Loss function that is used for Gradient Boosting models to calculate impurity.
    """
    def __init__(self, min_samples_split=2,
                       min_impurity=10e-7,
                       max_depth=float('inf'),
                       loss=None):
        # PARAMETERS
        self.min_samples_split = min_samples_split
        self.min_impurity = min_impurity
        self.max_depth = max_depth
        self.loss = loss

        # ATTRIBUTES
        self.root = None # Root
        self._impurity_calculation = None # classif : gain, regr : variance reduction
        self._leaf_value_calculation = None # One hot
        self.one_dim = None # if Gradient Boost

    def fit(self, x, y=None):
        self.one_dim = len(np.shape(y)) == 1
        self.root = self._build_tree(x, y)
        self.loss = None

    def predict(self, data):
        pass

    def _build_tree(self, x, y, current_depth=0):
        """ Recursive method which builds out the decision tree and splits X and respective y
        on the feature of X which (based on impurity) best separates the data"""

        largest_impurity = 0
        best_criteria = None
        best_sets = None

        # Augment y
        if len(np.shape(y)) == 1:
            y = np.expand_dims(y, axis=1)

        # Concatenate X and Y
        Xy = np.concatenate([x, y], axis=1)

        n_samples, n_features = np.shape(Xy)

        if len(x) >= self.min_samples_split and current_depth <= self.max_depth:

            for features_index in range(n_features):

                features_values = np.expand_dims(Xy[:, features_index], axis=1)
                unique_values = np.unique(features_values)

                # Try all possible values as a split
                for threshold in unique_values:
                    Xy1, Xy2 = divide_on_features(Xy, features_index, threshold)


                    self._impurity_calculation(Xy1, Xy2)