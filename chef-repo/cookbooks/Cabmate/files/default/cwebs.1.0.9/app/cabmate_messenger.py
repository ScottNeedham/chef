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

class CabmateMessenger():
    def __init__(self, dic):
        try:
            self.action_id=0
            self.action=''
            self.fare=0
            self.taxi=0
            self.event_no=0
            self.zone=1
            self.fleet=[]
            self.fleet_id= 0
            self.lon= 0.0
            self.lat= 0.0
            self.errorMsg=None
            self.operator_id = 1000

            res = {}
            self.error = False

            if isinstance(dic, dict):
                self.populate_object(dic)

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
                            ),
                            (msgconf.MT_NO_ENTRY,
                              msgconf.MT_YES_ENTRY,
                              msgconf.MT_KEEP_ENTRY,
                              msgconf.MT_CLR_ENTRY, #543
                              msgconf.MT_ADD_QENTRY,
                              msgconf.DUMP_QUEUES,
                              msgconf.MT_EMERG_CLR,
                              msgconf.MT_EVENT_MSG,
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
                if self.action in [ "ClearEmergencyEvent", "EmergencyClear"]:

                    self.event_no = msgconf.EV_EMERG_CLR # = 18

            if 'action_id' in dic:
                self.action_id = dic['action_id']
            if 'zone' in dic:
                self.zone = dic['zone']
            if 'operator_id' in dic :
                self.operator_id = dic['operator_id']
            if 'fleet' in dic:
                if type(dic["fleet"]) == list:
                    self.fleet = [i for i in dic["fleet"] ]
                else :
                    self.fleet.append (dic['fleet'] )
                self.fleet_id = self.fleet[0]

  
            if len (self.fleet) == 0 or self.taxi == 0 :
                self.error = True 
                self.errorMsg = "You must provide fleet number and taxi number"               

        except Exception as e:
            sys.stdout.write("%s: %s -  Exception %s\n" % ( \
                datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT), sys._getframe().f_code.co_name, str(e)))
            self.error = True

    def get_error(self):
        return self.error, self.errorMsg

    def get_result(self):
        return self.res

    def format_fleet(self):
        m = ['', '' ]
        
        rem=0
        if type(self.fleet) != list:
            return  [33 * b'\x00' , 33 * b'\x00' ]

        if len( self.fleet) > 8:
            rem = len( self.fleet) - 8
        if rem > 8 :
            rem = 8        
        rng = [8,  rem] 
        lst = [ self.fleet[0:8], self.fleet[8:16] ]
        idx=0
        #print self.fleet
        for row in rng:              
            l = lst[idx]
            print l         
            for x in lst[idx]:                                                                     
                m[idx] += str(x).rjust(4,'0')  
            print len  ( m[idx])       
            m[idx] +=  (33 - len(m[idx]) ) * b'\x00' 
            idx +=1  

        print len(m[0]), len(m[1])
        return m

    def send_msg(self, dic=None):
        try:
            sys.stdout.write("%s: entering %s\n" % (
                datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT), sys._getframe().f_code.co_name))

            res = {"status": 200, "result": {"message": "OK"}, "action" : self.action}

            
            if self.error is True:
                return json.dumps(res)

            self.action_id = CabmateMessenger.get_action_id(self.action)
            if self.action_id == 0:
                res['result']['message'] = 'failure: invalid action type'
                return json.dumps(res)

            if self.event_no not in [3,5,6,16,18, 19, 22, 25,28, 32, 35,36,59, 65, 66, 67, 68, 80, 73, 90,136, 157, 159,162,164]:
                res['result']['message'] = 'failure: invalid event number'
                return json.dumps(res)

            if len (self.fleet) == 0:
                self.error = True
                res = {"status": 500, "result": {"message": "You must provide fleet number"} }
                return json.dumps(res)                

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

            struct g_event_msg
            {
	            long event_no;
	            long time;				/* time event happened at */
	            long fare;				/* fare number if required */
	            long other_data;		/* other data if required */
	            long qual;              /* qualifier field used by q_proc */
	            long fstatus;
	            long meter_amount;		/* from longpad[2] */
	            long longpad;			/* padding */
	            float x ;				/* long xxx.xxxxxx */
	            float y ; 				/* lat yyy.yyyyyy */
	            short zone;				/* zone number if required */
	            short taxi;				/* taxi number if required */
	            short resp_uid;			/* who to send any response to */
	            short attribute;        /* used to store parcel/region */
	            short qid;              /* uid of who get q mesg */
	            short fleet;			/* for fleet access converted from shortpad[0] */
	            short redisp_taxi;		/* for now school runs taxi number */
	            char merchant_group;	/* convert spare[0] to this for cc_proc */
	            char num_sats ;			/* number of satellites 0-4 */
	            char mesg[4][33];		/* stores, msgs, forms, xnumreq ...*/
            	char rel_queue ; 		/* relative queue, bad comm... */
	            unsigned char statusbits;
            };

            MT_DEL_QENTRY
            event_no = *(int *)m->ms_msgdata;
            fare
            '''
            try:
                
                qid=0x400                
                attr=63
                
                base_fmt = 'I I I I I B B B B'
                dest = msgconf.Q_PROC

                if self.action_id not in [ msgconf.DUMP_QUEUES, msgconf.MT_EMERG_CLR, msgconf.MT_EVENT_MSG ] :
                    dHello = (self.event_no, 0, self.fare,0,0,0,0,0, 0.0, 0.0, self.zone, self.taxi, msgconf.CWEBS, attr, self.operator_id, qid, self.fleet_id)
                    sh = struct.Struct('8I 2f 7h')
                    packed_hello = sh.pack(*dHello)
                    ss_hello = struct.Struct(base_fmt + '%ds' % (sh.size))
                    cabmsg.gmsg_send(packed_hello, sh.size, msgconf.Q_PROC, 0, msgconf.MT_QUE_HELLO, ss_hello, self.operator_id)

                if self.action_id ==  msgconf.MT_ADD_QENTRY:
                    dData = (self.event_no, 0, self.fare, 0, 0, 0, 0, 0, self.lon, self.lat, self.zone, self.taxi,  msgconf.CWEBS, attr, qid, self.fleet_id)
                    print 'dData ', dData
                    s = struct.Struct('8I 2f 6h')
                    packed_data = s.pack(*dData)
                    ss_data = struct.Struct(base_fmt + '%ds' % (s.size))


                # CLEAR EMERGENCY MT_CLR_ENTRY = 543 EV_EMERG = 18
                elif self.action_id == msgconf.MT_EMERG_CLR:
                    m = self.format_fleet()
                   
                    dData = (msgconf.EV_EMERG, 0, self.fare, 0, 0, 0, 0, 0, \
                            self.lon, self.lat, self.zone, self.taxi,  msgconf.CWEBS, attr, qid, self.fleet_id, \
                            1, 2, 3, m[0], m[1], 66 * b'\x00', 0, 0)
                    print 'Sending to Q_PROC dData ', dData
                    s = struct.Struct('8I 2f 6h 1h 2b 33s 33s 66s 2b')
                    packed_data = s.pack(*dData)
                    ss_data = struct.Struct(base_fmt + '%ds' % (s.size))            
                    dest = msgconf.Q_PROC
                    self.action_id = msgconf.MT_CLR_ENTRY #= 543                       

                elif  self.action_id == msgconf.MT_EVENT_MSG:
                    dData = (self.event_no, 0, self.fare, 0, 0, 0, 0, 0, self.lon, self.lat, self.zone, self.taxi,  msgconf.CWEBS, attr, qid, self.fleet_id)
                    print 'Sending to  TFC dData ', dData
                    s = struct.Struct('8I 2f 6h')
                    packed_data = s.pack(*dData)
                    ss_data = struct.Struct(base_fmt + '%ds' % (s.size))            
                    dest = msgconf.TFC

                else :
                    dData = (self.event_no, self.taxi, 0, self.fare)
                    print 'dData ', dData
                    s = struct.Struct('4I')
                    packed_data = s.pack(*dData)
                    ss_data = struct.Struct(base_fmt + '%ds' % (s.size))               
                
                cabmsg.gmsg_send(packed_data, s.size, dest, msgconf.CWEBS, self.action_id, ss_data, self.operator_id)


                if self.action_id not in [ msgconf.DUMP_QUEUES, msgconf.MT_EMERG_CLR, msgconf.MT_EVENT_MSG] :
                    dHello = (self.event_no, 0, self.fare,0,0,0,0,0, self.lon, self.lat, self.zone, self.taxi, msgconf.CWEBS, attr, self.operator_id, qid, self.fleet_id)
                    sh = struct.Struct('8I 2f 7h')
                    packed_hello = sh.pack(*dHello)
                    ss_hello = struct.Struct(base_fmt + '%ds' % (sh.size))
                    cabmsg.gmsg_send(packed_hello, sh.size, msgconf.Q_PROC, 0, msgconf.MT_QUE_GOODBYE, ss_hello, self.operator_id)


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

    def send_hello(self):
        try:
            base_fmt = 'I I I I I B B B B'
            dest = msgconf.Q_PROC            
           
            qid=0x400                
            attr=63
            mt = msgconf.MT_QUE_HELLO        
           
            m = self.format_fleet()   
            dData = (msgconf.EV_EMERG, 0, self.fare, 0, 0, 0, 0, 0, self.lon, self.lat, self.zone, self.taxi,  msgconf.CWEBS, attr, qid, self.fleet_id, \
                                 1, 2, 3, m[0], m[1] ,66 * b'\x00', 0, 0)
            print 'sending Hello to Q_PROC dData ', dData

            s = struct.Struct('8I 2f 6h 1h 2b 33s 33s 66s 2b')

           
            packed_hello = s.pack(*dData)
            ss_hello = struct.Struct(base_fmt + '%ds' % (s.size))
            cabmsg.gmsg_send(packed_hello, s.size, dest, 0, mt, ss_hello, self.operator_id)
        except Exception as e:
            sys.stdout.write("%s: %s - Exception %s\n" % (
                datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT), sys._getframe().f_code.co_name,  str(e)))

    def send_goodbye(self):
        try:
            base_fmt = 'I I I I I B B B B'
            dest = msgconf.Q_PROC                        
           
            qid=0x400                
            attr=63
            mt = msgconf.MT_QUE_GOODBYE
            dMsg = (0, 0, self.fare,0,0,0,0,0, self.lon, self.lat, self.zone, self.taxi, msgconf.CWEBS, attr, self.operator_id, qid, self.fleet_id)
            sh = struct.Struct('8I 2f 7h')
            packed_hello = sh.pack(*dMsg)
            ss_hello = struct.Struct(base_fmt + '%ds' % (sh.size))
            cabmsg.gmsg_send(packed_hello, sh.size, dest , 0, mt, ss_hello, self.operator_id)
        except Exception as e:
            sys.stdout.write("%s: %s - Exception %s\n" % (
                datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT), sys._getframe().f_code.co_name,  str(e)))

            


if __name__ == "__main__":
    try:
        my_dic = [ #{"event_no" : msgconf.EV_EMERG, "action" : "AddEntry", "fare" : 0, "taxi" : 9006 },
                   #{"event_no" : msgconf.EV_EMERG, "action" : "ClearEntry", "fare" : 0, "taxi" : 8089 },
                   #{"event_no" : msgconf.EV_EMERG, "action" : "EmergencyClear", "taxi" : 8089 },
                   { "action" :  "ClearEmergencyEvent", "taxi" : 8089, "fleet" : [ 1, 2, 3, 5,6,7,8,56,78,98,76,54,34,12,5 ] },
                    { "action" :  "ClearEmergencyEvent", "taxi" : 8089, "fleet" : 1 },                   
                    #{"event_no" : msgconf.EV_EMERG, "action" : "DumpQueues" }
                ]

        for k in my_dic:
            m = CabmateMessenger(k)
            if m is not None:
                print m
                #resp = response
                #r = m.send_msg(k)
                r = m.format_fleet()
                

                print r
                print len(r[0]), len(r[1])

    except Exception as e:
        sys.stdout.write("%s: Exception in %s -  %s\n" % (
                datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT), sys._getframe().f_code.co_name, str(e)))
