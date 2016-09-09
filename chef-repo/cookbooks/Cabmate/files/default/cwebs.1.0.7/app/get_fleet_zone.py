import os
import json
import struct

zonestat  = "/data/fzstatus/normstat.fl"

def get_fleet_zone():
    file_name = zonestat
    print 'opening file ', file_name
    try:
        fp = open(file_name, "r")
        data = fp.read()
        fp.close()
    except Exception as e:
        print 'exception ', e
    #print data
    print 'length of data is ', len(data)
    print 'number of 64 block int records is ', len(data)/(16*16)
    print 'number of 4 block int records is ', len(data)/(4*4)
    frmt = (len(data)/4)*'i'
    #print frmt
    tmp = struct.unpack(frmt, data)
    print 'tmp length ', len(tmp)
    for i in range(len(data)/16):
        res = []
        for j in range(4):
            res.append(tmp[i*4+j] % 65536)
        print (i+16) % 16, res


def get_fleet_zone_status_by_fleet_id_303(fleet_id, channel_id_by_fleet_id):
    res_dic = {}
    if not channel_id_by_fleet_id.has_key(fleet_id):
        return res_dic
    else:
        channel_id = channel_id_by_fleet_id[fleet_id]
    file_name = zonestat
    print 'opening file ', file_name
    try:
        fp = open(file_name, "r")
        data = fp.read()
        fp.close()
    except Exception as e:
        print 'exception ', e
    #print data
    print 'length of data is ', len(data)
    print 'number of 64 block int records is ', len(data)/(16*16)
    print 'number of 4 block int records is ', len(data)/(4*4)
    frmt = (len(data)/4)*'i'
    #print frmt
    tmp = struct.unpack(frmt, data)
    print 'tmp length ', len(tmp)
    for i in range(len(data)/16):
        res = []
        for j in range(4):
            res.append(tmp[i*4+j] % 65536)
        if i > 16 and (i + 16) % 16 == channel_id:
            res_dic[res[0]] = (res[1],res[2])
        #print (i+16) % 16, res
    return json.dumps(res_dic)



if __name__ == '__main__':
    channel_id_by_fleet_id = {1: 1, 15: 1, 2: 2, 8: 2, 13: 2, 7: 3, 93: 3, 99: 3, 26: 4, 16: 5, 17: 6, 4: 7, 18: 8, 25:
9}
    get_fleet_zone()
    print  get_fleet_zone_status_by_fleet_id_303(2, channel_id_by_fleet_id)

