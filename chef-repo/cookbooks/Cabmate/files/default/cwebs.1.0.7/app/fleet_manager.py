from gevent import monkey; monkey.patch_all()
import sys
import struct
import json
import datetime
import requests
from bottle import Bottle, request, response

import errormsg as ErrorMsg

import msgconf
import cabmsg
import config.cwebsconf as Config

'''
#define RESTR_ACC_CUS_SIZE 12
#define RESTR_VIP_NUM_SIZE 13
#define MAX_DIS_ACCTS 16

#define STRTNUMSIZ      8
#define STRTNAMSIZ      34
#define CITYSIZ         34
#define BUILDSIZ        34
#define ACLSIZ          3
#define NAMSIZ          15
#define APTSIZ          8
#define CODESIZ         5
#define PHONESIZ        20

struct acct_info // size=256
{
    short num;                           
    char disabled;                       
    char modified;                      
   struct dis_accts restrict[MAX_DIS_ACCTS];
                                       
};
struct dis_accts    /* size 16 bytes */ 
{
    char accnt_num[RESTR_ACC_CUS_SIZE];
    long cus_num;
};

struct addr_struct //size=
{
    long x;                     
    long y;                     
    short zone;                
    short map_page;
    char map_ref[4];
    union postal_info
    {
        char postcode[8];          
        long zip;               
    }postal;
    char num[STRTNUMSIZ];               
    char street[STRTNAMSIZ];           
    char city[CITYSIZ];             
    char building[BUILDSIZ];           
    short junk;                 
};


struct phone_struct //size=20
{
    char digits[PHONESIZ];
};                                      

struct flt_access //size = 2B
{
    char disabled;                      
    char req_driver_id;                 
};

struct fleet_info
{
    char    name[24];                           
    short   number;                             
    short   num_of_taxis;                          
    struct  acct_info acct;          # h 2B 256s
    struct  addr_struct address;     # 2I 2h 4s I 8s 34s 34s 34s h                
    struct  phone_struct phone;      # 20s              
    struct  flt_access fl;           # 2B                
    char    dues;
    char    callout;                           
    char    dispatch_mode;                          
    char    offduty_form;                          
    char    zone_set;                           
    char    MDT_group;                          
    char    share_stale_fares;                      
    char    meteronrebooktimer;                     
    char    first_book_in_dest_on;                      
    unsigned char  no_activity_book_off_time;               
    unsigned char max_meton_time_to_retain_qpos;               
    unsigned char max_time_to_arrive_in_dest_zone;              
    short   next_first_dest_book_timer;                             
    char    DBOOKfeature;                           
    char    WakeupDriver;                              
    char    scarce_enabled;                           
    char    CCusefltname;                              
    unsigned long scarce_attributes;                    
    short   calloutlimit;
    char    prefix[6];
    struct  CalloutTime callouttime;                    
    short   virtualfleet;                               
    short   priorityzone;                               
    char    curbrotation;
    char    meterinstalled;
    char    pollmeterstats;
    char    secondarycontact[20];
    char    override_payment;                       
    char    VDM_MDTControlEnabled;
    char    ContinuousGPSUpdate;                       
    char    AutoLogin;                          
    char    AutoBook;                           
    unsigned long VDM_MDTControl;                      
    short   TempBookOffDuration;                        
    short   TempBookOffInterval;                        
    short   TempBookOffTimes;                       
    char    AllowedToViewDestinationAddr;                   
    char    PromptWheelChairFlagForm;                  
    char    NotifyModification;                    
    char    PostAllRides;                           
    char    AppliedLocal;                          
    char    MaxLocal;                             
    char    RebookOnMeterOff;                       
    char    GenerateLateETA;
    char    GenerateFarPickup;
    short   alternate_fleet[FLEETBACKUP];          
    char    FareDispatchMethod;                    
    char    MarketId[MARKETIDLEN+1];               
    char    pad[450];
};                                                



'''

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


if __name__ == "__main__":
    try:
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
        

    except Exception as e:
        sys.stdout.write("%s: Exception in %s -  %s\n" % (
                datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT), sys._getframe().f_code.co_name, str(e)))
