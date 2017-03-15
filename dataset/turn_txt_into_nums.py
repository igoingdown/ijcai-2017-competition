#!/usr/bin/python
# -*- coding:utf-8 -*-

"""
===============================================================================
author: 赵明星
desc:   将原始数据中的文本通过建立索引转换为数据。
===============================================================================
"""

import sys
reload(sys)
sys.setdefaultencoding('utf-8')


import pandas as pd
import numpy as np


def change_text_into_id(d, index, l):
	c = 0
	for item in l:
		if d.get(item[index], -1) == -1:
			d[item[index]] = c
			c += 1


def write_dict_into_text(file_name, d):
	with open(file_name, "wb") as f:
		for item in d.iteritems():
			print >>f, item[0], ":", item[1]


shop_info_list = []
with open("shop_info.txt", "rb") as f:
	for line in f:
		shop_info_list.append(line.split(","))

city_name_id_dict = {}
l1_class_dict = {}
l2_class_dict = {}
l3_class_dict = {}
city_counter = 0
l1_class_counter = 0
l2_class_counter = 0
l3_class_counter = 0

# TODO: 将文本域中文本提出，为每个文本域分别构建字典。
change_text_into_id(city_name_id_dict, 1, shop_info_list)
change_text_into_id(l1_class_dict, -3, shop_info_list)
change_text_into_id(l2_class_dict, -2, shop_info_list)
change_text_into_id(l3_class_dict, -1, shop_info_list)

# TODO： 将文本域替换为相应字典中的id。
for shop_info in shop_info_list:
	shop_info[1] = city_name_id_dict[shop_info[1]]
	shop_info[-3] = l1_class_dict[shop_info[-3]]
	shop_info[-2] = l2_class_dict[shop_info[-2]]
	shop_info[-1] = l3_class_dict[shop_info[-1]]

for shop_info in shop_info_list:
	for x in xrange(len(shop_info)):
		if shop_info[x] == "":
			shop_info[x] = 0

# TODO：将字典存入相应的文件中。
write_dict_into_text("city_name_id_dict.txt", city_name_id_dict)
write_dict_into_text("l1_class_dict.txt", l1_class_dict)
write_dict_into_text("l2_class_dict.txt", l2_class_dict)
write_dict_into_text("l3_class_dict.txt", l3_class_dict)


with open("index_version_shop_info.csv", "wb") as f:
	for shop_info in shop_info_list:
		f.write(",".join([str(x) for x in shop_info]) + "\n")






