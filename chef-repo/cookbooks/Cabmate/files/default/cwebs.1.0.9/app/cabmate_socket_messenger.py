from gevent import monkey; monkey.patch_all()
import sys
import struct
import json
import datetime
import requests
from bottle import Bottle, request, response
from random import randint

import errormsg as ErrorMsg

import msgconf
import cabmsg
import config.cwebsconf as Config
import thread
import time
import format_field

class CabmateSocketMessenger():
    def __init__(self, dic):
        try:
            self.action_id=0
            self.action=''
            self.fare=0
            self.taxi=0
            self.event_no=0
            self.zone=17
            self.fleet=[]
            self.lon= 70.111
            self.lat= 45.1111

            if isinstance(dic, dict):
                self.populate_object(dic)
            self.error = False
            res = {}

        except Exception as e:
            sys.stdout.write("%s: %s - Exception %s\n" % (
                datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT), sys._getframe().f_code.co_name, str(e)))
            self.error = True

    def __str__(self):
        return " action:%s event_no:%d fare:%d taxi:%d action_id:%d  " \
               %(self.action,
                self.event_no,
                self.fare,
                self.taxi,
                self.action_id)

    @staticmethod
    def get_action_id(action):
        try:
            my_dic = dict (zip( (msgconf.MT_NO_ENTRY_STR,
                            msgconf.MT_YES_ENTRY_STR,
                            msgconf.MT_KEEP_ENTRY_STR,
                            msgconf.MT_CLR_ENTRY_STR,
                            msgconf.MT_ADD_QENTRY_STR,
                            msgconf.DUMP_QUEUES_STR,
                            msgconf.MT_EMERG_CLR_STR,
                            msgconf.CLEAR_EMERGENCY_EVENT_STR,

                            msgconf.MT_CLIENT_HELLO_STR,
                            ),
                            (msgconf.MT_NO_ENTRY,
                              msgconf.MT_YES_ENTRY,
                              msgconf.MT_KEEP_ENTRY,
                              msgconf.MT_CLR_ENTRY,
                              msgconf.MT_ADD_QENTRY,
                              msgconf.DUMP_QUEUES,
                              msgconf.MT_EMERG_CLR,
                              msgconf.MT_EVENT_MSG,

                              msgconf.MT_CLIENT_HELLO,
                            ) 
                            ))
            if action in my_dic:
                print ' get_action_id returning %d ' % (my_dic[action])
                return my_dic[action]
            if action in [msgconf.MT_NO_ENTRY,
                           msgconf.MT_YES_ENTRY,
                           msgconf.MT_KEEP_ENTRY,
                           msgconf.MT_CLR_ENTRY,
                           msgconf.MT_ADD_QENTRY,
                           msgconf.DUMP_QUEUES,
                           msgconf.MT_EMERG_CLR,
                           msgconf.MT_EVENT_MSG,

                           msgconf.MT_CLIENT_HELLO,
                           msgconf.LM_CPU_SPEED,

                           msgconf.MT_GE_CALL,
                           ]:
                return action
        except Exception as e:
            sys.stdout.write("%s: %s = Exception %s\n" % (
                datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT), sys._getframe().f_code.co_name,  str(e)))

        return 0

    def populate_object(self, dic):
        try:
            if 'event_no' in dic:
                self.event_no = dic['event_no']
            if 'taxi' in dic:
                self.taxi = dic['taxi']
            if 'fare' in dic:
                self.fare = dic['fare']
            if 'action' in dic:
                self.action = dic['action']
                if self.action == "ClearEmergencyEvent":
                    self.event_no = msgconf.EV_EMERG_CLR 
            if 'action_id' in dic:
                self.action_id = dic['action_id']
            if 'zone' in dic:
                self.zone = dic['zone']
            if 'fleet' in dic:
                if type(dic["fleet"]) == list:
                    self.fleet = [i for i in dic["fleet"] ]
                else :
                    self.fleet = dic['fleet'] 

        except Exception as e:
            sys.stdout.write("%s: %s -  Exception %s\n" % ( \
                datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT), sys._getframe().f_code.co_name, str(e)))
            self.error = True

    def get_error(self):
        return self.error

    def get_result(self):
        return self.res

    def send_msg(self, dic=None):
        try:
            sys.stdout.write("%s: entering %s\n" % (
                datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT), sys._getframe().f_code.co_name))

            res = {"status": 200, "result": {"message": "OK"}, "action" : self.action}

            if dic is not None:
                self.populate_object(dic)
                if self.error is True:
                    return json.dumps(res)

            self.action_id = CabmateSocketMessenger.get_action_id(self.action)
            if self.action_id == 0:
                res['result']['message'] = 'failure: invalid action type'
                return json.dumps(res)


            if len (self.fleet) == 0:
                self.error = True
                res = {"status": 500, "result": {"message": "You must provide fleet number"} }
                return json.dumps(res)                

            '''
            if self.event_no not in [3,5,6,16,18, 19, 22, 25,28, 32, 35,36,59, 65, 66, 67, 68, 80, 73, 90,136, 157, 159,162,164]:
                res['result']['message'] = 'failure: invalid event number'
                return json.dumps(res)


            '''

            '''
            struct msg_struct
            {
   	            int ms_srcuid;
	            int ms_dstuid;
	            int ms_scnduid;
	            int ms_msgtype;
	            int ms_datasize;
	            char ms_srcmch;
	            char ms_dstmch;
	            char ms_priority;
	            char ms_reserved;
	            char ms_msgdata[ MAX_MSG_DATA_SIZE ];
            };

            struct msgbuff
            {
	            long msgpriority;
	            struct msg_struct msg_struct;
            };

            struct hello
            {
                char msgtype[4];
                long totsiz;
                long id;
                long machinetype;
                long machinenumber;
                long time; 
                char hostname[24];
                char cabWinRev[12];
            };
           
           struct client
            {
                long pid;
                long id;
            };

            struct localmsg
            {
                char msgtype[4];
                long totsiz;
                unsigned char lmtype;
                unsigned char flag1;   /* 1 = fares.fl, 2=futures 3=regulars 4=credit for message 21 RL 12.4.0 */
                unsigned char flag2;
                unsigned char flag3;
                char Sdata1[16];
                char Sdata2[16];
                long Ldata1;
                long Ldata2;
            };


struct fare_info_struct
{
    long fare_num;
    long fstatus;
    long dm_fstatus;
    long cus_num;
    long fare_amount;                           /* stores rate and/or authorize amount */
    long driver_id;
    long vip_num;
    long reg_fare_num;                          /* future/regular runs */
    long reg_disp_time;
    long pass_on_brd;                           /* for trip num Alan or HUB callnum by RL */
    long orig_time;                             /* Used to be in 2nd ff */
    unsigned long sys_ftypes1;                      /* second set of 32 bits */
    long passengers;
    unsigned fstatus1;
    long orig_rate;                             /* original rate/ meter price */
    long webId;                                 /* The Web User Id of who placed the call */

    struct addrstop stops[2];                       /* Pickup and destination */
    struct forminfo forms[2];
    struct phone_struct phone;
    struct special_data user_data;
    struct fdv_types fdvt;
    struct combat_vals point_val;
    struct redisp_fltinfo rflt;                     /* Used to be in 2nd ff */

    union fis_payment
    {                                   // Job can be charged to flexydial
        struct ttab_struct ttab;                    // or Taxitab
//      struct cabchrg_struct cabchg;                   // or Cabcharge
        char creditcard[FORMLEN];                   // or Credit Card
    } payment;
    unsigned long veh_class_32;
    struct g_event_xy code_9_event;
    union run_q_event                           // Richard November 5, 2007
    {
        struct g_event_xy code_77_event;
        struct run_info runinfo;
    } rgev;
    /* The reginfo is used in time calls file in job file events are used */
    union space_saver
    {
        struct g_event fare_events[NUM_FARE_EVENTS];
        struct regrun_info reginfo;
    } ss;
    /* The xjobinfo is used for either xtra pickups OR xtra remarks info */
    union extrajobinfo
    {
        struct xpickups xpickups[6];                    /* the remaining 6 pickup/dest addrs */
                                        /* the 6 form # 1 */
        char xremarks[6][MDTLINELEN];
    } xjobinfo;
    union extraforminfo
    {
        struct forminfo xforms[6];                  /* 6 form # 2 */
        char formspace[396];
    } xforminfo;
    struct reg_track regtrack;                      /* 16 bytes, was char structpad[16] */
    short que_priority;
    short prior_incr_time;
    short amount_type;
    short authorization_num;
    unsigned short fi_taxi;
    short fleet;                                /* Fare's or veh's fleet num */
    short taxi_dest_zone;
    short going_home_code;                          // CabWin is using rate/mileage
    short fare_fleet;
    unsigned short offer_taxi;
    short reserv_count;                         /* Used to be count in 2nd ff */ // 12.4.0 b12 used for CBOOK Zone
    short reserv_manifest;                          /* Used to be manifest in 2nd ff */
    unsigned short port_number;                     /* Used to be in 2nd ff */
    short orig_id;                              /* Used to be in 2nd ff */
    unsigned short reg_lead_time;                       /* regular/fut's last value */
    unsigned short reg_marks;                       /* reg, fut     */
    long reg_upd_time;                          /* reg, fut, when updating lead_time */
    char reg_sign;                              /* reg, fut's sign in queue     */
    unsigned char flag; /* was char shortpad before reg_lead_time,reg_marks,upd_time, reg_sign */
    char remarks[4][MDTLINELEN];
    char bid_info[4][MDTLINELEN];
    char accnt_num[12];     /* Used to be prog_accnt_num */
    char accnt_name[20];            /* Used to be acc_name */
    unsigned char codemsgctr;       /* unsigned char unused; */
    unsigned char quantity;
    unsigned char modem;            /* Used to be in 2nd ff */
    char driver_name[24];
    unsigned char   Flag2;      //Was uk_ftype October 7, 2014 RL
    char skadden_bits;
    char num_parcel;
    char weight;
    unsigned char Flag1;        // was loc before , recycled
    char landmark[MDTLINELEN];
    char borough[3];        /* the zip alias */
    long cc_rec_num;
    struct ei_config ei_conf;
    struct phone_struct xphones[6]; //Other pickup phone #s
    struct cvd_resp cvdresp[CVDRESPLEN];
    union pad_share
    {
        char charpad[4];//was 166 before cvdresp - was 286 before multi phones
        long rebuilt_time; /* only for tracking reg,fut,when rebuilding link */
    } ps;                                   /* was charpad[4], not a union  */
    char cvd_call_cycle;
    char q_posn;
    struct airport_info airport;
    short   CoPay;
};


            '''
            try:
                operator_id = 1200
                qid=0                
                attr=63
               
                base_fmt = 'I I I I I B B B B'
                dest = msgconf.CLISRV
                if self.action_id in [ msgconf.MT_CLIENT_HELLO ] :
                    #dHello = ('H   ', 0, 0, 0, 0, 0, 'LOCAL MACHINE ', 'CWEBS 1.0 ' )
                    #sh = struct.Struct('4s 5I 24s 12s')                    
                    #msgconf.CWEBS
                    dHello = (299, 299)
                    sh = struct.Struct('2I')
                    packed_hello = sh.pack(*dHello)
                    ss_hello = struct.Struct(base_fmt + '%ds' % (sh.size))
                    cabmsg.gmsg_send(packed_hello, sh.size, dest , 0, msgconf.MT_CLIENT_HELLO, ss_hello, msgconf.CWEBS)
                    
                if  self.action_id == msgconf.LM_CPU_SPEED:
                    dData = ('L   ', 0, msgconf.LM_CPU_SPEED, 0,0,0)
                    print 'dData ', dData
                    s = struct.Struct('4s I 4B')
                    packed_data = s.pack(*dData)
                    ss_data = struct.Struct(base_fmt + '%ds' % (s.size))            
                    cabmsg.gmsg_send(packed_data, s.size, dest , 0, msgconf.LM_CPU_SPEED, ss_data, msgconf.CWEBS)

                if  self.action_id == msgconf. MT_GE_CALL or self.action_id == msgconf. MT_HAILED_TRIP :
                    dest = msgconf.TFC
                    port_number=Config.BOTTLE_PORT
                    sspare=0
                    requester_ip= Config.BOTTLE_IP
                    #seqno = self.generate_SeqNo()
                    from socketcli import sClient
                    seqno = sClient.generate_seqno()
                    dData = (0, 0 ,0,0, 0,0,0,0,0,0,0,0,0,0, 0, 0,  ' ', port_number, sspare, requester_ip, seqno, 0)
                    print 'dData ', dData
                    s = struct.Struct('16I 4192s H H 64s 10s H')
                    packed_data = s.pack(*dData)
                    ss_data = struct.Struct(base_fmt + '%ds' % (s.size))            
                    cabmsg.gmsg_send(packed_data, s.size, dest , 0,  self.action_id, ss_data, msgconf.CWEBS)
                       


                '''
                else :
                    dData = (self.event_no, self.taxi, 0, self.fare)
                    print 'dData ', dData
                    s = struct.Struct('4I')
                    packed_data = s.pack(*dData)
                    ss_data = struct.Struct(base_fmt + '%ds' % (s.size))               
                
                cabmsg.gmsg_send(packed_data, s.size, dest, msgconf.CWEBS, self.action_id, ss_data,operator_id)

                if self.action_id not in [ msgconf.DUMP_QUEUES, msgconf.MT_EMERG_CLR, msgconf.MT_EVENT_MSG] :
                    dHello = (self.event_no, 0, self.fare,0,0,0,0,0, self.lon, self.lat, self.zone, self.taxi, msgconf.CWEBS, attr, operator_id, qid, self.fleet)
                    sh = struct.Struct('8I 2f 7h')
                    packed_hello = sh.pack(*dHello)
                    ss_hello = struct.Struct(base_fmt + '%ds' % (sh.size))
                    cabmsg.gmsg_send(packed_hello, sh.size, msgconf.Q_PROC, 0, msgconf.MT_QUE_GOODBYE, ss_hello, operator_id)

                '''
            except Exception as e:
                sys.stdout.write("%s: %s *** Exception %s\n" % (
                    datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT),  sys._getframe().f_code.co_name, str(e)))
                self.error = True
                res = {'status': 500, 'result': {'message': ErrorMsg.ERROR_MSG_EXCEPTION}}
                return json.dumps(res)

            res = {"status": 200, "result": {"message": "OK"}}

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
                   #{ "action_id" :  msgconf.MT_CLIENT_HELLO, "action" :  msgconf.MT_CLIENT_HELLO } ,
                   #{ "action" :  msgconf.LM_CPU_SPEED  } ,
                   #{ "action" :  msgconf.MT_GE_CALL  } ,

                 
                ]
        
        #thread.start_new_thread (cabmsg.receive_q)
        for k in my_dic:
            m = CabmateSocketMessenger(k)
            if m is not None:
                print m
                resp = response
                for i in range(1):
                    r = m.send_msg(k)
                    print r
                    time.sleep(1)

        '''
        time.sleep(1)
        driver_id=8080
        taxi=8080
        fleet_num = 2
        s  = struct.Struct('8I 2f 7h c B 33s 33s 33s 33s B B c c')        
        dData = (56, long(time.time()), 0, driver_id, 0, 0, 0, 0, 0.0, 0.0, 
                     0, taxi,0, 0, 0, fleet_num, 0, 
                     ' ', 3,
                     format_field.format_field("MDT SYNC REQUEST", 33),
                     33*" ", 33*" ", 33*" ", 0, 0, ' ', ' ')

        packed_data = s.pack(*dData)
        ss_data = struct.Struct(cabmsg.base_fmt + '%ds' % (s.size))            
        dest = msgconf.TFC                
                
        cabmsg.gmsg_send(packed_data, s.size, dest, msgconf.CWEBS,  msgconf.MT_VERIFY_ID, ss_data, 99)

        #myQ = cabmsg.CabmateQ()
        #myQ.send_login_msg(data=dData, msgid=1)
        #myQ.reset()

        '''
        from itcli import create_fare_to_bin
        packed_data, size_data = create_fare_to_bin()
        base_fmt = 'I I I I I B B B B'
        dest = msgconf.TFC
        port_number=Config.BOTTLE_PORT
        sspare=0
        requester_ip= Config.BOTTLE_IP
        from socketcli import sClient
        seqno = sClient.generate_seqno()

        ss_data = struct.Struct(base_fmt + '%ds' % ( size_data ) )            
        cabmsg.gmsg_send(packed_data, size_data, dest , 0, msgconf. MT_GE_CALL, ss_data, msgconf.CWEBS)

        time.sleep(1)

    except Exception as e:
        sys.stdout.write("%s: Exception in %s -  %s\n" % (
                datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT), sys._getframe().f_code.co_name, str(e)))

        time.sleep(10)
