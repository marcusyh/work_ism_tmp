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
    total_duration = 0
    
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
        if str(items.get('ad_id', 0)) != str(289):
            continue
        device = items.get('_device', '')
        duration = int(items.get('duration', 0))
        day = items['time'].strftime('%Y-%m-%d')
        sn = items.get('sn', '')
    
        total_duration += duration
    
        if day not in total_counts:
            total_counts[day] = {}
        if device not in total_counts[day]:
            total_counts[day][device] = {}
    
        if duration >= ad_len:
            total_counts[day][device]['full'] = total_counts[day][device].get('full', 0) + 1
        else:
            total_counts[day][device]['part'] = total_counts[day][device].get('part', 0) + 1
        total_counts[day][device]['all'] = total_counts[day][device].get('all', 0) + 1
    
        if day not in total_devices:
            total_devices[day] = {}
        if device not in total_devices[day]:
            total_devices[day][device] = {}
        total_devices[day][device][sn] = ''
    
    fhdlr.close()

    return total_duration, total_devices, total_counts


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

    summary_full, summary_part = 0, 0

    rslt = {}
    for device in sorted(dlst):
        drslt = []
        total = []
        for day in sorted(total_counts):
            tmp = total_counts[day].get(device, {})
            curr   = [tmp.get('part', 0), tmp.get('full', 0), tmp.get('all', 0)]
            total = [total[idx] + curr[idx] for idx in range(len(curr))] if total else curr

            drslt += curr
        drslt += total

        rslt[device] = drslt
        summary_part += total[0]
        summary_full += total[1]

    header, header2 = [''], ['']
    for x in sorted(total_counts):
        header  += [x, '', ''] 
        header2 += ['不完整曝光', '完整曝光', '总曝光']
    header  += ['%s天单设备类型合计' %(len(header)/3), '', '']
    header2 += ['不完整曝光', '完整曝光', '总曝光']

    return header, header2, rslt, summary_part, summary_full


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


def show_summary(devices, part, full, duration):
    print '总设备数, %s' %devices
    print '曝光总时长（小时）, %s' %float(Decimal(duration/3600).quantize(Decimal('.01'), rounding=ROUND_HALF_UP)) 
    print '曝光总次数, %s' %(part + full)
    print '不完整曝光总次数, %s' %part
    print '完整曝光总次数, %s' %full
    print '完整曝光率, %s' %float(Decimal(100 * full / (full+part)).quantize(Decimal('.01'), rounding=ROUND_HALF_UP)) 



fname = sys.argv[1]
fhdlr = open(fname, 'r')

start = datetime.datetime(2016, 1, 26)
end   = datetime.datetime(2016, 2, 1)
ad_id = 289
ad_len = 21


total_duration, total_devices, total_counts = get_source_info(fname, start, end, ad_id, ad_len)

devices_header, devices_rslt, devices_summary = get_devices_list(total_devices)
show_string(devices_header)
show_result(devices_rslt)

counts_header, counts_header2, counts_rslt, counts_part_summary, counts_full_summary = get_counts_list(total_counts)
show_string(counts_header)
show_string(counts_header2)
show_result(counts_rslt)

show_summary(devices_summary, counts_part_summary, counts_full_summary, total_duration)
