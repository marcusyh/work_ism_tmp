#coding: utf-8

import sys
reload(sys)
sys.setdefaultencoding('utf8')

import os
import datetime
from decimal import Decimal, ROUND_HALF_UP
from config import vendors


def get_source_info(fname, start, end, ad_id, ad_len):
    total_counts = {}
    total_devices = {}
    total_items = {}
    
    count = 0

    for l in fhdlr:
        if count % 10000 == 0:
            print count
        count += 1
        items = eval(l)
        if 'time' not in items:
            continue
        if items['time'] >= end or items['time'] <= start:
            continue
        day = items['time'].strftime('%Y-%m-%d')
        device = items.get('_device', '')
        item   = items.get('item', '')
        title  = items.get('title', '')
        sn = items.get('sn', '')
    
    
        if day not in total_counts:
            total_counts[day] = {}
        total_counts[day][device] = total_counts[day].get(device, 0) + 1
    
        if day not in total_devices:
            total_devices[day] = {}
        if device not in total_devices[day]:
            total_devices[day][device] = {}
        total_devices[day][device][sn] = ''
    
        if item not in total_items:
            total_items[item] = {}
        if title != '':
            total_items[item]['title'] = title
        total_items[item]['count'] = total_items[item].get('count', 0) + 1
    
    fhdlr.close()

    return total_devices, total_counts, total_items


def get_devices_list(total_devices):
    dlst = {}
    for k, v in total_devices.iteritems():
        for a, b in v.iteritems():
            dlst[a] = ''

    devices_all = 0

    rslt = {}
    for device in sorted(dlst):
        drslt = []
        total = []
        for day in sorted(total_devices):
            drslt.append(len(total_devices[day].get(device, [])))
            total += total_devices[day].get(device, [])
        d_total = len(set(total))
        drslt.append(d_total)
        rslt[device] = drslt
        devices_all += d_total

    header = [x for x in sorted(total_devices)]
    header.append('%s天单设备类型合计' %len(header))
    header.insert(0, '')

    return header, rslt, devices_all


def get_counts_list(total_counts):
    dlst = {}
    for k, v in total_counts.iteritems():
        for a, b in v.iteritems():
            dlst[a] = ''

    counts_all = 0

    rslt = {}
    for device in sorted(dlst):
        drslt = []

        total = 0
        for day in sorted(total_counts):
            drslt.append(total_counts[day].get(device, 0))
            total += total_counts[day].get(device, 0)
        drslt.append(total)

        rslt[device] = drslt
        counts_all += total

    header = [x for x in sorted(total_devices)]
    header.append('%s天单设备类型合计' %len(header))
    header.insert(0, '')

    return header, rslt, counts_all


def show_result(rslt):
    def print_vendor(rslt, vendor, vendor_name):
        total = []
        for device in vendor:
            if device not in rslt:
                continue
            drslt = rslt[device]
            total = [x+y for x, y in zip(total, drslt)] if total else drslt
            print '%s, %s' %(device, ', '.join(str(x) for x in drslt))
        print '%s, %s' %('%s合计' %vendor_name, ' ,'.join(str(x) for x in total))
        print 
        return total

    tmp_rslts = []
    tmp_names = ''
    for vendor in vendors:
        devices_list = vendors[vendor].get('devices')
        vendor_name  = vendors[vendor].get('name_zh')
        tmp_names   += vendor_name
        tmp_rslts.append(print_vendor(rslt, devices_list, vendor_name))
    
    total = [sum([row[idx] for row in tmp_rslts]) for idx in range(len(tmp_rslts[0]))]
    print '%s, %s' %('%s总合计' %tmp_names, ' ,'.join(str(x) for x in total))


def show_string(rslt):
    print ', '.join(str(x) for x in rslt)


def show_summary(devices, counts):
    print '总设备数, %s' %devices
    print '曝光总次数, %s' %counts

def write_items(total_items):
    h = open('/tmp/ad_items.csv', 'w')
    h.write('曝光次数, 视频Item, 视频title\n')
    for item, v in total_items.iteritems():
        h.write('%s, %s, %s\n' %(v.get('count', ''), item, v.get('title')))
    h.close()



fname = sys.argv[1]
fhdlr = open(fname, 'r')

start = datetime.datetime(2016, 1, 26)
end   = datetime.datetime(2016, 2, 1)
ad_id = 289
ad_len = 21


total_devices, total_counts, total_items = get_source_info(fname, start, end, ad_id, ad_len)

devices_header, devices_rslt, devices_summary = get_devices_list(total_devices)
show_string(devices_header)
show_result(devices_rslt)

counts_header, counts_rslt, counts_summary = get_counts_list(total_counts)
show_string(counts_header)
show_result(counts_rslt)

show_summary(devices_summary, counts_summary)

write_items(total_items)
