#!/usr/bin/python
# -*- coding:utf-8 -*-

"""
===============================================================================
author: 赵明星
desc:   第一个模型，使用LR。
===============================================================================
"""

from sklearn import preprocessing
from sklearn.linear_model import LogisticRegression
import dataset.generate_train_and_test_set_for_day_x as FEATURE

import sys
reload(sys)
sys.setdefaultencoding('utf-8')


def train_and_predict(train_feature, train_label, test_feature, day_x, mode):
    scale_train_feature = preprocessing.scale(train_feature)
    clf = LogisticRegression()
    clf.fit(scale_train_feature, train_label)
    scale_test_feature = preprocessing.scale(test_feature)
    predict_labels = clf.predict(scale_test_feature)
    if mode == "dev":
        dev_feature, dev_label = FEATURE.get_day_x_week2_dev_set(
                day_x,
                predict_labels)
        scale_week2_dev = preprocessing.scale(dev_feature)
        week_2_labels = clf.predict(scale_week2_dev)
        return predict_labels, week_2_labels, dev_label
    else:
        week_2_test = FEATURE.get_day_x_week2_test_set(day_x, predict_labels)
        scale_week2_test = preprocessing.scale(week_2_test)
        week_2_labels = clf.predict(scale_week2_test)
        return predict_labels, week_2_labels


if __name__ == "__main__":
    pass








