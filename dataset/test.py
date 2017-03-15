#!/usr/bin/python
# -*- coding:utf-8 -*-

"""
===============================================================================
author: 赵明星
desc:   测试一些不太熟悉的工具的用法。
===============================================================================
"""

import sys
reload(sys)
sys.setdefaultencoding('utf-8')


class D:
    def __init__(self, a1, a2):
        self.a = 10
        self.b = 2
        self.c = a1
        self.d = a2

    def func_1(self, ok = True):
        if ok:
            print "OK"
        else:
            print "Not OK"

    def func_2(self, f = 10):
        print "func_2"


if __name__ == '__main__':
    d = {}
    for idx, line in enumerate(open("shop_info.txt").readlines()):
        d[idx] = line.strip()

    for k, v in d.iteritems():
        print "key: {0}\nval: {1}\n\n\n".format(k, v)

    o = D(3, 1)
    for i in xrange(3):
        with open("file_test.txt", "a") as f:
            f.write(str(i) + "\n")
