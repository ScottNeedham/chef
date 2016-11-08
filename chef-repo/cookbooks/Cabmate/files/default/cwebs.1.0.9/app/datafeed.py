import time
import struct
import os
import sysv_ipc
import sys
import requests
import json

'''
res[ 0] 4 1I unsigned long      Fare_Number;
res[ 1] 4 2I unsigned long      Fare_Ftypes;    //Dispatched or Flagged Trip
res[ 2] 4 3I unsigned long      Fare_Ftypes1;   //Dispatched or Flagged Trip
res[ 3] 4 4I unsigned long      MDT_State;
res[ 4] 4 5I unsigned long      Driver_Id;
res[ 5] 2 1h unsigned short     Zone_Number;
res[ 6] 2 2h unsigned short     Zone_Queue_Position;
res[ 7] 2 3h unsigned short     Queue_Type;
res[ 8] 2 4h unsigned short     Sspare;
res[ 9] 1 c unsigned char       Meter_Suspended;
res[10] 1 c unsigned char       Driver_Suspended;
res[11] 1 c unsigned char       Emergency_Mode;
res[12] 1 c unsigned char       Meter_on;
res[13] 1 c unsigned char       Available;      //October 6, 2014 RL
res[14] 3s unsigned char   Cspare1[3];
res[15] 4 f float           X;
res[16] 4 f float           Y;
res[17] 4 1I unsigned        long VehicleId;
208 208s  unsigned char   Cspare[208];
'''

SHM_DISPATCHINFO = 48
DelayTime = 5
full_resource_name = "http://10.10.1.239:8889/dispatcher/queues/"
arcus_resource_name = "http://10.0.1.230:8090/v1/soon-to-clear"
test_resource_name = "http://10.0.1.239:8090/v1/soon-to-clear"
#full_resource_name = arcus_resource_name
full_resource_name = test_resource_name

lArcusStyle = False
lDebug = True
test_vehicles = [1054, 9020, 9053]
MAX_VEHICLES = 32000

QueueTypeDic = {"TAXI_Q": 0, "FARE_Q": 1, "BID_Q": 2, "OFFR_Q": 3, "ACCPT_Q": 4, "DEST_Q": 5,
"LOCAL_Q": 6, "PICKUP_Q": 7, "HOLD_Q": 8, "SFREE_Q": 9, "CVD_RESP_Q": 10, "SMS_Q": 11}
QueueFilter = {"ACCPT_Q": 4}
print str(QueueTypeDic)

def get_queue_name(id): 
    res = ""
    for k, v in QueueTypeDic.iteritems():
        if v == id:
            return k
    return res

class ShareDispatchInfo(object):


    def __init__(self, key):
        self.shm_dispinfo = None
        try:
            self.shm_dispinfo = sysv_ipc.SharedMemory(key["SHM_DISPATCHINFO"], flags = 0, mode = 0600, size = 0)
            self.shm_dispinfo_num = key["RECORDS"]
            self.shm_dispinfo_sz = key["SIZE"]
            #self.shm_dispinfo_frmt = '5I 4h 5c 3s 2f 1I 208s'
            self.shm_dispinfo_frmt = '5I H H H H 5B 3s 2f I 208s'
            print 'size from format ', struct.calcsize(self.shm_dispinfo_frmt)

            self.shm_dispinfo_struct = struct.Struct(self.shm_dispinfo_frmt)
            print 'size from structure ', self.shm_dispinfo_struct.size
            print 'size from input ', self.shm_dispinfo_sz
            if self.shm_dispinfo_sz != self.shm_dispinfo_struct.size:
                raise Exception('structure size mismatch')
            print 'key             ', self.shm_dispinfo.key
            print 'id              ', self.shm_dispinfo.id
            print 'size            ', self.shm_dispinfo.size
            print 'attached        ', self.shm_dispinfo.attached
            print 'number_attached ', self.shm_dispinfo.number_attached
            print 'permission      ', int(str(self.shm_dispinfo.mode), 8)
        #except ExistentialError as e:
        except Exception as e:
            print 'Exception %s' % (str(e))
            self.shm_dispinfo = None
        return

    def valid_vehicle_id(self, vehicle_id, max_vehicles = MAX_VEHICLES):
        res = False
        try:
            if vehicle_id > 0 and vehicle_id < max_vehicles:
                res = True
        except Exception as e:
            pass
        return res

    def read(self, filter=None):
        res_dic = {}
        lSuccess = False
        #frmt = '5I 4H 5B 3s 2f 1I 208s'
        #s = struct.Struct(frmt)
        #print "size ", s.size
        #print "size from calc ", struct.calcsize(frmt)
        if self.shm_dispinfo:
            if self.shm_dispinfo.key > 0:
                lSuccess = True
                try:
                    for i in range(1, self.shm_dispinfo_num):
                        datastr = self.shm_dispinfo.read(self.shm_dispinfo_sz, i*self.shm_dispinfo_sz)
                        res = struct.unpack(self.shm_dispinfo_frmt, datastr)
                        queue_type = int(res[7])
                        vehicle_id = int(res[17])
                        #if vehicle_id != 9007:
                        #    continue
                        if queue_type in filter:
                            if queue_type == QueueTypeDic["TAXI_Q"]:
                                if self.valid_vehicle_id(vehicle_id, max_vehicles = MAX_VEHICLES):
                                    res_dic[str(vehicle_id)] = {"job_number": str(res[0]),
                                                           "mdt_state": str(res[3]),
                                                           "driver_id": str(res[4]),
                                                           "zone": str(res[5]),
                                                           "meter_on": str(res[12]),
                                                           #"availability": chr(res[13]),
                                                           "availability": str(res[13]),
                                                           "X": str(res[15]),
                                                           "Y": str(res[16]),
                                                           "vehicle_id": str(res[17]),
                                                           "queue": "TAXI_Q"}
                                                           #"queue": "SFREE_Q"}

                            if queue_type == QueueTypeDic["SFREE_Q"]:
                                if self.valid_vehicle_id(vehicle_id, max_vehicles = MAX_VEHICLES):
                                    res_dic[str(vehicle_id)] = {"job_number": str(res[0]),
                                                           #"mdt_state": res[3],
                                                           #"driver_id": res[4],
                                                           "zone": res[5],
                                                           #"meter_on": res[12],
                                                           #"availability": chr(res[13]),
                                                           #"X": res[15],
                                                           #"Y": res[16],
                                                           "vehicle_id": str(res[17]),
                                                           "queue": "SFREE_Q"}

                            if queue_type == QueueTypeDic["ACCPT_Q"]:
                                if self.valid_vehicle_id(vehicle_id, max_vehicles = MAX_VEHICLES):
                                    res_dic[str(vehicle_id)] = {"job_number": str(res[0]),
                                                           "mdt_state": str(res[3]),
                                                           "driver_id": str(res[4]),
                                                           "zone": str(res[5]),
                                                           "meter_on": str(res[12]),
                                                           #"availability": chr(res[13]),
                                                           "availability": str(res[13]),
                                                           "X": str(res[15]),
                                                           "Y": str(res[16]),
                                                           "vehicle_id": str(res[17]),
                                                           "queue": "ACCPT_Q"}
                except Exception as e:
                    print 'Exception ', str(e)

                if lDebug and len(test_vehicles) > 0:
                    for i in test_vehicles:
                        if i > 0 and i < MAX_VEHICLES:
                            try:
                                datastr = self.shm_dispinfo.read(self.shm_dispinfo_sz, i*self.shm_dispinfo_sz)
                                res = struct.unpack(self.shm_dispinfo_frmt, datastr)
                                print "Debug VehicleNumber: ", i, res, " queue type ", int(res[7]), get_queue_name(int(res[7]))
                            except Exception as e:
                                print 'Exception ', str(e)
            else:
                print 'Error: invalid key ', self.shm_dispinfo.key
        else:
            print 'Error: shm_dispinfo is not logical True'

        #print res_dic
        return res_dic

    def deattach(self):
        try:
            self.shm_dispinfo.detach()
        except Exception as e:
            print 'Exception %s' % (str(e))
        return

if __name__ == "__main__":
    dispatch_info = ShareDispatchInfo({"SHM_DISPATCHINFO": SHM_DISPATCHINFO,
                                        "RECORDS": 32000,
                                        "SIZE": 256})
    print 'queue ids ', QueueTypeDic.values()
    while True:
        msg_dic = {}
        #res_dic = dispatch_info.read(filter=[QueueTypeDic["ACCPT_Q"], QueueTypeDic["TAXI_Q"], QueueTypeDic["SFREE_Q"]])
        res_dic = dispatch_info.read(filter=[QueueTypeDic["SFREE_Q"]])
        print 'res_dic: ', res_dic
        if not lArcusStyle: 
            msg_dic["data"] = res_dic
            msg_dic["msgtype"] = "queue"
        else:
            msg_dic = {}
            msg_dic["stc"] = json.dumps({"msgtype": "queue", "data": res_dic})
        print 'msg_dic: ', msg_dic
        
        try:
            print 'might be posting to ', full_resource_name, ' info ', json.dumps(msg_dic)
            if len(res_dic) > 0: 
                if not lArcusStyle:
                    r  = requests.post(full_resource_name, data = json.dumps(msg_dic), verify=False)
                else:
                    r  = requests.post(full_resource_name, data = msg_dic, verify=False)
                print (r.text, r.status_code)
        
        except Exception as e:
            print str(e)
        time.sleep(DelayTime)

    dispatch_info.deattach()

