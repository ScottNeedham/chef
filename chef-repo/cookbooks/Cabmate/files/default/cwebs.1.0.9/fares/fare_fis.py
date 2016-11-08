import os
import sys
import struct      
import datetime
import time

import format_field
import config.cwebsconf as Config
import fare_const as FareConstant
from fares.itcli import Fare

GUIDLENGTH = 36
CROSSSTREETLENGTH = 64
FULL_ADDRESS_MAXLEN = 128

class FareFis(Fare):   
    def __init__(self, fare_dic, zone, SeqNo, fn=''):
        self.cspare = 0
        self.guid = GUIDLENGTH  * b'\x00'
        self.crossstreet =  CROSSSTREETLENGTH  * b'\x00'
        self.full_pickup_address = FULL_ADDRESS_MAXLEN * b'\x00'
        self.full_dropoff_address = FULL_ADDRESS_MAXLEN * b'\x00'

        self._fare = Fare(fare_dic, zone, SeqNo, fn=fn) 
 
        try:
            if Config.ENABLE_FULL_ADDRESS:
                if "full_dropoff_address" in fare_dic:                
                    self.full_dropoff_address = format_field.format_field ( fare_dic["full_dropoff_address"], sz=FULL_ADDRESS_MAXLEN-1)
                    self._fare.sys_ftypes1 |= FareConstant.FULL_ADDRESS_PRESENT                           
                if "full_pickup_address" in fare_dic:
                    self.full_pickup_address =  format_field.format_field  (fare_dic["full_pickup_address"], sz=FULL_ADDRESS_MAXLEN-1)
                    self._fare.sys_ftypes1 |= FareConstant.FULL_ADDRESS_PRESENT               
            else:
                self._fare.sys_ftypes1 &= ~FareConstant.FULL_ADDRESS_PRESENT
        except AttributeError as e:
            sys.stdout.write("%s: Exception in FareFis __init__ %s \n" % (datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT), str(e)))  
        except Exception as e:
            self.full_pickup_address = FULL_ADDRESS_MAXLEN * b'\x00'
            self.full_dropoff_address = FULL_ADDRESS_MAXLEN * b'\x00'
            self._fare.sys_ftypes1 &= ~FareConstant.FULL_ADDRESS_PRESENT
            sys.stdout.write("%s: FareFis __init__ Exception %s \n" % (datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT), str(e)))  
           

    def fare_set_future(self, flag, pickup_time=None):
        return self._fare.fare_set_future(flag, pickup_time=pickup_time)

    def fare_future(self):
        return self._fare.fare_future()

    def to_msg(self):        
        return self._fare.to_msg()

    def fare_to_bin(self, pzone=None, seqno=None):
        try:      
            sys.stdout.write("%s: FareFis fare_to_bin  \n" % (datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT)))  
            if Config.ENABLE_FULL_ADDRESS:
            
                if not self._fare.is_future and self._fare.sys_ftypes1 & FareConstant.FULL_ADDRESS_PRESENT != 0 :               
                    add_data = (                 
                    #self.cspare,                
                    self.guid,
                    self.crossstreet,
                    self.full_pickup_address,
                    self.full_dropoff_address
                )                

                    data, fmts, errmsg = self._fare.fare_to_bin(pzone=pzone, seqno=seqno, packit=False)      

                    all_data = (data, add_data )

                    fare_fis_data = sum(all_data, ())                   

                    fmts.append('36s 64s 128s 128s')
               
                    f = ''.join(fmts)           
                    s = struct.Struct(f);              
                    packed_data = s.pack(*fare_fis_data)                                        
                    return packed_data, s.size, errmsg
                else:              
                    return self._fare.fare_to_bin(pzone=pzone, seqno=seqno)
            else:              
                return self._fare.fare_to_bin(pzone=pzone, seqno=seqno)
        except AttributeError:
            try:
                return self._fare.fare_to_bin(pzone=pzone, seqno=seqno)
            except Exception as e:
                sys.stdout.write("%s: FareFis Exception %s \n" % (datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT), str(e)))  

        except Exception as e:
            sys.stdout.write("%s: FareFis Exception %s \n" % (datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT), str(e)))  

        return None, 0, None

