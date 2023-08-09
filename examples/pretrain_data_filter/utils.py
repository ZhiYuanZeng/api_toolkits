# -*- coding:utf-8 -*-

# @Author:      zp
# @Time:        2023/4/7 15:19

import json
import re
import numpy as np
import os
from sklearn.linear_model import SGDClassifier
from sklearn.metrics import accuracy_score
from sklearn.metrics import f1_score, precision_score, recall_score
from sklearn.metrics import classification_report
from sklearn.model_selection import cross_validate, GridSearchCV, KFold, train_test_split  
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier
from sklearn.svm import SVC
from sklearn.neighbors import KNeighborsClassifier
from sklearn.neural_network import MLPClassifier
import joblib
from sklearn.preprocessing import label_binarize
from sklearn.metrics import precision_recall_curve, auc
from terminaltables import AsciiTable
class Classifier():
    def __init__(self) -> None:
        self.classifier = None
        self.scaler = None

    def fit(self, data, targets):
        data, targets = np.array(data), np.array(targets)
        data = data[:, :-1] # remove the overall score, because it seems to be useless
        scaler = StandardScaler()

        data = scaler.fit_transform(data)
        
        #classifier = SVC(C=1.0, kernel='rbf', class_weight={1:1.0, -1:1.5}, probability=True)
        classifier = SVC(C=1.0, kernel='rbf', class_weight={1:1.0, 0:1.5}, probability=True)
        classifier.fit(data, targets)
        self.scaler = scaler

        self.classifier = classifier
        
        #preds = self.classifier.predict(data)
        predict_proba = self.classifier.predict_proba(data)

        # 同时支持二分类及多分类的one hot
        # see issue https://github.com/scikit-learn/scikit-learn/issues/6191
        class_num = predict_proba.shape[1]
        gt_label_one_hot = label_binarize(targets, classes=np.arange(class_num + 1))[:, :-1]  # 装换成类似二进制的编码
        for class_id in range(class_num):
            cur_eval_result = []
            precisions_per_cls, recalls_per_cls, thresholds_per_cls = precision_recall_curve(
                gt_label_one_hot[:, class_id], predict_proba[:, class_id])
            precisions_per_cls = np.array(precisions_per_cls)
            recalls_per_cls = np.array(recalls_per_cls)
            thresholds_per_cls = np.array(thresholds_per_cls)

            for prec, recall, thresh in zip(precisions_per_cls, recalls_per_cls, thresholds_per_cls):
                cur_eval_result.append([prec, recall, thresh])
            print(f"precison recall curve for class id:{class_id}")

            table_data = [['precisions', 'recalls', "thresholds"]]
            table_data.extend(cur_eval_result)
            table = AsciiTable(table_data)
            print(table.table)

    def test(self, x_test, y_test=None, threshold=0.5):
        assert self.classifier is not None
        assert self.scaler is not None
        x_test = np.array(x_test)
        x_test = x_test[:, :-1]

        x_test = self.scaler.transform(x_test)
        #y_preds = self.classifier.predict(x_test)
        #y_preds = np.ones(x_test.shape[0])
        y_preds = np.zeros(x_test.shape[0])
        y_preds_proba = self.classifier.predict_proba(x_test)

        #y_preds[y_preds_proba[:, 0]>=threshold] = 0

        # 最佳threshold由class 0自己的pr曲线来挑出来， 但此处的thresh 要求为 1- positive threshold.
        y_preds[y_preds_proba[:, 1]>=threshold] = 1

        if y_test is not None:
            y_test = np.array(y_test)
            print(classification_report(y_test, y_preds))
        else:
            return {
                'preds':y_preds,
                "y_preds_proba_label": y_preds
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
        class_weight = {1:1.0, 0:1.5}
        #class_weight = {1:1.0, -1:1.5}

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


def create_output_path(output_dir, template, input_path, prefix="gptout_ad_filter", format="jsonl"):
    create_missing_directories(output_dir)
    input_name = os.path.basename(input_path).split(".")[0]
    output_path = f"{output_dir}/{prefix}_temp_{template}_data_{input_name}.{format}"
    return output_path

def create_missing_directories(path):
    # 分割路径为目录层级
    directories = path.split(os.path.sep)
    current_path = ""
    
    # 逐层创建目录
    for directory in directories:
        current_path = os.path.join(current_path, directory)
        if not os.path.exists(current_path):
            os.makedirs(current_path)
