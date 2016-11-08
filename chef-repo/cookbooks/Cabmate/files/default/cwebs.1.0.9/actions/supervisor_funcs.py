# coding=utf-8
from gevent import monkey; monkey.patch_all()
from bottle import Bottle, view, template, redirect, request, response, static_file, run, abort, route
import gevent 
import datetime
import json
import sys
import time
import struct


import cabmsg
import format_field
import socketcli
import msgconf

import config.cwebsconf as Config

import server_utils as Utils
import errormsg as ErrorMsg

from fares.its_event import its_event

import supervisor_message as SupervisorMsg

import vehicle_message as VehicleMsg

def _supervisor_action():
    try:        
        sys.stdout.write("%s: supervisor action %s\n" % (
            datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT),
            str(request.environ) ))

        fleet_num=0
        taxi=0

        response =  Utils.prepare_header('_supervisor_action', "default")
        if  response.status == 401:
            return            

        clen = request.content_length
        request.body.seek(0)
        Utils.set_default_headers(response)
        response.status = 500
        res = {'status': response.status,
               'result': { 'message': 'failure'}}
        try:
            action_dic = json.loads(str(request.body.read(clen)))
            sys.stdout.write("%s: action dictionary %s\n" % (
                datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT),
                str(action_dic) ))
        except Exception as e:
            print 'Exception ', str(e)
            return json.dumps(res)

        if not action_dic.has_key('action'):
            res['result']['message'] = 'failure: action field is missing'
            return json.dumps(res)
        
        if not action_dic['action'] in ["suspend", "reinstate", "login", "logout", "coded_msg"]:
            res['result']['message'] = 'failure: invalid action field value'
            return json.dumps(res)

        if not action_dic.has_key('driver_id'):
            res['result']['message'] = 'failure: driver_id field is missing'
            return json.dumps(res)
        try:
            driver_id = int(action_dic['driver_id'])
            if driver_id <= 0 :
                res['result']['message'] = 'ERR: DRIVER LOGON ID CANNOT BE ZERO'
                return json.dumps(res)  
            if valid_driver(driver_id) == False:
                res['result']['message'] = 'ERR: INVALID DRIVER ID '
                return json.dumps(res)
        except Exception as e:
            res['result']['message'] = 'failure: driver_id field is not int'
            return json.dumps(res)

        if not action_dic["action"] in ["suspend", "reinstate"]:
            if not action_dic.has_key('taxi'):
                res['result']['message'] = 'failure: taxi field is missing'
                return json.dumps(res)
            try:
                taxi = int(action_dic['taxi'])
                if taxi < 0 or taxi >  msgconf.MAXVEHNUM:
                    res['result']['message'] = 'ERR: INVALID TAXI NUMBER'
                    return json.dumps(res)   
                if valid_taxi(taxi) == False:
                    res['result']['message'] = 'ERR: INVALID TAXI ID'
                    return json.dumps(res)        
            except Exception as e:
                res['result']['message'] = 'failure: taxi field is not int'
                return json.dumps(res)

            if not action_dic.has_key('fleet'):
                res['result']['message'] = 'failure: fleet field is missing'
                return json.dumps(res)
            try:
                fleet_num = int(action_dic["fleet"])
            except Exception as e:
                res['result']['message'] = 'failure: fleet is not integer'
                return json.dumps(res)
        else:
            if action_dic.has_key('taxi'):  
                taxi = int(action_dic['taxi'])
            if action_dic.has_key('fleet'):
                fleet_num = int(action_dic["fleet"])


        if action_dic["action"] in ["suspend", "reinstate"]:
            if not action_dic.has_key('authority_id'):
                res['result']['message'] = 'failure: authority_id field is missing'
                return json.dumps(res)
            try:
                #authority_id = int(action_dic["authority_id"])
                authority_id = msgconf.CWEBS
            except Exception as e:
                res['result']['message'] = 'failure: authority_id is not int'
                return json.dumps(res)
            duration = 0
            if action_dic['action'] == "suspend":
                duration = msgconf.default_susp_duration
                if action_dic.has_key('duration'):
                    try:
                        duration = int(action_dic['duration'])
                    except Exception as e:
                        duration = msgconf.default_susp_duration

            if not action_dic.has_key('msg_for_dispatch'):
                res['result']['message'] = 'failure: message for dispatch is not present'
                return json.dumps(res)
            msg_for_dispatch = str(action_dic["msg_for_dispatch"])
           
            if len(msg_for_dispatch) > 32:
                msg_for_dispatch = msg_for_dispatch[:32]

            if not action_dic.has_key('msg_for_driver'):
                res['result']['message'] = 'failure: message for driver is not present'
                return json.dumps(res)
            msg_for_driver = str(action_dic["msg_for_driver"])
            if len(msg_for_driver) > 32:
                msg_for_driver = msg_for_driver[:32]
            dData = (driver_id, duration, long(time.time()), authority_id, msg_for_dispatch, msg_for_driver,  '1', '2', taxi, fleet_num, 8*'X')
            print 'dData ', dData
            s = struct.Struct('I I I h 33s 33s c c h h 8s')  #  suspension data
            packed_data = s.pack( *dData)
            data_size = s.size
            
            ss = struct.Struct(cabmsg.base_fmt + '%ds' % (s.size))  
           
            if action_dic['action'] == "suspend":
                cabmsg.gmsg_send(packed_data, data_size, msgconf.DM, 0, msgconf.MT_SUSP_DRIVER, ss)
            if action_dic['action'] == "reinstate":
                cabmsg.gmsg_send(packed_data, data_size, msgconf.DM, 0, msgconf.MT_REIN_DRIVER, ss)
         
            response.status = 200
            res = {'status': response.status, 'result': {'message': 'OK'}}
            return json.dumps(res)

        if action_dic["action"] in ["login", "logout"]:           
            try:
                SeqNo = socketcli. sClient.generate_seqno()
                action_dic['other_data'] = driver_id
                action_dic['sequence_number'] = SeqNo

                response.status, resp_message, res = send_event_request(SeqNo, action_dic, response)

                sys.stdout.write("%s: returning out of send_event_request ... [%s] \n" % ( datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT) , json.dumps(res) ) )
       
                return Utils.make_error_response(response, response.status, resp_message, res)

            except Exception as e:          
                sys.stdout.write("%s: Exception 1 %s " % ( datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT), str(e) ))
                Utils.set_default_headers(response)
                response.status = 500
                res = {"status": response.status, "result": {"message": ErrorMsg.ERROR_MSG_GENERAL_ERROR}}
                return json.dumps(res)            
       
        if action_dic["action"] == "coded_msg":
            sprv_obj = SupervisorMsg.SupervisorMessage(action_dic)
            if sprv_obj.getError() is True:
                response.status = 500
                res = {"status": response.status, "result": {"message": ErrorMsg.ERROR_MSG_GENERAL_ERROR}}
                return json.dumps(res)

            return sprv_obj.send_msg( response, action_dic)

    except Exception as e:
        sys.stdout.write("%s: exception is raised in supervisor action : %s\n" % ( datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT), str(e) ))

        Utils.set_default_headers(response)
        response.status = 500
        res = {'status': response.status, 'result': { 'message': 'failure'}}
        return json.dumps(res)


def send_event_request(SeqNo, dic, response):

    try:       

        res = {"status": response.status, "result": {"message": ''}}

        try:   
        

            its_evt = its_event(dic)      
            its_evt.event_no = msgconf.EV_XNUMREQ            
            its_evt.time = int (time.time())
            dest = msgconf.DM
            mt = msgconf. MT_EVENT_MSG    
            scndid = 0
            if dic['action'] == "logout":
                scndid = 1
              
            response.status, resp_message, res = send_event_to_host(its_evt, SeqNo, dest, mt, scndid=scndid, nowait=True)

            if not resp_message:
                resp_message = ErrorMsg.ERROR_MSG_GENERAL_ERROR

            if not res :
                res = {"status": response.status, "result": {"message": resp_message}}                 
       
            if 'result' in res:               
                res['result']['message'] = resp_message 
            else:
                res['result'] = { "message": resp_message}

            print ' res ==> ', res, ' status=',  response.status     

            res["status"] =  response.status       
                       
            sys.stdout.write("%s: returning out of handler send_event_request ... [%s] \n" % ( datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT) , json.dumps(res) ) )
       
            return response.status, resp_message, res

        except Exception as e:          
            sys.stdout.write("%s: *** Exception 1 %s " % ( datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT), str(e) ))
            Utils.set_default_headers(response)
            response.status = 500
            res = {"status": response.status, "result": {"message": ErrorMsg.ERROR_MSG_GENERAL_ERROR}}
            return response.status,  ErrorMsg.ERROR_MSG_GENERAL_ERROR, res

    except Exception as e:
        sys.stdout.write("%s: *** Exception 2 %s " % ( datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT), str(e) ))
        Utils.set_default_headers(response)
        response.status = 500
        res = {"status": response.status, "result": {"message": ErrorMsg.ERROR_MSG_GENERAL_ERROR}}
        return response.status,  ErrorMsg.ERROR_MSG_GENERAL_ERROR, res

    return response.status, ErrorMsg.ERROR_MSG_GENERAL_ERROR, res




def send_event_to_host(its_evt, SeqNo, dest, mt, nowait=False, scndid=0):
    try:     
        response.status = 200
        resp_message = "success"
        res = {}

        try:
            
            #print its_evt
            packed_data, size_data, errmsg = its_evt.object_to_bin()
            
            #print ' size data ==> %d  errmsg=%s'  % ( size_data, errmsg )           

        except Exception as e:
            print "send_event_to_host 1: Exception", str(e)
            return Utils.make_error_response(response, 500, ErrorMsg.ERROR_MSG_GENERAL_ERROR)
        

        if errmsg == None and size_data > 0:
            base_fmt = 'I I I I I B B B B'                   

            print ' size data ==> %d '  % ( size_data )

            ss_data = struct.Struct(base_fmt + '%ds' % ( size_data ) )   

            cabmsg.gmsg_send(packed_data, size_data, dest , scndid, mt , ss_data, msgconf.CWEBS)

            sys.stdout.write("%s: message is sent to the %d queue\n" % ( datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT), dest )) 

            if nowait is True:
                return 200, "success", {}          

            m = None
           
            try:                
                status=-1

                try:
                    numSecs = Config.QueueTimeoutDic["default"]
                    numIters = int (numSecs/msgconf.Q_TIMESLOT)
                except Exception as e:
                    numIters =  2/msgconf.Q_TIMESLOT                

                for sleep_counter in range(numIters) :
                    m = cabmsg.gmsg_rcv2()              
         
                    if m != None and len(m) >= 3:
                        sys.stdout.write("%s:  Received response from %d queue\n" % ( datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT), dest )) 
                        if m[3] == msgconf.MT_ENTER_CALL and  m[38] == SeqNo:
                            #print 'Received response  msgconf.MT_ENTER_CALL ==> ', m, ' sleep_counter = ' , sleep_counter   
                            
                            job_number = str(m[11])
                            zone = m[19]
                            fare_type = "immediate"
                            response.status = 200
                            resp_message = 'success'
                            res = {"status": response.status, "result": {"message": resp_message, "job_number": job_number, "fare_type": fare_type,"zone": zone}}                        
                            status =0                            
                            break;

                         ### ???? ####
                        if m[3] == msgconf.MT_MODFAREINFO and  m[13] == SeqNo:
                            #print 'Received response  msgconf.MT_MODFAREINFO ==> ', m, ' sleep_counter = ' , sleep_counter   
                            
                            job_number = str(m[9]) 
                            zone = m[11]                          
                            fare_type = "immediate"
                            response.status = 200
                            resp_message = 'success'
                            res = {"status": response.status, "result": {"message": resp_message, "job_number": job_number, "fare_type": fare_type,"zone": zone}}                        
                            status =0                            
                            break;

                        elif m[3] == msgconf.MT_NEWFARE and m[13] == SeqNo:
                            #print 'Received response  msgconf.MT_NEWFARE ==> ', m, ' sleep_counter = ' , sleep_counter   
                            job_number = str (m[9]) 
                            fare_type = "future"
                            response.status = 200
                            resp_message = 'success'
                            res = {"status": response.status, "result": {"message": resp_message, "job_number": job_number, "fare_type": fare_type,"zone": zone}}                                                    
                            status =0                            
                            break;


                        ### ???? ####
                        elif m[3] == msgconf.MT_UPD_FARE and m[13] == SeqNo: 
                            #print 'Received response  msgconf.MT_UPD_FARE ==> ', m, ' sleep_counter = ' , sleep_counter   
                            job_number = str (m[9]) 
                            fare_type = "future"
                            response.status = 200
                            resp_message = 'success'
                            res = {"status": response.status, "result": {"message": resp_message, "job_number": job_number, "fare_type": fare_type,"zone": zone}}                                                    
                            status =0                            
                            break

                        elif m[3] == msgconf.MT_OP_ERR and len(m) > 12 and  m[12] == SeqNo :   
                            #print 'Received response  ### msgconf.MT_OP_ERR ==> ', m, ' sleep_counter = ' , sleep_counter   
                            if m[10] == ErrorMsg.TFC_ZONE_ERRNO:
                                resp_message = ErrorMsg.ERROR_MSG_TFC_ZONE_ERRNO
                            else:
                                resp_message = m[13]
                            response.status = 500 
                            status =0
                            break
                        
                        elif m[3] == msgconf.MT_OP_ERR and len(m) > 12 and  m[12] == 0 :   
                            #print 'Received response  &&& msgconf.MT_OP_ERR ==> ', m, ' sleep_counter = ' , sleep_counter , ' error=', m[9]  
                            resp_message = m[9]
                            response.status = 500 
                            status =0
                            break


                        elif m[3] == msgconf.MT_OP_ERR and len (m ) >=  10 :   
                            #print 'Received response  *** msgconf.MT_OP_ERR ==> ', m, ' sleep_counter = ' , sleep_counter  , ' error=', m[9]   
                            if m[9] == ErrorMsg.TFC_ZONE_ERRNO:
                                resp_message = ErrorMsg.ERROR_MSG_TFC_ZONE_ERRNO
                            else:
                                resp_message = m[9]
                            response.status = 500 
                            status =0
                            break
                      
                    else:
                        #sys.stdout.write("%s:  No response from %d queue\n" % ( datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT), dest )) 
                        if status < 0:                    
                            gevent.sleep(msgconf.Q_TIMESLOT)
                                         
            except Exception as e:
                sys.stdout.write("%s: send_event_to_host 2 : Exception %s\n" % (datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT),  str(e) ) )         
                return Utils.make_error_response(response, 500, ErrorMsg.ERROR_MSG_GENERAL_ERROR)

        else:
            sys.stdout.write("%s: *** Could not send message to %d queue ***\n" % ( datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT), dest )) 
            resp_message =  errmsg

        return response.status, resp_message, res
    except Exception as e:
        sys.stdout.write("%s: send_event_to_host 3 : Exception %s\n" % (datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT),  str(e) ) )         
        return response.status, ErrorMsg.ERROR_MSG_GENERAL_ERROR, res        



def valid_driver(id):
    try:
        isvalid = False
        dir_name = '/data/drivers'
        file_name = str(id)
        full_path = '/'.join( [ dir_name, file_name])
        fp = open(full_path, "r")
        if fp != None:          
            isvalid = True
            fp.close()
    except Exception as e:
        sys.stdout.write("%s: valid_driver : Exception %s\n" % (datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT),  str(e) ) )                 

    return isvalid        


def valid_taxi(myid):
    try:
        isvalid = False
        full_path = '/data/taxiptr.ind'        

        frmt = 'I'        
        data_size = struct.Struct(frmt).size
        s = struct.Struct(frmt)
        print 'data structure size ', data_size
    
        with open(full_path, "rb") as fp:     
            count = 0
            bRun=True
            while bRun:  
                count = count + 1
                data = fp.read(data_size)
             
                if not data:
                    break 
                else:
                    if len(data) == data_size:
                        udata = s.unpack(data)
                        if count == myid:                            
                            bRun = True
                            isvalid = True                   

        fp.close()
    except Exception as e:
        sys.stdout.write("%s: valid_taxi : Exception %s\n" % (datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT),  str(e) ) )                 

    return isvalid        




def _device_sendmsg_q():
    try:      
        sys.stdout.write("%s: device sendmsg %s\n" % (
        datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT), str(request.environ) ))
       
        response =  Utils.prepare_header('device_sendmsg', "default")
        if  response.status == 401:
            return            

        clen = request.content_length
        request.body.seek(0)
        Utils.set_default_headers(response)
        response.status = 500
        res = {'status': response.status, 'result': {'message': 'failure'}}
        try:
            sendmsg_dic = json.loads(str(request.body.read(clen)))
            sys.stdout.write("%s: sendmsg_dic %s\n" % (
                datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT),
                str(sendmsg_dic) ))
        except Exception as e:
            print 'Exception while retrieving the JSON data', str(e)
            return json.dumps(res)
        try:
            taxi_no = int(sendmsg_dic["vehicle_id"])           
        except Exception as e:
            res['result'] = {'message': 'invalid vehicle_id'}
            return json.dumps(res)

        #gmsg_send(uid, LOCAL, taxi, MT_VEH_MSG, sizeof(struct vehicle_message), ROUT_PRI, (char *)vmsg);
        try: 
            msgtext = sendmsg_dic["msgtext"] if sendmsg_dic["msgtext"] else "text message to " + str(taxi_no)
        except Exception as e: 
            res['result'] = {'message': 'invalid msgtext'}
            return json.dumps(res)
            
        dic = {}
        dic ["msg_buffer"] = msgtext
        dic ["taxi" ] =  taxi_no
                   
        sys.stdout.write("%s: message is being sent ... \n" % ( datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT) ) )
    
        try:

            t = VehicleMsg.read_vehmsg_record(msgconf.NO_DIRECTIONS)

            if t != None and len(t) > 6:
                print ' packet_type {0}, buff_type {1}, discretes {2}'.format( t[4], t[5], t[6])
            else:
                sys.stdout.write("%s: could not read VEHMSG record \n" % ( datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT) ))
                Utils.set_default_headers(response)
                response.status = 500
                res = {'status': response.status, 'result': {'message': 'could not read VEHMSG record'}}
                return json.dumps(res)
            
            dic  ["packet_type" ] = t[4]
            dic  ["buff_type" ] = t[5]
            dic  ["discretes" ] = t[6]

            myveh = VehicleMsg.vehicle_message(dic)

            t = VehicleMsg.read_vehmsg_record(msgconf.NO_DIRECTIONS)

            packed, sz, err = myveh.object_to_bin()
            
            if err == None and sz > 0:
                base_fmt = 'I I I I I B B B B'                   

                print ' size data ==> %d '  % ( sz )

                ss_data = struct.Struct(base_fmt + '%ds' % ( sz ) )   

                dest = msgconf.BO
                
                cabmsg.gmsg_send(packed, sz, dest , taxi_no , msgconf.MT_VEH_MSG , ss_data, msgconf.CWEBS)

                sys.stdout.write("%s: message is sent to the %d queue\n" % ( datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT), dest )) 

                response.status = 200
                res = {'status': response.status, 'result': {'message': 'OK'}}
                return json.dumps(res)
    
        except Exception as e:
            sys.stdout.write("{0} : device sendmsg terminated due to exception {1} \n".format ( datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT) , str(e)))
            Utils.set_default_headers(response)
            response.status = 500
            res = {'status': response.status, 'result': {'message': 'failure'}}
            return json.dumps(res)

    except Exception as e:
        sys.stdout.write("{0} : device sendmsg terminated due to exception {1} \n".format( datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT), str(e) ))
        Utils.set_default_headers(response)
        response.status = 500
        res = {'status': response.status, 'result': {'message': 'failure'}}
        return json.dumps(res)