#!/usr/bin/env python
#coding=utf8

'''
    @update:    2016.6.28
    @by:        zhaomingxing
    @desc:      法国航空单程机票解析
'''

import re
import traceback
import time
import datetime
import sys
import random
from util.Browser import MechanizeCrawler as MC
import json
from lxml import html as HTML
from common.class_common import Flight, EachFlight
from util.crawl_func import request_post_data
from common.logger import logger
from common.common import get_proxy, invalid_proxy
from common.timezone import get_time_zone
from common.airline_common import Airline
from common.city_common import City

reload(sys)
sys.setdefaultencoding('utf-8')

TASK_ERROR = 12
PROXY_NONE = 21
PROXY_INVALID = 22
PROXY_FORBIDDEN = 23
DATA_NONE = 24
UNKNOWN_TYPE = 25
PARSE_ERROR = 27


cabin_pat = re.compile(r'cabinLabel: (.*?),')
price_pat = re.compile(r'\d+')

CONTENT_LEN = 1000

SearchURL_0 = 'http://www.airfrance.com.cn/cgi-bin/AF/CN/zh/local/process/standardbooking/ValidateSearchAction.do'
RefererURL_0 = 'http://www.airfrance.com.cn/CN/zh/common/home/home/HomePageAction.do'

SearchURL = 'http://www.airfrance.com.cn/cgi-bin/AF/CN/zh/local/process/standardbooking/DisplayFlightPageAction.do'
RefererURL = 'http://www.airfrance.com.cn/cgi-bin/AF/CN/zh/local/process/standardbooking/ValidateSearchAction.do'

def cal_time(time):
    dur = 0
    time_tmp = time.split(':')
    dur = int(time_tmp[0])*3600 + int(time_tmp[1])*60

    return dur

def getpostdata(dept_city, dest_city, year, month, day, nump, tp, ages):

    numOfInfant = 0
    numOfAdult = 0
    numOfChild = 0
    try:
        for i in range(len(ages)):
            if ages[i] == 'INF':
                numOfInfant += 1
            if ages[i] == 'CHD':
                numOfChild += 1
            else:
                numOfAdult += 1
            
    except:
        logger.error('airfranceFlight :: content format error')
        numOfAdult = 1

    postdatanew = 'arrivalType=AIRP&cabin='+ tp + '&plusOptions=&nbEnfants=' + str(numOfChild) + '&nbBebes=' + str(numOfInfant)  + '&nbPassenger=' + str(nump) + '&standardMandatory=true&calendarSearch=0&nbAdults=' + str(numOfAdult) + '&optionalUM=false&familyTrip=NON&flyingBlueMember=false&subCabin=MCHER&selectCabin=on&yearMonthDate='+ str(year) + str(month)  +'&corporateMode=false&isUM=false&dayDate=' + str(day) + '&departure=' + dept_city + '&mandatoryUM=true&paxTypoList=ADT&departureType=AIRP&typeTrip=1&arrival=' + dest_city + '&partnerRequest=false&nbChildren=' + str(numOfChild) + '&haul=LH'

    return postdatanew


def airfrance_parser(postData, dept_city, dest_city, year, month, day):

    tickets = []
    flights = {}
    result = {}
    result['para'] = {'ticket':tickets,'flight':flights}
    result['error'] = 0

    mc = MC()
    mc.set_debug(True)

    p = get_proxy(source = 'airfranceFlight')
    result['proxy'] = p
    if p == None or p == '':
        result['error'] = PROXY_NONE
        return result

    #mc.set_proxy(p)
    try:
        url0 = 'http://www.airfrance.com.cn/'
        page0 = mc.req('get', url0, html_flag = True)

        mc.add_referer(RefererURL_0)
        url1 = SearchURL_0
        page1 = mc.req('post', url1, postData, paras_type = 2, html_flag = True)

        mc.add_referer(RefererURL)
        url2 = SearchURL
        page2 = mc.req('post', url2, postData, paras_type = 2, html_flag = True)

    except Exception, e:
        result['error'] = PROXY_INVALID
        return result
    try:
        html = HTML.fromstring(page2.decode('utf-8'))
    except:
        logger.error('airfranceFlight :: page has no cotent')
        result['error'] = PROXY_INVALID
        return result

    try:
        flight_info = html.find_class('flight_list')[0].xpath('./tbody')[1]
    except:
        logger.error('airfranceFlight :: no data got!')
        result['error'] = DATA_NONE
        return result

    flight_detail_list = flight_info.find_class('desc accessibility--hide flight_row_detail')

    for i in range(len(flight_detail_list)):
        dur = flight_info.get_element_by_id('idFlightRecommendationOutbound_' + str(i)).find_class('time__right')[0].find_class('duration')[0].find_class('duration__value')[0].xpath('text()')[0]
        hour, minute = dur.strip().split('h')
        dur = int(hour) * 3600 + int(minute) * 60
        stop = 0
        
        flight_corp_list = []
        plane_type_list = []
        flight_no_list = []
        time_list = []
        airport_list = []
        day_differ_list = []
        day_counter = datetime.date(int(year), int(month), int(day))
        currency = 'CNY'

        for j in range(len(flight_detail_list[i].find_class('award__table')[0].find_class('award__row'))):
            if len(flight_detail_list[i].find_class('award__table')[0].find_class('award__row')[j].find_class('flight')) != 0:
                x = flight_detail_list[i].find_class('award__table')[0].find_class('award__row')[j].find_class('flight')[0].xpath('text()')[0]
                x_list = x.split(' ')
                x = ''.join([item for item in x_list])
                flight_no_list.append(x)

                x = flight_detail_list[i].find_class('award__table')[0].find_class('award__row')[j].find_class('right_hand_values')[1].find_class('desc_value')[0].xpath('text()')[0]
                plane_pat = re.compile(r'\d+')
                plane = plane_pat.findall(x)[0]
                plane_type_list.append(plane)
                stop += 1
                corp = flight_detail_list[i].find_class('award__table')[0].find_class('award__row')[j].find_class('right_hand_values')[0].find_class('desc_value')[0].xpath('text()')[0]
                flight_corp_list.append(corp.strip())
                
                try:
                    beg_time = flight_detail_list[i].find_class('award__table')[0].find_class('award__row')[j].find_class('t1__od__segment')[0].find_class('t1__od__ori')[0].find_class('t1__od__date')[0].xpath('text()')[0]
                    end_time = flight_detail_list[i].find_class('award__table')[0].find_class('award__row')[j].find_class('t1__od__segment')[0].find_class('t1__od__dest')[0].find_class('t1__od__date')[0].xpath('text()')[0]
                except Exception, e:
                    logger.error('airfranceFlight :: time error!')
                    result['error'] = PARSE_ERROR
                    return result
                
                minutes_1 = 0
                if(len(beg_time.strip().split(':')[1].split('+')) == 1): 
                    minutes_1 = int(beg_time.strip().split(':')[0]) * 60 + int(beg_time.strip().split(':')[1])
                else:
                    res = int(beg_time.strip().split(':')[1].split('+')[0].strip()) + int(beg_time.strip().split(':')[1].split('+')[1].strip())
                    minutes_1 = int(beg_time.strip().split(':')[0]) * 60 + res

                minutes_2 = 0
                if(len(end_time.strip().split(':')[1].split('+')) == 1):
                    minutes_2 = int(end_time.strip().split(':')[0]) * 60 + int(end_time.strip().split(':')[1])
                else:
                    res = int(end_time.strip().split(':')[1].split('+')[0].strip()) + int(end_time.strip().split(':')[1].split('+')[1].strip())
                    minutes_2 = int(end_time.strip().split(':')[0]) * 60 + res

                if minutes_1 < minutes_2:
                    b = datetime.datetime.now()
                    if(len(beg_time.strip().split(':')[1].split('+')) == 1):
                        b = datetime.datetime.combine(day_counter, datetime.time(int(beg_time.strip().split(':')[0]), int(beg_time.strip().split(':')[1])))
                    else:
                        res = int(beg_time.strip().split(':')[1].split('+')[0].strip()) + int(beg_time.strip().split(':')[1].split('+')[1].strip())
                        b = datetime.datetime.combine(day_counter, datetime.time(int(beg_time.strip().split(':')[0]), res))

                    e = b
                    if(len(end_time.strip().split(':')[1].split('+')) == 1):
                        e = datetime.datetime.combine(day_counter, datetime.time(int(end_time.strip().split(':')[0]), int(end_time.strip().split(':')[1])))
                    else:
                        res = int(end_time.strip().split(':')[1].split('+')[0].strip()) + int(end_time.strip().split(':')[1].split('+')[1].strip())
                        e = datetime.datetime.combine(day_counter, datetime.time(int(end_time.strip().split(':')[0]), res))
                    time_list.append('_'.join([b.strftime("%Y-%m-%dT%H:%M:%S"),  e.strftime("%Y-%m-%dT%H:%M:%S")]))
                    day_differ_list.append(0)
                else:
                    day_counter = day_counter + datetime.timedelta(days=1)

                    b = datetime.datetime.now()
                    if(len(beg_time.strip().split(':')[1].split('+')) == 1):
                        b = datetime.datetime.combine(day_counter, datetime.time(int(beg_time.strip().split(':')[0]), int(beg_time.strip().split(':')[1])))
                    else:
                        res = int(beg_time.strip().split(':')[1].split('+')[0].strip()) + int(beg_time.strip().split(':')[1].split('+')[1].strip())
                        b = datetime.datetime.combine(day_counter, datetime.time(int(beg_time.strip().split(':')[0]), res))

                    e = b
                    if(len(end_time.strip().split(':')[1].split('+')) == 1):
                        e = datetime.datetime.combine(day_counter, datetime.time(int(end_time.strip().split(':')[0]), int(end_time.strip().split(':')[1])))
                    else:
                        res = int(end_time.strip().split(':')[1].split('+')[0].strip()) + int(end_time.strip().split(':')[1].split('+')[1].strip())
                        e = datetime.datetime.combine(day_counter, datetime.time(int(end_time.strip().split(':')[0]), res))
                    time_list.append('_'.join([b.strftime("%Y-%m-%dT%H:%M:%S"),  e.strftime("%Y-%m-%dT%H:%M:%S")]))
                    day_differ_list.append(1)

                try:
                    beg_airport = flight_detail_list[i].find_class('award__table')[0].find_class('award__row')[j].find_class('t1__od__segment')[0].find_class('t1__od__ori')[0].find_class('t1__od__airport')[0].xpath('text()')[0]
                    end_airport = flight_detail_list[i].find_class('award__table')[0].find_class('award__row')[j].find_class('t1__od__segment')[0].find_class('t1__od__dest')[0].find_class('t1__od__airport')[0].xpath('text()')[0]
                    airport_list.append(beg_airport.strip())
                    airport_list.append(end_airport.strip())
                except Exception, e:
                    logger.error('airfranceFlight :: airport error!')
                    result['error'] = PARSE_ERROR
                    return result

        airport_list[0] = dept_city
        airport_list[-1] = dest_city
        stop_id_list = []

        for j in range(len(airport_list)/2):
            stop_id_list.append('_'.join([airport_list[2 * j], airport_list[2 * j + 1]]))
        stop_id = '|'.join([x for x in stop_id_list])
        flight_no = '_'.join([x for x in flight_no_list])
        plane_type = '_'.join([x for x in plane_type_list])
        stop -= 1
        flight_corp = '_'.join([x for x in flight_corp_list])
        stop_time = '|'.join([x for x in time_list])
        daydiff = '_'.join([str(x) for x in day_differ_list])       
        dept_id = dept_city
        dest_id = dest_city
        dept_day = str(year) + '-' + str(month) + '-' + str(day)
        dept_time = time_list[0].split('_')[0]
        dest_time = time_list[-1].split('_')[1]
        source = 'airfrance::airfrance'
        
        
        if len(flight_info.get_element_by_id('idFlightRecommendationOutbound_' + str(i)).find_class('cheapest')) != 0:
            other_info = flight_info.get_element_by_id('idFlightRecommendationOutbound_' + str(i)).find_class('cheapest')[0]
            cabin = cabin_pat.findall(other_info.find_class('price')[0].xpath('./@onclick')[0])[0]
            cabin = cabin[1:-1]
            cabins = []
            for _ in range(len(time_list)):
                cabins.append(cabin)
            seat_type = '_'.join([x for x in cabins])
            class_list = []
            for c in cabins:
                if c == u'经济舱' or c == u'尊尚经济舱':
                    class_list.append('E')
                if c == u'商务舱':
                    class_list.append('B')
            real_class = '_'.join([x for x in class_list])
            
            price = '';

            '''
            try:
                price = other_info.get_element_by_id('idSummaryInputOutboundPrice').xpath('./@value')[0]
            except Exception,e:
                logger.error('airfranceFlight :: idSummaryInputOutboundPrice not found!')
            '''

            try:
                price_list = price_pat.findall(other_info.find_class('price__value')[0].xpath('./span')[1].xpath('text()')[0])
                for p in price_list:
                    price += p
            except Exception,e:
                logger.error('airfranceFlight :: price_value class not found!')
                result['error'] = PARSE_ERROR
                return result
                
            price = float(price)

            flight = Flight()
            flight.tax = 0
            flight.flight_no = flight_no
            flight.plane_type = plane_type
            flight.flight_corp = flight_corp
            flight.dept_id = dept_id
            flight.dest_id = dest_id
            flight.dept_day = dept_day
            flight.dept_time = dept_time
            flight.dest_time = dest_time
            flight.dur = dur
            flight.price = price
            flight.currency = currency
            flight.seat_type = seat_type
            flight.real_class = real_class
            flight.stop_id = stop_id
            flight.stop_time = stop_time
            flight.daydiff = daydiff
            flight.source = source
            flight.stop = stop
            flight_tuple = (flight.flight_no,flight.plane_type,flight.flight_corp,flight.dept_id,flight.dest_id,flight.dept_day,\
                    flight.dept_time,flight.dest_time,flight.dur,flight.rest,flight.price,flight.tax,flight.surcharge,\
                    flight.promotion,flight.currency,flight.seat_type,flight.real_class,flight.package,flight.stop_id,flight.stop_time,\
                    flight.daydiff,flight.source,flight.return_rule,flight.change_rule,flight.stop,flight.share_flight,flight.stopby,\
                    flight.baggage,flight.transit_visa,flight.reimbursement,flight.flight_meals,flight.ticket_type,flight.others_info)
            tickets.append(flight_tuple)
        

        other_info = flight_info.get_element_by_id('idFlightRecommendationOutbound_' + str(i)).find_class('on')
        for k in range(len(other_info)):
            cabin = cabin_pat.findall(other_info[k].find_class('price')[0].xpath('./@onclick')[0])[0]
            cabin = cabin[1:-1]
            cabins = []

            for _ in range(len(time_list)):
                cabins.append(cabin)
            seat_type = '_'.join([x for x in cabins])
            class_list = []
            for c in cabins:
                if c == u'经济舱' or c == u'尊尚经济舱':
                    class_list.append('E')
                if c == u'商务舱':
                    class_list.append('B')
            real_class = '_'.join([x for x in class_list])

            price = ''
            
            '''
            try:
                price = other_info[k].get_element_by_id('idSummaryInputOutboundPrice').xpath('./@value')[0]
            except Exception,e:
                logger.error('airfranceFlight :: idSummaryInputOutboundPrice did not find!')
            '''

            try:
                price_list = price_pat.findall(other_info[k].find_class('price__value')[0].xpath('./span')[1].xpath('text()')[0])
                for p in price_list:
                    price += p
            except Exception,e:
                logger.error('airfranceFlight :: price_value not found!')
                result['error'] = PARSE_ERROR
                return result

            price = float(price)

            fligt = Flight()
            flight.tax = 0
            flight.flight_no = flight_no
            flight.plane_type = plane_type
            flight.flight_corp = flight_corp
            flight.dept_id = dept_id
            flight.dest_id = dest_id
            flight.dept_day = dept_day
            flight.dept_time = dept_time
            flight.dest_time = dest_time
            flight.dur = dur
            flight.price = price
            flight.currency = currency
            flight.seat_type = seat_type
            flight.real_class = real_class
            flight.stop_id = stop_id
            flight.stop_time = stop_time
            flight.daydiff = daydiff
            flight.source = source
            flight.stop = stop
            flight_tuple = (flight.flight_no,flight.plane_type,flight.flight_corp,flight.dept_id,flight.dest_id,flight.dept_day,\
                    flight.dept_time,flight.dest_time,flight.dur,flight.rest,flight.price,flight.tax,flight.surcharge,\
                    flight.promotion,flight.currency,flight.seat_type,flight.real_class,flight.package,flight.stop_id,flight.stop_time,\
                    flight.daydiff,flight.source,flight.return_rule,flight.change_rule,flight.stop,flight.share_flight,flight.stopby,\
                    flight.baggage,flight.transit_visa,flight.reimbursement,flight.flight_meals,flight.ticket_type,flight.others_info)
            tickets.append(flight_tuple)
    return result

def airfrance_task_parser(taskcontent):

    result = {}
    tickets = []
    flights = {}
    result['para'] = {'ticket':tickets,'flight':flights}
    result['error'] = 0

    try:
        infos = taskcontent.strip().split('&')
        dept_city = infos[0]
        dest_city = infos[1]
        day, month, year = infos[2][6:], infos[2][4:6], infos[2][0:4]
	nump = '1'
	tp = 'Y'
	ages = ['ADT'];
	if len(infos) >=4:
	    nump = str(infos[3])
	if len(infos) >=5:
	    tp = infos[4]
	    if tp == 'E':
		tp = 'Y'
	    elif tp == 'B':
		tp = 'C'
	    elif tp == 'F':
		tp = 'F'
	    elif tp == 'P':
		tp = 'W'
	'''
	因数据格式不一致，暂不支持头等舱
	'''
	if tp == 'F':
	    result['error'] = TASK_ERROR
	    return result

	if len(infos) >=6:
	    ages = infos[5].split('_')
	    flag = 0
	    for i in range(len(ages)):
		if float(ages[i]) >= 4 or float(ages[i]) == -1:
		    flag = 1
		else:
		    pass
		if float(ages[i]) == -1:
		    ages[i] = 'ADT'
		elif float(ages[i]) >= 0 and float(ages[i]) <= 1:
		    ages[i] = 'INF'
		elif float(ages[i]) > 1 and float(ages[i]) <= 11:
		    ages[i] = 'CHD'
		elif float(ages[i]) > 11 and float(ages[i]) <= 17:
		    ages[i] = 'YTH_MIN'
		elif float(ages[i]) > 17 and float(ages[i]) < 59:
		    ages[i] = 'ADT'
		elif float(ages[i]) >= 59:
		    ages[i] = 'YCD'
	    '''
	    因法航乘客需求，未满4岁不可单独乘车
	    '''
	    if flag == 0:
	 	result['error'] = TASK_ERROR
	 	return result
    except Exception, e:
        result['error'] = TASK_ERROR
        return result

    if dept_city == '' or dest_city == '' or infos[2] == '':
        result['error'] = TASK_ERROR
        return result

    postdata = getpostdata(dept_city, dest_city, year, month, day, nump, tp, ages)

    try:
        result = airfrance_parser(postdata, dept_city, dest_city, year, month, day)
    except Exception, e:
        result['error'] = 22
        return result

    return result


if __name__ == "__main__":
    res = airfrance_parser('PEK', 'FAU', '2016', '08', '10')

