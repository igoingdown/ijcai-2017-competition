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

import time
import torch.nn as nn


if __name__ == "__main__":
    startTime = time.clock()
    for i in xrange(10000):
        j = i * i
    endTime = time.clock()
    print "spends {0}s".format(endTime - startTime)
    print 1493/60.0
    l = [x for x in range(0, 200, 5)]
    m = []
    for i in range(0, 200):
        if i % 5 == 0:
            pass
        else:
            m.append(i)
    print l
    print m

    seq2seq = nn.Module()
    for p in seq2seq.parameters():
        print p




