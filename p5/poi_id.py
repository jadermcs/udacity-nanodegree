#!/usr/bin/python
import warnings
warnings.filterwarnings('ignore')
import sys
import pickle
sys.path.append("../tools/")

from feature_format import featureFormat, targetFeatureSplit
from tester import dump_classifier_and_data

### Task 1: Select what features you'll use.
### features_list is a list of strings, each of which is a feature name.
### The first feature must be "poi".
features_list = [
    'poi',
    'bonus',
    'other',
    'salary',
    'expenses',
    'to_messages',
    'from_poi_to_this_person',
    'from_messages',
    'from_this_person_to_poi',
    'shared_receipt_with_poi',
    'deferral_payments',
    'total_payments',
    'loan_advances',
    'restricted_stock_deferred',
    'deferred_income',
    'total_stock_value',
    'exercised_stock_options',
    'long_term_incentive',
    'restricted_stock',
    'director_fees',
    # New features
    'rcv_ratio',
    'sent_ratio',
    'holding_rate'
    ]

print(len(features_list))
### Load the dictionary containing the dataset
with open("final_project_dataset.pkl", "rb") as data_file:
    data_dict = pickle.load(data_file)
### Task 2: Remove outliers
data_dict.pop('TOTAL', 0)
data_dict.pop('THE TRAVEL AGENCY IN THE PARK', 0)
data_dict.pop('LOCKHART EUGENE E', 0)
import pandas as pd
import numpy as np
data = pd.DataFrame(data_dict).T
df = data.drop(columns=["email_address"]).astype(float)

df.loc[df.bonus > df.bonus.quantile(.99), 'bonus'] = np.nan
df.bonus.fillna(value=0, inplace=True)

df.loc[df.salary > df.salary.quantile(.99), 'salary'] = np.nan
df.salary.fillna(value=df.salary.mean(), inplace=True)

df.loc[:, 'poi'] = df['poi'].astype(np.int)
df.loc[:, 'bonus'] = df['bonus'].apply(np.sqrt)
df.loc[:, 'other'] = df['other'].apply(np.log1p)
df.loc[:, 'salary'] = df['salary'].apply(np.log1p)
df.loc[:, 'expenses'] = df['expenses'].apply(np.sqrt)
### Task 3: Create new feature(s)
df['rcv_ratio'] = df['from_poi_to_this_person'] / df['from_messages']
df['sent_ratio'] = df['from_this_person_to_poi'] / df['to_messages']
df['holding_rate'] = df['total_stock_value'] / df['salary']

df = df.fillna(0)
### Store to my_dataset for easy export below.
my_dataset = df.T.to_dict()

### Extract features and labels from dataset for local testing
data = featureFormat(my_dataset, features_list, sort_keys = True)
labels, features = targetFeatureSplit(data)

### Task 4: Try a varity of classifiers
### Please name your classifier clf for easy export below.
### Note that if you want to do PCA or other multi-stage operations,
### you'll need to use Pipelines. For more info:
### http://scikit-learn.org/stable/modules/pipeline.html
from sklearn.cross_validation import train_test_split
features_train, features_test, labels_train, labels_test = \
    train_test_split(features, labels, test_size=0.3, random_state=42)
# Provided to give you a starting point. Try a variety of classifiers.
from sklearn.metrics import classification_report
from sklearn.naive_bayes import GaussianNB
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.svm import LinearSVC
from sklearn.gaussian_process import GaussianProcessClassifier
from sklearn.gaussian_process.kernels import DotProduct
from sklearn.neighbors import KNeighborsClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.decomposition import PCA
from sklearn.pipeline import Pipeline

print("gbc")
clf = GradientBoostingClassifier()
clf.fit(features_train, labels_train)
print(classification_report(labels_test, clf.predict(features_test)))

# print("knn")
# clf = KNeighborsClassifier()
# clf.fit(features_train, labels_train)
# print(classification_report(labels_test, clf.predict(features_test)))

# print("rf")
# clf = RandomForestClassifier()
# clf.fit(features_train, labels_train)
# print(classification_report(labels_test, clf.predict(features_test)))

# print("svc")
# clf = LinearSVC()
# clf.fit(features_train, labels_train)
# print(classification_report(labels_test, clf.predict(features_test)))

# print("gprocess")
# clf = GaussianProcessClassifier(DotProduct())
# clf.fit(features_train, labels_train)
# print(classification_report(labels_test, clf.predict(features_test)))

print("gnb")
clf = GaussianNB()
clf.fit(features_train, labels_train)
print(classification_report(labels_test, clf.predict(features_test)))

print("logistic")
clf = LogisticRegression()
clf.fit(features_train, labels_train)
print(classification_report(labels_test, clf.predict(features_test)))
### Task 5: Tune your classifier to achieve better than .3 precision and recall
### using our testing script. Check the tester.py script in the final project
### folder for details on the evaluation method, especially the test_classifier
### function. Because of the small size of the dataset, the script uses
### stratified shuffle split cross validation. For more info:
### http://scikit-learn.org/stable/modules/generated/sklearn.cross_validation.StratifiedShuffleSplit.html
from sklearn.model_selection import GridSearchCV, StratifiedShuffleSplit
from sklearn.preprocessing import MinMaxScaler, Normalizer
from sklearn.feature_selection import SelectKBest, RFECV
from sklearn.ensemble import VotingClassifier

gbc = GradientBoostingClassifier(random_state=42)
sc = Normalizer()
pipe1 = Pipeline(steps=[
    # ("Scaler", sc),
    ("GBC", gbc)])

params = {
        "GBC__n_estimators": np.arange(50, 100, 5),
        "GBC__max_depth": np.arange(2, 10, 1),
        # "GBC__min_samples_split": np.arange(5,150,15),
        # "GBC__min_samples_leaf": np.arange(5,60,5),
          }

shuff = StratifiedShuffleSplit(n_splits = 5, random_state=42, test_size=.3,
                               train_size=None)

clf1 = GridSearchCV(
        pipe1,
        param_grid = params,
        scoring = 'f1',
        verbose=1,
        n_jobs=4
    )

print("gbc final")
clf1.fit(features_train, labels_train)
# print("atributes", clf1.best_params_)
print(classification_report(labels_test, clf1.predict(features_test)))

sc = MinMaxScaler()
skb = SelectKBest()
lr = LogisticRegression(random_state=42)
pipe2 = Pipeline(steps=[
    ("Scaler", sc),
    ("SKBest", skb),
    ("LR", lr)
    ])

params = {
    "LR__C":[1, 10, 100, 200, 300, 1000],
    "LR__tol":[1e-8, 1e-7, 1e-6, 1e-5, 1e-4],
    "LR__class_weight":['balanced'],
    "SKBest__k": range(1, len(features_list)) + ['all']
    }

shuff = StratifiedShuffleSplit(n_splits = 50, random_state=42)

clf2 = GridSearchCV(
    pipe2,
    param_grid=params,
    # scoring = 'f1',
    cv=shuff,
    verbose=1,
    n_jobs=4
    )

print("lr final")
clf2.fit(features_train, labels_train)
print("atributes", clf2.best_params_)
print(classification_report(labels_test, clf2.predict(features_test)))
exit()
# c1 = pipe1.set_params(**clf1.best_params_)
c2 = pipe2.set_params(**clf2.best_params_)
# clf = VotingClassifier([('gbc', c1),
#                         ('lrg', c2)],
#                        voting='soft',
#                        weights=[4, 5])
clf = c2
clf.fit(features_train, labels_train)
print(classification_report(labels_test, clf.predict(features_test)))
### Task 6: Dump your classifier, dataset, and features_list so anyone can
### check your results. You do not need to change anything below, but make sure
### that the version of poi_id.py that you submit can be run on its own and
### generates the necessary .pkl files for validating your results.

dump_classifier_and_data(clf, my_dataset, features_list)
