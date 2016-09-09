#coding=utf-8
from gevent import monkey; monkey.patch_all()
import gevent 
import datetime
import json
import sys, os
import time
import struct

app_dir = os.path.dirname(__file__) + "/.."
sys.path.append (app_dir )


import config.cwebsconf as Config
import fares.fare_const as FareConstant
import app.msgconf as msgconf

import config.local_settings as LocalSettings



class vehicle_message(object):
    """ Implement the C vehicle_message structure conversion for calls to DM """
  
    def __init__(self, *initial_data, **kwargs):
        
        try:
           
            self._msg_buffer = [ 33 * b'\x00' for x in range(4)]              
            self._packet_type = 0
            self._buff_type = 0
            self._discretes = 0         
            self._fleet = 0  
            self._fleet1 = 0
            self._zone = 0
            self._other_data = 0    
            self._junk = 16 * b'\x00'

            self.format_vehicle_message =  '33s 33s 33s 33s b b b b h h I 16s'  

            for mydic in initial_data:
                for key in mydic:
                    setattr(self, key, mydic[key])
            for key in kwargs:
                setattr(self, key, kwargs[key])

            
        except Exception as e:
            print ' vehicle_message *** Exception *** {0} '.format ( str(e) )            


    def __repr__(self):

        return ' zone={0} other={1} msg_buffer={2} taxi={3}'.format(    self.zone , self.other_data, self.msg_buffer, self.taxi) 

      

    def object_to_bin(self):
        try:
            errmsg = None

            d1 =  tuple ( self.msg_buffer )

            d2 = (
               
                self.packet_type ,
                self.buff_type ,
                self.discretes,
                self.fleet, 
                self.fleet1 ,
                self.zone ,
                self.other_data ,
                self._junk 
            )

            data = sum(  (d1, d2), ())          
        except Exception as e:
            print 'object_to_bin - Exception  {0} '.format( str(e) )     
            errmsg =  'object_to_bin - Error while converting to struct '                      

        try:
 
            print 'tuple ==> ', data

            s = struct.Struct(self.format_vehicle_message);
            print 'object_to_bin structure size ', s.size

            packed_data = s.pack(*data)   
     
            return packed_data, s.size, errmsg

        except Exception as e:
            print 'object_to_bin - Exception {0} '.format( str(e) )     
            errmsg =  'object_to_bin - Error while converting to struct '      
            

        return None, 0, errmsg


    def object_to_tuple(self):
        try:

            a=0
        except Exception as e:      
            print 'Exception {0} '.format ( str(e) )            


    @property
    def msg_buffer(self):
        return self._msg_buffer
    
    @property
    def packet_type (self):
        return self._packet_type 
       
    @property
    def buff_type(self):
        return self._buff_type
   

    @property
    def discretes (self):
        return self._discretes 
    
   
    @property
    def fleet(self):
        return self._fleet

    @property
    def fleet1(self):
        return self._fleet1

    @property
    def zone(self):
        return self._zone 

    @property
    def other_data(self):
        return self._other_data


    @msg_buffer.setter
    def msg_buffer(self, val):
        try:            
            if val != None:               
                if type(val) in  [str, unicode]:
                    import textwrap
                    val = textwrap.wrap( val, 33)
                if type(val) == list:
                    self._msg_buffer  = []
                    for k in val:                    
                        print k
                        self._msg_buffer.append( str(k[:33]) )             
                    for i in range(4-len(val)):
                        self._msg_buffer.append(33 * b'\x00' )
               

               
        except Exception as e:
            sys.stdout.write("{0}: Exception msg_buffer {1} \n".format(datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT), str(e) )) 

    
    @packet_type.setter
    def packet_type (self, val):
        self._packet_type = val
    
    @buff_type.setter
    def buff_type(self, val):
        self._buff_type = val
   

    @discretes.setter
    def discretes (self, val):
        self._discretes = val
    
   
    @fleet.setter
    def fleet(self, val):
        self._fleet = val

    @fleet1.setter
    def fleet1(self, val):
        self._fleet1 = val

    @zone.setter
    def zone(self, val):
        self._zone = val


    @other_data.setter
    def other_data(self, val):
        try:
            if type(val) == int:
                self._other_data = val
            else:
                self._other_data = int(val)
        except Exception as e:
            sys.stdout.write("{0}: Exception other_data {1} \n" .format(datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT), str(e) )) 






def read_vehmsg_record(myid):
    try:
        udata = None
        full_path = '/data/vehmsg.fl'        

        frmt =  '33s 33s 33s 33s b b b b h h I 16s'  
        data_size = struct.Struct(frmt).size
        s = struct.Struct(frmt)
        # print 'data structure size ', data_size

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
                            print '{0}'.format(udata)
                            bRun = True
                            isvalid = True                   

        fp.close()
    except Exception as e:
        sys.stdout.write("{0}: read_vehmsg_record : Exception {1}\n".format(datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT),  str(e) ) )                 

    return udata           


if __name__ == "__main__":
    
    try:
        
        seqno = '33333'
        dic = { "zone" : 17, "taxi" : 8080, "other_data" : 8080, 
                "msg_buffer" : [ " 1 test message for dispatch bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb ", 
                                    " 2 test message for dispatch"
                                  
                ]
                }
        myevt = vehicle_message(dic)
        
        print myevt

        packed, sz, err = myevt.object_to_bin()


        print ' size {0} '.format(sz)

        print ' packed {0} '.format(packed)

        

        t = read_vehmsg_record(msgconf.NO_DIRECTIONS)

        if t != None:
            print ' packet_type {0}, buff_type {1}, discretes {2}'.format( t[4], t[5], t[6])

    except Exception as e:
        print 'Exception {0} '.format ( str(e) )
