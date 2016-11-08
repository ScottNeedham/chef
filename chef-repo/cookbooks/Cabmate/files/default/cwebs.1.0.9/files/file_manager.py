from gevent import monkey; monkey.patch_all()
import sys, os
import struct
from ctypes import *
import json
import datetime
import requests
from bottle import Bottle, request, response
import collections 

if __name__ == "__main__":  
    app_dir = os.path.dirname(__file__) + "/.."
    sys.path.append (app_dir )

import app.errormsg as ErrorMsg

import app.msgconf
import app.cabmsg
import config.cwebsconf as Config

HEADER_FILE = '/data/header.fl'
FLEET_DATA_FILE = '/data/fleets.fl'
DRIVERS_DATA_FILE = '/data/drivers.fl'
LIMITS_DATA_FILE = '/data/limits.fl'

HEADER_FILE_FORMAT =  '128s 15I 6B 6s'
FLEET_DATA_FILE_FORMAT = '24s 2h   h 2B 256s   2I 2h 4s 2I 8s 34s 34s 34s h  20s   2B  11B 3c ' #'972B 24B' 
DRIVERS_DATA_FILE_FORMAT = '4I 21h 2c h 2c 12s I 12s I 12s I 12s I 12s I 12s I 12s I 12s I 12s I 12s I 12s I 12s I 12s I 12s I 12s I 12s 4I 33s 33s 2s 19I c 2s c 3I 2h 4s 8s 8s 34s 34s 34s h 20s 24s 4I 3h 2c I 4c I f 64h 2I c 3s I c 50s 50s c 2s 2I 20s I 2h I 36s'
LIMITS_DATA_FILE_FORMAT = '20I 6B 2c 6I 8B 2I h I' # remaining 512-134

#taxishadow.h
MIN_FILE_HEADER_RECORD = 14
LIMITS_HEADER_RECORD = 36
FLEET_HEADER_RECORD = 66
FLEETPTR_HEADER_RECORD = 74
FARES_HEADER_RECORD = 98
DRIVER_TYPES_HEADER_RECORD = 38
DRIVER_STATS_HEADER_RECORD = 133
DRIVERSERVER_LOG_HEADER_RECORD = 210
DRIVERS_HEADER_RECORD = 344
FLEETCVD_HEADER_RECORD = 444
MAX_FILE_HEADER_RECORD = 452

#Each entry : HEADER ID, File format
HeaderFileFormatDic = {
    "FLEET"     : [FLEET_HEADER_RECORD,  FLEET_DATA_FILE_FORMAT],
    "DRIVERS"   : [DRIVERS_HEADER_RECORD,  DRIVERS_DATA_FILE_FORMAT]

}

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

FileHeaderTuple = collections.namedtuple('file_header', 'filename rec_size num_recs max_recs')


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





class header_reader(object):

  def read_record(self, hdr_id):
    try:
       
        mytuple = FileHeaderTuple(filename='',  rec_size=0, num_recs=0,  max_recs=0)
        errmsg = "INVALID HEADER ID"
        if hdr_id < MIN_FILE_HEADER_RECORD or hdr_id > MAX_FILE_HEADER_RECORD:
            return errmsg, mytuple
        else:
            myfile = HEADER_FILE
            rec_fmt = HEADER_FILE_FORMAT
            rec_size = struct.Struct(rec_fmt).size

        statinfo = os.stat(myfile)
           
        #print ( statinfo )

        maxrec = statinfo.st_size / rec_size

        if maxrec < 1 or hdr_id > maxrec:
          print (' ERROR ....\n' )
          return errmsg,  mytuple

        #print ( ' maxrec={0} recsize={1} hdr_id={2} '.format( maxrec , rec_size, hdr_id) )


        offset = int (hdr_id ) * int(rec_size)

        #print  (' offset = {0}'.format ( offset) )

        f = os.open(myfile, os.O_RDONLY)
        try:     
          os.lseek(f, offset, 0)  
        except Exception as e:
          print (' read_header_record {0}  '.format ( str (e)) )
          return "LSEEK FAILED" , mytuple

        try:
          d = os.read(f, rec_size)
          if len(d)  == rec_size :
            #print ' Received data ... '
            data =  struct.Struct(rec_fmt).unpack(d)   
            #print ' unpacked ... ', data
            #print (' name={0} rec_size={1} num_recs={2}  max_recs={3} '.format ( data[0], data[1], data[2],  data[3] ) )
            mytuple = FileHeaderTuple (filename=data[0].strip('b\00'), rec_size=data[1], num_recs=data[2],  max_recs=data[3] )
          
            return "OK", mytuple
        except Exception as e:
          print (' read_header_record {0}  '.format ( str (e)) )
          return "READ FAILED" , mytuple

    except Exception as e:
      print (' read_header_record {0}  '.format ( str (e)) )
      return errmsg, mytuple


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

    def read_record(self, myid, file_rec_size=None, recid=None, filename=''):
        try:
            errmsg = "INVALID ID"
            if recid < 0 or filename=='':
                return errmsg, -1
            else:
                if myid ==  FLEET_HEADER_RECORD:                   
                    rec_fmt = FLEET_DATA_FILE_FORMAT
                elif myid == DRIVERS_HEADER_RECORD:                  
                    rec_fmt = DRIVERS_DATA_FILE_FORMAT
                elif myid == LIMITS_HEADER_RECORD:
                    rec_fmt = LIMITS_DATA_FILE_FORMAT
                else:
                    return "Not implemented", -1, []


            #print (' *** passed in fn ={0} len={1} ****'.format ( str(filename), len(filename)) )
            #filename = filename.strip('b\00')
            #print (' *** passed in fn ={0} len={1} ****'.format ( str(filename), len(filename)) )

            rec_size = struct.Struct(rec_fmt).size

            #Adjust format size if necessary
            if rec_size < file_rec_size :
                #print (' needs %d bytes' % (file_rec_size-rec_size) )
                fmt = '%dB' % ( file_rec_size-rec_size)
                rec_fmt = ' '.join ( [ rec_fmt, fmt ] )
                rec_size = struct.Struct(rec_fmt).size

            statinfo = os.stat(filename)
           
            #print statinfo

            maxrec = statinfo.st_size / rec_size

            if maxrec < 1 or recid > maxrec:
                print (' ERROR ....myid={0} maxrec={1} file_size={2}\n'. format (recid, maxrec, statinfo.st_size  ))
                return errmsg, -1, []

            #print  (' maxrec={0} recsize={1} myid={2} '.format( maxrec , rec_size, recid) )

            offset = int (recid ) * int(rec_size)

            #print  ' offset = {0}'.format ( offset) 

            f = os.open(filename, os.O_RDONLY)
            try:     
                os.lseek(f, offset, 0)  
            except Exception as e:
                print (' read_data_file_record {0}  '.format ( str (e)) )
                return "LSEEK FAILED" , -1, []

            try:
                d = os.read(f, rec_size)
                if len(d)  == rec_size :
                    #print ' Received data ... '
                    data =  struct.Struct(rec_fmt).unpack(d)   
                    #print ' unpacked ... ', data
                    #print ' name={0} number={1} num_of_taxis={2} zone_set={3}, mdt_group={4} '.format ( data[0], data[1], data[2], data[26], data[27] )
                    return "OK", 1, data
            except Exception as e:
                print (' read_data_file_record {0}  '.format ( str (e)) )
                return "READ FAILED" , -1, []

        except Exception as e:
            print (' read_data_file_record {0}  '.format ( str (e)) )
            return errmsg, -1, []


    def write_record(self, myid, file_rec_size=None, recid=None, filename='', data=None):
        try:
            errmsg = "INVALID ID"
            if recid < 0 or filename=='':
                return errmsg, -1
            else:
                if myid ==  FLEET_HEADER_RECORD:                   
                    rec_fmt = FLEET_DATA_FILE_FORMAT
                elif myid == DRIVERS_HEADER_RECORD:                  
                    rec_fmt = DRIVERS_DATA_FILE_FORMAT
                elif myid == LIMITS_HEADER_RECORD:
                    rec_fmt = LIMITS_DATA_FILE_FORMAT
                else:
                    return "Not implemented", -1, []
            if data == None:
                return "No Data to write!", -1, []

   
            rec_size = struct.Struct(rec_fmt).size
            if rec_size < file_rec_size :
                #print (' needs %d bytes' % (file_rec_size-rec_size) )
                fmt = '%dB' % ( file_rec_size-rec_size)
                rec_fmt = ' '.join ( [ rec_fmt, fmt ] )
                rec_size = struct.Struct(rec_fmt).size


            statinfo = os.stat(filename)
           
            print statinfo

            maxrec = statinfo.st_size / rec_size

            if maxrec < 1 or recid > maxrec:
                print (' ERROR ....myid={0} maxrec={1} file_size={2}\n'. format (recid, maxrec, statinfo.st_size  ))
                return errmsg, -1, []

            #print  (' maxrec={0} recsize={1} myid={2} '.format( maxrec , rec_size, recid) )

            offset = int (recid ) * int(rec_size)

            print  ' offset = {0}'.format ( offset) 

            f = os.open(filename, os.O_RDWR)
            try:     
                os.lseek(f, offset, 0)  
            except Exception as e:
                print (' read_data_file_record {0}  '.format ( str (e)) )
                return "LSEEK FAILED" , -1, []

            try:
                s = struct.Struct(rec_fmt)
                packed_data = s.pack(*data) 
                num = os.write(f, packed_data )
                if num  == rec_size :
                    #print ' Received data ... '                    
                    #print ' unpacked ... ', data
                    #print ' 0={0} 1={1} 2={2} 21={3}, 22={4} '.format ( data[0], data[1], data[2], data[21], data[22] )

                    return "OK", 1, data
                else:
                    return "Error on Writing", -1, []
            except Exception as e:
                print (' write_data_file_record {0}  '.format ( str (e)) )
                return "WRITE FAILED" , -1, []

        except Exception as e:
            print (' write_data_file_record {0}  '.format ( str (e)) )
            return errmsg, -1, []

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

        from files.system_limits import can_send_msg_to_vehicle
        numrec=3

        if len(sys.argv) > 1:
            print ( "Trying with record # {0} instead of {1}".format(sys.argv[1], numrec) )
            numrec = int (sys.argv[1])
     
        shdr = header_reader()
        #Need innerID, MDT_group, Z_set
        datafile = data_file_reader()

        rec_size = 0
        err, t= shdr.read_record(FLEET_HEADER_RECORD)
        if err == 'OK':            
            print ( ' *************** {0} **********'.format (t) )

            print (' {0} file_name={1} rec size={2} num_recs={3} '.format ( err,  t.filename, t.rec_size, t.num_recs ) )
            err, s, d = datafile.read_record(FLEET_HEADER_RECORD,  filename=t.filename, file_rec_size=t.rec_size, recid=t.num_recs - 1)
          
        err, t = shdr.read_record(DRIVERS_HEADER_RECORD)
        if err == 'OK':
            print ( ' *************** {0} **********'.format (t) )
            print (' {0} file_name={1} rec size={2} num_recs={3}'.format ( err, t.filename,  t.rec_size, t.num_recs ) )
            err, s, d = datafile.read_record(DRIVERS_HEADER_RECORD, filename=t.filename, file_rec_size=t.rec_size, recid=t.num_recs - 1)
          
        err, t= shdr.read_record(LIMITS_HEADER_RECORD)
        if err == 'OK':            
            print ( ' *************** {0} **********'.format (t) )

            print (' {0} file_name={1} rec size={2} num_recs={3} '.format ( err,  t.filename, t.rec_size, t.num_recs ) )
            err, s, d = datafile.read_record(LIMITS_HEADER_RECORD,  filename=t.filename, file_rec_size=t.rec_size, recid=t.num_recs - 1)      
            if d and len(d) > 0:
                print (' taxi_supv = {0}'.format( chr(d[21])) )

        r = can_send_msg_to_vehicle()
        print (' Yes ? ', r )

    except Exception as e:
        sys.stdout.write("%s: Exception in %s -  %s\n" % (
                datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT), sys._getframe().f_code.co_name, str(e)))


    adr = addr_struct()
    print ( ' size of adr  = {0} phone_struct={1} dis_accts_struct={2} acct_info_struct={3} fleet_info_struct={4}'. format ( \
                                sizeof(adr), sizeof(phone_struct), sizeof(dis_accts_struct), sizeof(acct_info_struct) ,
                                sizeof(fleet_info_struct) ) )


