import sys

import config.cwebsconf as Config
import datetime
import time
from fares import fare_const as FareConstant
import errormsg as ErrMsg
import msgconf
import scap

import config.local_settings as LocalSettings

GPS_MULTIPLIER = 1000000

class ZoneInfo(object):

    def __init__(self, dic, SeqNo, fn=''):
       
        self._error = False
      
        self._zone = -1
        self._fleet =-1  
        self._x = 0.0
        self._y = 0.0     
        self._sequence_number = SeqNo
        self._lead_time = 0

        try:
            if 'pick_up_lng' and 'pick_up_lat' in dic:
                self._x =  float(dic["pick_up_lng"] )
                self._y =  float(dic["pick_up_lat"] )
            elif 'lon' and 'lat' in dic:
                self._x =  float(dic["lon"] )
                self._y =  float(dic["lat"] )           
        except Exception as e:
            self._x = 0.0
            self._y = 0.0    
            self._error = True
            sys.stdout.write("%s: ZoneInfo Exception 1 %s \n" % ( datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT) , str(e) ) )

     
        try:
            if 'fleet' in dic:
                self._fleet = int (dic["fleet"])
            elif 'fleet_number' in dic:
                self._fleet = int (dic["fleet_number"])                
        except Exception as e:
            self._fleet =  -1
            self._error = True
            sys.stdout.write("%s: ZoneInfo Exception  %s \n" % ( datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT) , str(e) ) )
            

    @property
    def lead_time(self):
        return self._lead_time

    @property
    def zone(self):
        return self._zone
    
    @lead_time.setter
    def lead_time(self, val):
        try:
            if type(val) == int:
                self._lead_time = val
            elif type(val) == str:
                self._lead_time = int(val)
        except ValueError as e:
            sys.stdout.write("%s: ZoneInfo Exception  %s \n" % ( datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT) , str(e) ) )            
    
    @zone.setter
    def zone(self, val):
        self._zone = val

    def __repr__(self):
        return ' ZoneInfo : fleet=%d lat=%f lon=%f zone=%d lead_time=%d' % ( self._fleet, self._x, self._y, self._zone, self._lead_time)


    def get_error(self):
        return self._error

 
    def get_fleet(self):
        return self._fleet
          

    def info_to_bin(self, seqno=None):
        from socketcli import sClient  
        import struct       

        try:
            errmsg = None

            port_number=LocalSettings.BOTTLE_PORT
            sspare=0
            requester_ip= LocalSettings.BOTTLE_IP  
      
            if seqno != None:
                self.sequence_number = seqno

            sys.stdout.write("%s: Sending ... fleet=%d \n" % (datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT), self._fleet))    

            d1 = (
                0, 0, 0, 0, 0, 0, 0, 0,
                self._x, self._y,                  
                self._zone, 0, 0, 0, 0, self._fleet, 0,
                b'\x00', b'\x00', 33*b'\x00', 33*b'\x00', 33*b'\x00', 33*b'\x00',  b'\x00',  b'\x00'
                )               
            d2 = (0, port_number, sspare, requester_ip, self._sequence_number, 0, 0)
               
            data = (d1, d2)
            data = sum(data, ())

            fmts = [          
                '8I 2f 7h 2c 33s 33s 33s 33s 2c ',
                'H H H 64s 10s 2H'
            ]
            # port number, sspare, requester_IP, sequence_number')
     
            print 'data ', data

            f = ''.join(fmts)
            #print 'format ', f
            s = struct.Struct(f);
            print 'info_to_bin structure size ', s.size
            packed_data = s.pack(*data)

        except Exception as e:
            print ' info_to_bin Exception %s ' % ( str(e) )
            errmsg = 'Error while formatting'
     
        return packed_data, s.size, errmsg




if __name__ == "__main__":
    
    try:
        seqno = 33333
        dic = { "lat" : 12.0, "lon" : 56.00, "fleet" : 1}
        zone_info = ZoneInfo(dic, seqno)

        
        


    except Exception as e:
        print 'Exception %s ' % ( str(e) )
