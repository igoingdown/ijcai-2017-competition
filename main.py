#!/usr/bin/python
# -*- coding:utf-8 -*-

"""
===============================================================================
author: 赵明星
desc:   主函数，先调用数据集处理函数生成训练集和测试集。
        然后调用一个model进行训练和预测。
===============================================================================
"""

import dataset.generate_train_and_test_set_for_day_x as FEATRUE
import models.lr_model as LR
import models.knn_model as KNN
import models.svm_model as SVM
import models.gbdt_model as GBDT
import models.rf_model as RF
import numpy as np

import prediction_example.integrate_res as INTEGRATE

import sys
reload(sys)
sys.setdefaultencoding('utf-8')


def calculate_loss(predict_labels, known_labels):
    if len(predict_labels) != len(known_labels):
        raise Exception("prediction and real label don\'t have equal length!")
    loss = 0.0
    for i in xrange(len(predict_labels)):
        if len(predict_labels[i]) != len(known_labels[i]):
            raise Exception("length is not equal!")
        for j in xrange(len(predict_labels[i])):
            loss += abs(predict_labels[i][j] - known_labels[i][j]) / \
                    (predict_labels[i][j] + known_labels[i][j])
    loss /= (len(predict_labels) * len(predict_labels[0]))
    return loss


def choose_model(train_feature, train_label,
                     dev_feature, day_x, model, mode="dev"):
    if model == 'svm':
        return SVM.svc(train_feature, train_label, dev_feature, day_x, mode)
    if model == 'knn':
        return KNN.train_and_predict(train_feature, train_label,
                                     dev_feature, day_x, mode)
    if model == "lr":
        return LR.train_and_predict(train_feature, train_label,
                                    dev_feature, day_x, mode)
    if model == "gbdt":
        return GBDT.train_and_predict(train_feature, train_label,
                                      dev_feature, day_x, mode)
    if model == "rf":
        return RF.train_and_predict(train_feature, train_label,
                                    dev_feature, day_x, mode)


def main(model):
    for i in range(1, 8):
        print i
        feature_no_dev, label_no_dev, dev_feature, dev_label = \
                FEATRUE.get_day_x_train_and_dev_set(i)
        week_1_labels, week_2_labels, week2_dev_label = \
                choose_model(feature_no_dev, label_no_dev,
                                    dev_feature, i, model)
        if i == 1:
            prediction_labels = np.vstack((week_1_labels, week_2_labels))
            known_labels = np.vstack((dev_label, week2_dev_label))
        else:
            prediction_labels = np.vstack((prediction_labels,
                                           week_1_labels, week_2_labels))
            known_labels = np.vstack((known_labels, dev_label,
                                      week2_dev_label))
    loss = calculate_loss(prediction_labels, known_labels)
    print "model {0} loss is: {1}\n".format(model, loss)
    with open("model loss.txt", "w+") as f:
        print >>f, "{0} model accuracy is {1}\n".format(model, loss)
    for i in range(1, 8):
        print i
        feature, label, test_feature = FEATRUE.get_day_x_train_and_test_set(i)
        test_labels, week_2_test_labels = \
                choose_model(feature, label, test_feature, i, model, "")

        with open("prediction_example/week_1_day_{0}.csv".format(i), "w") as f:
            for l in test_labels:
                f.write(str(l) + '\n')
        with open("prediction_example/week_2_day_{0}.csv".format(i), "w") as f:
            for l in week_2_test_labels:
                f.write(str(l) + '\n')
    INTEGRATE.integrate(model)


if __name__ == "__main__":
    main("knn")
    main("lr")
    main("gbdt")
    main("svm")
    main("rf")


