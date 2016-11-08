import time
import struct
import cabmsg
import os
import msgconf
import sysv_ipc


class VehicleParams(object): 


    def __init__(self, vehicle_dic=None):
        self.taxi_no = -1

        try:

            #return self.init_object()

            if vehicle_dic is not None and isinstance(vehicle_dic, dict):
                try:
                    self.taxi_no = int(vehicle_dic["vehicle_number"])
                except Exception as e:
                    pass 
                self.sys_ftypes = 0
                self.usr_ftypes = 0
                self.dtypes = 0
                self.vtypes = 0
                try:
                    self.fleet = int(vehicle_dic["fleet"])
                except Exception as e:
                    self.fleet = 0
                self.vehicle_type = 0    
                try:  
                    self.baseunit = int(vehicle_dic["baseunit"])
                except Exception as e:
                    self.baseunit = 0     
             
                self.from_zone = 32*[0]
                if vehicle_dic.has_key("from_zone"):
                    for k in range(len(vehicle_dic["from_zone"])):
                        self.from_zone[k] = vehicle_dic["from_zone"][k]

                #print 'from_zone ' , self.from_zone

                # default 
                self.to_zone = 32*[0]
                if vehicle_dic.has_key("to_zone"):
                    for k in range(len(vehicle_dic["to_zone"])):
                        self.to_zone[k] = vehicle_dic["to_zone"][k]

                #print 'to_zone ' , self.to_zone
                try:
                    self.training = int(vehicle_dic["training"])
                except Exception as e:
                    self.training = 0
                try:
                    self.max_passengers = vehicle_dic["maximum_passengers"]
                except Exception as e:
                    self.max_passengers = 0
                self.sspare = 0 
                # term type?

                try:
                    self.fleet_name = vehicle_dic["fleet_name"].encode('utf8') if isinstance(vehicle_dic["fleet_name"], unicode) else vehicle_dic["fleet_name"]
                except Exception as e:
                    self.fleet_name = '\0'
                self.alias = '\0'
                try:
                    self.alias = vehicle_dic["alias"].encode('utf8') if isinstance(vehicle_dic["alias"], unicode) else vehicle_dic["alias"]
                except Exception as e:
                    self.alias = '\0'
        
                try:
                    self.voice = vehicle_dic["voice"]
                except Exception as e:
                    self.voice = 'N'
                try:
                    self.sale = vehicle_dic["sale"]
                except Exception as e:
                    self.sale = 'N'

                # alternate_fleet
                self.alternate_fleet = 10*[0]
                if vehicle_dic.has_key("alternate_fleet"):
                    for k in range(len(vehicle_dic["alternate_fleet"])):
                        try:
                            if k < 10:
                                self.alternate_fleet[k] = int(vehicle_dic["alternate_fleet"][k])
                        except Exception as e:
                            continue

                self.drivers = 10*[0]
                if vehicle_dic.has_key("drivers"):
                    for k in range(len(vehicle_dic["drivers"])):
                        try:
                            if k < 10:
                                self.drivers[k] = long(vehicle_dic["drivers"][k])
                        except Exception as e:
                            continue 
        
                try:
                    self.cur_driver = int(vehicle_dic["cur_driver"])
                except Exception as e:
                    self.cur_driver = 0
           
                self.veh_class_32 = 0
                if vehicle_dic.has_key("veh_class_32"):
                    for i in vehicle_dic["veh_class_32"]:
                        try:
                            print i, int(i), self.veh_class_32
                            itype = int(i)
                            if itype in range(32):
                                self.veh_class_32 = self.veh_class_32 + (1 << itype)
                        except Exception as e:
                            pass

                self.disallowedchannels = ""
           
                temp = 16*['N'] 
                if vehicle_dic.has_key('disallowedchannels'):
                    for i in vehicle_dic["disallowedchannels"]:
                        try:
                            ic = int(i)
                            if ic in range(16):
                                temp[ic] = 'Y' 
                        except Exception as e:  
                            pass
            
                for c in temp:
                    self.disallowedchannels = self.disallowedchannels + c 
        
                self.baseunit = 0
                cnt = 0
                for c in temp:
                    if c == 'N':
                        break
                    cnt = cnt + 1
                self.baseunit = cnt
                print 'base unit ', self.baseunit
                    
                self.VDM_MDTControlEnabled = 'N' 
                try:
                    self.VDM_MDTControlEnabled = vehicle_dic['VDM_MDTControlEnabled']
                except Exception as e:
                    pass
        
                self.RearSeatVivotechEnabled = 'N'
                try:
                    self.RearSeatVivotechEnabled = vehicle_dic['RearSeatVivotechEnabled']
                except Exception as e:
                    pass
        
                self.VDM_MDTControl = 0
                try:
                    self.VDM_MDTControl = vehicle_dic["VDM_MDTControl"]
                except Exception as e:
                    pass
            
                #'license_expiry_date': 1577854
                #self.expiryTime,               # expiryTime
                self.expiryTime = 0
                try:
                    self.expiryTime = vehicle_dic["license_expiry_date"]
                except Exception as e:
                    pass
                self.spare = 28*' '
        
                self.new_alias = '\0'
                try:
                    self.new_alias = vehicle_dic["long_alias"].encode('utf8') if isinstance(vehicle_dic["long_alias"], unicode) else vehicle_dic["long_alias"]
                except Exception as e:
                    self.new_alias = '\0'
                #self.new_alias  'long_alias':
                #'mobile_phone': '22222222\x00', 'cur_driver': 0, 'phone': '11111111\x00
                self.phone = '\0'
                try:
                    self.phone = vehicle_dic["phone"]
                except Exception as e:
                    self.phone = '\0'

                self.mobile_phone = '\0'
                try:
                    self.mobile_phone = vehicle_dic["mobile_phone"]
                except Exception as e:
                    self.mobile_phone = '\0'
            else:
                self.init_object()
                return

        except Exception as e:
            print ' Exception in init object ', str(e)

    def init_object(self):
        self.new_alias = '\0'
        self.mobile_phone = '\0'
        self.taxi_no = -1

        self.sys_ftypes = 0
        self.usr_ftypes = 0     # fdv_types: usr_ftypes user defined fare types
        self.dtypes = 0         # fdv_types: dtypes_32 user defined driver types
        self.vtypes = 0         # fdv_types: vtypes user defined vehicle types
        self.taxi_no = 0        # taxi_number
        self.fleet = 0          # fleet
        self.vehicle_type = 0   # vehicle_type
        self.baseunit = 0 
        self.from_zone = 32*[0]        # baseunit
           
        self.to_zone = 32*[0]   

        self.training = 0              # training: is this taxi working the training system?
        self.max_passengers = 0       # max_passengers
        self.sspare = 0               # sspare
        self.comp_num = 0             # comp_num
        self.termtype = 0             # termtype: MDT3602 = '0', MDT4021 = '1'
        self.termrev =  4*[0]         # termrev[4]: not used in 4.3
        self.fleet_name = 24*[0]      # fleet_name[24]
        self.alias =  4*[0]           # alias[4]
        self.voice = 0                # voice
        self.sale = 0                  # sale
        self.cspare =  2*[0]           # cspare[2]

        self.alternate_fleet = 32 *[0]    
        self.drivers = 32*[0]   
        
        self.cur_drive = 0                           # cur_driver
        self.veh_class_32 = 0                          # self.veh_class_32,          # veh_class_32
        self.disallowedchannels =  16*[0]      # disallowedchannels[16]
        self.VDM_MDTControlEnabled = 0                        # self.VDM_MDTControlEnabled
        self.RearSeatVivotechEnabled = 0  # RearSeatVivotechEnabled
        self.cspare =  2*[0]             # CSpare[2]
        self.VDM_MDTControl = 0           # VDM_MDTControl
        self.expiryTime = 0
         
        self.phone = '\0'


    def vehicle_info_to_tuple(self):
        if len(self.alias) > 4: 
            self.alias = self.alias[:4]
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
         'SS',                          # CSpare[2]
          0,           # VDM_MDTControl
         self.expiryTime,               # expiryTime
         "0123456789012345678901234567")
        values2 = (
            self.taxi_no,
            self.new_alias, 
            self.phone, 
            self.mobile_phone
        )
        print 'values1 ', values1
        print 'values2 ', values2
        return (values1, values2) 
    

    def vehicle_add_cmt(self, dData, dData0): 
        ss = struct.Struct('5I 4c 320s')
        s = struct.Struct('4I 71h 2c 4s 24s 4s 2c 2s 10h 12I 16s 2c 2s 2I 28s')   # taxi info data
        packed_data = s.pack( *dData)
        data_size = s.size
        cabmsg.gmsg_send(packed_data, data_size, msgconf.TFC, 0, msgconf.MT_ADD_TAXI, ss)

        ss0 = struct.Struct('5I 4c 51s')   #  packet 1

        s0 = struct.Struct('h 9s 20s 20s')   # extended taxi info data
        packed_data0 = s0.pack( *dData0)
        data_size0 = s0.size
        cabmsg.gmsg_send(packed_data0, data_size0, msgconf.TFC, 0, msgconf.MT_EXTENDED_TAXI_INFO, ss0)
        return 

    def vehicle_modify_cmt(self, dData, dData0):
        #ss = struct.Struct('5I 4c 320s')
        s = struct.Struct('4I 71h 2c 4s 24s 4s 2c 2s 10h 12I 16s 2c 2s 2I 28s')   # taxi info data
        packed_data = s.pack( *dData)
        data_size = s.size
        ss = struct.Struct(cabmsg.base_fmt + '%ds' % (s.size))  
        cabmsg.gmsg_send(packed_data, data_size, msgcof.TFC, 0, msgconf.MT_MODTAXINFO, ss)

        #ss0 = struct.Struct('5I 4c 51s')   #  packet 1

        s = struct.Struct('h 9s 20s 20s')   # extended taxi info data
        packed_data0 = s.pack( *dData0)
        data_size = s.size
        ss = struct.Struct(cabmsg.base_fmt + '%ds' % (s.size))  
        cabmsg.gmsg_send(packed_data, data_size, msgconf.TFC, 0, msgconf.MT_EXTENDED_TAXI_INFO, ss)
        return

    def vehicle_info_to_struct(self):
        frmt = '4I 71h 2c 4s 24s 4s 2c 2s 10h 12I 16s 2c 2s 2I 28s'
        s = struct.Struct(frmt)
        dData, dDataE = self.vehicle_info_to_tuple()
        print 'vehicle data: ', dData
        print 'vehicle extended data: ', dDataE  
        packed_data = s.pack(*dData)
        data_size = s.size
        print 'data packed ... ' 
        sE = struct.Struct("h 9s 20s 20s")   # extended taxi info data
        packed_dataE = sE.pack( *dDataE)
        data_sizeE = sE.size
        print 'returning packed stuff' 
        return (packed_data, data_size, packed_dataE, data_sizeE)

    def add_modify_vehicle(self, action):
        try:
            
            if self.taxi_no > -1:
                print 'taxi_no ', self.taxi_no, 'copying to sturct '  
                packed_data, data_size, packed_dataE, data_sizeE = self.vehicle_info_to_struct()
                print 'data_size ', data_size, ' data_sizeE ', data_sizeE
                ss = struct.Struct('I I I I I c c c c 208s')
                print 'add_modify_vehicle action ', action, ' code ', msgconf.vehicle_msg[action]     
                packed_msg = ss.pack(msgconf.CWEBS,
                                 msgconf.TFC,
                                 0,
                                 msgconf.vehicle_msg[action],   
                                 data_size,
                                 '0',
                                 '0',
                                 '1',
                                 'a',
                                 packed_data)
                print 'first message ... is prepared...'
                ssE = struct.Struct('5I 4c 51s')
                packed_msgE = ss.pack(msgconf.CWEBS,
                                 msgconf.TFC,
                                 0,
                                 msgconf.MT_EXTENDED_TAXI_INFO,
                                 data_sizeE,
                                 '0',
                                 '0',
                                 '1',
                                 'a',
                                 packed_dataE)
                print 'second message ... is prepared...'
                print 'msgconf.MT_EXTENDED_TAXI_INFO ', msgconf.MT_EXTENDED_TAXI_INFO
                mq = sysv_ipc.MessageQueue(msgconf.TFC, flags=sysv_ipc.IPC_CREAT, mode=0666, max_message_size = 8064)
                try:
                    print 'sending 1st message'
                    mq.send(packed_msg, block=False, type=msgconf.ROUT_PRI)
                #except sysv_ipc.BusyError:
                except Exception as e:
                    #print "Queue is full"
                    print str(e)
                print '1st message - done'
                
                try:
                    print 'sending 2nd message'
                    mq.send(packed_msgE, block=False, type=msgconf.ROUT_PRI) 
                #except sysv_ipc.BusyError:
                except Exception as e:
                    print str(e)
                #mq.remove()
                print '2nd message - done'
            else:
                print 'invalid vehicle'
        except Exception as e:
            print 'exception is raised in add_modify_vehicle', str(e)
            return


    def delete_vehicle(self, taxi_no):
        try:
            if taxi_no > -1:
                driver_id = 0
                fleet = 0 
                dData = (driver_id, taxi_no, fleet)
                s = struct.Struct('2I h')  # tif index data
                packed_data = s.pack(*dData)
                data_size = s.size
   
                ss = struct.Struct('I I I I I c c c c 10s')
                packed_msg = ss.pack(msgconf.CWEBS,
                    msgconf.TFC,
                    0,
                    msgconf.MT_DELETE_TAXI,
                    data_size,
                    '0',
                    '0',
                    '1',
                    'a',
                    packed_data)
                mq = sysv_ipc.MessageQueue(msgconf.TFC, flags=sysv_ipc.IPC_CREAT, mode=0666, max_message_size = 8064)
                try:
                    mq.send(packed_msg, block=False, type=msgconf.ROUT_PRI)
                except sysv_ipc.BusyError:
                    print "Queue is full - will not send"
                #mq.remove()   
        except ValueError:
            pass


    def read_taxirec(self, taxinum):

        bError = False
        taxifile = "/data/taxirecs.fl"

    
        taxirec_fmts =  [ 
            '8I 2f',
            '540c',
            '9I 10h 12c',
            #'4I 1h 1h 300c', # == taxi info struct =320 bytes (320c)
            '4I 1h 1h 1h 1h 32h 32h 1h 1h 1h 2c 4s 24s 4s 2c 2s 10h 10I 1I 1I 16s 2c 2s 2I 28s', ## # == taxi info struct =320 bytes (320c)
            '24s 2I 2h 4I 2h 1I 1h 2c',
            '1h 2c 64I',
            '3I 33s 33s 2s 3I 16I 4c 1I 4h 1I',
            '1h 9c 18s 4s 1c 9s 20s 277c '
            '5I 1I 2c 1h 2f 2I 2c 1h 5f 2c 1h 4I 1c 20s 1c 130s'
            ]
    
        rec_fmt = ''.join(taxirec_fmts)
        rec_size = struct.Struct(rec_fmt).size

        bError = False
        try:
            with open(taxifile, "rb") as f:
                count = 0
                bRun=True
                while bRun:  
                    count = count + 1
                    data = f.read(rec_size)
             
                    if not data:
                        bError=True
                        fp.close()
                        break 
                    else:
                        if (len(data) == rec_size):
                            udata = struct.Struct(rec_fmt).unpack(data)
             
                            tis_start = 581
                            taxi_number_offset = 4
                            fleetname_offset = 4 + 71 + 2 + 1
                            alias_offset =  fleetname_offset  + 1
                            alternate_offset = alias_offset  + 4
                            driver_offset = alternate_offset + 10
                            curdrv_offset = driver_offset + 10

                            if  udata[tis_start + taxi_number_offset ] == taxinum:
                                print ' Found it ==> taxi#[%d] fleet#[%d] fleetname=[%s] alias[%s] curdrv [%d] \n' \
                                            % ( udata[585]  \
                                                , udata[586] \
                                                , udata[tis_start+fleetname_offset] \
                                                , udata[tis_start+alias_offset] \
                                                , udata[tis_start+curdrv_offset ] \
                                                )                     
                                for i in range(10):
                                    print 'alternate fleet %d ' % (udata[tis_start+alternate_offset + i])
                                for i in range(10):
                                    print 'drivers %d ' % (udata[tis_start+driver_offset + i])   

                                bRun=False                                                     

                        else:
                            bRun=False

        except Exception as e:
            bError = True
            print 'exception ', e

   
        return bError


if __name__ == "__main__":
    try:
        print 'test: do nothing'
        mytaxi = 9006
        dic = {}
        myTaxiRec = VehicleParams(dic)
        myTaxiRec.read_taxirec(mytaxi)

    except Exception as e:
        print 'Exception in main ', str(e)
