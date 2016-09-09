import json
import os, sys


import config.cwebsconf as Config
import struct
import scap

if not Config.l303Site:
    import zqqlib

test_fleets  = {"CALGARY": 1, "UK": 2, "FTL": 100}


def get_fleet_info():
    fleet_info = zqqlib.get_fleet_info()
    max_zone = 0
    fleet_id_by_channel_id = {}
    channel_id_by_fleet_id = {}
    zone_number_by_channel_id = {}
    for info, count in zip(fleet_info, range(len(fleet_info))):
        print 'fleet #', count+1, ' mdt ', info[0], ' number of zones ', info[1], ' fleet number ', info[2]
    # if not first record and if the zone number is nonzero
        if info[0] > 0 and info[1] > 0:
            fleet_id_by_channel_id[info[0]] = info[2]
            channel_id_by_fleet_id[info[2]] = info[0]
            zone_number_by_channel_id[info[0]] = info[1]
        if info[1] > max_zone:
            max_zone = info[1]
    print 'max zone for all fleets', max_zone
    return fleet_id_by_channel_id, channel_id_by_fleet_id, zone_number_by_channel_id

def get_fleet_zone_status():
    fleet_zone_info = zqqlib.get_fleet_zone_status()
    print 'fleet, zone, veh, fare, dest'
    for fzi in fleet_zone_info:
        print fzi

#
# returns vehicle position in the zone for 
# each of the zone sets  - all sites 
#
def get_vehicles_in_the_zone(fleet_qfolder):
    res_dic = {}
    for zoneset in ['0', '1', '2', '3', '4']:
        zone_set_dic = {}
        zone_name_list = []
        file_name = os.path.join(fleet_qfolder, "taxi_queue_" + zoneset.strip()+ ".fl")
        print 'opening file ', file_name
        try:
            for aline in open(file_name):
                print aline
                veh = aline.split(',')
                if len(veh) > 2:
                    zone_name = veh[0]
                    if zone_name not in zone_name_list:
                        zone_name_list.append(zone_name)
                    zone_info = []
                    for v in veh[1::2]:
                        zone_info.append(v)
                    if not zone_set_dic.has_key(zone_name):
                        zone_set_dic[zone_name] = zone_info
                    else:
                        zone_set_dic[zone_name].extend(zone_info)
        except Exception as e:
            print 'exception %s occured ', e
        res = []
        for iz in zone_name_list:
            res_tuple = (iz, )
            for v in zone_set_dic[iz]:
                res_tuple = res_tuple + (v,)
            res.append(res_tuple)
        res_dic[zoneset] = res
    return json.dumps(res_dic)
               
#
# this is a general method which employs  C lib
#
def get_fleet_zone_status_by_fleet_id(fleet_id, channel_id_by_fleet_id, zone_number_by_channel_id, lActiveOnly=False):
    res_dic = {}
    if channel_id_by_fleet_id.has_key(fleet_id):
        channel_id = channel_id_by_fleet_id[fleet_id]
        fleet_zone_info = zqqlib.get_fleet_zone_status()
        for fzi in fleet_zone_info:
            if fzi[0] == channel_id:
	        if lActiveOnly:
	            if fzi[2] > 0 and fzi[3] > 0:    
                        res_dic[fzi[1]] = (fzi[2], fzi[3])
                else:
		    res_dic[fzi[1]] = (fzi[2], fzi[3])    			
        if res_dic.has_key(0):
            del res_dic[0]
    return json.dumps(res_dic)	    
    
def get_fleet_zone_status_by_fleet_id_303(fleet_id, channel_id_by_fleet_id):
    res_dic = {}
    if not channel_id_by_fleet_id.has_key(fleet_id):
        return res_dic
    else:
        channel_id = channel_id_by_fleet_id[fleet_id]
    file_name = Config.normstat
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


def get_all_zones(fleet_to_zoneset):
    res_dic = {}
    
    lFleetSeparation = scap.is_fleet_separation_on()        
    if lFleetSeparation: 
        file_name = Config.normstat             #/data/fzstatus
    else:
        file_name = Config.normstat_nofleet     #/data/zstatus

    zone_status_struct = struct.Struct('i i i i')
    print 'opening file ', file_name
    try:
        fp = open(file_name, "r")
        fp.close()
    except Exception as e:
        print 'Exception ', str(e)
        return res_dic
    fleet_id_by_channel_id = {} 
    with open(file_name, "rb") as f:
        count = 0
        total_count = 0
        while True:
            count = count + 1
            total_count = total_count + 1
            data = f.read(zone_status_struct.size)
            if not data:
                break
            if data and total_count <= 16:
                udata = zone_status_struct.unpack(data)
                ud_0 = udata[0] % 65536
                ud_1 = udata[1] % 65536
                ud_2 = udata[2] % 65536
                ud_3 = udata[3] % 65536
                if ud_0 > 0 and  ud_1 > 0:
                    fleet_id_by_channel_id[count - 1] = ud_1
            if data and total_count > 16:
                udata = zone_status_struct.unpack(data)
                ud_0 = udata[0] % 65536
                ud_1 = udata[1] % 65536
                ud_2 = udata[2] % 65536
                ud_3 = udata[3] % 65536
                if ud_0 > 0:
                    try:  
                        zoneset_id = fleet_to_zoneset[fleet_id_by_channel_id[count - 1]]
                        if res_dic.has_key(zoneset_id):
                            if ud_0 >  0 and (ud_0 not in res_dic[zoneset_id]):
                                res_dic[zoneset_id].append(ud_0)
                        else:
                            res_dic[zoneset_id] = []
                            if ud_0 > 0:
                                res_dic[zoneset_id].append(ud_0)
                    except Exception as e:
                        pass 
            if count == 16:
                count = 0
        for k, v in res_dic.iteritems():
            res_dic[k] = sorted(v)
    return json.dumps(res_dic)


def get_fzstatus(fleet_number):
    res_dic = {}
    file_name = Config.normstat
    zone_status_struct = struct.Struct('i i i i')
    print 'opening file ', file_name
    try:
        fp = open(file_name, "r")
        fp.close()
    except Exception as e:
        print 'Exception ', str(e)
        return res_dic
    channel_id_by_fleet_id = {}
    with open(file_name, "rb") as f:
        count = 0
        total_count = 0
        while True:
            count = count + 1
            total_count = total_count + 1
            data = f.read(zone_status_struct.size)
            if not data:
                break
            if data and total_count <= 16:
                udata = zone_status_struct.unpack(data)
                ud_0 = udata[0] % 65536
                ud_1 = udata[1] % 65536
                ud_2 = udata[2] % 65536
                ud_3 = udata[3] % 65536
                if ud_0 > 0 and  ud_1 > 0:
                    channel_id_by_fleet_id[ud_1] = count
                if total_count == 16:
                    if not channel_id_by_fleet_id.has_key(fleet_number):
                        break
            if data and total_count > 16:
                if count == channel_id_by_fleet_id[fleet_number]:
                    udata = zone_status_struct.unpack(data)
                    ud_0 = udata[0] % 65536
                    ud_1 = udata[1] % 65536
                    ud_2 = udata[2] % 65536
                    ud_3 = udata[3] % 65536
                    if ud_0 > 0 and (ud_1 >= 0 and ud_2 >= 0):
                        res_dic[ud_0] = [ud_1, ud_2]
            if count == 16:
                count = 0
    return json.dumps(res_dic)


def get_fleet_zone_totals(channel_id_by_fleet_id):
    print 'zone queue totals...'
    #####   1    2    3    4     5     6    7      8     9     10   11   12
    print 'taxi,fare,bid,offer,accept,dest,local,pickup,total,sfree,cvd,num'
    fleet_zone_totals = zqqlib.get_fleet_zone_totals()
    print 'zone totals'
    for fzt in fleet_zone_totals:
        print fzt
    print 'new zone totals'
    dic_to_transfer = {}
    for fleet_id, channel_id in channel_id_by_fleet_id.iteritems():
        print ' mdt ', channel_id, ' fleet_id ', fleet_id, ' tots ', fleet_zone_totals[channel_id][1:]
	# clear vehicles 
	vehs = fleet_zone_totals[channel_id][1]
	# number of jobs 
	fares = fleet_zone_totals[channel_id][2]
	# busy cars 
	bcars = 0 
	for i in [5, 6, 8, 10]: 
	    bcars = bcars + fleet_zone_totals[channel_id][i]
	total_cars = fleet_zone_totals[channel_id][9]    
        dic_to_transfer[fleet_id] = [vehs, fares, bcars, total_cars]
    print json.dumps(dic_to_transfer)
    return json.dumps(dic_to_transfer)


def get_fleet_zone_totals_303(channel_id_by_fleet_id):
    file_name = Config.normtots
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


if __name__ == "__main__":
    fleet_id_by_channel_id, channel_id_by_fleet_id, zone_number_by_channel_id = get_fleet_info()
    print get_fleet_zone_totals(channel_id_by_fleet_id)
    get_fleet_zone_status()
    print get_fleet_zone_status_by_fleet_id(1, channel_id_by_fleet_id, zone_number_by_channel_id)
    print get_vehicles_in_the_zone()
    #
    # 303 stuff  
    #get_fleet_totals()
    #channel_id_by_fleet_id = {1: 1, 15: 1, 2: 2, 8: 2, 13: 2, 7: 3, 93: 3, 99: 3, 26: 4, 16: 5, 17: 6, 4: 7, 18: 8, 25: 9}
    #res = get_fleet_zone_totals_303(channel_id_by_fleet_id)

