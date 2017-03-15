#!/usr/bin/python
# -*- coding:utf-8 -*-

"""
===============================================================================
author: 赵明星
desc:   从第x天的csv文件中读取数据，生成训练集，测试集。
        作为后面模型的输入。
===============================================================================
"""

import time
import pandas as pd
import numpy as np

import sys
reload(sys)
sys.setdefaultencoding('utf-8')


def read_file(mode, day_x):
    start_time = time.clock()
    df = pd.read_csv("dataset/" + mode + "_day_{0}.csv".format(day_x),
                     header=None)
    arr = np.array(df)
    end_time = time.clock()
    return arr


def read_shop_info(f_name):
    df = pd.read_csv(f_name, header=None)
    arr = np.array(df)
    arr = [x[2:] for x in arr]
    return arr


def get_day_x_train_and_test_set(day_x):
    shop_feature = read_shop_info("dataset/index_version_shop_info.csv")
    pay_feature = read_file("pay", day_x)
    view_feature = read_file("view", day_x)
    weather_feature = read_file("weather", day_x)
    train_pay = [x[-21: -1] for x in pay_feature]
    train_view = [x[-21: -1] for x in view_feature]
    train_weather = [x[-23: -3] for x in weather_feature]
    train_feature = np.hstack((train_pay, train_view,
                               train_weather, shop_feature))
    train_label = [x[-1] for x in pay_feature]
    test_pay = [x[-20:] for x in pay_feature]
    test_view = [x[-20:] for x in view_feature]
    test_weather = [x[-22: -2] for x in weather_feature]
    test_feature = np.hstack((test_pay, test_view,
                              test_weather, shop_feature))
    return train_feature, train_label, test_feature


def get_day_x_week2_test_set(day_x, last_week_prediction):
    # 需要在MODEL里面改！model训练是一个过程，测试分两步，分别预测两周的情况。
    # 这个函数要把上周的test的label，作为本轮test最后一周的feature。
    # 同时weather要改最后一行，view可以不变
    shop_feature = read_shop_info("dataset/index_version_shop_info.csv")
    pay_feature = read_file("pay", day_x)
    view_feature = read_file("view", day_x)
    weather_feature = read_file("weather", day_x)
    # test_pay最后一个维度改为模型上周的预测输出。
    test_pay = [x[-19:] for x in pay_feature]
    last_pre = np.reshape(last_week_prediction,
                          (len(last_week_prediction), 1))
    test_pay = np.hstack((test_pay, last_pre))
    test_view = [x[-20:] for x in view_feature]
    test_weather = [x[-21: -1] for x in weather_feature]
    test_feature = np.hstack((test_pay, test_view,
                              test_weather, shop_feature))
    return test_feature


def get_day_x_train_and_dev_set(day_x):
    shop_feature = read_shop_info("dataset/index_version_shop_info.csv")
    pay_feature = read_file("pay", day_x)
    view_feature = read_file("view", day_x)
    weather_feature = read_file("weather", day_x)
    train_pay = [x[-22: -2] for x in pay_feature]
    train_view = [x[-22: -2] for x in view_feature]
    train_weather = [x[-24: -4] for x in weather_feature]
    train_feature = np.hstack((train_pay, train_view,
                               train_weather, shop_feature))
    train_label = [x[-2] for x in pay_feature]
    dev_feature = [train_feature[x] for x in range(0, 2000, 5)]
    dev_label = [train_label[x] for x in range(0, 2000, 5)]
    train_feature_without_dev = []
    train_label_without_dev = []
    for i in xrange(len(train_feature)):
        if i % 5 == 0:
            pass
        else:
            train_feature_without_dev.append(train_feature[i])
            train_label_without_dev.append(train_label[i])
    return train_feature_without_dev, train_label_without_dev, \
           dev_feature, dev_label


def get_day_x_week2_dev_set(day_x, last_prediction ):
    shop_feature = read_shop_info("dataset/index_version_shop_info.csv")
    pay_feature = read_file("pay", day_x)
    view_feature = read_file("view", day_x)
    weather_feature = read_file("weather", day_x)
    # test_pay最后一个维度改为模型上周的预测输出。
    test_pay = [x[-20: -1] for x in pay_feature]
    last_pre = np.reshape(last_prediction, (len(last_prediction), 1))
    print len(test_pay)
    print len(test_pay[0])
    print len(last_pre)
    print len(last_pre[0])
    test_pay = [test_pay[x] for x in range(0, 2000, 5)]
    dev_pay = np.hstack((test_pay, last_pre))
    test_view = [x[-22: -2] for x in view_feature]
    dev_view = [test_view[x] for x in range(0, 2000, 5)]
    test_weather = [x[-23: -3] for x in weather_feature]
    dev_weather = [test_weather[x] for x in range(0, 2000, 5)]
    dev_shop_feature = [shop_feature[x] for x in range(0, 2000, 5)]
    dev_feature = np.hstack((dev_pay, dev_view,
                              dev_weather, dev_shop_feature))
    test_label = [x[-1] for x in pay_feature]
    dev_label = [test_label[x] for x in range(0, 2000, 5)]
    return dev_feature, dev_label


if __name__ == "__main__":
    get_day_x_train_and_test_set(1)

















