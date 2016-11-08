import sys, os
import datetime
import time

if __name__ == "__main__":  
    app_dir = os.path.dirname(__file__) + "/.."
    sys.path.append (app_dir )


import config.cwebsconf as Config
from fares import fare_const as FareConstant
from app import errormsg as ErrMsg
from app import msgconf
from app import scap

import config.local_settings as LocalSettings

GPS_MULTIPLIER = 1000000
NUM_POINTS = 3



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


    def read_zone_record(self, filenum=1):

        try:
            import struct

            numcols = -1
            numrows = -1

            x_origin = -1
            y_origin = -1
            x_step = -1
            y_step = -1
            x_to_whole_number = -1
            y_to_whole_number = -1


            errmsg = 'Error reading grid record'
            myfile = "/data/zone_grid_info_%d.dat" % (filenum)
            
            statinfo = os.stat(myfile)
           
            print statinfo

            gridfmt =  '13I' 

            '''
            long    origin_x ; /** the grid's origin longitude as an integer **/
            long    origin_y ; /** the grid's origin latitude as an integer **/
            long    max_x ; /* farthest node's x value */
            long    max_y ; /* farthest node's y value */
            long    actual_num_columns_used ; /* not used for now */
            long    actual_num_rows_used ; /* not used for now */
            long    num_of_columns ; /** number of columns in the grid **/
            long    num_of_rows ; /** number of rows in the grid **/
            long    step_value_x ; /** the grid's long step value **/
            long    step_value_y ; /** the grid's lat step value **/
            long    x_to_whole_number ; /** used to convert float -> int **/
            long    y_to_whole_number ; /** same **/
            long    num_of_nodes ;
            '''

            myfmt = gridfmt # ''.join(farefmts)
            print  ' fmt size = %d'  % ( struct.Struct(myfmt ).size ) 
            print 'fmt %s' % (myfmt)

            rec_size = struct.Struct(myfmt).size

            maxrec = statinfo.st_size / rec_size

            if maxrec < 1:
                print ' ERROR ....\n'
                return errmsg

            print  ' max rec = %d'  % ( maxrec ) 

            try:
                with open(myfile, "rb") as f:
                    count = 0
                    bRun=True
                   
                    while bRun and count < maxrec:  
                        count = count + 1
                        data = f.read(rec_size)
             
                        if not data:
                            print 'No data .... count = ', count
                            break 
                        else:                        
                            if (len(data) == rec_size):
                                udata = struct.Struct(myfmt ).unpack(data)                                
                                print udata
                                if len(udata) == 13:
                                    numcols = udata [ 6 ]  
                                    numrows = udata [ 7 ]  
                                    x_origin = udata [ 0 ]  
                                    y_origin = udata [ 1 ]  
                                    x_step = udata [ 8 ]  
                                    y_step = udata [ 9 ]  
                                    x_to_whole_number = udata [10]  
                                    y_to_whole_number = udata [11]  

                            return  (numcols, numrows, x_origin, y_origin, x_step, y_step, x_to_whole_number, y_to_whole_number)                                    
            except Exception as e:                                
                print 'Exception 1 %s ' % ( str(e) )

        except Exception as e:                                
            print 'Exception read_zone_record %s ' % ( str(e) )

        return (numcols, numrows, x_origin, y_origin, x_step, y_step, x_to_whole_number, y_to_whole_number)


    def read_zone_grid_record(self, filenum, grid_info, x, y):

        try:
            import struct

            errmsg = 'Error reading zone grid data record'
            myfile = "/data/zone_grid_%d.dat" % (filenum)
            
            statinfo = os.stat(myfile)
           
            print statinfo

            myfmt =  '2H' 
           
            print 'fmt size = %d'  % ( struct.Struct(myfmt ).size ) 
            print 'fmt %s' % (myfmt)

            rec_size = struct.Struct(myfmt).size

            maxrec = statinfo.st_size / rec_size

            print  'max rec = %d'  % ( maxrec ) 

            maxsize = grid_info[0]  *  grid_info [1]  

            if maxrec <  maxsize :
                print ' ERROR in file size .... Expecting {0} Found {1} \n'.format (  maxsize, maxrec )
                return errmsg

            try:
                with open(myfile, "rb") as f:  
                    try:
                        ly = ( int (GPS_MULTIPLIER * y) ) /  grid_info [4]  
                        lx = ( int (GPS_MULTIPLIER * x) ) /  grid_info [5]  
                    except Exception as e:                                
                        print 'Exception 1 %s ' % ( str(e) )

                    try:
                        ytail = (grid_info [6]   * y - grid_info [2]  ) /  grid_info [4]  
                        xtail = (grid_info [7]   * x - grid_info [3]  ) /  grid_info [5]  

                    except Exception as e:                                
                        print 'Exception 2 %s ' % ( str(e) )

                    try:
                        j = int(ytail)
                        i = int(xtail)

                    except Exception as e:                                
                        print 'Exception 3 %s ' % ( str(e) )

                   
                    try:
                        for item in ( (i-1, j-1), ( i, j-1), (i+1, j-1)):
                            offset = ( item[0]  *  grid_info[0] + item[1] ) *  rec_size
                            print ' item[0]={0} item[1]={1}  grid_info[0]={2}  offset={3} ' .format( item[0], item[1],  grid_info[0],  offset )
                            os.lseek(f, offset, os.SEEK_SET)     
                        
                            data = f.read(rec_size* NUM_POINTS)
             
                            if not data:
                                print 'No data .... item = ', item
                                break 
                            else:                        
                                if (len(data) ==  rec_size* NUM_POINTS):
                                    udata = struct.Struct(myfmt ).unpack(data) 
                                    if  udata[0] and udata[1] :                               
                                        print udata
                    except Exception as e:                                
                        print 'Exception 4 %s ' % ( str(e) )


                               
            except Exception as e:                                
                print 'Exception 5 %s ' % ( str(e) )

        except Exception as e:                                
            print 'Exception read_zone_record %s ' % ( str(e) )



if __name__ == "__main__":
    
    try:
        seqno = 33333
        dic = { "lat" : 40.0, "lon" : 56.00, "fleet" : 1}
        zone_info = ZoneInfo(dic, seqno)
    except Exception as e:
        print 'Exception %s ' % ( str(e) )

    try:
        for i in range (1, 5):
            r = zone_info.read_zone_record(i)
            print  'fnum={0} col= {1} row={2}  '.format ( i, r[0]  , r [1]   )
            if r[0] > 0 and r[1] > 0:
                zone_info.read_zone_grid_record( i, r, 4, 75)
    except Exception as e:
        print 'Exception %s ' % ( str(e) )

