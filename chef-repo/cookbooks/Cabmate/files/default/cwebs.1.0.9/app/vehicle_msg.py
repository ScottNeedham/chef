   
import sys
import time
import struct

import sysv_ipc
import msgconf
import datetime
import smalldb

import config.cwebsconf as Config

import format_field
from bottle import  request, response
import json


from itertools import chain


MAX_NUM_ENTRIES = 4
MAX_ENTRY_LEN   = 33


class PrintableList(list): # for a list of dicts
    def __str__(self):
        return '. '.join(' '.join(str(x) for x in
            chain.from_iterable(zip((item[0], 'is', 'and'), item[1])))
                for item in (item.items()[0] for item in self)) + '.'

class PrintableDict(dict): # for a dict
    def __str__(self):
        return '. '.join(' '.join(str(x) for x in
            chain.from_iterable(zip((item[0], 'is', 'and'), item[1])))
                for item in self.iteritems()) + '.'



class VehicleMessage():

    def __init__(self, dic, msgid):

        try:
            #sys.stdout.write("%s: entering %s\n" % (datetime.datetime.strftime(datetime.datetime.now(),  '%Y-%m-%d %H:%M:%S'), ' __init__' ))
           
            self.error = False
            self.operator_id =  msgconf.CWEBS  
            self.operator_name =  "CWEBS"
            self.driver_name =  ""
            self.farenumber = 0
            self.fleet = -1
            self.zone = -1

            if msgid in ( msgconf.VEHICLE_MSG, msgconf.DRIVER_MSG):
                self.event_no = msgconf.EV_VEHICLE_MSG  
            elif msgid == msgconf.FLEET_MSG:
                self.event_no = msgconf.EV_FLEET_MSG  

            else:
                 self.error=True
                 print "Issue with msgid ",  msgid , "while creating VehicleMessage "

            self.time =  int(time.time())          
            self.fare = 0              
            self.other_data = 0        
            self.qual = 0              
            self.fstatus = 0
            self.meter_amount = 0    
            self.longpad = 0          
            self.x = 0.0          
            self.y = 0.0          
            self.zone = 0         
            self.taxi = 0     
            self.resp_uid = msgconf.CWEBS     
            self.attribute = 0     
            self.qid  = 0            
            self.fleet = 0           
            self.redisp_taxi = 0     
            self.merchant_group = '0'   
            self.num_sats = '0'  

            self.mesg = []
            
            for i in range(MAX_NUM_ENTRIES):
                self.mesg.append(MAX_ENTRY_LEN*' ')
                
            self.rel_queue  = ' '      
            self.statusbits = ' '

            self.populateObject(dic)

        except Exception as e:
            self.error=True
            print "Issue creating VehicleMessage object", e
     

    def __str__(self):
        return  
        {
            'event_no' :  self.event_no,
            'operator_id' : self.operator_id ,
            'operator_name' : self.operator_name,
            'driver_id' : self.driver_id,            
            'driver_name ' : self.driver_name,
            'fleet' : self.fleet,
            'taxi' : self.taxi,
            'msg':  '\n'.join(self.mesg)


        }


    def populateObject(self, dic):

        try:
            #sys.stdout.write("%s: entering %s\n" % (datetime.datetime.strftime(datetime.datetime.now(),  '%Y-%m-%d %H:%M:%S'), 'populateObject' ))
            if dic:
                if "zone" in dic:
                    self.zone = dic["zone"]
                if "fleet" in dic:
                    self.fleet = dic["fleet"]
                if "driver_id" in dic:
                    self.driver_id = dic["driver_id"]
                if "duration" in dic:
                    self.duration = dic["duration"]
                if "taxi" in dic:
                    self.taxi = dic["taxi"]
               
                if "operator_id" in dic:
                    self.operator_id = dic["operator_id"]

                if "farenumber" in dic:
                    self.farenumber = dic["farenumber"] 
                if "driver_name" in dic:
                    self.driver_name =  dic["driver_name"] 
                if "operator_name" in dic:
                    self.operator_name = dic["operator_name"]

                
                if dic.has_key("mesg"):
                    if len(dic["mesg"]) > 0:
                        for m , i in zip(dic["mesg"], range(len(dic["mesg"])) ):
                            if len(m) >MAX_ENTRY_LEN:
                                m = m[:MAX_ENTRY_LEN]
                            self.mesg[i] = format_field.format_field(m, MAX_ENTRY_LEN, True)
                                      

        except Exception as e:
            print "Issue decoding data dict", e(str)
            sys.stdout.write("%s: %s exception=%s\n" % (datetime.datetime.strftime(datetime.datetime.now(),  '%Y-%m-%d %H:%M:%S'), 'populateObject' , str(e) ))

  


    def send_driver_msg(self, dic=None):
        
        sys.stdout.write("%s: entering %s\n" % (datetime.datetime.strftime(datetime.datetime.now(),  '%Y-%m-%d %H:%M:%S'), ' send_driver_msg' ))

        response.status = 200
        res = {"status": response.status, "result": {"message": "OK"}}

        try:

            self.populateObject(dic)

        except Exception as e:
            
            print "Issue decoding data dict", e
            sys.stdout.write("%s: entering %s\n" % (datetime.datetime.strftime(datetime.datetime.now(),  '%Y-%m-%d %H:%M:%S'), str(e) ))

            response.status = 500
            res = {"status": response.status, "result": {"message": "Issue decoding data dict"}}
            return json.dumps(res)

        try:
            data = (
                    self.event_no, 
                    self.time, 
                    self.fare, 
                    self.other_data,
                    self.qual, 
                    self.fstatus, 
                    self.meter_amount, 
                    self.longpad,
                    self.x, 
                    self.y, 
                    self.zone, 
                    self.taxi, 
                    self.resp_uid, 
                    self.attribute,
                    self.qid, 
                    self.fleet, 
                    self.redisp_taxi,  
                    self.merchant_group, 
                    self.num_sats,
                    ''.join(self.mesg),
                    self.rel_queue, 
                    self.statusbits)
            print 'Preparing data ', data           

        except Exception as e:
            sys.stdout.write("%s:  Issue building data structure" % (datetime.datetime.strftime(datetime.datetime.now(),  '%Y-%m-%d %H:%M:%S'), str(e) ))

            response.status = 500
            res = {"status": response.status, "result": {"message": "Issue building data structure"}}
            sys.stdout.write("%s: entering %s\n" % (datetime.datetime.strftime(datetime.datetime.now(),  '%Y-%m-%d %H:%M:%S'), str(e) ))
            return json.dumps(res)

        try:
            #  size is 192 bytes       
            #  s0  = struct.Struct('8I 2f 7h c c 33s 33s 33s 33s c c') 
            s0  = struct.Struct('8I 2f 7h c c 132s c c') 

            packed_data0 = s0.pack( *data)
            data_size0 = s0.size
            print 'data size ', data_size0
            ss = struct.Struct('I I I I I c c c c 192s')   #  packet
            # Build msg to be sent.
            msg = (msgconf.CWEBS,           #  msg.msg_struct.ms_srcuid
                msgconf.DM,                  #  msg.msg_struct.ms_dstuid
                0,                           #  msg.msg_struct.ms_scnduid
                msgconf.MT_EVENT_MSG,        #  msg.msg_struct.ms_msgtype
                data_size0,                  #  msg.msg_struct.ms_datasize
                '0',                          #  msg.msg_struct.ms_srcmch
                '0',                          #  msg.msg_struct.ms_dstmch
                '1',                          #  msg.msg_struct.ms_priority
                'a',                          #  msg.msg_struct.ms_reserved
                packed_data0)                 #  msg.msg_struct.ms_msgdata
            packed_msg = ss.pack(*msg)

        except Exception as e:
            sys.stdout.write("%s: Issue with data " % (datetime.datetime.strftime(datetime.datetime.now(),  '%Y-%m-%d %H:%M:%S'), str(e) ))
            response.status = 500
            res = {"status": response.status, "result": {"message": "Issue with data"}}
            return json.dumps(res)
            
  
        mq = sysv_ipc.MessageQueue(msgconf.DM, flags=sysv_ipc.IPC_CREAT, mode=0666, max_message_size = 8064)

        try:
            mq.send(packed_msg, block=False, type=msgconf.ROUT_PRI)

        except sysv_ipc.BusyError:
            sys.stdout.write("%s: Queue is full on send " % (datetime.datetime.strftime(datetime.datetime.now(),  '%Y-%m-%d %H:%M:%S'), str(e) ))

        #mq.remove()
        #time.sleep(1)  
      
        sys.stdout.write("%s: exiting %s\n" % (datetime.datetime.strftime(datetime.datetime.now(),  '%Y-%m-%d %H:%M:%S'), ' send_driver_msg' ))
        return json.dumps(res)

    def getError(self):
        return self.error



    def createLogEntry(self, dic):
    
        sys.stdout.write("%s: entering %s\n" % (datetime.datetime.strftime(datetime.datetime.now(),  '%Y-%m-%d %H:%M:%S'), __name__))
   
        try:

            #Default some of the keys:
            if "driver_id" not in dic:
                dic["driver_id"] = -1
            if "fleet" not in dic:
                dic["fleet"]  = -1
            if "taxi" not in dic:
                dic["taxi"] = -1

            if 'date' not in dic:
                dic['date'] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

            #Logs schema
            data_logs_src = smalldb.DB(Config.DB_LOGS_HOST, Config.DB_LOGS_USER, Config.DB_LOGS_PASSWORD, Config.DB_LOGS_NAME)
            data_logs_src.connect()
           
            sql_stat = '''
                INSERT INTO messages
                (
                    fromuser,
                    touser,
                    date,
                    fleet,
                    vehicle,
                    message,
                    fromname,
                    toname
                )
                VALUES (
                %u,
                %u,
                \'%s\',
                %u,
                %u,
                \'%s\',
                \'%s\',
                \'%s\'
                );
                ''' % ( 
                    dic["operator_id"] ,
                    dic["driver_id"] ,
                    dic["date"] , 
                    dic["fleet"],                 
                    dic["taxi"] ,
                   ''.join(self.mesg),
                   self.operator_name,
                   self.driver_name
                )

            sys.stdout.write("%s: %s Execution ... %s\n" % (datetime.datetime.strftime(datetime.datetime.now(),  '%Y-%m-%d %H:%M:%S'), __name__, sql_stat))

            info =  data_logs_src.insert_update(sql_stat)
    
        except Exception as e:
            sys.stdout.write("%s: createLogEntry exception %s \n" % (datetime.datetime.strftime(datetime.datetime.now(),  '%Y-%m-%d %H:%M:%S'), e ))
        
            pass

        data_logs_src.close() 
    

    def findVehicle(self, driver_id):
        try:
           
            res_dic = {"vehicle_number": -1, "long_alias": "", "alias": "",  "count": 0, "fleet": 0}

            data_src = smalldb.DB(Config.DB_HOST, Config.DB_USER, Config.DB_PASSWORD, 'cabmate')
            data_src.connect()
           
            sql_stat = ''' SELECT currentVehicle FROM cabmate.driver where drivernumber = %s ORDER by LastUpdate desc ''' % (driver_id)

            sys.stdout.write("%s: %s Execution ...  %s \n" % (datetime.datetime.strftime(datetime.datetime.now(),  '%Y-%m-%d %H:%M:%S'),  __name__, sql_stat))

            info = data_src.fetch_many(sql_stat)
            count = 0
            if len(info) > 0:
                for (vehicle) in info:
                    if len(vehicle) > 0 and vehicle > 0:
                        res_dic["vehicle_number"] = vehicle[0]
                print json.dumps(res_dic)
                return res_dic


        except Exception as e:
            sys.stdout.write("%s:  findVehicle exception %s \n" % (datetime.datetime.strftime(datetime.datetime.now(),  '%Y-%m-%d %H:%M:%S'), str(e)  ))

    def taxirec(self):

        try:
            taxifile = "/data/taxirecs.fl"

            fp = open(taxifile, "r")
            data1 = fp.read()
            fp.close()

            print 'length of full data is ', len(data1), 
            #frmt = '4I 71h 2c 4s 24s 4s 2c 2s 10h 12I 16s 2c 2s 2I 28s'
            frmt = '8I 2f 540c 9I 10s 12c 4I 71h 2c 4s 24s 4s 2c 2s 10h 12I 16s 2c 2s 2I 28s 24c 2I 2h 4I 2h 1I 1h 2c 64I 3I 33s 33s 2s 3I 16I 4c 1I 4h  1I  2h 8c 18s 4s 1c 9s 20s 277c 5I 1I 2c 1h 2f 2I 2c 1h 5f 2c 1h 4I 1c 20s 1c 130s'
            print frmt
            data_size1 = struct.Struct(frmt).size
            s = struct.Struct(frmt)
            print 'data structure size ', data_size1
    
            
            with open(taxifile, "rb") as f:
                count = 0
                bRun=True
                while bRun:  
                    count = count + 1
                    data = f.read(data_size1)
             
                    if not data:
                        break 
                    else:
                        if (len(data) == data_size1):
                            udata = s.unpack(data)
                            if count == 1:
                                print 'len data tuple=', len(udata)
                            if 'PVFLEET_2' in udata:
                                print count, udata[500:700]
                            if 'NEWYORK' in udata:
                                print count, udata[500:700]
                            if count == 317:
                                print ' data tuple=', udata

                            #if udata[8] == 9006:
                            #    for i in range(len(udata)):#

                            #        print ' udata[', i, ']= ', udata[i]
                                
                            #    bRun=False
                        else:
                            bRun=False

        except Exception as e:
            print 'exception ', e

    '''
    def taxi_info_to_struct(self):
        frmt = '4I 71h 2c 4s 24s 4s 2c 2s 10h 12I 16s 2c 2s 2I 28s'
        taxistruct= struct.Struct(frmt)
        taxiData = self.vehicle_info_to_tuple()
        print 'taxi data: ', taxiData
        packed_data = taxistruct.pack(*taxiData)
        data_size = taxistruct.size
        print 'returning packed taxi' 
        return (packed_data)


    def vehicle_info_to_tuple(self):
        
        values1 = (         
         self.sys_ftypes, #0x00000080,# fdv_types: sys_ftypes system defines fare types
         self.usr_ftypes, #0, # fdv_types: usr_ftypes user defined fare types
         self.dtypes,     # fdv_types: dtypes_32 user defined driver types
         self.vtypes,     # fdv_types: vtypes user defined vehicle types
         self.taxi_no,     # taxi_number
         self.fleet,       # fleet
         self.vehicle_type,     # vehicle_type
         self.baseunit,         # baseunit
         self.from_zone[0],           # from_zone0
         self.from_zone[1],           # from_zone1
         self.from_zone[2],           # from_zone2
         self.from_zone[3],           # from_zone3
         self.from_zone[4],           # from_zone4
         self.from_zone[5],           # from_zone5
         self.from_zone[6],           # from_zone6
         self.from_zone[7],           # from_zone7
         self.from_zone[8],           # from_zone8
         self.from_zone[9],           # from_zone9
         self.from_zone[10],           # from_zone10
         self.from_zone[11],           # from_zone11
         self.from_zone[12],           # from_zone12
         self.from_zone[13],           # from_zone13
         self.from_zone[14],           # from_zone14
         self.from_zone[15],           # from_zone15
         self.from_zone[16],           # from_zone16
         self.from_zone[17],           # from_zone17
         self.from_zone[18],           # from_zone18
         self.from_zone[19],           # from_zone19
         self.from_zone[20],           # from_zone20
         self.from_zone[21],           # from_zone21
         self.from_zone[22],           # from_zone22
         self.from_zone[23],           # from_zone23
         self.from_zone[24],           # from_zone24
         self.from_zone[25],           # from_zone25
         self.from_zone[26],           # from_zone26
         self.from_zone[27],           # from_zone27
         self.from_zone[28],           # from_zone28
         self.from_zone[29],           # from_zone29
         self.from_zone[30],           # from_zone30
         self.from_zone[31],           # from_zone31
         self.to_zone[0],            # to_zone0
         self.to_zone[1],            # to_zone1
         self.to_zone[2],            # to_zone2
         self.to_zone[3],            # to_zone3
         self.to_zone[4],            # to_zone4
         self.to_zone[5],            # to_zone5
         self.to_zone[6],            # to_zone6
         self.to_zone[7],            # to_zone7
         self.to_zone[8],            # to_zone8
         self.to_zone[9],            # to_zone9
         self.to_zone[10],           # to_zone10
         self.to_zone[11],           # to_zone11
         self.to_zone[12],           # to_zone12
         self.to_zone[13],           # to_zone13
         self.to_zone[14],           # to_zone14
         self.to_zone[15],           # to_zone15
         self.to_zone[16],           # to_zone16
         self.to_zone[17],           # to_zone17
         self.to_zone[18],           # to_zone18
         self.to_zone[19],           # to_zone19
         self.to_zone[20],           # to_zone20
         self.to_zone[21],           # to_zone21
         self.to_zone[22],           # to_zone22
         self.to_zone[23],           # to_zone23
         self.to_zone[24],           # to_zone24
         self.to_zone[25],           # to_zone25
         self.to_zone[26],           # to_zone26
         self.to_zone[27],           # to_zone27
         self.to_zone[28],           # to_zone28
         self.to_zone[29],           # to_zone29
         self.to_zone[30],           # to_zone30
         self.to_zone[31],           # to_zone31
         self.training,              # training: is this taxi working the training system?
         self.max_passengers,        # max_passengers
         self.sspare,                # sspare
         '0',                        # comp_num
         '1',                        # termtype: MDT3602 = '0', MDT4021 = '1'
         '0',                        # termrev[4]: not used in 4.3
         self.fleet_name,            # fleet_name[24]
         self.alias,             # alias[4]
         '\0',                          # voice
         self.sale,                  # sale
         'SS',                       # cspare[2]
         self.alternate_fleet[0],    # alternate_fleet0
         self.alternate_fleet[1],    # alternate_fleet1
         self.alternate_fleet[2],    # alternate_fleet2
         self.alternate_fleet[3],    # alternate_fleet3
         self.alternate_fleet[4],    # alternate_fleet4
         self.alternate_fleet[5],    # alternate_fleet5
         self.alternate_fleet[6],    # alternate_fleet6
         self.alternate_fleet[7],    # alternate_fleet7
         self.alternate_fleet[8],    # alternate_fleet8
         self.alternate_fleet[9],    # alternate_fleet9
         self.drivers[0],            # drivers0
         self.drivers[1],            # drivers1
         self.drivers[2],            # drivers2
         self.drivers[3],            # drivers3
         self.drivers[4],            # drivers4
         self.drivers[5],            # drivers5
         self.drivers[6],            # drivers6
         self.drivers[7],            # drivers7
         self.drivers[8],            # drivers8
         self.drivers[9],            # drivers9
         0,                          # cur_driver
         self.veh_class_32,                          # self.veh_class_32,          # veh_class_32
         self.disallowedchannels,    # disallowedchannels[16]
         self.VDM_MDTControlEnabled,                        # self.VDM_MDTControlEnabled
         self.RearSeatVivotechEnabled,  # RearSeatVivotechEnabled
         cspare,
         VDM_MDTControl,                    
         expiryTime,                   
         DynamoDBalias,                 
         Spare[11]  
         )                       
       
      
        
        return (values1) 


    '''

if __name__ == "__main__":

    import requests
    driver = 8089
    taxi = 8089
    
    data_dic={}
    
    data_dic["fleet"] = 2
    data_dic["taxi"] = driver 
    data_dic["zone"] = 101
    data_dic["driver_id"] = taxi
    
    data_dic["date"] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    data_dic["operator_id"] = 1001
    data_dic["farenumber"] = 233
    data_dic["driver_name"] = "MALCOLM X"
    data_dic["operator_name"] = "CHE GUEVARA"

    data_dic["mesg"] = ['FLEET MESSAGE FROM CWEBS' ,  'CWEBS 8089 22222' ,  'CWEBS 8089 333333' ,  'CWEBS 4444444444444' ]


    #vehmsg = VehicleMessage(data_dic, msgconf.VEHICLE_MSG)

    vehmsg = VehicleMessage(data_dic, msgconf.FLEET_MSG)

   
    try:
        if vehmsg.getError() == False:
            print 'sending a request to vehicle ', taxi
            #r =   vehmsg.send_driver_msg(data_dic, 1) 
            r = requests.post(full_resource_name, data = json.dumps(data_dic), headers=headers)
            print 'done...'
            #print 'status code ', r.status_code
            #print 'url ', r.url
            #print 'text ', r.text
        else:
            print  'Error with object ...'

        #msg.createLogEntry(data_dic)


    except Exception as e:
        print 'Exception in main', str(e)

    

    
