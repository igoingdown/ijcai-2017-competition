#!/usr/bin/python
# -*- coding:utf-8 -*-

"""
===============================================================================
author: 赵明星
desc:   从中国天气网抓取所有城市时间范围内每天的天气信息，
        目的是将天气作为模型的一个特征。
===============================================================================
"""

import sys
reload(sys)
sys.setdefaultencoding('utf-8')


import requests
import datetime
from pypinyin import lazy_pinyin
from os import listdir
from os.path import isfile, join
from lxml import html as  HTML
import cPickle
import time
import pandas as pd
import numpy as np
import re


def getCityNames():
    cityNames = []
    with open("city_name_id_dict.txt") as f:
        for line in f:
            cityName, id = line.strip().split(":")
            cityNames.append(cityName.strip())
    return cityNames


def getCityIds():
    cityIds = []
    with open("city_name_id_dict.txt") as f:
        for line in f:
            cityName, id = line.strip().split(":")
            cityIds.append(id.strip())
    return cityIds


def getCitySymbol(cities):
    symbolCities = []
    for c in cities:
        s_list = lazy_pinyin(unicode(c, "utf-8"))
        s = "".join(s_list)
        # print c, "   ", s.encode('ascii', 'ignore')
        symbolCities.append(s.encode('ascii', 'ignore'))
    return symbolCities


def generateCityIdToSymbolDict():
    ids = getCityIds()
    cities = getCityNames()
    symbols = getCitySymbol(cities)
    cityId2SymbolDict = {}
    if len(ids) == len(symbols):
        for i in xrange(len(symbols)):
            cityId2SymbolDict[ids[i]] = symbols[i]
    with open("cityIdToSymbolDict.pickle", "w") as f:
        cPickle.dump(cityId2SymbolDict, f)
    return cityId2SymbolDict


def getWeatherPages():
    cities = getCityNames()
    symbolCities = getCitySymbol(cities)
    startTime = datetime.datetime(2015, 6, 1, 0, 0, 0, 0)
    endTime = datetime.datetime(2016, 11, 1, 0, 0, 0, 0)
    startMonth = startTime.strftime("%Y%m")
    while startTime < endTime:
        startTime += datetime.timedelta(days=1)
        curMonth = startTime.strftime("%Y%m")
        if curMonth != startMonth:
            # print curMonth
            for s in symbolCities:
                """
                    只添加url爬不到天气信息，
                    添加一些header之后就OK了。
                """
                h = {"a":1,  "b":"c"}
                headers = {
                    'Accept-Encoding':'gzip, deflate, sdch',
                    'Accept-Language':'zh-CN,zh;q=0.8,en;q=0.6',
                    'Connection':'keep-alive',
                    'Host':'lishi.tianqi.com',
                    'Referer':'http://lishi.tianqi.com/{0}/{1}.html'.format(
                            s, curMonth),
                    'Upgrade-Insecure-Requests':'1',
                    'User-Agent':'Mozilla/5.0 ' +
                                 '(Macintosh; Intel Mac OS X 10_12_2)' +
                                 'AppleWebKit/537.36 (KHTML, like Gecko) ' +
                                 'Chrome/56.0.2924.87 Safari/537.36'
                         }

                url = "http://lishi.tianqi.com/{0}/{1}.html".format(s,
                                                                    curMonth)
                # print url
                r = requests.get(url, headers= headers)
                fName = "weathers/" + "_".join([s, curMonth]) + ".html"
                with open(fName, "w") as f:
                    f.write(r.text)
            startMonth = curMonth


def getWeatherInfoFromPages(cities, symbols):
    """
    @:desc:  先把信息存下来，然后再遍历所有页面进行提取。
    @:param:
             cities：城市的中文名列表
             symbols ：城市名的拼音列表
    :return: 先把处理结果以pickle写到文件里去，
             写成一个字典，city_id到每天的天气情况列表的字典。
             {city_id: {date:"最低气温，最高气温，多云，风向，风速"}}
             其中不知道的字段用"UNK"代替。
             这样每个city的每个date都多出了5个特征。
             然后把这个dict返回。
    """
    startTime = time.clock()
    cityIdToCityNameDict = generateCityIdToSymbolDict()
    cityIdAndNames =[x for x in cityIdToCityNameDict.iteritems()]
    files = [join("weathers", f) for f in listdir("weathers")]
    cityIdToDateWeatherDict = {}
    for f in files:
        with open(f) as page:
            pageContent = page.read()
            html = HTML.fromstring(pageContent.decode('utf-8'))
            weatherStatistic = html.find_class('tqtongji2')[0].xpath("./ul")
            citySymbol = f.strip().split("/")[1].split("_")[0]
            for c, s in cityIdAndNames:
                if citySymbol == s:
                    cityId = c
            if cityId not in cityIdToDateWeatherDict:
                cityIdToDateWeatherDict[cityId] = {}
            for i in xrange(len(weatherStatistic)):
                if i == 0:
                    continue
                weatherPiece = []
                for li in weatherStatistic[i].xpath("./li"):
                    l = li.xpath("text()")
                    if len(l) == 0:
                        try:
                            dateString = li.xpath("./a/text()")[0]
                        except:
                            weatherPiece.append("UNK")
                        nums = dateString.split("-")
                        y, m, d = [int(x) for x in nums]
                        weatherDay = datetime.date(y, m, d)
                    else:
                        weatherPiece.append(l[0])
                    cityIdToDateWeatherDict[cityId][weatherDay] \
                        = ",".join(weatherPiece)
    cityIdToDateWeatherDict['54'] = cityIdToDateWeatherDict['39']
    with open("cityIdToDateWeatherDict.pickle", "w") as w_f:
        cPickle.dump(cityIdToDateWeatherDict, w_f)
    endTime = time.clock()
    print "extract weather info from html" \
          " pages spends {0}s".format(endTime - startTime)
    return cityIdToDateWeatherDict


def generateWeekDayWeatherFeature(weather_info, mode):
    shop_info_fm = pd.read_csv("index_version_shop_info.csv",
                               header=None)
    shop_info = np.array(shop_info_fm)
    w = weather_info.iteritems()
    for k, v in w:
        print k
    # weathers = number_weather_piece(weather_info)
    shop_city_ids = [x[1] for x in shop_info]
    startDate = datetime.date(2015, 7, 1)
    endDate = datetime.date(2016, 11, 15)
    for i in xrange(7):
        with open(mode + "_day_{0}.csv".format(i + 1), "w") as w_f:
            for city_id in shop_city_ids:
                average_tem = []
                d = startDate + datetime.timedelta(days=i)
                while d < endDate:
                    if d in weather_info[str(city_id)]:

                        l = weather_info[str(city_id)][d].split(",")
                    else:
                        print city_id, " ", d
                        print "weather info lost!"
                        l = ['20', '20']
                    t = float(l[0]) + float(l[1]) / 2.0
                    average_tem.append(str(t))
                    d += datetime.timedelta(days=7)
                w_f.write(",".join(average_tem) + "\n")


def number_weather_piece(weather_info):
    """
    :desc: 将原来的字符串形式的天气信息形式化为数字形式。
    :param weather_info: 一个dict，形式为：
                         {shop_id:{date:"高温，低温，天气，风向，风速"}}
    :return: 返回一个dict，形式为：
             {shop_id:{date:"高温，低温，天气(num)，风速(num)"}}
    """
    weather_class = {}
    class_count = 0
    num_pattern = re.compile("\d")
    for shop in weather_info.keys():
        for d in weather_info[shop].keys():
            weather_piece = weather_info[shop][d]
            l = weather_piece.split(",")
            wind_speeds = num_pattern.findall(l[4])
            if len(wind_speeds) == 0:
                wind_speeds.append("0")
            if l[2] not in weather_class:
                weather_class[l[2]] = class_count
                class_count += 1
            weather_info[shop][d] = ",".join(
                [l[0], l[1], str(weather_class[l[2]]),
                  wind_speeds[0]])
    return weather_info


if __name__ == "__main__":
    # d = getWeatherInfoFromPages("", "")
    with open("cityIdToDateWeatherDict.pickle") as f:
        d = cPickle.load(f)
    generateWeekDayWeatherFeature(d, "weather")












