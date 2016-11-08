import os
import sys
import struct


if __name__ == "__main__":  
    app_dir = os.path.dirname(__file__) + "/.."
    sys.path.append (app_dir )


import app.dblayer as dblayer

PICKUP_ADDR_OFFSET = 16
DEST_ADDR_OFFSET = PICKUP_ADDR_OFFSET + 17
FDVT_OFFSET = 55
QUE_PRIORITY_OFFSET =  FDVT_OFFSET + 4 + 2 + 18 +2 + 7 + 305 + 2 + 2 

class fare_container(object):

    def __init__(self, fare_type="immediate"):

        self._error = True
        self._fare_type =  fare_type
      
        try:
            #self._msgId = 389
            
            self._fare_num = 0
            self._fstatus = 0
            self._dm_fstatus = 0
           
            self._cus_num= 0
            self._fare_amount = 0
            self._driver_id = 0

            self._vip_num = 0
            self._reg_fare_num = 0
            self._pass_on_brd = 0
            self._orig_time = 0

            self._sys_ftypes1 = 0
            self._passengers = 0
            self._fstatus1 = 0
            self._orig_rate = 0          
            self._webId=0 

            self._pickup_x = 0
            self._pickup_y = 0

            self._pickup_zone = 0
            self._pickup_num = 7*' '
            self._pickup_street = 33*' '
            self._pickup_city = 33*' '
            self._pickup_building = 33*' '
            self._pickup_apt = 7 * ' '
            self._pickup_code = 7 * ' '


            self._dest_x = 0
            self._dest_y = 0
            self._dest_zone = 0
            self._dest_num  = 7*' '
            self._dest_street = 33*' '
            self._dest_city  = 33 * ' '
            self._dest_building = 7 * ' ' 
            self._dest_apt = 7 * ' '
            self._dest_code  = 7 * ' '
 

            self._fdvt_sys_ftypes = 0
            self._fdvt_usr_ftypes = 0
            self._fdvt_dtypes_32 = 0
            self._fdvt_vtypes = 0  

            self._fi_taxi = 0
            self._reg_marks = 0   
            self._flag = 0
            self._flag1 = 0
            self._flag2 = 0
           
            postcode_format = '8s' 

            fmts = [
            '16I ' ,
            '2i h H 4s ', postcode_format , ' 8s 34s 34s 34s 1H 8s 8s 33s 3c',  # addr_struct addr_extra       
            '2i h H 4s ', postcode_format , ' 8s 34s 34s 34s 1H 8s 8s 33s 3c',       
            '66s 66s' ,  # forminfo
            ' 20s'  ,  # phone
            ' 80s 16s' ,  # special_data
            ' 4I ' ,  # fdv_types   
            ' 4s ' ,  # combat_vals 
            ' 22s ' ,  #  redisp_fltinfo
            ' 3b B 20s 3s 8s 9s 20s I I I H H I I I 100s ' ,  # 192s = payment => num args = 18
            ' I' ,     # veh_class_32
            ' 16s' , 
            ' 1B 1B H H H I I ' ,   # rgev    num args = 7
            '24I 7I 10H I 69H 194c', # ss , num args = 305
            '198s 1338s ',           #' 1536s ' = xjobinfo, num args = 2
            '396s 16s' ,      # xforminfo regtrack, num args = 2
            ' 4h H 4h H 2h H h 2H I 2B 33s 33s 33s 33s 132s 12s 20s 3B 24s 5B 33s 3s 1I' ,        #que_priority ... reg_marks=arg16(short) flag=arg19 flag2=arg31
            '8b 104s', #         ' 112s '  ei_config
            ' 120s' , # xphones
            ' 160s' ,  # cvd_resp * 10       
            ' 4s' ,   # pad_share
            ' 2s' , 
            ' 60s ' , # airport_info
            ' H' ,  # CoPay           
            ]
            # offset = 2 + 18 +2 + 7 + 305 + 2 + 2 + 16
            self._fareformat = ''.join(fmts)

            
            self._error = False
        except Exception as e:
            print ' Exception in init ', str(e)
            self._error = True

  
    @property
    def fare_type(self):
        return self._fare_type
    
    @property
    def fareformat(self):
      return self._fareformat
    
    @property
    def error(self):
        return self._error
        
    @property
    def fare_num(self):
        return self._fare_num 

    @property
    def fstatus(self):    
        self._fstatus

    @property
    def dm_fstatus(self):
        return self._dm_fstatus


    @property
    def  cus_num(self):      
        return self._cus_num

    @property
    def fare_amount(self):
        return self._fare_amount

    @property
    def driver_id(self):
        return self._driver_id

    @property
    def             vip_num(self):
        return self._vip_num

    @property
    def reg_fare_num         (self):
        return self._reg_fare_num 

    @property
    def         pass_on_brd(self):
        return self._pass_on_brd

    @property
    def         orig_time(self):
        return self._orig_time


    @property
    def sys_ftypes1(self):
        return self._sys_ftypes1


    @property
    def        passengers(self): 
        return self._passengers

    @property
    def         fstatus1(self):
        return self._fstatus1


    @property
    def  orig_rate(self): 
        return self._orig_rate

        
    @property
    def webId(self):
        return self._webId


    @property
    def pickup_x(self):
        return self._pickup_x

    @property
    def       pickup_y  (self): 
        return self._pickup_y 

    @property
    def pickup_zone (self):
        return self._pickup_zone 

    @property
    def pickup_num(self):
        return self._pickup_num

    @property
    def pickup_street(self):        
        return self._pickup_street


    @property
    def  pickup_city(self):       
        return self._pickup_city

    @property
    def pickup_building(self):        
        return  self._pickup_building 

    @property
    def  pickup_lat(self):       
        return   self._pickup_apt

    @property
    def pickup_code(self):            
        return self._pickup_code 

    @property
    def dest_x(self):            
        return self._dest_x

    @property
    def  dest_y(self):           
        return self._dest_y 

    @property
    def  dest_zone(self):    
        return self._dest_zone 

    @property
    def      dest_num(self):       
        return  self._dest_num 

    @property
    def  dest_street(self):       
        return  self._dest_street 

    @property
    def  dest_city(self):
        return self._dest_city 
    
    @property
    def  dest_building(self):
        return self._dest_building 
    
    @property
    def   dest_apt(self):
        return self._dest_apt 

    @property
    def  dest_code(self):
        return self._dest_code 

    @property
    def  fdvt_sys_ftypes(self):
        return self._fdvt_sys_ftypes

    @property
    def  fdvt_usr_ftypes(self):
        return  self._fdvt_usr_ftypes 

    @property
    def   fdvt_dtypes_32(self):
        return  self._fdvt_dtypes_32

    @property
    def  fdvt_vtypes(self):
        return self._fdvt_vtypes 

    @property
    def fi_taxi(self):
        return self._fi_taxi

    @property
    def reg_marks(self):
        return self._reg_marks

    @property
    def flag(self):
        return self._flag
    
    @property
    def flag2(self):
        return self._flag2
 
    @property
    def flag1(self):
        return self._flag1

    #### Setters
    @error.setter
    def error(self, val):
        self._error = val

    @fare_num.setter
    def fare_num(self, val):
        self._fare_num  = val

    @fstatus.setter
    def fstatus(self, val):    
        self._fstatus= val

    @dm_fstatus.setter
    def dm_fstatus(self, val):
        self._dm_fstatus= val


    @cus_num.setter
    def  cus_num(self, val):      
        self._cus_num= val

    @fare_amount.setter
    def fare_amount(self, val):
        self._fare_amount= val

    @driver_id.setter
    def driver_id(self, val):
        self._driver_id= val

    @vip_num.setter
    def  vip_num(self, val):
        self._vip_num= val

    @reg_fare_num.setter
    def reg_fare_num         (self, val):
        self._reg_fare_num = val

    @pass_on_brd.setter
    def         pass_on_brd(self, val):
        self._pass_on_brd= val

    @orig_time.setter
    def         orig_time(self, val):
        self._orig_time= val


    @sys_ftypes1.setter
    def sys_ftypes1(self, val):
        self._sys_ftypes1= val


    @passengers.setter
    def        passengers(self, val): 
        self._passengers= val

    @fstatus1.setter
    def         fstatus1(self, val):
        self._fstatus1 = val


    @orig_time.setter
    def orig_rate(self, val): 
        self._orig_rate= val

        
    @webId.setter
    def webId(self, val):
        self._webId = val


    @pickup_x.setter
    def pickup_x(self, val):
        self._pickup_x = val

    @pickup_y.setter
    def       pickup_y  (self, val): 
        self._pickup_y = val

    @pickup_zone.setter
    def pickup_zone (self, val):
        self._pickup_zone = val

    @pickup_num.setter
    def pickup_num(self, val):
        self._pickup_num= val

    @pickup_street.setter
    def pickup_street(self, val):        
        self._pickup_street = val


    @pickup_city.setter
    def  pickup_city(self, val):       
        self._pickup_city = val

    @pickup_building.setter
    def pickup_building(self, val):        
        self._pickup_building = val

    @pickup_lat.setter
    def  pickup_lat(self, val):       
        self._pickup_apt = val

    @pickup_code.setter
    def pickup_code(self, val):            
        self._pickup_code = val

    @dest_x.setter
    def dest_x(self, val):            
        self._dest_x = val

    @dest_y.setter
    def  dest_y(self, val):           
        self._dest_y = val

    @dest_zone.setter
    def         dest_zone(self, val):    
        self._dest_zone = val

    @dest_num.setter
    def      dest_num(self, val):       
        self._dest_num = val

    @dest_street.setter
    def  dest_street(self, val):       
        self._dest_street = val

    @dest_city.setter
    def  dest_city(self, val):
        self._dest_city = val
    
    @dest_building.setter
    def  dest_building(self, val):
        self._dest_building = val
    
    @dest_apt.setter
    def   dest_apt(self, val):
        self._dest_apt = val

    @dest_code.setter
    def  dest_code(self, val):
        self._dest_code = val


    @fdvt_sys_ftypes.setter
    def fdvt_sys_ftypes(self, val):
        self._fdvt_sys_ftypes = val

    @fdvt_usr_ftypes.setter
    def fdvt_usr_ftypes(self, val):
        self._fdvt_usr_ftypes = val

    @fdvt_dtypes_32.setter
    def fdvt_dtypes_32(self, val):
        self._fdvt_dtypes_32 = val

    @fdvt_vtypes.setter
    def fdvt_vtypes(self, val):
        self._fdvt_vtypes = val

    @fi_taxi.setter
    def fi_taxi(self, val):
        self._fi_taxi = val

    @flag.setter
    def flag(self, val):
        self._flag = val
    
    @flag2.setter
    def flag2(self, val):
        self._flag2 = val
    

    @reg_marks.setter
    def reg_marks(self, val):
        self._reg_marks = val
        

    @flag1.setter
    def flag1(self, val):
        self._flag1 = val
        
    def read_record(self, recnum=1):

        try:

            errmsg = 'Error reading fare record'
            farefile = "/data/fares.fl"
            if self.fare_type == "future":
                farefile = "/data/futures.fl"

            statinfo = os.stat(farefile)
           
            #print statinfo

            if (statinfo.st_size < 4256 * recnum):
                print ' ERROR ....\n'
                return errmsg    
           

            farefmt = self.fareformat # ''.join(farefmts)
            #print  ' fmt size = %d'  % ( struct.Struct(farefmt ).size ) 
            #print 'fmt %s' % (farefmt)

            rec_size = struct.Struct(farefmt).size

            maxrec = statinfo.st_size / rec_size

            if maxrec < recnum:
                print ' ERROR ....\n'
                return errmsg

            #print  ' max rec = %d'  % ( maxrec ) 

            try:
                with open(farefile, "rb") as f:
                    count = 0
                    bRun=True
                    while bRun and count <= recnum:  
                        count = count + 1
                        data = f.read(rec_size)
             
                        if not data:
                            print 'No data .... count = ', count
                            break 
                        else:
                            if (len(data) == rec_size):

                                udata = struct.Struct(farefmt ).unpack(data)
                                #print count%rec_size, udata
                                
                                if udata[0] == recnum:
                                    print ' found fare number %d len(udata)=%d' % ( udata[0], len(udata) )
                                    #print count%rec_size, udata

                                    self.fare_num = udata[0]
                                    self.fstatus = udata[1]
                                    self.dm_fstatus = udata[2]
           
                                    self.cus_num= udata[3]
                                    self.fare_amount = udata[4]
                                    self.driver_id = udata[5]

                                    self.vip_num = udata[6]
                                    self.reg_fare_num = udata[7]

                                    self.reg_disp_time  = udata[8]     
                                    self.pass_on_brd = udata[9]
                                    self.orig_time  =  udata[10]     

                                    self.sys_ftypes1 = udata[11]
                                    self.passengers = udata[12]
                                    self.fstatus1 = udata[13]
                                    self.orig_rate = udata[14]    
                                    self.webId = udata[15] 

                                
                                    offset = PICKUP_ADDR_OFFSET
                                    self.pickup_x =  udata[offset] 
                                    self.pickup_y =  udata[offset + 1]                                   
                                    self.pickup_zone =  udata[offset + 2] 
                                    self.pickup_num =  udata[offset + 3] 
                                    self.pickup_street =  udata[offset + 4] 
                                    self.pickup_city =  udata[offset + 5] 
                                    self.pickup_building =  udata[offset + 6] 
                                    self.pickup_apt =  udata[offset + 7] 
                                    self.pickup_code =  udata[offset + 8] 
                                    
                                    offset = DEST_ADDR_OFFSET 
                                    self.dest_x = udata[offset]
                                    self.dest_y = udata[offset+1]
                                    self.dest_zone =  udata[offset+2]
                                    self.dest_num  =  udata[offset+3]
                                    self.dest_street =  udata[offset+4]
                                    self.dest_city  =  udata[offset+5]
                                    self.dest_building =  udata[offset+6]
                                    self.dest_apt =  udata[offset+7]
                                    self.dest_code  =  udata[offset+8]
                                                                     
                                    offset = FDVT_OFFSET 
                                    self.fdvt_sys_ftypes = udata[offset]
                                    self.fdvt_usr_ftypes =  udata[offset+1]
                                    self.fdvt_dtypes_32 =  udata[offset+2]
                                    self.fdvt_vtypes =  udata[offset+3]


                                    offset = QUE_PRIORITY_OFFSET

                                    self.fi_taxi = udata[offset + 4]

                                    self.reg_marks=  udata[offset+15]
                                    self.flag=  udata[offset+18]
                                    self.flag2 = udata[offset+30]
                                    self.flag1 = udata[offset+34]

                                    self.error = False
                                    bRun = False
                                   
                                    return errmsg

            except Exception as e:
                print '*** 2 farerec exception ', e(str)
                self.error = True                
                return errmsg

        except Exception as e:
            print '*** 3 farrec exception ', e(str)
            self.error = True
            return errmsg

        return None

    
    def to_tuple(self):
        try:
            d = (
                self.fare_num,
                self.fstatus,
                self.dm_fstatus,         
                self.cus_num,
                self.fare_amount,
                self.driver_id ,
                self.vip_num ,
                self.reg_fare_num ,
                self.reg_disp_time,
                self.pass_on_brd,
                self.orig_time,
                self.sys_ftypes1,
                self.passengers,
                self.fstatus1,
                self.orig_rate ,
                self.webId,
           
                self.pickup_x ,
                self.pickup_y,

                self.pickup_zone,
                self.pickup_num ,
                self.pickup_street ,
                self.pickup_city ,
                self.pickup_building ,
                self.pickup_apt ,
                self.pickup_code ,

                self.dest_x ,
                self.dest_y ,
                self.dest_zone ,
                self.dest_num  ,
                self.dest_street ,
                self.dest_city  ,
                self.dest_building ,
                self.dest_apt ,
                self.dest_code,

                self.fdvt_sys_ftypes ,
                self.fdvt_usr_ftypes ,
                self.fdvt_dtypes_32,
                self.fdvt_vtypes,

            )
            
            return d

        except Exception as e:
            print '*** to_tuple exception ', e(str)
            self.error = True
                  

        return None


def retrieve_pickup_zone(fare_num, fare_type="immediate"):
    try:
        zone=0
        if fare_type in [ "immediate", "future"] :
            stored_fare = fare_container(fare_type)
            if not  stored_fare.error:
                stored_fare. read_record( int(fare_num ))
                if not stored_fare.error:
                    zone = stored_fare.pickup_zone
    except Exception as e:
        sys.stdout.write("%s: dispatch save_book_order_tfc 5 : Exception %s\n" % (datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT),  str(e) ) )         
        zone = 0

    return zone


def retrieve_is_zip(fare_num, fare_type="immediate"):
    try:
        ftypes=-1
        if fare_type in [ "immediate", "future"] :
            stored_fare = fare_container(fare_type)
            if not  stored_fare.error:
                stored_fare. read_record( int(fare_num ))
                if not stored_fare.error:
                    ftypes  = stored_fare.sys_ftypes1
                    if ftypes & ZIPCODE_JOB > 0:
                        is_zip = True
                    else:
                        is_zip = False
                    return (True, is_zip)
    except Exception as e:
        sys.stdout.write("%s: dispatch save_book_order_tfc 5 : Exception %s\n" % (datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT),  str(e) ) )         
    
    # Return a tuple to indicate valid response
    # i.e. : error, result
    return (False, False)




class fare_container_db(object):

    def __init__(self, fare_type="immediate"):
        
        self._error = True
        self._fare_type =  fare_type
      
        try:         
            self._fare_num = 0           
            self._pickup_zone = 0            
            self._fi_taxi = 0
            self._error = False
           
        except Exception as e:
            sys.stdout.write("%s: fare_container_db : Exception %s\n" % (datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT),  str(e) ) )  
    

    @property
    def fare_type(self):
        return self._fare_type    
  
    @property
    def error(self):
        return self._error
        
    @property
    def fare_num(self):
        return self._fare_num 

    @property
    def pickup_zone (self):
        return self._pickup_zone 

    @property
    def fi_taxi (self):
        return self._fi_taxi 

    @error.setter
    def error(self, val):
        self._error = val

    @fare_num.setter
    def fare_num(self, val):
        self._fare_num  = val

    @pickup_zone.setter
    def pickup_zone (self, val):
        self._pickup_zone = val

    @fi_taxi.setter
    def fi_taxi (self, val):
        self._fi_taxi = val

    def read_record(self, fare_num):
      try:
        self.fare_num = fare_num
        self.fi_taxi = -1
        self.pickup_zone = -1

            
        fare_num, taxi, zone = dblayer.read_fare_record(fare_num, "immediate")

        print ' t={0}, z={1}'.format( taxi, zone )

        self.fi_taxi = taxi       
        self.pickup_zone = zone

        print ' t={0}, z={1}'.format( taxi, zone )
            
      except Exception as e:
        print ' Exception in read_record ...', str(e)
            
      return (fare_num, self.fi_taxi, self.pickup_zone)
      

def main(): 

    # Fare record size is 4256
    #farestruct = '16I 1992s 2200s'

 
    try:
        print ' main ....'
       
        fare_t = "immediate"       
    
        try:
            if len(sys.argv)  > 2:
                ft =   sys.argv[2]
                if ft in ["immediate", "future"]:         
                    fare_t = ft
            num = int (sys.argv[1])
            
        except Exception as e:
            print ' Exception %s ' % ( str(e) )
            num=1340

        f = fare_container(fare_t) 
        if not f.error:
            f. read_record(num)
        if not f.error:
            print ' ---> ' , f.to_tuple()
       
        print 'pick up zone=%d dest_zone=%d ' % ( f.pickup_zone, f.dest_zone)
        print 'pick up x,y=%s %s  dest x,y=%s %s ' % ( f.pickup_x, f.pickup_y, f.dest_x, f.dest_y)


        print 'fdvt_sys_ftypes=0x%x fdvt_usr_ftypes =0x%x fdvt_dtypes_32 =%x fdvt_vtypes =%x '  \
                                % ( f.fdvt_sys_ftypes , f.fdvt_usr_ftypes , f.fdvt_dtypes_32, f.fdvt_vtypes )



        print 'fi_taxi=%d reg_marks=0x%x flag=0x%x flag1=0x%x flag2=0x%x'  % (f.fi_taxi, f.reg_marks, f.flag, f.flag1, f.flag2)

    except Exception as e:
        print ' Exception in main ...', str(e)
        pass



def read_fare_db(): 

    # Fare record size is 4256
    #farestruct = '16I 1992s 2200s'
                
 
    try:      
        tup=()
        fare, taxi, zone = (-1,-1,-1)
        fare_t = "immediate"       
    
        try:
            if len(sys.argv)  > 2:
                ft =   sys.argv[2]
                if ft in ["immediate", "future"]:         
                    fare_t = ft
            if len(sys.argv)  > 1 :
                num = str (sys.argv[1])
            
        except Exception as e:
            print ' read_fare_db - Exception %s ' % ( str(e) )
            num=18753

        f = fare_container_db(fare_t) 
        if not f.error:
             fare, taxi, zone = f. read_record(num)
        
        print ' fare=%s pick up zone=%d taxi=%d ' % ( fare, taxi, zone  )
        
    except Exception as e:
        print ' Exception in read_fare_db ...', str(e)
        pass


if __name__ == "__main__":
    read_fare_db()
    #main()


