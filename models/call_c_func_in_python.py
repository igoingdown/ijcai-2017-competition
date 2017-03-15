#!/usr/bin/python
# -*- coding:utf-8 -*-

"""
===============================================================================
author: 赵明星
desc:   尝试在python程序中调用C语言编写的程序。
===============================================================================
"""

import ctypes
import time

import sys
reload(sys)
sys.setdefaultencoding('utf-8')


if __name__ == "__main__":
    lib = ctypes.cdll.LoadLibrary("/Users/zhaomingxing/PycharmProjects" +
        "/ijcai-17-competition/models/liba.so")
    lib.foo.restype = ctypes.c_float
    beginTime = time.clock()
    print lib.foo(10000)
    endTime = time.clock()
    print endTime - beginTime

    beginTime = time.clock()
    j = 0.0
    for i in xrange(10000):
        j = i * i
    print j
    endTime = time.clock()
    print endTime - beginTime








