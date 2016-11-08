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
import fare_const as FareConstant
import app.msgconf as msgConf

import config.local_settings as LocalSettings




class its_event(object):
    """ Implement the C its_event structure conversion for calls to DM """
  
    def __init__(self, *initial_data, **kwargs):
        
        try:
           
            self._event_no = 0
            self._time = 0
            self._fare = 0
            self._other_data = 0
            self._qual = 0
            self._fstatus = 0
            self._meter_amount = 0
            self._longpad = 0
            self._x = 0.0             
            self._y = 0.0          
            self._zone = 0        
            self._taxi = 0      
            self._uid = msgConf.CWEBS    
            self._attribute = 0
            self._qid = 0         
            self._fleet = 0  
            self._redisp_taxi = 0
            self._merchant_group = 0
            self._num_sats = 0
            self._mesg = [ 33 * b'\x00' for x in range(4)]        
            self._rel_queue = 0    
            self._statusbits = 0

 
            self._port_number = LocalSettings.BOTTLE_PORT
            self._sspare = 0
            self._sequence_number = 10 * b'\x00'
            self._requester_ip = LocalSettings.BOTTLE_IP

            self._filler = [0 for i in range(2) ]  ####>>> Added for struct formatting   <<<######

            self.format_its_event = '8I 2f 7H 2b 33s 33s 33s 33s 2b H H 64s 10s 2H' 

            #'H H 64s 10s H', # port number, sspare, requester_IP, sequence_number

            for mydic in initial_data:
                for key in mydic:
                    setattr(self, key, mydic[key])
            for key in kwargs:
                setattr(self, key, kwargs[key])

            
        except Exception as e:
            print ' its_event *** Exception *** %s ' % ( str(e) )            


    def __repr__(self):

        return ' time=%ld zone=%d fare=%d event_no=%d sequence_number=%s other=%d' % (  self.time,  self.zone ,  self.fare, self.event_no , self.sequence_number, self.other_data) 

      

    def object_to_bin(self):
        try:
            errmsg = None

            d1 = (
            self._event_no,
            self._time,
            self._fare,
            self._other_data,
            self._qual,
            self._fstatus,
            self._meter_amount,
            self._longpad ,
            self._x ,         
            self._y ,          
            self._zone ,
            self._taxi ,      
            self._uid ,
            self._attribute ,
            self._qid ,     
            self._fleet ,
            self._redisp_taxi ,
            self._merchant_group ,
            self._num_sats 
            )

        except Exception as e:
            print 'object_to_bin - Exception 1 %s ' % ( str(e) )     
            errmsg =  'object_to_bin - Error while converting to struct '               

        try:
            d2 = tuple (self._mesg )
        except Exception as e:
            print 'object_to_bin - Exception 2 %s ' % ( str(e) )     
            errmsg =  'object_to_bin - Error while converting to struct '   

        try:
            d3 = (
            self._rel_queue ,
            self._statusbits ,
 
            self._port_number ,
            self._sspare ,
            self._sequence_number ,
            self._requester_ip 
            )

        except Exception as e:
            print 'object_to_bin - Exception 3 %s ' % ( str(e) )     
            errmsg =  'object_to_bin - Error while converting to struct '   

        try:
            d4= tuple(self._filler )
            
        except Exception as e:
            print 'object_to_bin - Exception 4 %s ' % ( str(e) )     
            errmsg =  'object_to_bin - Error while converting to struct '   


        try:
            #Convert all the tuples into one flat tuple                     
            data = sum(  (d1, d2, d3, d4), ())          
            
            print 'tuple ==> ', data

            s = struct.Struct(self.format_its_event);
            print 'object_to_bin structure size ', s.size

            packed_data = s.pack(*data)   
     
            return packed_data, s.size, errmsg

        except Exception as e:
            print 'object_to_bin - Exception %s ' % ( str(e) )     
            errmsg =  'object_to_bin - Error while converting to struct '      
            

        return None, 0, errmsg


    def object_to_tuple(self):
        try:

            a=0
        except Exception as e:      
            print 'Exception %s ' % ( str(e) )            

    @property
    def time(self):
        return self._time


    @property
    def uid(self):
        return self._uid


    @property
    def fare(self):
        return self._fare


    @property
    def taxi(self):
        return self._taxi


    @property
    def zone(self):
        return self._zone

    @property
    def event_no(self):
        return self._event_no


    @property
    def port_number(self):
        return self._port_number


    @property
    def sequence_number(self):
        return self._sequence_number

    
    @property
    def requester_ip(self):
        return self.requester_ip

    @property
    def other_data(self):
        return self._other_data
    

    @time.setter
    def time(self, val):
        self._time = val           
      

    @uid.setter
    def uid(self, val):
        self._uid = val


    @fare.setter
    def fare(self, val):
        self._fare = val


    @taxi.setter
    def taxi(self, val):
        self._taxi = val


    @zone.setter
    def zone(self, val):
        self._zone = val

    @event_no.setter
    def event_no(self, val):
        self._event_no = val

    @port_number.setter
    def port_number(self, val):
        self._port_number = val

    @sequence_number.setter
    def sequence_number(self, val):
        self._sequence_number = val
    
    @requester_ip.setter
    def requester_ip(self, val):
        self._requester_ip = val

    @other_data.setter
    def other_data(self, val):
        try:
            if type(val) == int:
                self._other_data = val
            else:
                self._other_data = int(val)
        except Exception as e:
            sys.stdout.write("%s: Exception other_data %s \n"  % (datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT), str(e) )) 


class future_cancel_event(object):
    """ Implement the C cancel_event structure conversion for calls to TIMEMGR """
  
    def __init__(self, farenum=0):        
        try:           

            self._fare = farenum
            self._ftypes =  FareConstant.FUTURE
           

            self.format_event = '2I'             
           
        except Exception as e:
            print 'future_cancel_event Exception %s ' % ( str(e) )            


    def __repr__(self):
        return 'fare=%d ftypes=%d ' % (  self._fare, self._ftypes ) 


    @property
    def fare(self):
        return self._fare

    @fare.setter
    def fare(self, val):
        self._fare = val

    def object_to_bin(self):
        try:
            errmsg = None

            data = (               
                self._fare,
                self._ftypes
            )

            print 'tuple ==> ', data

            s = struct.Struct(self.format_event);
            print 'object_to_bin structure size ', s.size

            packed_data = s.pack(*data)   
     
            return packed_data, s.size, errmsg

        except Exception as e:
            print 'object_to_bin - Exception %s ' % ( str(e) )     
            errmsg =  'object_to_bin - Error while converting to struct '      
            

        return None, 0, errmsg



if __name__ == "__main__":
    
    try:
        seqno = '33333'
        dic = { "zone" : 0, "fleet" : 5, "fare" : 4565, "sequence_number": seqno, "event_no" : 45, "other_data" : 18080, "taxi": 8080}
        myevt = its_event(dic)

        print myevt
     
        myevt.time =   int (time.time())

        print myevt

        packed, sz, err = myevt.object_to_bin()


        print ' size %d ' % ( sz )

        print ' packed %s ' % ( packed )

        base_fmt = 'I I I I I B B B B'

        ss = struct.Struct(base_fmt + '%ds' % ( sz ) )   

        import app.cabmsg as cabmsg
        import app.msgconf as msgconf

        cabmsg.gmsg_send(packed, sz, msgconf.TFC, 0, msgconf.MT_SUSP_TAXI, ss, msgconf.CWEBS)
    except Exception as e:
        print 'Exception %s ' % ( str(e) )
