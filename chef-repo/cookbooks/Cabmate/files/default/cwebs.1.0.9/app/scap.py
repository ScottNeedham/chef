import sys 
import os
import time
import struct
import config.cwebsconf as Config


SCAP_PARAM_TYPE_FLAG = 0
SCAP_PARAM_TYPE_NUMERIC = 1
SCAP_PARAM_TYPE_STRING = 2

SCAP_SYS_PARAM = 1
SCAP_APP_PARAM = 2
SCAP_CHAN_PARAM = 3


'''
sys_filename = "/home/souaaz/data/spparams.fl"
app_filename = "/home/souaaz/data/apparams.fl"
chan_filename ="/home/souaaz/data/chparams.fl"
'''

param_file_dic = {
    SCAP_SYS_PARAM : Config.sys_filename,
    SCAP_APP_PARAM : Config.app_filename,
    SCAP_CHAN_PARAM : Config.chan_filename,
}

SCAP_SYS_MAX=1505

scap_sys_dic = {
    "SP_fleet_related_op_on" :      683,
    "SP_multi_fleet_zoning_on" :    809,
    "SP_q_sizes_as_MDT_Group on" :  810,
    "SP_in_out_enabled" :           1078,
    "SP_bailout_dispatch_call_on" : 1276,
    "SP_bailout_code_value" :       1277,
    "SP_flat_rate_tag_in_fare_details" : 1346,
}

scap_app_dic = {
    "DEFAULT_FLEET" : 139,
}


'''
struct sysparams {
0  short sp_class;          // 1-99
1  short sp_chg_info_uid;   // Process UID to inform (DET_UID_INFORM).
2  int sp_disp_seq_num;     // 1-999
3  int sp_param_num;        //
4  int sp_param_val;        // Value of Flag or Number
5  int sp_param_max;        // Maximum value of Flag or Number
6  int sp_param_min;        // Minimum value of Flag or Number
7  int sp_param_default;    // Default value of Flag or Number
8  char sp_group;           // 0-System, 1-Application, 2-Channel
9  char sp_type;            // 0-Flag, 1-Number, 2-String
10  char sp_access;          // 1-Customer, 2-FieldSupport, 3-Engineering
11  char sp_opt_num;         // Link to system Option Number
12  char sp_new_param;       //
13  char sp_param_str[26];   // Value of String
14  char sp_param_desc[50];  // Description
15  char sp_define_name[40]; // Programming name
16  short xuid[MAX_UID];     // Extra process UIDs to inform (TO_SAVE_CMD).
17  long sp_entry_date;      // TO_ADD_CMD
18  long sp_modified_date;   // TO_MOD_CMD
20  char junk[73];           // Should be 256 bytes.
};
'''

s = struct.Struct('2h 6I 5B 26s 50s 41s 10h 2I 76s') # Should be 256 bytes.
data_size = s.size
#print 'data structure size ', data_size

param_supported = {
    "param_app_list" : [ 139],
    "param_sys_list" : [ 683, 809, 810,  1078, 1276, 1277, 1346 ] 
}


def read_scap_parameter(scap_num, file_id=SCAP_SYS_PARAM):
    try:
        res={}

        if scap_num  < 0 or scap_num >  SCAP_SYS_MAX:     
            res["param_message"] = "Invalid parameter number"

        if  (file_id == SCAP_SYS_PARAM  and scap_num in param_supported["param_sys_list"] ) \
                or ( file_id == SCAP_APP_PARAM  and scap_num in param_supported["param_app_list"] ) :
            res = read_parameter(scap_num, file_id)   
        else:       
            res["param_message"] = "Unsupported parameter number"
            res["param_num"] = scap_num

    except Exception as e:
        return res;

    return res

def _write_scap_parameter(scap_num, scap_val, file_id=SCAP_SYS_PARAM):
    try:
        res={}

        if scap_num  < 0 or scap_num >  SCAP_SYS_MAX:     
            res["param_message"] = "Invalid parameter number"

        if  (file_id == SCAP_SYS_PARAM  and scap_num in param_supported["param_sys_list"] ) \
                or ( file_id == SCAP_APP_PARAM  and scap_num in param_supported["param_app_list"] ) :
            res = _write_parameter(scap_num, scap_val, file_id)   
        else:       
            res["param_message"] = "Unsupported parameter number"
            res["param_num"] = scap_num

    except Exception as e:
        return res;

    return res


def read_parameter(scap_num, file_id=SCAP_SYS_PARAM):
    res = None
    try:
        if file_id > len(param_file_dic):
            file_id = SCAP_SYS_PARAM
        filename = param_file_dic[file_id]
        f = open(filename, "rb")
    except Exception as e:
        f.close()
        return None
    f.close() 
    
    if scap_num  < 0 or scap_num >  SCAP_SYS_MAX:
        return None    
    with open(filename, "rb") as f:
        count = 0 
        f.seek(scap_num*data_size)
        data = f.read(data_size)
        if not data:
            return None     
        else: 
            udata = s.unpack(data)
            #print scap_num, udata
            res = {
                    "param_num": udata[3], 
                    "param_val": udata[4], 
                    "param_min" : udata[6],
                    "param_max" : udata[5],
                    "param_type": udata[9], 
                    "param_desc": udata[14].strip().strip('\0'), 
                    "param_define_name": udata[15].strip().strip('\0') 
                   }
        
    return res


def _write_parameter(scap_num, scap_val, file_id=SCAP_SYS_PARAM):
    res = None
    try:
        if file_id > len(param_file_dic):
            file_id = SCAP_SYS_PARAM
        filename = param_file_dic[file_id]
        f = open(filename, "rb")
    except Exception as e:
        f.close()
        return None

    f.close() 
    
    print 'write_parameter'
    if scap_num  < 0 or scap_num >  SCAP_SYS_MAX:
        return None    
    with open(filename, "rb") as f:
        count = 0 
        f.seek(scap_num*data_size)
        data = f.read(data_size)
        if not data:
            return None     
        else: 
            udata = s.unpack(data)
            print scap_num, udata, '\n'
            res = {
                    "param_num": udata[3], 
                    "param_val": udata[4], 
                    "param_min" : udata[6],
                    "param_max" : udata[5],
                    "param_type": udata[9], 
                    "param_desc": udata[14].strip().strip('\0'), 
                    "param_define_name": udata[15].strip().strip('\0') 
                   }

            #if udata[3] == scap_num and scap_val >= udata[6] and scap_val <= udata[5]:
            #    udata[4] = scap_val

            
         
    return res


def is_fleet_separation_on():
    result = False
    try:
        res_dic = read_scap_parameter(scap_sys_dic["SP_fleet_related_op_on"])
        if res_dic:
           if res_dic["param_type"] == SCAP_PARAM_TYPE_FLAG and res_dic["param_val"] == 1:
               result = True 
        if result:
            print 'fleet separation is on'
        else:
            print 'fleet separation is off'
    except Exception as e:
        return result
    return result


def multi_fleet_zoning_on():
    result = False
    try:
        res_dic = read_scap_parameter(scap_sys_dic["SP_multi_fleet_zoning_on"])
        if res_dic:
           if res_dic["param_type"] == SCAP_PARAM_TYPE_FLAG and res_dic["param_val"] == 1:
               result = True 
        if result:
            print 'multi fleet zoning is on'
        else:
            print 'multi fleet zoning is off'
    except Exception as e:
        return result
    return result


def MDT_Group():
    result = False
    try:
        res_dic = read_scap_parameter(scap_sys_dic["SP_q_sizes_as_MDT_Group on"])
        if res_dic:
           if res_dic["param_type"] == SCAP_PARAM_TYPE_FLAG and res_dic["param_val"] == 1:
               result = True 
        if result:
            print "SP MDT Group is ON "
        else:
            print "SP MDT Group is OFF"
    except Exception as e:
        return result
    return result

def default_fleet():
    result = False
    try:
        res_dic = read_scap_parameter(139, SCAP_APP_PARAM)
        if res_dic:
            if res_dic["param_type"] == SCAP_PARAM_TYPE_NUMERIC :
               print "Default fleet is ", res_dic["param_val"]
            else: 
                print 'Error while reading default fleet '
    except Exception as e:
        return result
    return result

#flat_rate_tag_in_fare_details() 
def flat_rate_tag_in_fare_details() :
    result = 0
    try:
        res_dic = read_scap_parameter(1346, SCAP_SYS_PARAM)
        if res_dic:
            if res_dic["param_type"] == SCAP_PARAM_TYPE_NUMERIC :
               print "flat_rate_tag_in_fare_details ", res_dic["param_val"]
            else: 
                print 'Error while reading flat_rate_tag_in_fare_details '
    except Exception as e:
        return result
    return result

def read_all_fleet():
    is_fleet_separation_on()
    multi_fleet_zoning_on()
    default_fleet()
    MDT_Group()    

if __name__ == "__main__":
    param_num = 683
    file_id = SCAP_SYS_PARAM
    try:
        if len(sys.argv) > 1 and sys.argv[1]:
            try:
                param_num = int (sys.argv[1])
            except Exception as e:
                print 'Exception %s ' % ( str(e) )
                param_num = 683 
        if len(sys.argv) > 2 and sys.argv[2]:
            try:
                file_id = int (sys.argv[2])
            except Exception as e:
                print 'Exception %s ' % ( str(e) )
                file_id = SCAP_SYS_PARAM                

        res = read_scap_parameter( param_num, file_id)
    except Exception as e:
        print 'Exception %s ' % ( str(e) ) 

    if res is not None:
        print(' %s' % (res) )
        # print ' %s = %s' % ( res['define_name'], res['param_val'])

    read_all_fleet()
  


