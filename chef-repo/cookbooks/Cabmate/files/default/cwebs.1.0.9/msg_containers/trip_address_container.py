import os
import sys
import struct

app_dir = os.path.dirname(__file__) + "/.."
sys.path.append (app_dir )


import config.cwebsconf as Config
import fares.fare_const as FareConstant
import config.local_settings as LocalSettings
import app.msgconf as msgconf


SEQNO_LEN = 10
GUIDLENGTH = 36
CROSSSTREETLENGTH = 64
MAX_HOSTIP = 64
FULL_ADDRESS_MAXLEN = 128

class TripAddressContainer(object):

    def __init__(self, *initial_data, **kwargs):

        self.error = True
        try:
            self.msgId = msgconf.MT_TRIP_UPDATE_ADDRESS

            self._fare_number = 0
            self._port_number = LocalSettings.BOTTLE_PORT          

            self._requestor_ip = LocalSettings.BOTTLE_IP
            self._sequence_number = SEQNO_LEN * b'\x00'
            self._guid = GUIDLENGTH * b'\x00'
            self._crossstreet = CROSSSTREETLENGTH * b'\x00'
            self._full_pickup_address = FULL_ADDRESS_MAXLEN * b'\x00'
            self._full_dropoff_address = FULL_ADDRESS_MAXLEN * b'\x00'

            self.bin_format = 'I H 64s 10s 36s 64s 128s 128s'

            '''
            struct its_trip_fare
            {
                long                fare_number;
                unsigned short      port_number;                                           
                char                requestor_IP[MAX_HOSTIP];       
                char                sequence_number[SEQNO_LEN];     
                char                guid[GUIDLENGTH];               
                char                crossstreet[CROSSSTREETLENGTH];
                char                full_pickup_address[FULL_ADDRESS_MAXLEN];
                char                full_dropoff_address[FULL_ADDRESS_MAXLEN];
            };

            '''
            
            try:
                for mydic in initial_data:
                    for key in mydic:                        
                        setattr(self, key, mydic[key])           
                for key in kwargs:
                    setattr(self, key, kwargs[key])
            except Exception as e:
                sys.stdout.write("{0} __init__ Exception during attribute setting {1}".format (datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT), str(e) ))                     
            
            self.error = False
        except Exception as e:
            sys.stdout.write("{0} __init__ Exception  {1}".format (datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT), str(e) ))                     
            self.error = True

    def __str__(self):
        pass

    def __repr__(self):
        return 'msgid={0} fare_number={1} sequence_number={2} '.format ( self.msgid, self.fare_number, self.sequence_number)
        #return dict((name, self.format_value(getattr(self, name))) for name in dir(self))

    @property
    def fare_number(self):
        return self._fare_number

    @property
    def port_number(self):
        return self._port_number

  
    @property
    def requestor_ip(self):
        return self._requestor_ip

    @property
    def sequence_number(self):
        return self._sequence_number

    @property
    def guid(self):
        return self._guid

    @property
    def crossstreet(self):
        return self._crossstreet

    @property
    def full_pickup_address(self):
        return self._full_pickup_address

    @property
    def full_dropoff_address(self):
        return self._full_dropoff_address

    @fare_number.setter
    def fare_number(self, val):
        try:           
            if type(val) in [str, unicode]:
                val = int(val)        
            self._fare_number = val
        except Exception as e:
            print('fare_number.setter Exception %s ' % (str(e)))

    @full_dropoff_address.setter
    def full_dropoff_address(self, val):
        if type(val) == unicode:
            val = val.encode('utf-8')
        self._full_dropoff_address = val

    @full_pickup_address.setter
    def full_pickup_address(self, val):
        if type(val) == unicode:
            val = val.encode('utf-8')        
        self._full_pickup_address = val

    @sequence_number.setter
    def sequence_number(self, val):
        try:    
            if type(val) in [int]:                   
                val = str(val)
            self._sequence_number = val
        except Exception as e:
            print('sequence_number.setter Exception %s ' % (str(e)))


    def getError(self):
        return self.error
        pass


    def sendMsg(self):
        pass


  
    def populateObject(self, dic):

        try:
            self.error = False

        except Exception as e:
            sys.stdout.write("%s: exception %s\n" % (datetime.datetime.strftime(datetime.datetime.now(),  '%Y-%m-%d %H:%M:%S'), str(e) ))            
            self.error = True           
            pass
            

   
    def object_to_bin(self):
        try:
            retmsg = None
            data = ()

                         
            data = (              
            self._fare_number,
            self._port_number,          
            self._requestor_ip,
            self._sequence_number,
            self._guid,
            self._crossstreet,
            self._full_pickup_address,
            self._full_dropoff_address
            )


        except Exception as e:
            print 'object_to_bin - Exception during tuple generation %s ' % ( str(e) )     
            retmsg = 'object_to_bin - Error while converting to struct '               
      
        try:
            
            if data is not None:
                print 'tuple ==> ', data

                s = struct.Struct(self.bin_format);
                print 'object_to_bin structure size ', s.size

                packed_data = s.pack(*data)   
     
                return packed_data, s.size, retmsg

        except Exception as e:
            print 'object_to_bin - Exception during sending %s ' % ( str(e) )     
            retmsg =  'object_to_bin - Error while converting to struct '      
            

        return None, 0, retmsg


def send_trip_full_address(data=None):
    try:
        retmsg = "Error"

        if data == None:
            return "No Data"

        myevt = TripAddressContainer(data)

        packed, sz, err = myevt.object_to_bin()

        print ' size %d ' % ( sz )

        print ' packed %s ' % ( packed )

        base_fmt = 'I I I I I B B B B'

        ss = struct.Struct(base_fmt + '%ds' % ( sz ) )   

        import app.cabmsg as cabmsg
        import app.msgconf as msgconf

        # msgconf.MT_TRIP_UPDATE_ADDRESS
        cabmsg.gmsg_send(packed, sz, msgconf.MYCABMATEFARESRV, 0,  myevt.msgId, ss, msgconf.CWEBS)

        retmsg = "OK"

    except Exception as e:
        print 'send_trip_full_address Exception %s ' % ( str(e) )
        retmsg = str(e)

    return retmsg


if __name__ == "__main__":
    try:
        seqno = 33333
        dic = { 
                "fare_number" :  '5702', 
                "sequence_number": seqno,
                "full_dropoff_address" : "875 VLADIVOSOK PLAZA MOSKOVA, SOME COUNTRY, YZ 56544",
                "full_pickup_address" : "Oosterdoksstraat 114, Amsterdam, Noord-Holland 1011, Netherlands",
        }

        send_trip_full_address(dic)
    except Exception as e:
        print 'main Exception %s ' % ( str(e) )
        