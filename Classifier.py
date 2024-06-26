import numpy as np
from sklearn.neighbors import KNeighborsClassifier
from sklearn.svm import SVC
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier, AdaBoostClassifier, BaggingClassifier
from sklearn.naive_bayes import MultinomialNB, GaussianNB
from sklearn.linear_model import LogisticRegression
from sklearn.neural_network import MLPClassifier
from sklearn.model_selection import GridSearchCV
from sklearn.dummy import DummyClassifier
import warnings

warnings.filterwarnings("ignore", category=DeprecationWarning)
warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", category=Warning)


class Classifier:

    def __init__(self, typename, params=None):
        if params is None:
            params = {}
        __classifiers__ = {
            'Dummy': DummyClassifier,
            'KNN': KNeighborsClassifier,
            'M-NaiveBayes': MultinomialNB,
            'G-NaiveBayes': GaussianNB,
            'SVC': SVC,
            'DecisionTree': DecisionTreeClassifier,
            'RandomForest': RandomForestClassifier,
            'LogisticRegression': LogisticRegression,
            'MLP': MLPClassifier,
            'AdaBoost': AdaBoostClassifier,
            'Bagging': BaggingClassifier
        }
        if typename not in __classifiers__.keys():
            raise Exception('Available Classifiers: ', __classifiers__.keys())
        self.classifier = __classifiers__[typename]
        self.params = params
        self.model = self.classifier(**self.params)

    def fit(self, tr_data, tr_labels):
        return self.model.fit(tr_data, tr_labels)

    def predict(self, tst_data):
        return self.model.predict(tst_data)

    def score(self, tst_data, tst_labels):
        return self.model.score(tst_data, tst_labels)

    def tune(self, tr_data, tr_labels, tune_params=None, best_only=False, scoring='f1'):
        if not tune_params:
            tune_params = self.params
        tuner = GridSearchCV(self.model, tune_params, n_jobs=4, verbose=1, scoring=scoring)
        tuner.fit(tr_data, tr_labels)
        self.model = tuner.best_estimator_
        if best_only:
            return {'score': tuner.best_score_, 'parmas': tuner.best_params_}
        else:
            param_scores = {}
            results = tuner.cv_results_
            for i, param in enumerate(tuner.cv_results_['params']):
                param_str = ', '.join("{!s}={!r}".format(key, val) for (key, val) in param.items())
                param_scores[param_str] = {'test_score': results['mean_test_score'][i],
                                           'train_score': results['mean_train_score'][i]}
            return param_scores

    def get_model(self):
        if getattr(self, 'model', None):
            return self.model
        else:
            raise Exception('Model has not been created yet.')

    def test_and_plot(self, tst_data, tst_labels, class_num=2):
        tst_data = np.array(tst_data)
        tst_labels = np.array(tst_labels).reshape(-1, 1)
        predicted_tst_labels = self.model.predict(tst_data)
        conf = np.zeros([class_num, class_num])
        confnorm = np.zeros([class_num, class_num])
        for i in range(0, tst_data.shape[0]):
            j = tst_labels[i, :]
            k = predicted_tst_labels[i]
            conf[j, k] = conf[j, k] + 1
        for i in range(0, class_num):
            confnorm[i, :] = conf[i, :] / np.sum(conf[i, :])
        return self.model.score(tst_data, tst_labels)
