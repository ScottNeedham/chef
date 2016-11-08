#coding=utf-8
import os, sys, struct

#if os.path.dirname(sys.argv[0]) == 'msg_containers' : 
if __name__ == "__main__":  
    app_dir = os.path.dirname(__file__) + "/.."
    sys.path.append (app_dir )


import fares.fare_const as FareConstant
import app.msgconf as msgConf
import config.local_settings as LocalSettings



SEQNO_LEN = 10
PAYMENT_TYPE_LEN = 2
HOSTNAME_MAX_SIZE = 64

class payment_container(object):
    """ Implement the C its_payment_type_change structure conversion for calls to DM """
  
    def __init__(self, SeqNo,  mydic, msgtype = msgConf.MT_PAYMENT_TYPE_CHANGE):
        
        try:  

            self.msgid =  msgtype 

            if  self.msgid == msgConf.MT_PAYMENT_TYPE_CHANGE:
                self.bin_format = '10s 2s 64s I H'         

            if  self.msgid == msgConf.MT_UPDATE_FARE_AMOUNT:
                self.bin_format = '10s 64s I I H'  

            '''

            #define MAXHSIZE        64

            //82 bytes
            struct  its_payment_type_change     
            {
                char        SequenceNumber[10];     
                char        PaymentType[2];         //The Payment Type CO = Card On File, PI = Payment In Car
                char        OrigIP[MAXHSIZE];       // 64
                long        FareNumber;             
                unsigned    short remPort;
            };


            struct  its_final_fare_amount               //84 bytes in total December 10, 2014 RL
            {
                char           SequenceNumber[10];     //for async communication
                char           OrigIP[MAXHSIZE];       //The originator IP
                long           FareNumber;             //The fare number
                unsigned long  FareAmount;
                unsigned short remPort;
            };

            '''         
           
            self._sequence_number = SEQNO_LEN * b'\x00'             
            self._payment_type = PAYMENT_TYPE_LEN * ' ' #  [0 for i in range(2) ]  
            padding =  HOSTNAME_MAX_SIZE -  len(LocalSettings.BOTTLE_IP)
            self._requester_ip = ''.join ( [LocalSettings.BOTTLE_IP , padding *  b'\x00' ] )
            self._fare = 0                               
            self._port_number = LocalSettings.BOTTLE_PORT

            self._fare_amount = 0
           
            
            for key in mydic:
                setattr(self, key, mydic[key])
            

            
        except Exception as e:
            print ' payment_container *** Exception *** %s ' % ( str(e) )            


    def __repr__(self):
        return 'msgid=%d fare=%d sequence_number=%s payment_type=%s fare_amount=%d' % (  self.msgid, self.fare, self.sequence_number, self.payment_type, self.fare_amount) 
        #return dict((name, self.format_value(getattr(self, name))) for name in dir(self))

    def object_to_bin(self):
        try:
            errmsg = None
            data = ()

            if self.msgid == msgConf.MT_PAYMENT_TYPE_CHANGE :
                if len (self._payment_type) > 2:
                    errmsg = ' invalid Payment Type'

                data = (
                    self.sequence_number ,
                    self.payment_type ,   
                    self.requester_ip ,
                    self.fare ,                           
                    self.port_number 
                )

            if self.msgid == msgConf.MT_UPDATE_FARE_AMOUNT :               
                data = (
                    self.sequence_number ,                    
                    self.requester_ip ,
                    self.fare ,           
                    self.fare_amount,                
                    self.port_number 
                )


        except Exception as e:
            print 'object_to_bin - Exception 1 %s ' % ( str(e) )     
            errmsg =  'object_to_bin - Error while converting to struct '               

       
        try:
            
            if data is not None:
                print 'tuple ==> ', data

                s = struct.Struct(self.bin_format);
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
    def msgid(self):
        return self._msgid


    @property
    def fare(self):
        return self._fare

    @property
    def payment_type(self):
        return self._payment_type

    @property
    def fare_amount(self):
        return self._fare_amount

    @property
    def port_number(self):
        return self._port_number


    @property
    def sequence_number(self):
        return self._sequence_number

    
    @property
    def requester_ip(self):
        return self._requester_ip


    @fare.setter
    def fare(self, val):
        try:
            if type(val) == str:
                val = int(val)
            self._fare = val
        except Exception as e:
            sys.stdout.write("%s: Error while setting job  %s \n" % (datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT), str(e)))  



    @port_number.setter
    def port_number(self, val):
        self._port_number = val


    @sequence_number.setter
    def sequence_number(self, val):
        try:
            if type(val) == int:
                val = str(val)
            self._sequence_number = val
        except Exception as e:
            sys.stdout.write("%s: Error while setting sequence number %s \n" % (datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT), str(e)))  


    
    @requester_ip.setter
    def requester_ip(self, val):
        self._requester_ip = val


    @payment_type.setter
    def payment_type(self, val):
        try:
            if val != None and len(val) <= 2:               
                if val in ["CA", "AC", "CC", "CR", "PI", "CO", "OT"]:
                    self._payment_type = val
        except Exception as e:
            sys.stdout.write("%s: Error while setting payment type %s \n" % (datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT), str(e)))  


    @fare_amount.setter
    def fare_amount(self, val):
        try:
            if type(val) == str:
                val = int(val)
            self._fare_amount = val
        except Exception as e:
            sys.stdout.write("%s: Error while setting fare amount %s \n" % (datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT), str(e)))  



    @msgid.setter
    def msgid(self, val):
        try:
            if val in [msgConf.MT_PAYMENT_TYPE_CHANGE,  msgConf.MT_UPDATE_FARE_AMOUNT] :
                self._msgid = val
           
        except Exception as e:
            sys.stdout.write("%s: Error while setting msg type %s \n" % (datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT), str(e)))  
            




if __name__ == "__main__":
    
    try:       

        seqno = '33333'
        dic = {  "fare" : '4565', "sequence_number": seqno, "port_number" : 8000}
        myevt = payment_container(seqno, dic)

        print myevt
     
        myevt.port_number =  12345


        myevt.payment_type =  'AC'

        print myevt

        packed, sz, err = myevt.object_to_bin()

        if err == None:
            print ' size %d ' % ( sz )

            print ' packed %s ' % ( packed )
        else:
            print ' invalid contents %s ' % ( err )

    except Exception as e:
        print 'Exception %s ' % ( str(e) )

