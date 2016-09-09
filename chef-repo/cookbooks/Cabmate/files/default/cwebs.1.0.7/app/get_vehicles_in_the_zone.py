import os
import json

fleet_qfolder = "/data/export/"

def get_vehicles_in_the_zone():
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
                    #zone_set_list.append((aline.split(',')[0], aline.split(',')[1]))
        except Exception as e:
            print 'exception %s occured ', e
        #print 'zone_name_list ', zone_name_list
        #print 'zone_set_dic ', zone_set_dic
        res = []
        for iz in zone_name_list:
            res_tuple = (iz, )
            for v in zone_set_dic[iz]:
                res_tuple = res_tuple + (v,)
            res.append(res_tuple)
        res_dic[zoneset] = res
    for zoneset in ['0', '1', '2', '3', '4']:
        print 'zoneset ', zoneset, ' follows'
        print res_dic[zoneset]
    return json.dumps(res_dic)

if __name__ == '__main__':
    get_vehicles_in_the_zone()
