import sys
import time
import struct
import binascii
import sysv_ipc
import msgconf
import datetime
import smalldb

import config.cwebsconf as Config
import errormsg as ErrorMsg
import format_field
from bottle import  request, response
import json
import cwebsserv
import readhmac
import hmac
import hashlib
import hmac
import base64
import requests

import cabmsg


MAX_NUM_ENTRIES = 3
MAX_ENTRY_LEN   = 32

class SupervisorMessage():

    def __init__(self, dic):
        self.error = True
        self.res = {}
        try:
            self.driver_id = -1
            self.code = 0
            self.authority_id = -1
           
            self.taxi = -1
            self.fleet = -1

            self.mesg = []
            
            for i in range(MAX_NUM_ENTRIES):
                self.mesg.append(MAX_ENTRY_LEN*' ')
    
            self.res = self.populateObject(dic)


            self.error = False
        except Exception as e:
            self.error = True

    def getError(self):
        return self.error

    def getResult(self):
        return self.res

    def populateObject(self, dic):

        response.status = 200
        res = {"status": response.status, "result": {"message": "OK"}}

        try:
            if dic:
                if "fleet" in dic:
                    self.fleet = int(dic["fleet"])
                if "driver_id" in dic:
                    self.driver_id = int(dic["driver_id"])
               
                if "taxi" in dic:
                    self.taxi = int(dic["taxi"])
                       
                if dic.has_key("mesg"):
                    if len(dic["mesg"]) > 0:
                        for m , i in zip(dic["mesg"], range(len(dic["mesg"])) ):
                            if len(m) >MAX_ENTRY_LEN:
                                m = m[:MAX_ENTRY_LEN]
                            self.mesg[i] = format_field.format_field(m, MAX_ENTRY_LEN, True)

                if not dic.has_key('authority_id'):
                    #sys.stdout.write("%s: no authority id %s\n" % (datetime.datetime.strftime(datetime.datetime.now(),  '%Y-%m-%d %H:%M:%S')  , str(e) ))   
                    res['result']['message'] = 'failure: authority_id field is missing'
                    self.error = True
                    res ["status"] = 500                    
                    return res
                    
                try:
                    self.authority_id = int(dic["authority_id"])
                except Exception as e:
                    #sys.stdout.write("%s: no authority id %s\n" % (datetime.datetime.strftime(datetime.datetime.now(),  '%Y-%m-%d %H:%M:%S')  , str(e) ))     
                    res['result']['message'] = 'failure: authority_id is not int'
                    self.error = True
                    res ["status"] = 500
                    return res
                    

                if not dic.has_key('msg_id'):
                    res['result']['message'] = 'failure: code id field is missing'
                    self.error = True
                    res ["status"] = 500
                    return res
                    #sys.stdout.write("%s: no msg id \n" % (datetime.datetime.strftime(datetime.datetime.now(),  '%Y-%m-%d %H:%M:%S') ))     
                try:
                    self.code = int(dic['msg_id'])
                except Exception as e:
                    sys.stdout.write("%s: populateObject exception %s\n" % (datetime.datetime.strftime(datetime.datetime.now(),  '%Y-%m-%d %H:%M:%S'), str(e) ))                           
                    res['result']['message'] = 'failure: code id field is not int'
                    self.error = True
                    res ["status"] = 500
                    return res

        except Exception as e:
            sys.stdout.write("%s: populateObject Issue decoding dict - Exception %s\n" % (datetime.datetime.strftime(datetime.datetime.now(),  '%Y-%m-%d %H:%M:%S'), str(e) ))                           
            res['result']['message'] = 'Issue decoding dictionary'
            self.error = True
            res ["status"] = 500

        return res


    def send_msg(self, response, dic=None):
        #sys.stdout.write("%s: entering %s\n" % (datetime.datetime.strftime(datetime.datetime.now(),  '%Y-%m-%d %H:%M:%S'), ' send_msg' ))

        response.status = 200
        res = {"status": response.status, "result": {"message": "OK"}}

        try:
            if dic is not None :

                res = self.populateObject(dic)

                if self.error == True:
                    return json.dumps(res)
                       
            if self.code not in [0, 1, 2]:
                res['result']['message'] = 'failure: code id is not 0,1,2'
                return json.dumps(res)
            
            reason0 = reason1 = reason2 = '\0'
            '''
            struct coded_msg
            {
                long driver_id;
                long msg_num;
                short oper_id;
                char reason[3][32];
                short taxi;
                short fleet;
            };                          
            '''
            try:               
                dData = (self.driver_id, self.code, self.authority_id, ''.join(self.mesg), self.taxi, self.fleet)
                s  = struct.Struct('2I h 96s 2h')
                packed_code = s.pack( *dData)
                code_size = s.size
                ss = struct.Struct(cabmsg.base_fmt + '%ds' % (s.size))                
                cabmsg.gmsg_send(packed_code, code_size, msgconf.DM, 0, msgconf.MT_CODED_MSG_FROM_SUPERVISOR, ss)               
            except Exception as e:
                sys.stdout.write("%s: snd_msg exception %s\n" % (datetime.datetime.strftime(datetime.datetime.now(),  '%Y-%m-%d %H:%M:%S'), str(e) ))            
                self.error = True
                response.status = 500
                res = {'status': response.status, 'result': {'message':  ErrorMsg.ERROR_MSG_EXCEPTION}}
                  
           
            response.status = 200
            res = {"status": response.status, "result": {"message": "OK"}}

            return json.dumps(res)

        
        except Exception as e:
            sys.stdout.write("%s: send_msg exception %s\n" % (datetime.datetime.strftime(datetime.datetime.now(),  '%Y-%m-%d %H:%M:%S'), str(e) ))            
            self.error = True
            response.status = 500
            res = {'status': response.status, 'result': {'message':  ErrorMsg.ERROR_MSG_EXCEPTION}}
            return json.dumps(res)

