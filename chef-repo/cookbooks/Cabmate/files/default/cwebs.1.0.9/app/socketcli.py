from gevent import monkey; monkey.patch_all()

import sys
import socket
import time
import datetime
import config.cwebsconf as Config
from random import randint


import gevent 

dead_sleep = 1.0
IREQ_PING = '85'

class sClient():


    def __init__(self, SocketServerHost, SocketServerPort, lock):
        self.ITaxiSrvReqDic = {}
        self.lock = lock #gevent.lock.Semaphore()
        self.SocketServerHost = SocketServerHost
        self.SocketServerPort = SocketServerPort
        self.LastPing = -1  
        self.Reconnecting = True

        #sys.stdout.write("%s: !!! entering %s\n" % (datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT), __name__))
        sys.stdout.write("%s: !!! creating socket\n" % (datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT) ))
           
        self.reset()

        try:
            self.connect()  
           
        except Exception as e:
            sys.stdout.write("%s: !!! socket error on init %s\n" % (
            datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT), str(e) ))

        #sys.stdout.write("%s: !!! returning out of init LastPing=%d SocketConnet=%s\n" % (datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT), self.LastPing, str(self.SocketConnect) ))        
        return      

    def  reset(self):
        try:
            self.sockobj = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sockobj.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)        
            self.SocketConnect = False 

        except Exception as e:
            sys.stdout.write("%s: !!! socket error on reset %s\n" % (
                datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT), str(e) ))

    def connect(self):
        try:  
            sys.stdout.write("%s: !!! connecting to socket on %s %s\n" % ( datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT),
                        self.SocketServerHost, 
                        self.SocketServerPort))
            
            self.sockobj.connect( (self.SocketServerHost, self.SocketServerPort))
            
            sys.stdout.write("%s: !!! socket object %s\n" % ( datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT), str(self.sockobj)))
            self.SocketConnect = True   
            self.Reconnecting  = False

        except Exception as e:
            sys.stdout.write("%s: !!! socket error on connect %s\n" % (
                datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT), str(e) ))
            self.SocketConnect = False  
            self.Reconnecting  = True


    def reconnect(self):
        try:
            while True:
                self.reset()
                self.connect()                
                if self.SocketConnect == True:
                    break;
                gevent.sleep(5)
        except Exception as e:
            sys.stdout.write("%s: !!! socket error on re-connect %s\n" % (
                datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT), str(e) ))
                 

    def socket_reconnect(self, sleep_time = 5):
        sys.stdout.write("%s: ??? entering reconnect thread\n" % (
                    datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT)  ))
        while True:
            gevent.sleep(60)
            sys.stdout.write("%s: ??? reconnect is up from sleep\n" % (
                    datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT)  ))
            
            time_since_last_ping = int(time.time()) - self.LastPing
            if  not self.Reconnecting :
                if (self.LastPing != -1 and int(time.time()) - self.LastPing > 60) or (self.LastPing == -1 and not self.SocketConnect):
                    try:
                        sys.stdout.write("%s: ??? shutting down due to reconnect\n" % (
                            datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT)  ))
                        self.sockobj.shutdown(socket.SHUT_RDWR)
                        self.sockobj.close()
                    except Exception as e:
                        sys.stdout.write("%s: ??? exception on shutdown %s\n" % (
                            datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT), 
                            str(e) ))
            
                    self.Reconnecting = True
                    self.SocketConnect = False 
                    self.sockobj = None 
                    gevent.sleep(sleep_time)
                    self.sockobj = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    
                    self.sockobj.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                    try:  
                        sys.stdout.write("%s: ??? reconnecting to socket on %s %s\n" % (
                            datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT), 
                            self.SocketServerHost, 
                            self.SocketServerPort))
                        self.sockobj.connect((self.SocketServerHost, self.SocketServerPort))
                        self.Reconnecting = False
                        sys.stdout.write("%s: ??? socket object %s\n" % (
                            datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT), 
                            str(self.sockobj)))
                        self.SocketConnect = True
                    except Exception as e:
                        sys.stdout.write("%s: ??? socket error on init %s\n" % (
                            datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT), str(e) ))
                else:
                    sys.stdout.write("%s: ??? no reconnect - last ping %s time since last ping %s socket connect %s\n" % (
                        datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT), 
                        str(self.LastPing), 
                        str(time_since_last_ping), 
                        str(self.SocketConnect)  
                    ))
            return      
        
    def send_client_request(self, message):
        sys.stdout.write("%s: ??? sending message>>>%s\n" % (
            datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT), 
            message))
        if self.SocketConnect and self.sockobj: 
            try:
                self.sockobj.sendall(message)
                #except socket.error:
            except Exception as e:
                self.SocketConnect = False 
        else:
            sys.stdout.write("%s: ??? message will not be delivered\n" % (datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT)))         
        return
     
    def receive_server_response(self):
        dead_sleep = 1.0
        IREQ_PING = '85'
        sys.stdout.write("%s: !!! starting server response thread\n" % ( datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT) ))
        while True:
            msg_type = ''
            lMessageId = False
            lMessagePayload = False
            lMessage = False
            #sys.stdout.write("%s: !!! reading message type\n" % ( datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT) ))
        
            try:
                msg_type = self.sockobj.recv(2)
                #sys.stdout.write("%s: !!! message type %s\n" % ( datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT), msg_type ))
                if msg_type == b'':
                    self.socket_reconnect(10)
                    raise RuntimeError("socket connection broken on message type")
                lMessageId = True
            except Exception as e:
                print 'Exception ', str(e)          
                gevent.sleep(dead_sleep)
                continue

            #if lMessageId:
            #    sys.stdout.write("%s: !!! client received message of type>>>%s\n" % (datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT), msg_type))    
            #    sys.stdout.write("%s: !!! reading message length\n" % ( datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT)))   
             
            #print 'client received message of type ', msg_type
            msg_length_str = ''
            try:
                msg_length_str = self.sockobj.recv(4).strip(' ')
                if msg_length_str == b'':
                    self.socket_reconnect(10)
                    #raise RuntimeError("socket connection broken on message length")
                lMessagePayload = True
            except Exception as e:
                print 'Exception ', str(e) 
                gevent.sleep(dead_sleep)
                continue

            #sys.stdout.write("%s: !!! reading message payload\n" % (
            #    datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT)
            #    ))  

            #if lMessagePayload:
            #    sys.stdout.write("%s: !!! message length>>>%s\n" % ( datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT), msg_length_str))    
        
            try:
                msg = ''
                msg_length = int(msg_length_str)        
                if msg_length > 0:
                    msg = self.sockobj.recv(msg_length)
                if msg == b'':
                    self.socket_reconnect(10)
                    #raise RuntimeError("socket connection broken on message content")    
                lMessage = True
            except Exception as e:
                print 'Exception ', str(e)
                gevent.sleep(dead_sleep)
                continue

            if lMessageId and lMessagePayload and lMessage:   
                seqNo=-1  
                if msg_type in ['90','99', '50', '51', '93','54', '56', '68', '59', '0D', '0F', '0H']:
                    
                    sys.stdout.write("%s: !!! message  type>>>%s>>>message length>>>%s\n" % (
                        datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT),
                        msg_type,
                        msg_length_str))            
                    
                    sys.stdout.write("%s: !!! msg>>>%s>>>\n" % (
                        datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT),
                        msg))

                    sys.stdout.write("%s: !!! SeqNo>>>%s>>>\n" % (
                    datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT), msg[0:10] ))
                    
                    if msg_type in [ '90', '99', '50', '51', '93']:
                        seqNo = msg[0:10]
                    elif msg_type in ['54', '56', '68', '59', '0D', '0F', '0H']:
                        tmpseqNo = msg[612:622]
                        seqNo = msg[1066:1076]                    

                    if seqNo > 0:
                        self.lock.acquire()
                        self.ITaxiSrvReqDic[seqNo] = {'msg_type': msg_type, 'msg_length': msg_length, 'msg': msg}
                        self.lock.release()

                        sys.stdout.write("%s: !!! self.ITaxiSrvReqDic['%s']=%s\n" % (
                            datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT),
                            seqNo,
                            str(self.ITaxiSrvReqDic[seqNo])))
            
                        sys.stdout.write("%s: !!! ITaxiSrvReqDic number of records=%s\n" % (
                            datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT), len(self.ITaxiSrvReqDic)))

                #print ">>>self.ITaxiSrvReqDic['%s']=%s" % (msg[0:10], str(self.ITaxiSrvReqDic[msg[0:10]]))  
                elif msg_type in ['52']:
                        sys.stdout.write("%s: !!! message 52 msg_type>>>%s>>> msg_length>>>%s>>> msg>>>%s>>> status>>>%s>>> SeqNo>>>%s>>>\n" % (
                            datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT),
                            msg_type, msg_length, msg, msg[70:86], msg[92:102]))
           
                elif msg_type in ['-1'] and msg == 'Shutdown temporarily':
                    sys.stdout.write("%s: !!! itaxisrv is shutting down\n" % (datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT)))         
                    self.socket_reconnect(10)
                elif msg_type == IREQ_PING:
                    self.LastPing = int(time.time())
                    '''
                    sys.stdout.write("%s: !!! PING msg_type>>>%s>>>msg_length>>>%s>>>msg>>>%s>>>>LastPing>>>%s>>>\n" % (
                        datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT),
                        msg_type, msg_length, msg, self.LastPing) )
                    '''
                else: 
                    sys.stdout.write("%s: !!! unrecognized message msg_type>>>%s>>>msg_length>>>%s>>>msg>>>%s>>>\n" % (
                        datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT),
                        msg_type, msg_length, msg) )

    
    @staticmethod
    def generate_seqno():
        anum = 0
        while not anum > 0: 
            anum = randint(2000000001, 3000000000) 
        return str(anum)

    def generate_SeqNo(self):
        anum = 0
        while not anum > 0: 
            anum = randint(2000000001, 3000000000) 
        return str(anum)

    def init_dic_entry(self, seqno, dic):
        self.lock.acquire()
        self.ITaxiSrvReqDic [seqno] = dic
        self.lock.release()

    def remove_dic_entry(self, seqno):
        self.lock.acquire()    
        del self.ITaxiSrvReqDic[seqno]
        self.lock.release()        
        