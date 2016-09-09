from gevent import monkey; monkey.patch_all()
import gevent 
import sys
import time
import struct
import binascii
import sysv_ipc
import msgconf

from bottle import  request, response
import json

import os
import datetime
import traceback
import config.cwebsconf as Config

import random


#########################


base_fmt = 'I I I I I B B B B'

def gmsg_init():

    """
    gmsg_init() : creates the Q 

    """

    try:
        dstid=msgconf.TFC
        mq = sysv_ipc.MessageQueue(dstid, flags=sysv_ipc.IPC_CREAT, mode=0666, max_message_size = 8064)
   
    except Exception as e:
        print 'Exception ', str(e)
  
    return



def gmsg_send(data, data_size, dstid, scndid, mtype, ss, srcid=msgconf.CWEBS):

    """ 
        Build msg to be sent. 
    """
    msg = ( srcid,             #  msg.msg_struct.ms_srcuid
            dstid,                     #  msg.msg_struct.ms_dstuid
            scndid,                    #  msg.msg_struct.ms_scnduid
            mtype,                     #  msg.msg_struct.ms_msgtype
            data_size,                 #  msg.msg_struct.ms_datasize
            0,                       #  msg.msg_struct.ms_srcmch
            0,                       #  msg.msg_struct.ms_dstmch
            1,                       #  msg.msg_struct.ms_priority
            10,                       #  msg.msg_struct.ms_reserved
            data)                      #  msg.msg_struct.ms_msgdata
    print 'packet size ', data_size
    packed_msg = ss.pack(*msg)
    
    try:
        mq = sysv_ipc.MessageQueue(dstid, flags=sysv_ipc.IPC_CREAT , mode=0666, max_message_size = 8064)
    except Exception as e:
        print ' gmsg_send Exception ', str(e)

    try:
        mq.send(packed_msg, block=False, type=msgconf.ROUT_PRI)
    except Exception as e:
        print ' gmsg_send Exception ', str(e)
    #except sysv_ipc.BusyError:
    #    print "Queue is full, ignoring"

    #mq.remove()
    
    return

def gmsg_rcv2(sleep_time=5):
    try:

        rmq = sysv_ipc.MessageQueue(msgconf.CWEBS, max_message_size = 8064)

     
        #print 'receive_q %s %d\n' % ( __name__, localCount )
        packed_msg, t = rmq.receive( block=False, type= msgconf.ROUT_PRI)

        if t == msgconf.ROUT_PRI:
            data_size = len(packed_msg) - 24
          
            #print ' packed_msg_type=%d, packed_msg_len=%d \n' %(t, len(packed_msg))    

            if len(packed_msg)  > 0 :
                msg_format = 'I I I I I c c c c %ds' % data_size
                ss = struct.Struct(msg_format)
                # Structure of the message:
                # 0      | 1      | 2       | 3       | 4        | 5      | 6      | 7        | 8        | 9
                # srcuid | dstuid | scnduid | msgtype | datasize | srcmch | dstmch | priority | reserved | msgdata
                msg = ss.unpack(packed_msg)

                
                #print ' msg type = ', msg[3]
                #print ' data size = ' , msg[4]
                #print ' data content = [%s]'  % (msg[9])
                #print " Size of the packet: ", len(packed_msg), " (bytes)" , '\n'
                #print " Size of the message: ", ss.size , " (bytes)" , '\n'
                #print " Message itself: ", binascii.hexlify(packed_msg) , '\n'
                #print ' Unpacked Message: ', msg
                

              
                #bother only about data content ...
                if  msg[4] > 0 :
                    if msg[3] == msgconf.MT_OP_ERR :
                        print ' cabmsg.gmsg_rcv2 Received error ....' 
                        m = ()
                        # packed = 79, datalen=51.
                        # data len 9msg[4] = packed_len -28
                        if msg[4] in [22, 58, 51, 42 ]:
                            m_format = 'I I I I I c c c c %ds c c c c c'  % (msg[4] -1)
                            s = struct.Struct(m_format)
                            try:
                                m = s.unpack(packed_msg) 
                               
                                return m                            
                                
                            except Exception as e:
                                sys.stdout.write("%s: MT_OP_ERR Exception 1 %s\n" % (datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT), str(e)))    
                                return msg
                                  
                        else:
                            m_format = 'I I I I I c c c c H h 64s 10s 134s H'
                            s = struct.Struct(m_format)
 
                            print  ' s.size ==> %d [%s]'  % ( s.size, m_format )
                            try:
                                m = s.unpack(packed_msg) 
                               
                                return m

                            except Exception as e:
                                sys.stdout.write("%s: MT_OP_ERR Exception 2 %s\n" % (datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT), str(e)))    

                    #immediate data size = 272
                    if msg[3] == msgconf.MT_ENTER_CALL :
                        #print ' Received response ....'
                        m_format = 'I I I I I c c c c 8I 2f 7H 2c 33s 33s 33s 33s 2c H H H 64s 10s 3H'
                        s = struct.Struct(m_format)

                        #print  ' s.size ==>' , s.size
                        try:
                            m = s.unpack(packed_msg)  
                            #for i in range(len(m)) :
                            #    print i , '=', m[i]
                            #print ' m ==>' , m
                            #print ' time stamp=',  m[10]
                            
                            print ' fare number =', m[11]
                            print ' other_data = ', m[12]
                            print ' zone =', m[19]
                            print ' taxi =', m[20]
                            print ' resp_uid =', m[21]
                            print ' port number =', m[35]
                            print ' ip address =', m[37]
                            print ' sequence number =', m[38]
                            

                            return m

                        except Exception as e:
                            sys.stdout.write("%s: MT_ENTER_CALL Exception %s\n" % (datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT), str(e)))    

                    #FUTURE
                    # data size = 84, packed len = 112)
                    if msg[3] in [ msgconf.MT_NEWFARE, msgconf.MT_UPD_FARE, msgconf.MT_MODFAREINFO] :
                        #struct its_farenumber
                        m_format = 'I I I I I c c c c I h H 64s 10s I'
                        s = struct.Struct(m_format)
                        #print  ' s.size ==>' , s.size
                        try:
                            m = s.unpack(packed_msg)  
                            '''
                            for i in range(len(m)) :
                                print i , '=', m[i]
                        
                            print ' fare number =', m[9]
                            print ' sequence number =', m[13]
                            '''
                            return m

                        except Exception as e:
                            sys.stdout.write("%s: MT_NEWFARE/MT_UPD_FARE/MT_MODFAREINFO  Exception %s\n" % (datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT), str(e)))    

                    if msg[3] == msgconf.MT_GET_ZONE_BY_LAT_LONG:
                        m_format = 'I I I I I c c c c 8I 2f 7H 2c 33s 33s 33s 33s 2c H H H 64s 10s 3H'
                        s = struct.Struct(m_format) 
                        #print  ' s.size ==>' , s.size
                        try:
                            m = s.unpack(packed_msg) 
                            ''' 
                            for i in range(len(m)) :
                                print i , '=', m[i]

                            print ' leadtime = ', m[12]
                            print ' zone =', m[19]
                            print ' sequence number =', m[38]
                            '''
                            return m

                        except Exception as e:
                            sys.stdout.write("%s: MT_GET_ZONE_BY_LAT_LONG Exception %s\n" % (datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT), str(e)))    


    except sysv_ipc.PermissionsError, sysv_ipc.ExistentialError:
        sys.stdout.write("%s: Message could not be received. Check if os queue exist and its permission\n" % (datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT)))
        #time.sleep(self.settings.OS_MQ_SLEEP) 
        gevent.sleep(self.settings.OS_MQ_SLEEP)        

    except sysv_ipc.BusyError:
        #sys.stdout.write("%s: Queue is full, ignoring\n" % (datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT)))        
        pass

    except sysv_ipc.InternalError:
        sys.stdout.write("%s: A severe error ocurred in os message queue. Aborting...\n" % (datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT)))
              
                
    except Exception as e:
        sys.stdout.write("%s: An unexpected error occurred.\nDetails:\n%s [%s]\n" % (datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT), traceback.format_exc() , str(e) ))
 

def gmsg_rcv(maxCount = 1):  

    print 'gmsg_rcv '
    rmq = sysv_ipc.MessageQueue(msgconf.CWEBS, max_message_size = 8064)

    print 'Starting Q receiver '
    countLoop = 0
    if rmq == None:
        sys.stdout.write("%s: Could not get a message queue. Aborting...\n" % (datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT)))
        return

    try:
        m = None
        while countLoop < maxCount:
            try:
                #print 'gmsg_rcv '
                packed_msg, t = rmq.receive(block=False, type= msgconf.ROUT_PRI)

                if t == msgconf.ROUT_PRI:
                    
                    data_size = len(packed_msg) - 24
          
                    print ' packed_msg_type=%d, packed_msg_len=%d' %(t, len(packed_msg))

                    if len(packed_msg)  > 0 :
                        msg_format = 'I I I I I c c c c %ds' % data_size
                        ss = struct.Struct(msg_format)
                        # Structure of the message:
                        # 0      | 1      | 2       | 3       | 4        | 5      | 6      | 7        | 8        | 9
                        # srcuid | dstuid | scnduid | msgtype | datasize | srcmch | dstmch | priority | reserved | msgdata
                        msg = ss.unpack(packed_msg)

                        #print ' msg type = ', msg[3]
                        #print ' data size = ' , msg[4]
                        #print ' data content = [%s]'  % (msg[9:])
                        #print " Size of the packet: ", len(packed_msg), " (bytes)" , '\n'
                        #print " Size of the message: ", ss.size , " (bytes)" , '\n'
                        #print " Message itself: ", binascii.hexlify(packed_msg) , '\n'
                        #print ' Unpacked Message: ', msg

                        
                        p = str(msg[9])
                        #print ' Message: ', p

                        '''
                        struct its_errormsg
                        {
                            unsigned short      port_number;                        
                            short               errnum;                             
                            char                requestor_IP[MAX_HOSTIP];           # 64 requestor IP 64 
                            char                sequence_number[SEQNO_LEN];         # 10 sequence number 
                            char                errmsg[EMSGLEN];
                        };
                        '''

                        if msg[3] == msgconf.MT_OP_ERR :
                            #m_format = 'I I I I I c c c c H H 64s 10s 132s 2H'
                            m_format = 'I I I I I c c c c H H 64s 2H 10s 4H 134s'
                            s = struct.Struct(m_format)
                            #print  ' sequence number  = '  , p[235:245]
                            #print  ' error message  = ' ,  p[245:266] 

                            #print  ' s.size ==>' , s.size
                            
                            try:
                                m = s.unpack(packed_msg)  
                                '''
                                for i in range(len(m)) :
                                    print i , '=', m[i]
                                '''
                                return m

                            except Exception as e:
                                sys.stdout.write("%s: MT_OP_ERR Exception %s\n" % (datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT), str(e)))    


 

                        if msg[3] == msgconf.MT_ENTER_CALL :
                            m_format = 'I I I I I c c c c 8I 2f 7H 2c 33s 33s 33s 33s 2c H H H 64s 10s 3H'
                            s = struct.Struct(m_format)

                            #print  ' s ==>' , s
                            #print  ' s.size ==>' , s.size

                            try:
                                m = s.unpack(packed_msg)  
                                '''
                                for i in range(len(m)) :
                                    print i , '=', m[i]
                                print ' m ==>' , m
                                print ' time stamp=',  m[10]
                                print ' fare number =', m[11]
                                print ' zone =', m[19]
                                print ' port number =', m[35]
                                print ' ip address =', m[37]
                                print ' sequence number =', m[38]
                                '''

                                return m

                            except Exception as e:
                                sys.stdout.write("%s: MT_ENTER_CALL Exception %s\n" % (datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT), str(e)))    

                           

                #gevent.sleep(1)                    
                countLoop +=1
                #print 'Sleep in  msg_recv'
                #time.sleep(1000)

            except sysv_ipc.PermissionsError, sysv_ipc.ExistentialError:
                sys.stdout.write("%s: Message could not be received. Check if os queue exist and its permission\n" % (datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT)))
                gevent.sleep(self.settings.OS_MQ_SLEEP)          

            except sysv_ipc.BusyError:
                #sys.stdout.write("%s: Queue is full, ignoring\n" % (datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT)))        
                pass

            except sysv_ipc.InternalError:
                sys.stdout.write("%s: A severe error ocurred in os message queue. Aborting...\n" % (datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT)))
              
                

            except Exception, e:
                sys.stdout.write("%s: An unexpected error occurred.\nDetails:\n%s \n" % (datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT), traceback.format_exc() ))
                

   
    except sysv_ipc.BusyError:
        print "Queue is full, ignoring"
        pass

    except Exception as e:
        sys.stdout.write("%s: Exception %s\n" % (datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT), str(e)))
        #pass
    
    #print 'Return from msg_recv'
    return 


class MyStruct:
  def __init__(self, **kwargs):
    for k, v in kwargs.items():
      setattr(self, k, v)

class DriverSusp(MyStruct):
  pass



class CabmateMessage(object):


    def __init__(self, d):
       
        try:
            self.msgpriority = d["msgpriority"]
        except KeyError:
            self.msgpriority = 13
        try:
            self.ms_srcuid = d["ms_srcuid"]
        except KeyError:
            self.ms_srcuid = 0
        try:
            self.ms_dstuid = d["ms_dstuid"]
        except KeyError:
            self.ms_dstuid = 0
        try:
            self.ms_scnduid = d["ms_scnduid"]
        except KeyError:
            self.ms_scnduid = 0
        try:
            self.ms_msgtype = d["ms_msgtype"]
        except KeyError:
            self.ms_msgtype = 0
        try:
            self.ms_datasize = d["ms_datasize"]
        except KeyError:
            self.ms_datasize = 0
        try:
            self.ms_srcmch = d["ms_srcmch"]
        except KeyError:
            self.ms_srcmch = 0
        try:
            self.ms_dstmch = d["ms_dstmch"]
        except KeyError:
            self.ms_dstmch = 0
        #Routine priority (java byte)
        try:
            self.ms_priority = d["ms_priority"]
        except KeyError:
            self.ms_priority = 13
        try:
            self.ms_reserved = d["ms_reserved"]
        except KeyError:
            self.ms_reserved = 0
        try:
            self.ms_msgdata = d["ms_msgdata"]
        except KeyError:
            self.ms_msgdata = 8064*' '


    def tobin(self):
        print 'self.ms_srcuid', self.ms_srcuid
        print 'self.ms_dstuid', self.ms_dstuid
        print 'self.ms_scnduid', self.ms_scnduid
        print 'self.ms_msgtype', self.ms_msgtype
        vals2 = (self.ms_srcuid,
                 self.ms_dstuid,
                 self.ms_scnduid,
                 self.ms_msgtype,
                 self.ms_datasize,
                 self.ms_srcmch,
                 self.ms_dstmch,
                 self.ms_priority,
                 self.ms_reserved)
        ss = struct.Struct('I I I I I b b b b')
        packed_data_ss = ss.pack(*vals2)

        vals = (#self.msgpriority,
                packed_data_ss,
                self.ms_msgdata)
        s = struct.Struct('24s 24s')
        packed_data = s.pack(*vals)
        print 'msg.tobin structure size ', s.size
        #print 'header size with 2c ', struct.calcsize('I I I I I I c c c c')
        #print 'header size with 2b ', struct.calcsize('I I I I I I b b b b')
        #print 'with header.........', struct.calcsize('I I I I I I b b b b 24s')
        #print 'without header......', struct.calcsize('24s')
        return packed_data
'''
	dData = (driver_id, duration, int(time.time()), authority_id,  
	msg_for_dispatch, msg_for_driver,  '1', '2', taxi, fleet_num, 8*'X')
	print 'dData ', dData 		    
        cabmsg.send_supervisor_msg(action_dic['action'], dData)		
'''	

def send_supervisor_msg(action, dData):
    '''
    print 'actionX', action, 'X', "suspend"
    print 'driver_idX', dData[0], 'X', 9007
    print 'durationX', dData[1], 'X', 1
    print 'timeX', dData[2], 'X', long(time.time())
    print 'authority_idX', dData[3], 'X', 667
    print 'msg_for_dispatchX', dData[4], 'X', "INAPPROPRIATE LANGUAGE BAD SMELL"
    print 'msg_for_driverX', dData[5], 'X', "BRING YOUR GAME ASAP"
    print '1X', dData[6], 'X', '1'
    print '2X', dData[7], 'X', '2'
    print 'taxiX', dData[8], 'X', 9007
    print 'fleet_numX', dData[9], 'X', 2
    print 'XXXXXXXXA', dData[10], 'A', "ABCDEFGH" 
    print 'msgconf.CWEBSX', msgconf.CWEBS, 'X', 99
    print 'msgconf.DMX', msgconf.DM, 'X', 2
    print 'msgconf.resource_msg[action]X', msgconf.resource_msg[action], 'X', 600 
    '''
    
    s = struct.Struct('I I I h 33s 33s c c h h 8s')  #  suspension data
    packed_data = s.pack( *dData)
    data_size = s.size
    
    # use little endian system for packing
    ss = struct.Struct('I I I I I c c c c 96s')   #  packet
    # Build msg to be sent.
    msg = (msgconf.CWEBS,          #  msg.msg_struct.ms_srcuid
           msgconf.DM,                    #  msg.msg_struct.ms_dstuid
           0,                             #  msg.msg_struct.ms_scnduid
           msgconf.resource_msg[action],  #  msg.msg_struct.ms_msgtype
           data_size,                     #  msg.msg_struct.ms_datasize
              '0',                        #  msg.msg_struct.ms_srcmch
              '0',                        #  msg.msg_struct.ms_dstmch
              '1',                        #  msg.msg_struct.ms_priority
              'a',                        #  msg.msg_struct.ms_reserved
              packed_data)                #  msg.msg_struct.ms_msgdata
    packed_msg = ss.pack(*msg)

    mq = sysv_ipc.MessageQueue(msgconf.DM, flags=sysv_ipc.IPC_CREAT | sysv_ipc.IPC_EXCL, mode=0666, max_message_size = 8064)

    try:
        mq.send(packed_msg, block=False, type=msgconf.ROUT_PRI)
    except sysv_ipc.BusyError:
        print "Queue is full on send"
    #mq.remove()

    print "Size of the packet: ", data_size, " (bytes)" , '\n'
    print "Packet itself: ", binascii.hexlify(packed_data) , '\n'
    print "Size of the message: ", ss.size , " (bytes)" , '\n'
    print "Message itself: ", binascii.hexlify(packed_msg) , '\n'
    print 'Unpacked Message: ', ss.unpack(packed_msg)
    return


def send_login_msg(data, msgid, mq=None):
    if msgid == 1:
        #  size is ??? bytes       
        s0  = struct.Struct('8I 2f 7h c B 33s 33s 33s 33s B B c c') 
        #s0  = struct.Struct('8I 2f 7h 2c 33s 33s 33s 33s c B c c')    
        packed_data0 = s0.pack( *data)
        data_size0 = s0.size
        print 'send_login_msg data size ', data_size0
        ss = struct.Struct('I I I I I B B B B  %ds'  % data_size0 )   #  packet
        # Build msg to be sent.
        msg = (msgconf.CWEBS,          #  msg.msg_struct.ms_srcuid
               msgconf.TFC,            #  msg.msg_struct.ms_dstuid
               msgconf.CWEBS,          #  msg.msg_struct.ms_scnduid
               msgconf.MT_VERIFY_ID,   #  msg.msg_struct.ms_msgtype
               data_size0,             #  msg.msg_struct.ms_datasize
              0,                     #  msg.msg_struct.ms_srcmch
              0,                     #  msg.msg_struct.ms_dstmch
              1,                     #  msg.msg_struct.ms_priority
              10,                     #  msg.msg_struct.ms_reserved
              packed_data0)             #  msg.msg_struct.ms_msgdata
        packed_msg = ss.pack(*msg)

        try:
            if mq != None:
                mq.send(packed_msg, block=False, type=msgconf.ROUT_PRI)
            else:
                print "Q is None ..."    
        except sysv_ipc.BusyError:
            print "Queue is full on send"
        #mq.remove()
        gevent.sleep(1)  
    
    if msgid == 2:
        #  size is 162 bytes       
        s1  = struct.Struct('h 33s 33s 33s 33s 4B 2h I 16s')  
        packed_data1 = s1.pack( *data)
        data_size1 = s1.size

        ss = struct.Struct('I I I I I c c c c %ds' % (data_size1) )   #  packet
        # Build msg to be sent.
        msg = (msgconf.CWEBS,          #  msg.msg_struct.ms_srcuid
               msgconf.DM,             #  msg.msg_struct.ms_dstuid
               0,                      #  msg.msg_struct.ms_scnduid
               msgconf.MT_GPS_STATUS,   #  msg.msg_struct.ms_msgtype
               data_size1,             #  msg.msg_struct.ms_datasize
              '0',                     #  msg.msg_struct.ms_srcmch
              '0',                     #  msg.msg_struct.ms_dstmch
              '1',                     #  msg.msg_struct.ms_priority
              'a',                     #  msg.msg_struct.ms_reserved
              packed_data1)             #  msg.msg_struct.ms_msgdata
        packed_msg = ss.pack(*msg)

        mq = sysv_ipc.MessageQueue(msgconf.DM, flags=sysv_ipc.IPC_CREAT| sysv_ipc.IPC_EXCL, mode=0666, max_message_size = 8064)
        try:
            mq.send(packed_msg, block=False, type=msgconf.ROUT_PRI)
        except sysv_ipc.BusyError:
            print "Queue is full on send"
        #mq.remove()
    return


def receive_q(sleep_time=5):
    try:
        localCount=0

        rmq = sysv_ipc.MessageQueue(msgconf.CWEBS, max_message_size = 8064)

        if rmq != None:
            try:
                while True:

                    try:
                        #print 'receive_q %s %d\n' % ( __name__, localCount )
                        packed_msg, t = rmq.receive( block=False, type= msgconf.ROUT_PRI)

                        if t == msgconf.ROUT_PRI:
                            process_q_msg(packed_msg)
                        gevent.sleep(sleep_time)
                        localCount +=1


                    except sysv_ipc.PermissionsError, sysv_ipc.ExistentialError:
                        sys.stdout.write("%s: receive_q - Message could not be received. Check if os queue exist and its permission\n" % (datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT)))
                        return -1
                
                    except sysv_ipc.BusyError:
                        #sys.stdout.write("%s: test_Q - Queue is full, ignoring\n" % (datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT))) 
                        gevent.sleep(sleep_time) 
                        localCount +=1      
                        continue

            except sysv_ipc.InternalError:
                sys.stdout.write("%s: receive_q - A severe error ocurred in os message queue. Aborting...\n" % (datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT))) 
                pass   

            except Exception, e:
                sys.stdout.write("%s: receive_q - An unexpected error occurred.\nDetails:\n%s \n" % (datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT), traceback.format  ))      
                pass            

        else:
            print ' receive_q - No Q available. Aborting ... \n'
            return -1
    except Exception as e:
        print 'Exception in receive_q', str(e)
        pass
    
    return 0


def process_q_msg(packed_msg):
    try:

        data_size = len(packed_msg) - 24
          
        #print ' packed_msg_len=%d' %(len(packed_msg))

        if len(packed_msg)  > 0:
            msg_format = 'I I I I I B B B B %ds' % data_size
            ss = struct.Struct(msg_format)
                        # Structure of the message:
                        # 0      | 1      | 2       | 3       | 4        | 5      | 6      | 7        | 8        | 9
                        # srcuid | dstuid | scnduid | msgtype | datasize | srcmch | dstmch | priority | reserved | msgdata
            msg = ss.unpack(packed_msg)


            try: 
                print 'msg src:%d,  type:%d, datasize:%d, packetsize:%d bytes, message size:%d bytes\n' %( msg[0],  msg[3], msg[4], len(packed_msg), ss.size )
          
                #print ' data content = [%s]'  % (msg[9:])
                #print "Size of the packet: ", len(packed_msg), " (bytes)" , '\n'
                #print "Size of the message: ", ss.size , " (bytes)" , '\n'
                #print "Message itself: ", binascii.hexlify(packed_msg) , '\n'
                #print 'Unpacked Message: ', msg

                if msg[0] in msgconf.MsgQPeerDict and msg[3] in msgconf.MsgEventDict:
                    sys.stdout.write("%s: message src:%s type:%s\n" % ( datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT), msgconf.MsgQPeerDict[msg[0] ] , msgconf.MsgEventDict [msg[3] ]))

            except Exception as e:
                sys.stdout.write("%s: process_q_msg - An unexpected error occurred.\nDetails:\n%s \n" % (datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT), traceback.format  ))   
                pass

        else:
            sys.stdout.write('Unknown message received len =%d\n'  % ( len(packed_msg) ) )

    except Exception as e:
        sys.stdout.write("%s: process_q_msg - An unexpected error occurred.\nDetails:\n%s \n" % (datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT), traceback.format  ))   
        pass

class CabmateQ():

    def __init__(self):
        self.key = random.randint(sysv_ipc.KEY_MIN, sysv_ipc.KEY_MAX)
        self.mq = sysv_ipc.MessageQueue(self.key, sysv_ipc.IPC_CREX)
        self.mq_tfc =  sysv_ipc.MessageQueue(msgconf.TFC)

    def send_login_msg(self, data, msgid):
        if self.mq_tfc != None:
            send_login_msg(data, msgid, self.mq_tfc)
        else:
            print 'Cannot send ... '

    def reset(self):
        if self.mq != None:
            self.mq.remove()   



def gmsg_main():
    #while True:
    try:        
        gmsg_rcv()
        gevent.sleep(1000)

    except Exception as e:
        print 'Exception %s ' % ( str(e) )


if __name__ == "__main__":
    #while True:
    try:

        while True:   
            gmsg_rcv()
            gevent.sleep(1000)

    except Exception as e:
        print 'Exception %s ' % ( str(e) )
