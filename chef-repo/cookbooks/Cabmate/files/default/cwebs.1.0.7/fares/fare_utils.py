from gevent import monkey; monkey.patch_all()
import gevent 
import datetime
import json
import sys
import time

import config.cwebsconf as Config
import server_utils as Utils
import errormsg as ErrorMsg


'''
	Return lWillCall, pickup_datetime
'''
def check_pickup(order_dic)

	try:
        sys.stdout.write("%s: reading pickup datetime\n" % (datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT)) ) 
        
        lWillCall = False
        pickup_datetime = ""
        if order_dic.has_key("will_call"):
            if order_dic["will_call"] == 'Y':
                lWillCall = True

        if order_dic.has_key("pickup_datetime"):
            try:
                pickup_datetime = datetime.datetime.strptime(
                    order_dic["pickup_datetime"], 
                    Config.DateFormat_SaveOrder_Input
                )
            except Exception as e:
                pickup_datetime = Utils.get_default_server_time()
                sys.stdout.write("default time %s \n" % (pickup_datetime))
                pass
        else:
            pickup_datetime = Utils.get_default_server_time()
            sys.stdout.write("default time %s \n" % (pickup_datetime))
        
        if not lWillCall and order_dic.has_key("pickup_datetime"):
            try:
                sys.stdout.write("%s: order_dic['pickup_datetime']=%s\n" % (
                    datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT), 
                order_dic["pickup_datetime"]) 
                ) 
                pickup_datetime = datetime.datetime.strptime(
                    order_dic["pickup_datetime"], 
                    Config.DateFormat_SaveOrder_Input
                )
            except Exception as e:
                pickup_datetime = Utils.get_default_server_time()
                sys.stdout.write("default time %s \n" % (pickup_datetime))
                pass
        else:
            pickup_datetime = Utils.get_default_server_time()
            sys.stdout.write("default time %s \n" % (pickup_datetime))
            sys.stdout.write("%s: pickup datetime is determined as %s\n" % (datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT), str(pickup_datetime))) 

    except Exception as e:
    	pass

    return lWillCall, pickup_datetime 
