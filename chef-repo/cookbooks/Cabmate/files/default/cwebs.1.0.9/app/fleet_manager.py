from gevent import monkey; monkey.patch_all()
import sys, os
import struct
from ctypes import *
import json
import datetime
import requests
from bottle import Bottle, request, response


if __name__ == "__main__":  
    app_dir = os.path.dirname(__file__) + "/.."
    sys.path.append (app_dir )

import errormsg as ErrorMsg

import msgconf
import cabmsg
import config.cwebsconf as Config

HEADER_FILE = '/data/header.fl'
HEADER_FILE_FORMAT =  '128s 15I 6B 6s'

FLEET_DATA_FILE = '/data/fleets.fl'
FLEET_DATA_FILE_FORMAT = '24s 2h   h 2B 256s   2I 2h 4s 2I 8s 34s 34s 34s h  20s   2B  11B 3c ' #'972B 24B' 

#taxishadow.h
MIN_FILE_HEADER_RECORD = 14
FLEET_HEADER_RECORD = 66
FLEETPTR_HEADER_RECORD = 74
FARES_HEADER_RECORD = 98
#FL_DRIVER_TYPES            38
MAX_FILE_HEADER_RECORD = 452


RESTR_ACC_CUS_SIZE = 12
RESTR_VIP_NUM_SIZE = 13
MAX_DIS_ACCTS = 16
STRTNUMSIZ  =   8
STRTNAMSIZ =    34
CITYSIZ  =    34
BUILDSIZ =    34
ACLSIZ   =     3
NAMSIZ   =    15
APTSIZ   =    8
CODESIZ  =     5
PHONESIZ =     20
FLEETBACKUP  = 10     
MARKETIDLEN   =  16



class addr_struct(Structure): 
    _fields_ = [  ("x", c_int ) ,       #long x;
                ("y", c_int ) ,         # long y;    
                ("zone" , c_short),     #short zone;              
                ( "map_page", c_short), # short map_page;
                 ( "map_ref", c_char * 4), # char map_ref[4];
                ("postal_info", c_char * 8),  # union postal_info
                ( "num", c_char * STRTNUMSIZ), # char num[STRTNUMSIZ]
                ( "street", c_char * STRTNAMSIZ),  # char street[STRTNAMSIZ];   
                ( "city", c_char * CITYSIZ), # char city[CITYSIZ];   
                ( "building", c_char * BUILDSIZ), #  char building[BUILDSIZ]; 
                ("junk", c_short)           #  padding to make if modulo 4
                ]
 
class phone_struct(Structure):    # 20s    
    _fields_ = [  ("digits", c_char *  PHONESIZ) 
                ]

class dis_accts_struct(Structure):    #size 16 bytes 
    _fields_ = [
            ("accnt_num", c_char * RESTR_ACC_CUS_SIZE),
            ("cus_num", c_int)
   ]

class acct_info_struct(Structure): #size=256
    _fields_ = [
            ( "num", c_short ),                           
            ( "disabled", c_char),                      
            ( "modified", c_char),  
            ( "restrict", dis_accts_struct * MAX_DIS_ACCTS)  ]

class flt_access_struct(Structure): #2B
    _fields_ = [
            ("disabled", c_char ),                      
            ("req_driver_id", c_char )    
        ]

class CalloutTime_struct(Structure):
    _fields_ = [
        ("FromTime", c_int),                                
        ("ToTime", c_int),                                             
        ]


class fleet_info_struct(Structure):
    _fields_ = [
        ("name", c_char * 24 ),                           
        ("number", c_short),                             
        ("num_of_taxis" , c_short),                         
        ("acct", acct_info_struct),          # h 2B 256s
        ("address", addr_struct ) ,    # 2I 2h 4s I 8s 34s 34s 34s h                
        ("phone", phone_struct),      # 20s              
        ("fl", flt_access_struct),           # 2B                
        ("dues", c_char),
        ("callout", c_char),                           
        ("dispatch_mode", c_char),                         
        ("offduty_form", c_char),                         
        ("zone_set", c_char),                          
        ("MDT_group", c_char),                          
        ("share_stale_fares", c_char),                      
        ("meteronrebooktimer", c_char),                    
        ("first_book_in_dest_on", c_char),                      
        ("no_activity_book_off_time", c_ubyte),           #unsigned char      
        ("max_meton_time_to_retain_qpos", c_ubyte),       #unsigned char                
        ("max_time_to_arrive_in_dest_zone", c_ubyte),     #unsigned char               
        ("next_first_dest_book_timer", c_short ),  
        ("DBOOKfeature" , c_char),                              
        ("WakeupDriver", c_char),                                  
        ("scarce_enabled", c_char),                                
        ("CCusefltname", c_char),                                  
        ("scarce_attributes", c_uint),                   
        ("calloutlimit", c_short),
        ("prefix", c_char * 6),
        ("callouttime", CalloutTime_struct),                   
        ("virtualfleet", c_short),                               
        ("priorityzone", c_short),                              
        ("curbrotation", c_char), 
        ("meterinstalled", c_char), 
        ("pollmeterstats", c_char), 
        ("secondarycontact", c_char * 20), 
        ("override_payment", c_char),                        
        ("VDM_MDTControlEnabled", c_char), 
        ("ContinuousGPSUpdate", c_char),                       
        ("AutoLogin", c_char),                         
        ("AutoBook", c_char),                           
        ("VDM_MDTControl", c_uint),                    
        ("TempBookOffDuration", c_short),                        
        ("TempBookOffInterval", c_short),                       
        ("TempBookOffTimes", c_short),                      
        ("AllowedToViewDestinationAddr", c_char),                   
        ("PromptWheelChairFlagForm", c_char),                  
        ("NotifyModification", c_char),                     
        ("PostAllRides", c_char),                           
        ("AppliedLocal", c_char),                          
        ("MaxLocal", c_char),                             
        ("RebookOnMeterOff", c_char),                       
        ("GenerateLateETA", c_char), 
        ("GenerateFarPickup", c_char), 
        ("alternate_fleet", c_short * FLEETBACKUP),          
        ("FareDispatchMethod", c_char),                    
        ("MarketId", c_char * (MARKETIDLEN+1) ),            
        ("pad", c_char * 450),    
    ]

class addr_tuple(Structure): 
     (  
                ("x", c_int ) ,       #long x;
                ("y", c_int ) ,         # long y;    
                ("zone" , c_short),     #short zone;              
                ( "map_page", c_short), # short map_page;
                 ( "map_ref", c_char * 4), # char map_ref[4];
                ("postal_info", c_char * 8),  # union postal_info
                ( "num", c_char * STRTNUMSIZ), # char num[STRTNUMSIZ]
                ( "street", c_char * STRTNAMSIZ),  # char street[STRTNAMSIZ];   
                ( "city", c_char * CITYSIZ), # char city[CITYSIZ];   
                ( "building", c_char * BUILDSIZ), #  char building[BUILDSIZ]; 
                ("junk", c_short)           #  padding to make if modulo 4
     )
 
class phone_struct(Structure):    # 20s    
    _fields_ = [  ("digits", c_char *  PHONESIZ) 
                ]

class dis_accts_struct(Structure):    #size 16 bytes 
    _fields_ = [
            ("accnt_num", c_char * RESTR_ACC_CUS_SIZE),
            ("cus_num", c_int)
   ]

class acct_info_struct(Structure): #size=256
    _fields_ = [
            ( "num", c_short ),                           
            ( "disabled", c_char),                      
            ( "modified", c_char),  
            ( "restrict", dis_accts_struct * MAX_DIS_ACCTS)  ]

class flt_access_struct(Structure): #2B
    _fields_ = [
            ("disabled", c_char ),                      
            ("req_driver_id", c_char )    
        ]

class CalloutTime_struct(Structure):
    _fields_ = [
        ("FromTime", c_int),                                
        ("ToTime", c_int),                                             
        ]


class fleet_info_struct(Structure):
    _fields_ = [
        ("name", c_char * 24 ),                           
        ("number", c_short),                             
        ("num_of_taxis" , c_short),                         
        ("acct", acct_info_struct),          # h 2B 256s
        ("address", addr_struct ) ,    # 2I 2h 4s I 8s 34s 34s 34s h                
        ("phone", phone_struct),      # 20s              
        ("fl", flt_access_struct),           # 2B                
        ("dues", c_char),
        ("callout", c_char),                           
        ("dispatch_mode", c_char),                         
        ("offduty_form", c_char),                         
        ("zone_set", c_char),                          
        ("MDT_group", c_char),                          
        ("share_stale_fares", c_char),                      
        ("meteronrebooktimer", c_char),                    
        ("first_book_in_dest_on", c_char),                      
        ("no_activity_book_off_time", c_ubyte),           #unsigned char      
        ("max_meton_time_to_retain_qpos", c_ubyte),       #unsigned char                
        ("max_time_to_arrive_in_dest_zone", c_ubyte),     #unsigned char               
        ("next_first_dest_book_timer", c_short ),  
        ("DBOOKfeature" , c_char),                              
        ("WakeupDriver", c_char),                                  
        ("scarce_enabled", c_char),                                
        ("CCusefltname", c_char),                                  
        ("scarce_attributes", c_uint),                   
        ("calloutlimit", c_short),
        ("prefix", c_char * 6),
        ("callouttime", CalloutTime_struct),                   
        ("virtualfleet", c_short),                               
        ("priorityzone", c_short),                              
        ("curbrotation", c_char), 
        ("meterinstalled", c_char), 
        ("pollmeterstats", c_char), 
        ("secondarycontact", c_char * 20), 
        ("override_payment", c_char),                        
        ("VDM_MDTControlEnabled", c_char), 
        ("ContinuousGPSUpdate", c_char),                       
        ("AutoLogin", c_char),                         
        ("AutoBook", c_char),                           
        ("VDM_MDTControl", c_uint),                    
        ("TempBookOffDuration", c_short),                        
        ("TempBookOffInterval", c_short),                       
        ("TempBookOffTimes", c_short),                      
        ("AllowedToViewDestinationAddr", c_char),                   
        ("PromptWheelChairFlagForm", c_char),                  
        ("NotifyModification", c_char),                     
        ("PostAllRides", c_char),                           
        ("AppliedLocal", c_char),                          
        ("MaxLocal", c_char),                             
        ("RebookOnMeterOff", c_char),                       
        ("GenerateLateETA", c_char), 
        ("GenerateFarPickup", c_char), 
        ("alternate_fleet", c_short * FLEETBACKUP),          
        ("FareDispatchMethod", c_char),                    
        ("MarketId", c_char * (MARKETIDLEN+1) ),            
        ("pad", c_char * 450),    
    ]



class FleetManager():
    def __init__(self, dic):
        try:
            self.action_id=0
            self.action=0
            self.event_no=0
            self.fleet=0
            self.name=0
            self.zone_set = 0
            self.mdt_group = 1
            self.operator_id=0
            self.error_msg = ''

            if isinstance(dic, dict):
                self.populate_object(dic)
            self.error = False
            res = {}

        except Exception as e:
            sys.stdout.write("%s: %s - Exception %s\n" % (
                datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT), sys._getframe().f_code.co_name, str(e)))
            self.error = True

    def __str__(self):
        return " action:%s event_no:%d fleet:%d name:%s zone_set:%d mdt_group:%d action_id:%d  operator_id:%d error:%s" \
               %(self.action,
                self.event_no,
                self.fleet,
                self.name,
                self.zone_set,
                self.mdt_group,
                self.action_id,
                self.operator_id,
                self.error_msg)

  
    def populate_object(self, dic):
        try:
            if 'event_no' in dic:
                self.event_no = dic['event_no']
            if 'fleet' in dic:
                self.fleet = int( dic['fleet'])
                if type(self.fleet) != int:
                    self.error = True                
            if 'name' in dic:
                self.name =str(dic['name'])
                if type(self.name) == str:
                    self.name = self.name[:24]
                else:
                    self.error = True

            if 'zone_set' in dic:
                self.zone_set = int( dic['zone_set'])
            
            if 'mdt_group' in dic:
                self.mdt_group = int( dic['mdt_group'])


            if 'action' in dic:
                self.action = dic['action']              
            if 'action_id' in dic:
                self.action_id = dic['action_id']
        
            if 'operator_id' in dic:
                self.operator_id = dic['operator_id']

            self.set_filler()

        except Exception as e:
            sys.stdout.write("%s: %s -  Exception %s\n" % ( \
                datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT), sys._getframe().f_code.co_name, str(e)))
            self.error = True
            self.error_msg = str(e)

    def set_filler(self):

        #h  h 2B 256s 2I 2h 4s I 8s 34s 34s 34s h  20s 2B 4B ==> # h 300s 132s 20s 6B
        #h
        # h 2B 256s
        # 2I 2h 4s I 8s 34s 34s 34s h
        # 20s
        # 2B
        # 4B

        self.num_of_taxis = 0            # h         = 2     
        self.acct = '0'          # h 2B 256s = 300
        self.address = '0'     # 2I 2h 4s I 8s 34s 34s 34s h  = 132
        self.phone = '0'      # 20s              
        self.fl = 0 * 2           # 2B                
        self.dues = 0                    # B
        self.callout = 0                 # B          
        self.dispatch_mode = 0         # B               
        self.offduty_form = 0            # B              

       

    def get_error(self):
        return self.error

    def get_result(self):
        return self.res

    def send_msg(self, dic=None):
        try:
            sys.stdout.write("%s: entering %s\n" % (
                datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT), sys._getframe().f_code.co_name))

            res = {"status": 500, "result": {"message": ErrorMsg.ERROR_MSG_GENERAL_ERROR}}

            if dic is not None:
                self.populate_object(dic)     

            if self.error is True:
                sys.stdout.write("%s: Found error in dic  %s\n" % (
                    datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT), sys._getframe().f_code.co_name))                
                res['result']['message'] = self.error_msg
                return json.dumps(res)   
            try:
               
                if  self.action_id == msgconf.MT_MODFLEETINFO :
                    
                    filler_fmt = 'h 260s 136s 20s 2B 4B'
                    dData = (self.name, self.fleet, 
                                        self.num_of_taxis ,     # h         = 2     
                                        self.acct ,             # h 2B 256s = 304
                                        self.address,           # 2I 2h 4s I 8s 34s 34s 34s h  = 132
                                        self.phone,             # 20s              
                                        0 ,                     # 2B               
                                        0, 
                                        self.dues ,             # B
                                        self.callout,           # B          
                                        self.dispatch_mode,     # B               
                                        self.offduty_form,      # B
                                        self.zone_set, self.mdt_group )
                    #print 'dData ', dData
                    '''
                        char    name[24];                           
                        short   number;                             
                        short   num_of_taxis;            # h         = 2     
                        struct  acct_info acct;          # h 2B 256s = 260
                        struct  addr_struct address;     # 2I 2h 4s I 8s 34s 34s 34s h  = 132
                        struct  phone_struct phone;      # 20s              
                        struct  flt_access fl;           # 2B                
                        char    dues;                    # B
                        char    callout;                 # B          
                        char    dispatch_mode;           # B               
                        char    offduty_form;            # B              
                        char    zone_set;                           
                        char    MDT_group;                          
                    '''
                    s = struct.Struct('24s h ' + filler_fmt + ' B B ')
                    packed_data = s.pack(*dData)
                    ss_data = struct.Struct(cabmsg.base_fmt + '%ds' % (s.size))            
                    dest = msgconf.TFC                
                
                   

                    cabmsg.gmsg_send(packed_data, s.size, dest, msgconf.CWEBS, self.action_id, ss_data, self.operator_id)

                    res = {"status": 200, "result": {"message": "OK"}}
                else:                    
                    res = {'status': 500, 'result': {'message': ErrorMsg.ERROR_MSG_UNSUPPORTED_MESSAAGE_TYPE } }

            except Exception as e:
                sys.stdout.write("%s: %s - Exception %s\n" % (
                    datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT),  sys._getframe().f_code.co_name, str(e)))
                self.error = True
                res = {'status': 500, 'result': {'message': ErrorMsg.ERROR_MSG_EXCEPTION}}
                return json.dumps(res)

           

            return json.dumps(res)

        except Exception as e:
            sys.stdout.write("%s: %s - Exception %s\n" % (
                datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT), sys._getframe().f_code.co_name,  str(e)))
            self.error = True

            res = {'status': 500, 'result': {'message': ErrorMsg.ERROR_MSG_EXCEPTION}}
            return json.dumps(res)



class header_reader(object):

  def read_record(self, hdr_id):
    try:
      errmsg = "INVALID HEADER ID"
      if hdr_id < MIN_FILE_HEADER_RECORD or hdr_id > MAX_FILE_HEADER_RECORD:
        return errmsg, -1
      else:
        myfile = HEADER_FILE
        rec_fmt = HEADER_FILE_FORMAT
        rec_size = struct.Struct(rec_fmt).size

        statinfo = os.stat(myfile)
           
        print ( statinfo )

        maxrec = statinfo.st_size / rec_size

        if maxrec < 1 or hdr_id > maxrec:
          print (' ERROR ....\n' )
          return errmsg, -1

        print ( ' maxrec={0} recsize={1} hdr_id={2} '.format( maxrec , rec_size, hdr_id) )


        offset = int (hdr_id ) * int(rec_size)

        print  (' offset = {0}'.format ( offset) )

        f = os.open(myfile, os.O_RDONLY)
        try:     
          os.lseek(f, offset, 0)  
        except Exception as e:
          print (' read_header_record {0}  '.format ( str (e)) )
          return "LSEEK FAILED" , -1

        try:
          d = os.read(f, rec_size)
          if len(d)  == rec_size :
            print ' Received data ... '
            data =  struct.Struct(rec_fmt).unpack(d)   
            print ' unpacked ... ', data
            print (' name={0} recsize={1} num_recs={2}  maxrecs={3} '.format ( data[0], data[1], data[2],  data[3] ) )
            return "OK", 1
        except Exception as e:
          print (' read_header_record {0}  '.format ( str (e)) )
          return "READ FAILED" , -1

    except Exception as e:
      print (' read_header_record {0}  '.format ( str (e)) )
      return errmsg, -1


  def __init__(self) :
    try:
      self.gf_pathname = 128*b'\x00';
      self.gf_ph_recsize = 0
      self.gf_num_recs = 0
      self.gf_max_recs = 0
      self.gf_num_deleted = 0
      self.gf_first_deleted = 0
      self.gf_offset_delete_mark_in_rec = 0
      self.gf_value_delete_mark_in_rec = 0
      self.gf_backup_flags = 0
      self.gf_cantreuse_fd = 0
      self.gf_shadowed = 0
      self.gf_shdw_toid = 0
      self.gf_shdw_priority = 0
      self.gf_shdw_hiwater = 0
      self.gf_shdw_markfileno = 0
      self.gf_action_code = 0
      self.gf_entry_type = 0
      self.gf_sub_type = 0
      self.gf_fill_char = 0
      self.gf_activated = 0
      self.gf_JUNK = 0
      self.gf_opt_num = 0
      self.gf_dummy = 6 * b'\x00' 

    except Exception as e:
      print (' read_header_record {0}  '.format ( str (e)) )


class data_file_reader(object):

  def read_record(self, myid):
    try:
      errmsg = "INVALID ID"
      if myid < 0:
        return errmsg, -1
      else:
        myfile = FLEET_DATA_FILE 
        rec_fmt = FLEET_DATA_FILE_FORMAT
        rec_size = struct.Struct(rec_fmt).size

        if rec_size < 1024 :
          print (' needs %d bytes' % (1024-rec_size) )
          fmt = '%dB' % ( 1024-rec_size)
          rec_fmt = ' '.join ( [ rec_fmt, fmt ] )
          rec_size = struct.Struct(rec_fmt).size

        statinfo = os.stat(myfile)
           
        print statinfo

        maxrec = statinfo.st_size / rec_size

        if maxrec < 1 or myid > maxrec:
          print (' ERROR ....myid={0} maxrec={1} file_size={2}\n'. format (myid, maxrec, statinfo.st_size  ))
          return errmsg, -1

        print  (' maxrec={0} recsize={1} myid={2} '.format( maxrec , rec_size, myid) )

        offset = int (myid ) * int(rec_size)

        print  ' offset = {0}'.format ( offset) 

        f = os.open(myfile, os.O_RDONLY)
        try:     
          os.lseek(f, offset, 0)  
        except Exception as e:
          print (' read_data_file_record {0}  '.format ( str (e)) )
          return "LSEEK FAILED" , -1

        try:
          d = os.read(f, rec_size)
          if len(d)  == rec_size :
            print ' Received data ... '
            data =  struct.Struct(rec_fmt).unpack(d)   
            print ' unpacked ... ', data
            print ' name={0} number={1} num_of_taxis={2} zone_set={3}, mdt_group={4} '.format ( data[0], data[1], data[2], data[26], data[27] )
            return "OK", 1
        except Exception as e:
          print (' read_data_file_record {0}  '.format ( str (e)) )
          return "READ FAILED" , -1

    except Exception as e:
      print (' read_data_file_record {0}  '.format ( str (e)) )
      return errmsg, -1


  def __init__(self) :
    try:
      self.pathname = 128*b'\x00';
      self.recsize = 0
      self.num_recs = 0
      self.max_recs = 0
    except Exception as e:
      print  (' data_file_reader {0}  '.format ( str (e)) )



if __name__ == "__main__":
    try:
        numrec=3

        if len(sys.argv) > 1:
            print ( "Trying with record # {0} instead of {1}".format(sys.argv[1], numrec) )
            numrec = int (sys.argv[1])
      

        '''
        my_dic = [ #{"event_no" : msgconf.EV_EMERG, "action" : "AddEntry", "fare" : 0, "taxi" : 9006 },
                   #{"event_no" : msgconf.EV_EMERG, "action" : "ClearEntry", "fare" : 0, "taxi" : 8089 },
                   #{"event_no" : msgconf.EV_EMERG, "action" : "EmergencyClear", "taxi" : 8089 },
                   { "action_id" : msgconf.MT_MODFLEETINFO, "action" : "ModFleet", "fleet" : 11,  "name" : "MYTEST-FLEET_SAMIRA", "operator_id" : 1000},
                    #{"event_no" : msgconf.EV_EMERG, "action" : "DumpQueues" }
                ]
        for k in my_dic:
            m = FleetManager(k)
            
            if m is not None:
                print m            
                resp = response
                r = m.send_msg(k)
                print r
        '''

        shdr = header_reader()

        err, s = shdr.read_record(FLEET_HEADER_RECORD)

        print (' {0} {1}'.format ( err, s) )

        #Need innerID, MDT_group, Z_set
        datafile = data_file_reader()

        err, s = datafile.read_record(numrec)


    except Exception as e:
        sys.stdout.write("%s: Exception in %s -  %s\n" % (
                datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT), sys._getframe().f_code.co_name, str(e)))


    adr = addr_struct()
    print ( ' size of adr  = {0} phone_struct={1} dis_accts_struct={2} acct_info_struct={3} fleet_info_struct={4}'. format ( \
                                sizeof(adr), sizeof(phone_struct), sizeof(dis_accts_struct), sizeof(acct_info_struct) ,
                                sizeof(fleet_info_struct) ) )


