# -*- coding:utf-8 -*-

# @Author:      zp
# @Time:        2023/4/7 15:19

import json
import re
import numpy as np

from sklearn.linear_model import SGDClassifier
from sklearn.metrics import accuracy_score
from sklearn.metrics import f1_score, precision_score, recall_score

from sklearn.model_selection import cross_validate, GridSearchCV, KFold, train_test_split  
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier
from sklearn.svm import SVC
from sklearn.neighbors import KNeighborsClassifier
from sklearn.neural_network import MLPClassifier
import joblib
    
class Classifier():
    def __init__(self) -> None:
        self.classifier = None
        self.scaler = None

    def fit(self, data, targets):
        data, targets = np.array(data), np.array(targets)
        data = data[:, :-1] # remove the overall score, because it seems to be useless
        scaler = StandardScaler()

        data = scaler.fit_transform(data)
        
        classifier = SVC(C=1.0, kernel='rbf', class_weight={1:1.0, -1:1.5})
        classifier.fit(data, targets)
        self.scaler = scaler

        self.classifier = classifier
        preds = self.classifier.predict(data)
        print('train precision: {}'.format(precision_score(targets, preds)))
    
    def test(self, x_test, y_test=None):
        assert self.classifier is not None
        assert self.scaler is not None
        x_test = np.array(x_test)
        x_test = x_test[:, :-1]

        x_test = self.scaler.transform(x_test)
        y_preds = self.classifier.predict(x_test)

        if y_test is not None:
            y_test = np.array(y_test)
            f1 = f1_score(y_test, y_preds)
            precision = precision_score(y_test, y_preds)
            acc = accuracy_score(y_test, y_preds)
            recall = recall_score(y_test, y_preds)
            return {
                'preds':y_preds,
                'labels':y_test,
                'acc': acc,
                'f1':f1,
                'precision':precision,
                'recall': recall
            }
        else:
            return {
                'preds':y_preds
            }
    
    def save_model(self, model_path):
        state_dict = {
            'model': self.classifier,
            'scaler': self.scaler
        }
        joblib.dump(state_dict, model_path)
        print(f'save classifier and scaler to {model_path}')

    def load_model(self, model_path):
        state_dict = joblib.load(model_path)
        self.classifier = state_dict['model']
        self.scaler = state_dict['scaler']
        print(f'load classifier and scaler from {model_path}')
    
    def cross_validate(self, data, targets):
        data, targets = np.array(data), np.array(targets)
        cv_strategy = KFold(n_splits=5, shuffle=True, random_state=42)

        self.scaler = StandardScaler()
        data = self.scaler.fit_transform(data)

        # Grid search
        param_grid = {'C': [0.1,1, 10, 100], 'penalty': ['l2']}
        class_weight = {1:1.0, -1:1.5}

        linear_classifier = GridSearchCV(LogisticRegression(class_weight = class_weight), param_grid, refit=True, verbose=2)
        hinge_classifier = SGDClassifier(loss='hinge', random_state=42, class_weight = class_weight)
        tree_classifier = RandomForestClassifier(n_estimators=100, random_state=42, max_depth=10, min_samples_split=2, min_samples_leaf=1, class_weight = class_weight)
        svm_classifier =  SVC(C=1.0, kernel='rbf', class_weight = class_weight)
        knn_classifier = KNeighborsClassifier(n_neighbors=5)
        mlp_classifier = MLPClassifier(hidden_layer_sizes=(10, 5), activation='relu', alpha=0.001)

        classifiers = [linear_classifier, hinge_classifier, tree_classifier, svm_classifier, knn_classifier, mlp_classifier]
        self.classifier = hinge_classifier
        for cls in classifiers:
            print(f'================ cross-valdiate results of {type(cls)} =======================')
            scores = cross_validate(cls, data, targets, cv=cv_strategy, scoring=('accuracy', 'precision', 'recall', 'f1'))
            print('test_accuracy:', round(sum(scores['test_accuracy'])/len(scores['test_accuracy']), 2))
            print('test_precision:', round(sum(scores['test_precision'])/len(scores['test_precision']), 2))
            print('test_recall:', round(sum(scores['test_recall'])/len(scores['test_recall']), 2))
            print('test_f1:', round(sum(scores['test_f1'])/len(scores['test_f1']), 2))

    def tune_thresold(self, data, targets):
        data, targets = np.array(data), np.array(targets)
        targets = targets > 0
        X_train, X_test, y_train, y_test = train_test_split(data, targets, test_size=0.2, random_state=42)
        classifier = SVC(C=1.0, kernel='rbf')  # Set probability=True to enable decision function probabilities
        classifier.fit(X_train, y_train)
        thresholds = [0.6, 0.7, 0.8, 0.9]
        for t in thresholds:
            y_pred_proba = classifier.predict_proba(X_test)[:, 1]
            print(y_pred_proba)
            y_pred = (y_pred_proba > t).astype(int)
            precision = precision_score(y_test, y_pred)
            print(f'precision:{precision}')

def report_naive(preds, labels):
    y_hat = []
    y = []
    for l,r in zip(labels, preds):
        if isinstance(r, list):
            y_hat.append(all([_r==1.0 for _r in r]))
            print(y_hat)
            y.append(l>0)
    print(f'acc: {round(accuracy_score(y, y_hat), 2)}')
    print(f'precision: {round(precision_score(y, y_hat), 2)}')
    print(f'recall: {round(recall_score(y, y_hat), 2)}')
    print(f'f1: {round(f1_score(y, y_hat), 2)}')

def report_error_examples(ids, texts, preds, labels, file_name=None):
    if file_name is not None:
        file_to_print = open(file_name, 'a+')
    else:
        file_to_print = None
    
    for i in range(len(texts)):                
        if preds[i][-1] * labels[i] < 0:
            print(f'id:{ids[i]}, texts:{texts[i]}, predict:{preds[i]}, label:{labels[i]}', file=file_to_print)
            print('--------------------------------------------------------')