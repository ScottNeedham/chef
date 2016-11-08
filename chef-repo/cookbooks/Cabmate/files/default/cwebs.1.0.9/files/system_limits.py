
from gevent import monkey; monkey.patch_all()
import sys, os
import struct
import json
import datetime
import collections 


if __name__ == "__main__":  
    app_dir = os.path.dirname(__file__) + "/.."
    sys.path.append (app_dir )


import config.cwebsconf as Config

from files.file_manager import header_reader, data_file_reader, LIMITS_HEADER_RECORD

#from param 20 to 27
SystemLimitsTuple = collections.namedtuple('taxi_params', 'bid_rotate taxi_supv rej_state cb_o_area p_rebook cbook_unlimit max_meton_time_to_retain_qpos max_time_to_arrive_in_dest_zone' )




#default to taxi_supv param
def read_system_limits(param_id=21):
    try:
        out =  { "result": -1, "id" : param_id, "value" : "" }
        sl =  SystemLimitsTuple( bid_rotate='',
                                taxi_supv='', rej_state='', 
                                cb_o_area='', p_rebook='',
                                cbook_unlimit='', max_meton_time_to_retain_qpos='',
                                max_time_to_arrive_in_dest_zone='' )
        if param_id < 0:
            return out, sl
        shdr = header_reader()
        datafile = data_file_reader()
        err, t= shdr.read_record(LIMITS_HEADER_RECORD)
        if err == 'OK':            
            #print ( ' *************** {0} **********'.format (t) )

            #print (' {0} file_name={1} rec size={2} num_recs={3} '.format ( err,  t.filename, t.rec_size, t.num_recs ) )
            err, s, d = datafile.read_record(LIMITS_HEADER_RECORD,  filename=t.filename, file_rec_size=t.rec_size, recid=t.num_recs - 1)      
            if d and len(d) >= 27:               
                sl =  SystemLimitsTuple( bid_rotate=d[20],
                                        taxi_supv=d[21], rej_state=d[22], 
                                        cb_o_area=d[23], p_rebook=d[24],
                                        cbook_unlimit=d[25], max_meton_time_to_retain_qpos=d[26],
                                        max_time_to_arrive_in_dest_zone=d[27] )

                

            if param_id <= len(d):
                if param_id in range (20, 26 ) or param_id in range (34, 42 ):
                    out["value"] =  chr( d[param_id] )
                else:
                    out["value"] =  d[param_id] 
                out["result"] = "success"

                return out, sl
    except Exception as e:
        sys.stdout.write("{0}: Exception in {1} -  {2}\n".format (
                datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT), sys._getframe().f_code.co_name, str(e)))      
    return out, sl

def can_send_msg_to_vehicle():
    try:
        res, sl = read_system_limits(param_id=21)
        if res ["result"] == "success":
            if sl.taxi_supv == 'V' or sl.taxi_supv == ord('V'):            
                return True
        return False

    except Exception as e:
        sys.stdout.write("{0}: Exception in {1} -  {2}\n".format (
                datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT), sys._getframe().f_code.co_name, str(e)))      

        return False

#Just for supv_taxi
def write_system_limits(param_id=None, param_val = None):
    try:
        if param_id > 0 and param_id != 21:
            return "System Limits : Write Not Implemented for param_id {0}".format ( param_id )
        if param_id == None or param_id < 0:
            return "System Limits : Invalid parameter id "

        if param_id == 21 and param_val in ['V', 'S']:

            out =  { "result": -1, "id" : param_id, "value" : "" }
            sl =  SystemLimitsTuple( bid_rotate='',
                                taxi_supv='', rej_state='', 
                                cb_o_area='', p_rebook='',
                                cbook_unlimit='', max_meton_time_to_retain_qpos='',
                                max_time_to_arrive_in_dest_zone='' )
       
            shdr = header_reader()
            datafile = data_file_reader()
            err, t= shdr.read_record(LIMITS_HEADER_RECORD)
            if err == 'OK':            
                print ( ' *************** {0} **********'.format (t) )

                print (' {0} file_name={1} rec size={2} num_recs={3} '.format ( err,  t.filename, t.rec_size, t.num_recs ) )
                myfilename=t.filename #'/home/souaaz/data/limits.fl'
                print (' {0} file_name={1} rec size={2} num_recs={3} '.format ( err,  myfilename, t.rec_size, t.num_recs ) )
                err, s, d = datafile.read_record(LIMITS_HEADER_RECORD,  filename=myfilename, file_rec_size=t.rec_size, recid=t.num_recs - 1)      
                if d and len(d) >= 27:               
                    sl =  SystemLimitsTuple( bid_rotate=d[20],
                                        taxi_supv=d[21], 
                                        rej_state=d[22], 
                                        cb_o_area=d[23], 
                                        p_rebook=d[24],
                                        cbook_unlimit=d[25], 
                                        max_meton_time_to_retain_qpos=d[26],
                                        max_time_to_arrive_in_dest_zone=d[27] )

                
                    if sl. taxi_supv == param_val or sl. taxi_supv == ord(param_val):
                        return "System Limits : Write Not Required for param_id {0} param_value {1}".format ( param_id, param_val )
                    else:
                        
                        try:
                            new_d = sum(  ( ( d[:21] ) ,  ( ord(param_val) , ) ,   (d[22:]) ), ())          
                            #print (' old_d {0}'.format ( d) )
                            #print (' new_d {0}'.format ( new_d) )
                            err, s, d = datafile.write_record(LIMITS_HEADER_RECORD,  filename=myfilename, file_rec_size=t.rec_size, recid=0, data=new_d)    
                            if err == "OK":
                                return "System Limits : Write Performed for param_id {0} param_value {1}, in file={2}".format ( param_id, param_val, sl.taxi_supv)
                            else:
                                return "System Limits : Error while updating file for param_id {0} param_value {1}, in file={2}".format ( param_id, param_val, sl.taxi_supv)
                        except Exception as e:
                            sys.stdout.write("{0}: ** Exception in {1} -  {2}\n".format (
                                datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT), sys._getframe().f_code.co_name, str(e)))   
                            return "{0} : Error {1}".format ( sys._getframe().f_code.co_name, str (e) )

                else:
                    return "Could not read data in System limits"
            else:
                return err
        else:
             return "System Limits : Invalid parameters"
    except Exception as e:
        sys.stdout.write("{0}: Exception in {1} -  {2}\n".format (
                datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT), sys._getframe().f_code.co_name, str(e)))              
        return "{0} : Error {1}".format ( sys._getframe().f_code.co_name, str (e) )

    return "System Limits : Unknown Error "

if __name__ == "__main__":
    try:
       
        '''
        r = can_send_msg_to_vehicle()
        print (' Yes ? ', r )
        '''

        s = write_system_limits (21, 'V')
        print ( '  write_system_limits : {0}'.format (s) )

    except Exception as e:
        sys.stdout.write("%s: Exception in %s -  %s\n" % (
                datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT), sys._getframe().f_code.co_name, str(e)))

