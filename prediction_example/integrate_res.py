#!/usr/bin/python
# -*- coding:utf-8 -*-

"""
===============================================================================
author: 赵明星
desc:   将生成的预测数据合成一份完整的预测数据。
===============================================================================
"""

import pandas as pd
import numpy as np
import get_weekday_order as UTIL

import sys
reload(sys)
sys.setdefaultencoding('utf-8')


def integrate(model_type):
    examples_df = pd.read_csv("prediction_example/prediction_example.csv",
                              header=None)
    examples_arr = np.array(examples_df)
    shop_ids = [[x[0] for x in examples_arr]]
    shop_ids = np.reshape(shop_ids, (len(shop_ids[0]), 1))

    start_weekday = UTIL.get_start_weekday()
    print start_weekday
    weekdays = [start_weekday + 1]
    for i in range(1, 8):
        if i > start_weekday + 1:
            weekdays.append(i)
    for i in range(1, 8):
        if i < start_weekday + 1:
            weekdays.append(i)
    print weekdays
    for i in weekdays:
        df = pd.read_csv("prediction_example/week_1_day_{0}.csv".format(i),
                         header=None)
        labels = np.array(df)
        shop_ids = np.hstack((shop_ids, labels))
    for i in weekdays:
        df = pd.read_csv("prediction_example/week_2_day_{0}.csv".format(i),
                         header=None)
        labels = np.array(df)
        shop_ids = np.hstack((shop_ids, labels))
    with open("prediction_example/{0}_prediction.csv".format(model_type),
              "a") as f:
        for s in shop_ids:
            s = [str(x) for x in s]
            f.write(",".join(s) + '\n')


if __name__ == "__main__":
    pass














