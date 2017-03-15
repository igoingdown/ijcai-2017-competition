#!/usr/bin/python
# -*- coding:utf-8 -*-

"""
===============================================================================
author: 赵明星
desc:   读取用户的行为数据并进行简要的分析。
===============================================================================
"""

import sys
reload(sys)
sys.setdefaultencoding('utf-8')

import datetime
import time
import cPickle
import pandas as pd


def userBehaviorCount(readFile, writeFile):
    """
    :param readFile: 要读取的文件名
    :param writeFile: 要写入的文件名
    :return: 无返回，直接将生成的dict写到pickle文件中。
    """
    shop_Info_dict = {}
    with open(readFile) as f:
        startTime = time.clock()
        for line in f:
            user_id, shop_id, time_stamp = line.strip().split(",")
            payDate = \
                datetime.datetime.strptime(time_stamp,
                                           "%Y-%m-%d %H:%M:%S").date()
            if shop_id not in shop_Info_dict:
                shop_Info_dict[shop_id] = {}
            if payDate not in shop_Info_dict[shop_id]:
                shop_Info_dict[shop_id][payDate] = 0
            shop_Info_dict[shop_id][payDate] += 1
        endTime = time.clock()
        print "read file{0} spends {1}s".format(readFile,
                                                endTime - startTime)
        startTime = time.clock()
        with open(writeFile, "w") as w_f:
            cPickle.dump(shop_Info_dict, w_f)
        endTime = time.clock()
        print "write file {0} spends {1}s".format(writeFile,
                                                  endTime - startTime)


def sortByShopIdAndDate(shopInfoDict, pickle):
    sortedDateInfoList = []
    keyList = [str(i) for i in range(1, 2001)]
    startTime = time.clock()
    for k in keyList:
        shopInfo = {}
        startDate = datetime.date(2015, 7, 1)
        endDate = datetime.date(2016, 11, 15)
        d = startDate
        while d < endDate:
            if k in shopInfoDict:
                if d in shopInfoDict[k]:
                    shopInfo[d] = shopInfoDict[k][d]
                else:
                    shopInfo[d] = 0
            else:
                shopInfo[d] = 0
            d += datetime.timedelta(days=1)
        if d == startDate:
            print len(shopInfo)
            print endDate - startDate
        sortedDateInfoList.append(shopInfo)
    endTime = time.clock()
    print "it spends {0}s".format(endTime - startTime)
    print len(sortedDateInfoList)
    with open(pickle, "w") as f:
        cPickle.dump(sortedDateInfoList, f)


def addExtraUserView(shop_Info_dict, readFile, writeFile):
    with open(readFile) as f:
        startTime = time.clock()
        for line in f:
            user_id, shop_id, time_stamp = line.strip().split(",")
            payDate = \
                datetime.datetime.strptime(time_stamp,
                                           "%Y-%m-%d %H:%M:%S").date()
            if shop_id not in shop_Info_dict:
                shop_Info_dict[shop_id] = {}
            if payDate not in shop_Info_dict[shop_id]:
                shop_Info_dict[shop_id][payDate] = 0
            shop_Info_dict[shop_id][payDate] += 1
        endTime = time.clock()
        print "read file{0} spends {1}s".format(readFile,
                                                endTime - startTime)
    startTime = time.clock()
    with open(writeFile, "w") as w_f:
        cPickle.dump(shop_Info_dict, w_f)
    endTime = time.clock()
    print "write file {0} spends {1}s".format(writeFile,
                                              endTime - startTime)

def generateWeekDayCountFeature(sortedDateInfo, mode):
    startDate = datetime.date(2015, 7, 1)
    endDate = datetime.date(2016, 11, 1)
    for i in xrange(7):
        with open(mode + "_day_{0}.csv".format(i + 1), "w") as w_f:
            for j in xrange(2000):
                d = startDate + datetime.timedelta(days=i)
                counts = []
                while d < endDate:
                    counts.append(str(sortedDateInfo[j][d]))
                    d += datetime.timedelta(days=7)
                w_f.write(",".join(counts) + "\n")




if __name__ == "__main__":
    """
    userBehaviorCount("user_pay.txt", "shop_datePayCount.pickle")
    userBehaviorCount("user_view.txt", "shop_dateViewCount.pickle")



    with open("shop_datePayCount.pickle") as f:
        shop_datePayCount = cPickle.load(f)
    with open("shop_dateViewCount.pickle") as f:
        shop_dateViewCount = cPickle.load(f)
    """

    """
    # 将extra_user_view的信息加到viewCount中。
    addExtraUserView(shop_dateViewCount,
                     "../extra_user_view/extra_user_view.txt",
                     "shop_dateViewCount.pickle")
    with open("shop_dateViewCount.pickle") as f:
        shop_dateViewCount = cPickle.load(f)
    """

    """
    sortByShopIdAndDate(shop_datePayCount, "sortedShopDatePayList.pickle")
    sortByShopIdAndDate(shop_dateViewCount, "sortedShopDateViewList.pickle")
    """

    with open("sortedShopDatePayList.pickle") as f:
        payList = cPickle.load(f)
    with open("sortedShopDateViewList.pickle") as f:
        viewList = cPickle.load(f)
    # generateWeekDayCountFeature(payList, "pay")
    generateWeekDayCountFeature(viewList, "view")





