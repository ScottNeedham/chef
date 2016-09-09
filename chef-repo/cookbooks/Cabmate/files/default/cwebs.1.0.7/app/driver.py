import time
import struct
import cabmsg
import os
import msgconf
import sysv_ipc

class DriverParams(object): 


    def __init__(self, driver_dic, action):
        self.DriverNum = -1

        try:
            self.DriverNum = int(driver_dic["DriverNum"])
        except (KeyError, ValueError):
            pass        
        ###########################################
        #now_time = long(time.time())
        #start_time = stop_time = now_time
        #taxi = valid taxi number
        ###########################################
        try:
            self.start_time = int(driver_dic["start_time"])
        except Exception as e:
            self.start_time = -1
        try:
            self.stop_time = int(driver_dic["stop_time"])
        except Exception as e:
            self.stop_time = -1
        self.taxi_no = 0 
        self.fleets = 10*[0] 
        
        self.num_fleets = 0  
        if driver_dic.has_key("valid_fleets"):
            for fleet in driver_dic["valid_fleets"]:
                try:
                    if self.num_fleets < 10:
                        self.fleets[self.num_fleets] = int(fleet)
                        self.num_fleets = self.num_fleets + 1   
                except Exception as e:
                    continue
        
        self.taxis = 10*[0]

        if driver_dic.has_key("taxis"):
            for taxi, itaxi in zip(driver_dic["taxis"], range(len(driver_dic["taxis"]))):
                try:
                    if itaxi < 10:
                        self.taxis[itaxi] = int(taxi) 
                except Exception as e:
                    continue

        self.disable_driver = 'N'   
        try:
            if driver_dic["disable_driver"] == 'Y':
                self.disable_driver = str(driver_dic["disable_driver"])
        except Exception as e:
            self.disable_driver = 'N'
        
        if action == "add":
            self.modified = 'N'
            print 'action ', action, ' modified ', self.modified
        elif action in ["update", "modify"]:
            self.modified = 'Y'
            print 'action ', action, ' modified ', self.modified
        else:
            raise Exception("invalid action")
            
        
        try:
            self.acct_disabled = driver_dic["acct_disabled"]
        except Exception as e:
            self.acct_disabled = 'N' 

        self.acct_info_num = 0
        self.acct_info_mod = 'N'
        self.acct_info = 16*['\0 ', 0]

        if driver_dic.has_key("disabled_accounts"):
            i = 0  
            for t in driver_dic["disabled_accounts"]:
                self.acct_info[i] = t.encode('utf8') if isinstance(t, unicode) else t 
                i = i + 1
            if i > 0:
                self.acct_info_mod = 'Y'
                self.acct_info_num = i / 2
         
        
        self.susp_duration = 0
        self.susp_susptime = 0
        self.susp_oper_id = 0
        self.susp_reason0 = ' '
        self.susp_reason1 = ' '
        self.susp_junk = 2*' '
        self.susp_from_period = 0
        self.susp_to_period = 0
        self.susp_no_days = 0 
        self.susp_areas = 16*[0]
        self.susp_parcel = ' '
        self.susp_junk2 = 2*' '

        self.LimitReinstate = 'N' 

        self.susp_no_accept = 0
        
        try:
            self.addr_x = driver_dic["addr_x"]
        except Exception as e:
            self.addr_x = 0 
        
        try:  
            self.addr_y = driver_dic["addr_y"]
        except Exception as e:
            self.addr_y = 0    
        
        try:
            self.zone = driver_dic["zone"]
        except Exception as e:
            self.zone = 0 
        
        self.map_page = 0
        self.map_ref = ' ' 
        
        self.postal = '\0'
        try:
            self.postal = driver_dic["postal"].encode('utf8') if isinstance(driver_dic["postal"], unicode) else driver_dic["postal"]
        except Exception as e:
            self.postal = '\0'
        
        self.num = '\0'
        try:
            self.num = driver_dic["num"]
        except Exception as e:
            self.num = '\0'
        
        self.street = '\0'
        try:
            self.street = driver_dic["street"].encode('utf8') if isinstance(driver_dic["street"], unicode) else driver_dic["street"]
        except Exception as e:
            self.street = '\0'
        
        self.city = '\0'
        try:
            self.city = driver_dic["city"].encode('utf8') if isinstance(driver_dic["city"], unicode) else driver_dic["city"]
        except Exception as e:
            self.city = '\0'
        
        self.building = '\0'
        try:
            self.building = driver_dic["building"].encode('utf8') if isinstance(driver_dic["building"], unicode) else driver_dic["building"]
        except Exception as e:
            self.building = '\0'
        
        self.addr_junk = 0

        self.phone = '\0'
        try:
            self.phone = driver_dic["phone"].encode('utf8') if isinstance(driver_dic["phone"], unicode) else driver_dic["phone"]
        except Exception as e:
            self.phone = '\0'

        self.name = '\0'
        try:
            self.name = driver_dic["name"].encode('utf8') if isinstance(driver_dic["name"], unicode) else driver_dic["name"]
        except Exception as e:
            self.name = '\0'
        
        self.system_fare_types = 0
        self.user_fare_types = 0
        self.user_driver_types = 0
        if driver_dic.has_key("user_driver_types"):
            for i in driver_dic["user_driver_types"]:
                try:
                    print i, int(i), self.user_driver_types 
                    itype = int(i)
                    if itype in range(32):
                        self.user_driver_types = self.user_driver_types +  (1 << itype) 
                except Exception as e:
                    pass
        self.user_vehicle_types = 0
        try: 
            self.cur_combat_pts = driver_dic["current_combat_points"] 
        except Exception as e:
            self.cur_combat_pts = 0 
        
        self.spare1 = 0 
        try: 
            self.cur_taxi = driver_dic["cur_taxi"]
        except (KeyError, ValueError): 
            self.cur_taxi = 0  
        try:
            self.supervisor = driver_dic["supervisor"] 
        except (KeyError, ValueError):
            self.supervisor = 'N'
        
        try:
           self.discallout = driver_dic["discallout"]
        except (KeyError, ValueError):
            self.discallout = 'N'
        
        try: 
            self.tot_combat_pts = driver_dic["total_combat_points"]
        except (KeyError, ValueError): 
            self.tot_combat_pts = 0 

        try: 
            self.driver_group = driver_dic["driver_group"]
        except (KeyError, ValueError): 
            self.driver_group = ' '
            
        self.dues = ' '
        try:
            self.MDT_Display = driver_dic["MDT_Display"]
        except (KeyError, ValueError): 
            self.MDT_Display = 'N' 
        try: 
            self.FareOfferViaSMS = driver_dic["fare_offer_via_sms"]
        except (KeyError, ValueError):
            self.FareOfferViaSMS = 'N' 
        try: 
            self.shift_id = driver_dic["shift_id"]
        except (KeyError, ValueError):
            self.shift_id = 0 
        
        self.balance = 0.0   
        self.from_zone = 32*[0]
        if driver_dic.has_key("from_zone"):
            for k in range(len(driver_dic["from_zone"])):
                self.from_zone[k] = driver_dic["from_zone"][k]
            
        self.to_zone = 32*[0]
        if driver_dic.has_key("to_zone"):
            for k in range(len(driver_dic["to_zone"])):
                self.to_zone[k] = driver_dic["to_zone"][k]

        self.WakeupFromTime = -1
        self.WakeupToTime = -1
        try: 
            self.WakeupDriver = driver_dic["wakeup_driver"]
        except (KeyError, ValueError):
            self.WakeupDriver = 'N'

        self.spare2 = 3*' '
        self.LastWakeupTime = 0 
        try:
            self.PremiereDriver = driver_dic["premiere_driver"]
        except (KeyError, ValueError):
            self.PremiereDriver = 'N' 
        
        self.primary_email = '\0'
        try:
            #self.primary_email = driver_dic["primary_email"]
            self.primary_email = driver_dic["primary_email"].encode('utf8') if isinstance(driver_dic["primary_email"], unicode) else driver_dic["primary_email"]
        except (KeyError, ValueError):
            self.primary_email = '\0'
        
        self.secondary_email = '\0'
        try:
            #self.secondary_email = driver_dic["secondary_email"]
            self.secondary_email = driver_dic["secondary_email"].encode('utf8') if isinstance(driver_dic["secondary_email"], unicode) else driver_dic["secondary_email"]
        except (KeyError, ValueError):
            self.secondary_email = '\0'
        
        try:
            self.DenyTempBookOff = driver_dic["deny_temp_book_off"]
        except (KeyError, ValueError): 
            self.DenyTempBookOff = 'N' 
        
        self.cpad = 2*' ' 
        self.PremiereDriverFareSuspensionTime = 0
        self.LastOpenPremiereDriverFareTime = -1
        
        try:
            if driver_dic.has_key("mobile_phone"):
                #self.mobilephone = str(driver_dic["mobile_phone"])
                self.mobilephone = driver_dic["mobile_phone"].encode('utf8') if isinstance(driver_dic["mobile_phone"], unicode) else str(driver_dic["mobile_phone"])
        except (KeyError, ValueError):
            self.mobilephone = '\0'
       
        self.Status = 0
        try:
            self.NumberOfTempBookOff = int(driver_dic["number_of_temp_book_off"]) 
        except (KeyError, ValueError): 
            self.NumberOfTempBookOff = 0

        self.sPad = 0
        
        self.PIN = 0
        try:
            self.PIN = int(driver_dic["driver_pin"])
        except (KeyError, ValueError): 
            self.PIN = 0 
        self.pads = 36*' '
        return
    
    def driver_info_to_tuple(self):
        print 'modified ', self.modified
        values = (
            self.DriverNum, 
            self.start_time, 
            self.stop_time, 
            self.taxi_no, 
            self.fleets[0], 
            self.fleets[1],  
            self.fleets[2], 
            self.fleets[3],  
            self.fleets[4], 
            self.fleets[5], 
            self.fleets[6], 
            self.fleets[7], 
            self.fleets[8], 
            self.fleets[9], 
            self.taxis[0], 
            self.taxis[1], 
            self.taxis[2], 
            self.taxis[3], 
            self.taxis[4], 
            self.taxis[5], 
            self.taxis[6], 
            self.taxis[7], 
            self.taxis[8], 
            self.taxis[9],
            self.num_fleets,
            self.disable_driver, 
            self.modified, 
            self.acct_info_num, 
            self.acct_disabled, 
            self.acct_info_mod, 
            self.acct_info[0*2 + 0], 
            self.acct_info[0*2 + 1], 
            self.acct_info[1*2 + 0],
            self.acct_info[1*2 + 1],
            self.acct_info[2*2 + 0],
            self.acct_info[2*2 + 1],
            self.acct_info[3*2 + 0],
            self.acct_info[3*2 + 1],
            self.acct_info[4*2 + 0],
            self.acct_info[4*2 + 1],
            self.acct_info[5*2 + 0],
            self.acct_info[5*2 + 1],
            self.acct_info[6*2 + 0],
            self.acct_info[6*2 + 1],
            self.acct_info[7*2 + 0],
            self.acct_info[7*2 + 1],
            self.acct_info[8*2 + 0],
            self.acct_info[8*2 + 1],
            self.acct_info[9*2 + 0],
            self.acct_info[9*2 + 1],
            self.acct_info[10*2 + 0],
            self.acct_info[10*2 + 1],
            self.acct_info[11*2 + 0],
            self.acct_info[11*2 + 1],
            self.acct_info[12*2 + 0],
            self.acct_info[12*2 + 1],
            self.acct_info[13*2 + 0],
            self.acct_info[13*2 + 1],
            self.acct_info[14*2 + 0],
            self.acct_info[14*2 + 1],
            self.acct_info[15*2 + 0],
            self.acct_info[15*2 + 1],
            self.susp_duration, 
            self.susp_susptime, 
            self.susp_oper_id, 
            self.susp_reason0, 
            self.susp_reason1,
            self.susp_junk,
            self.susp_from_period, 
            self.susp_to_period, 
            self.susp_no_days, 
            self.susp_areas[0], 
            self.susp_areas[1], 
            self.susp_areas[2], 
            self.susp_areas[3], 
            self.susp_areas[4], 
            self.susp_areas[5], 
            self.susp_areas[6], 
            self.susp_areas[7], 
            self.susp_areas[8], 
            self.susp_areas[9], 
            self.susp_areas[10], 
            self.susp_areas[11], 
            self.susp_areas[12], 
            self.susp_areas[13], 
            self.susp_areas[14], 
            self.susp_areas[15], 
            self.susp_parcel, 
            self.susp_junk2, 
            self.LimitReinstate, 
            self.susp_no_accept, 
            self.addr_x, 
            self.addr_y,
            self.zone, 
            self.map_page, 
            self.map_ref, 
            self.postal, 
            self.num,
            self.street, 
            self.city, 
            self.building, 
            self.addr_junk, 
            self.phone, 
            self.name, 
            self.system_fare_types,
            self.user_fare_types,
            self.user_driver_types,
            self.user_vehicle_types, 
            self.cur_combat_pts, 
            self.spare1, 
            self.cur_taxi,
            self.supervisor,
            self.discallout,
            self.tot_combat_pts,
            self.driver_group,
            self.dues,
            self.MDT_Display, 
            self.FareOfferViaSMS, 
            self.shift_id, 
            self.balance, 
            self.from_zone[0],
            self.from_zone[1], 
            self.from_zone[2],
            self.from_zone[3], 
            self.from_zone[4], 
            self.from_zone[5],
            self.from_zone[6],
            self.from_zone[7],
            self.from_zone[8],
            self.from_zone[9],
            self.from_zone[10],
            self.from_zone[11],
            self.from_zone[12],
            self.from_zone[13],
            self.from_zone[14],
            self.from_zone[15],
            self.from_zone[16],
            self.from_zone[17],
            self.from_zone[18],
            self.from_zone[19],
            self.from_zone[20],
            self.from_zone[21],
            self.from_zone[22],
            self.from_zone[23],
            self.from_zone[24],
            self.from_zone[25],
            self.from_zone[26],
            self.from_zone[27],
            self.from_zone[28],
            self.from_zone[29],
            self.from_zone[30],
            self.from_zone[31],
            self.to_zone[0],
            self.to_zone[1],
            self.to_zone[2],
            self.to_zone[3],
            self.to_zone[4],
            self.to_zone[5],
            self.to_zone[6],
            self.to_zone[7],
            self.to_zone[8],
            self.to_zone[9],
            self.to_zone[10],
            self.to_zone[11],
            self.to_zone[12],
            self.to_zone[13],
            self.to_zone[14],
            self.to_zone[15],
            self.to_zone[16],
            self.to_zone[17],
            self.to_zone[18],
            self.to_zone[19],
            self.to_zone[20],
            self.to_zone[21],
            self.to_zone[22],
            self.to_zone[23],
            self.to_zone[24],
            self.to_zone[25],
            self.to_zone[26],
            self.to_zone[27],
            self.to_zone[28],
            self.to_zone[29],
            self.to_zone[30],
            self.to_zone[31],
            self.WakeupFromTime, 
            self.WakeupToTime, 
            self.WakeupDriver,
            self.spare2,
            self.LastWakeupTime, 
            self.PremiereDriver, 
            self.primary_email, 
            self.secondary_email,
            self.DenyTempBookOff,
            self.cpad,
            self.PremiereDriverFareSuspensionTime,
            self.LastOpenPremiereDriverFareTime,
            self.mobilephone,
            self.Status, 
            self.NumberOfTempBookOff,
            self.sPad, 
            self.PIN, 
            self.pads)
        return values
    
    def driver_info_to_struct(self):
        frmt = '4I 21h 2c h 2c 12s I 12s I 12s I 12s I 12s I 12s I 12s I 12s I 12s I 12s I 12s I 12s I 12s I 12s I 12s I 12s 4I 33s 33s 2s 19I c 2s c 3I 2h 4s 8s 8s 34s 34s 34s h 20s 24s 4I 3h 2c I 4c I f 64h 2I c 3s I c 50s 50s c 2s 2I 20s I 2h I 36s'
        s = struct.Struct(frmt)
        dData = self.driver_info_to_tuple()
        print 'driver data: ', dData
        packed_data = s.pack(*dData)
        data_size = s.size
        print 'returning packed stuff' 
        return (packed_data, data_size)

    def add_modify_driver(self, action):
        try:
            
            if self.DriverNum > -1: 
                packed_data, data_size = self.driver_info_to_struct()
                print 'data_size ', data_size
                #changed from 1024 check sdhr for record 344 
                ss = struct.Struct('I I I I I c c c c 1028s')
                if action == "add":
                    #msg_code_id = msgconf.MT_ADDDRIVERREC
                    msg_code_id = msgconf.MT_MODDRIVERINFO
                    print 'adding driver record ' 
                elif action in ["update", "modify"]:
                    msg_code_id = msgconf.MT_MODDRIVERINFO
                    print 'modifying driver record'
                print 'message ', msg_code_id, ' will be sent'
                packed_msg = ss.pack(msgconf.CWEBS,
                                 msgconf.TFC,
                                 0,
                                 msg_code_id,
                                 data_size,
                                 '0',
                                 '0',
                                 '1',
                                 'a',
                                 packed_data)

                mq = sysv_ipc.MessageQueue(msgconf.TFC, flags=sysv_ipc.IPC_CREAT, mode=0666, max_message_size = 8064)
                try:
                    print 'sending add or modify driver message'
                    mq.send(packed_msg, block=False, type=msgconf.ROUT_PRI)
                except sysv_ipc.BusyError:
                    print "Queue is full"
                #mq.remove()
            else:
                print 'invalid driver'
        except Exception as e:
            print 'Exception ', str(e)
            pass


def delete_driver(DriverNum):
    try:
        if DriverNum > -1:
            ss = struct.Struct('I I I I I c c c c I')
            packed_msg = ss.pack(msgconf.CWEBS,
                msgconf.TFC,
                0,
                msgconf.MT_DELDRIVERREC,
                4,
                '0',
                '0',
                '1',
                'a',
                 DriverNum)
            mq = sysv_ipc.MessageQueue(msgconf.TFC, flags=sysv_ipc.IPC_CREAT, mode=0666, max_message_size = 8064)
            try:
                mq.send(packed_msg, block=False, type=msgconf.ROUT_PRI)
            except sysv_ipc.BusyError:
                pass
                print "Queue is full - will not send"
           #mq.remove()
    except ValueError:
        pass


if __name__ == "__main__":
    print 'test'
    #
    #print 'modifying driver' 
    #drv = DriverParams({"DriverNum": 6666})
    #drv.add_modify_driver()
    #
    #print 'deleting driver' 
    #delete_driver(89)
