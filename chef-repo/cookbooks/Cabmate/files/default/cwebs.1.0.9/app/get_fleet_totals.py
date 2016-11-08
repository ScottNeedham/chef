import os
import json
import struct
qtotals = "/data/fzstatus/normtots.fl"
#qtotals = "./test.fl"

def get_fleet_totals():
    file_name = qtotals
    print 'opening file ', file_name
    try:
        fp = open(file_name, "r")
        data = fp.read()
        fp.close()
    except Exception as e:
        print 'exception ', e
    #print data
    print 'length of data is ', len(data)
    print 'expected length of data is ', 4*12*16
    frmt = (len(data)/4)*'i'
    #print frmt
    tmp = struct.unpack(frmt, data)
    print 'tmp length ', len(tmp)
    tmp = tmp + (16*12 - len(tmp))*(0,)
    for i in range(16):
        print i+1, tmp[i*12:i*12+12]

def get_fleet_zone_totals_303(channel_id_by_fleet_id):
    file_name = qtotals
    print 'opening file ', file_name
    try:
        fp = open(file_name, "r")
        data = fp.read()
        fp.close()
    except Exception as e:
        print 'exception occured ', e
    #print data
    print 'length of data is ', len(data)
    print 'expected length of data is ', 4*12*16
    frmt = (len(data)/4)*'i'
    #print frmt
    tmp = struct.unpack(frmt, data)
    print 'tmp length ', len(tmp)
    tmp = tmp + (16*12 - len(tmp))*(0,)
    dic_to_transfer = {}
    for fleet_id, channel_id in channel_id_by_fleet_id.iteritems():
        print fleet_id, channel_id
        vehs = tmp[channel_id * 12]
        fares = tmp[channel_id *12 + 1]
        bcars = 0
        for i in [4, 5, 7, 9]:
            bcars = bcars + tmp[channel_id * 12 + i]
        total_cars = tmp[channel_id * 12 + 8]
        dic_to_transfer[fleet_id] = [vehs, fares, bcars, total_cars]
    res  = json.dumps(dic_to_transfer)
    print res
    return res


if __name__ == '__main__':
    get_fleet_totals()
    channel_id_by_fleet_id = {1: 1, 15: 1, 2: 2, 8: 2, 13: 2, 7: 3, 93: 3, 99: 3, 26: 4, 16: 5, 17: 6, 4: 7, 18: 8, 25: 9}
    res = get_fleet_zone_totals_303(channel_id_by_fleet_id)
