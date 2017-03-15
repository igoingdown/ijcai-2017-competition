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
import datetime

import sys
reload(sys)
sys.setdefaultencoding('utf-8')


def get_start_weekday():
    startDate = datetime.date(2015, 7, 1)
    endDate = datetime.date(2016, 11, 15)
    for i in xrange(7):
        d = startDate + datetime.timedelta(days=i)
        while d < endDate:
            if d == datetime.date(2016, 11, 1):
                return i
            d += datetime.timedelta(days=7)


if __name__ == "__main__":
    print get_start_weekday()














