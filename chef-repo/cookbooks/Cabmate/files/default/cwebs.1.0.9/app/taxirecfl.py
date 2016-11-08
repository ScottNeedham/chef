import struct
import json


'''
frmt = '4I 71h 2c 4s 24s 4s 2c 2s 10h 12I 16s 2c 2s 2I 28s'

struct fdv_types
{
    unsigned long sys_ftypes;           /* system defines fare types */
    unsigned long usr_ftypes;           /* user defined fare types */
    unsigned long dtypes_32;            /* user defined driver types */
    unsigned long vtypes;               /* user defined vehicle types */
};                      

struct taxi_info_struct
{
    struct  fdv_types veh_types; //4 * long
    short   taxi_number;
    short   fleet;
    short   vehicle_type;
    short   baseunit;
    short   from_zone[ MAX_ZONES ]; //32
    short   to_zone[ MAX_ZONES ]; //32
    short   training;                           /* is this taxi working the training system ? */
    short   max_passengers;
    unsigned short sspare; // ==> 71 short
    char    comp_num;
    char    termtype;                           /* MDT3602 = '0', MDT4021 = '1' */
    char    termrev[4];                         /* not used in 4.3 */
    char    fleet_name[24];
    char    alias[4];
    char    voice;
    char    sale;
    char    cspare[2];
    short   alternate_fleet[FLEETBACKUP]; //10
    long    drivers[MULTI_DRIVERS]; //10
    long    cur_driver;
    unsigned long veh_class_32;
    char    disallowedchannels[MAX_DISALLOWED_CHANNELS];
    char    VDM_MDTControlEnabled;                      // 24
    char    RearSeatVivotechEnabled;                    // 25
    char    CSpare[2];                          // 26
    unsigned long VDM_MDTControl;                       // 27
    unsigned long expiryTime;                       // 28
    char    DynamoDBalias[17];                  //April 29, 2015 RL This is the same as DeviceNumber;
    char    Spare[11];                          // 29 //    char    Spare[32]; // was 8
};                                      /* This stucture is 208 bytes 6.1 */

8I 2f 540c 
9I 10h 12c 
320c 
24s 2I 2h 4I 2h 1I 1s 2c
1h 2c 64I 
3I 33s 33s 2s 3I 16I 4c 1I 4h 1I 
1h 9c 18s 4s 1c 9s 20s 277c 
5I 1I 2c 1h 2f 2I 2c 1h 5f 2c 1h 4I 1c 20s 1c 130s  
struct cab_struct   /* This is the new taxirec file */
{
    long    position_time ;             
    long    local_expiry_time ;         
    long    ROT_expiry_time ;           
    unsigned long sys_ftypes1;          
    long    bidding_fare;               
    long    cl_preferred_status_expiry_time;    
    long    dual_book_time;             
    long    ss_inactive_time;           
    float   x ;                 
    float   y ;                 
    struct  g_event veh_events[NUM_TAXI_EVENTS];    //12 * 45(NUM_TAXI_EVENTS=45) = 540c
    struct  taxi_status status;         // 9I 10h 12c (total = 68 bytes)
    struct  taxi_info_struct taxinfo;       // 320c
    struct  driver_state state;         //24c 2I 2h 4I 2h 1I 1h 2c => 64c
    struct  acct_info acct;             //1h 2c 64I ==> 260
    struct  susp_struct suspinfo;           //3I 33s 33s 2s 3I 16I 4c 1I => 164
    short   bid_local_stand ;           
    short   first_book_zone ;           
    short   point;                  
    short   book_priority;          // 4h   
    long    last_closest_PD_offer_time;     
    unsigned short  taxistate;          
    unsigned char misc_status;          
    char    driver_group;               
    char    driver_dues;                
    char    preference ;                
    char    sale;                   
    unsigned char   stat;               
    char    num_sats ;              
    char    bid_local ;             
    char    cash_layout_status;         
    char    last_auth_num[18];                  
    char    last_auth_time[4];          
    unsigned char num_futures_assigned;     
    char    newAlias[9];                
    char    PhoneNumber[PHONESIZ];      // = 20 chars
    char    charpad[277];               //offset = 1531
    struct pickup_struct last_pickup;   //offset = 1808 : 5I 1I 2c 1h 2f 2I 2c 1h 5f 2c 1h 4I 1c 20s 1c 130s  ==> 240
    int shift_id;                       //offset = 1828 : 1I 2c 1h 2f 2I 2c 1h 5f 2c 1h 4I 1c 20s 1c 130s 
    unsigned char num_fares_assigned;   // 2c 1h 2f 2I 2c 1h 5f 2c 1h 4I 1c 20s 1c 130s  
    char    offduty_step;               // 1c 1h 2f 2I 2c 1h 5f 2c 1h 4I 1c 20s 1c 130s 
    short   driver_home_zone;           // 1h 2f 2I 2c 1h 5f 2c 1h 4I 1c 20s 1c 130s 
    float   driver_home_x;              // 2f 2I 2c 1h 5f 2c 1h 4I 1c 20s 1c 130s 
    float   driver_home_y;              // 1f 2I 2c 1h 5f 2c 1h 4I 1c 20s 1c 130s 
    long    last_driver_id;             // 2I 2c 1h 5f 2c 1h 4I 1c 20s 1c 130s 
    long    last_job_time;              // 1I 2c 1h 5f 2c 1h 4I 1c 20s 1c 130s 
    struct  meter_statis meterstat;  //2c 1h 5f   ==> offset = 1852 2c 1h 5f 2c 1h 4I 1c 20s 1c 130s 
    char    GPS_status_pkt_recv;   //==> offset 1876     //2c 1h 4I 1c 20s 1c 130s 
    char    MDT_Display;            //1c 1h 4I 1c 20s 1c 130s    
    short   spad;                   //1h 4I 1c 20s 1c 130s 
    long    driverrecnum;           //4I 1c 20s 1c 130s 
    long    LastOpenPremiereDriverFareTime;     
    long    PremiereDriverFareSuspensionTime;   
    long    lastCCRecord;               
    char    FareOfferViaSMS;            //offset=1896
    char    MobilePhoneNumber[PHONESIZ];        // = 20 chars, offset = 1897
    char    VDM_delivered;              // offset = 1917
    char    DenyTempBookOff;                        // Feb 29, 2012 RL
    char    tbookoff_limit_enable;                  //July 21, 2015 RL CCI 78593
    unsigned long reinstateTime;                    // Jan 12, 2012 RL
    char    NumberConsecutiveLocal;                 // July 12, 2012 RL
    char    SerialNumber[51];                       // August 16, 2012 RL
    char    NARejAccTimer;                          // October 24, 2012 RL
    char    sourceupdate;                           // November 09, 2015 RL
    char    market[17];                             // February 18, 2016 RL to support market id maximum 16 characters
    char    pad[53];                                /* added April 12, 2005 RL was 70 bytes */
};



'''



def taxirec_2():

    taxifile = "/data/taxirecs.fl"

    fp = open(taxifile, "r")
    data = fp.read()
    fp.close()
    
    

    fmts =  [ 
        '8I 2f',
        '540c',
        '9I 10h 12c',
        #'4I 1h 1h 300c', # == taxi info struct =320 bytes (320c)
        '4I 1h 1h 1h 1h 32h 32h 1h 1h 1h 2c 4s 24s 4s 2c 2s 10h 10I 1I 1I 16s 2c 2s 2I 28s', ## # == taxi info struct =320 bytes (320c)
        '24s 2I 2h 4I 2h 1I 1h 2c',
        '1h 2c 64I',
        '3I 33s 33s 2s 3I 16I 4c 1I 4h 1I',
        '1h 9c 18s 4s 1c 9s 20s 277c '
        #'5I 1I 2c 1h 2f 2I 2c 1h 5f 2c 1h 4I 1c 20s 1c 130s'
        '5I 1I 2c 1h 2f 2I 2c 1h 5f 2c 1h 4I 1c 20s 1c 1c 1c I 51s 1c 1c 17s 53s'        
        ]
    
    total=0;    
    for item in fmts:
        print  ' fmt size = %d'  % ( struct.Struct(item).size ) 
        total += struct.Struct(item).size 
        print ' total =%d '  % ( total )

    rec_fmt = ''.join(fmts)
    rec_size = struct.Struct(rec_fmt).size

    try:
        with open(taxifile, "rb") as f:
            count = 0
            bRun=True
            while bRun:  
                count = count + 1
                data = f.read(rec_size)
             
                if not data:
                    break 
                else:
                    if (len(data) == rec_size):
                        udata = struct.Struct(rec_fmt).unpack(data)
                        #print count%rec_size, udata
                        #start of taxi_info_struct = 581
                        #taxi number at idx = 585
                        #fleet at idx = 586
                        tis_start = 581
                        taxi_number_offset = 4
                        fleetname_offset = 4 + 71 + 2 + 1
                        alias_offset =  fleetname_offset  + 1
                        alternate_offset = alias_offset  + 4
                        driver_offset = alternate_offset + 10
                        curdrv_offset = driver_offset + 10
                        if  udata[tis_start + taxi_number_offset ] in range(1000,9999):
                            print '%d taxi#[%d] fleet#[%d] fleetname=[%s] alias[%s] curdrv [%d] \n' \
                                            % (count%rec_size, udata[585] , udata[586] \
                                                , udata[tis_start+fleetname_offset] \
                                                , udata[tis_start+alias_offset] \
                                                , udata[tis_start+curdrv_offset ] \
                                                )

                            
                            for i in range(10):
                                print 'alternate fleet %d ' % (udata[tis_start+alternate_offset + i])
                            for i in range(10):
                                print 'drivers %d ' % (udata[tis_start+driver_offset + i])   
                                                         

                            '''
                            idx = 585
                            for i in range(71):
                                print '%d ' % (udata[idx + i])
                            idx += 71
                            for i in range(2):
                                print '%c ' % (udata[idx + i])
                            idx += 2
                            for i in range(2):
                                print '%s ' % (udata[idx + i])
                            print ' idx+i %d' %( idx+i)
                            '''

                    else:
                        bRun=False

    except Exception as e:
        print 'exception ', e



s = struct.Struct('i i i i') # Should be 16 bytes.
data_size = struct.Struct(4*'i').size
print 'data structure size ', data_size


def taxirec():

    taxifile = "/data/taxirecs.fl"

    fp = open(taxifile, "r")
    data1 = fp.read()
    fp.close()
    
    print 'length of data is ', len(data1), 
    frmt = '4I 71h 2c 4s 24s 4s 2c 2s 10h 12I 16s 2c 2s 2I 28s'
    print frmt
    data_size1 = struct.Struct(frmt).size
    s = struct.Struct(frmt)
    print 'data structure size ', data_size1

    #tmp = struct.unpack(frmt, data1)
    #print 'tmp length ', len(tmp)
    '''
    for i in range(len(data1)/data_size1):
        res = []
        for j in range(4):
            res.append(tmp[i*4+j] % 65536)
        if i > 16 and (i + 16) % 16 == channel_id:
            res_dic[res[0]] = (res[1],res[2])
        #print (i+16) % 16, res
    c["VDM_MDTControlEnabled"] = 'N'
    '''
    try:
        with open(taxifile, "rb") as f:
            count = 0
            bRun=True
            while bRun:  
                count = count + 1
                data = f.read(data_size1)
             
                if not data:
                    break 
                else:
                    if (len(data) == data_size1):
                        udata = s.unpack(data)
                        print count%data_size1, udata

                    else:
                        bRun=False

    except Exception as e:
        print 'exception ', e

def all_zones(fleet_to_zoneset):
    res_dic = {}
    file_name1 = '/data/fzstatus/normstat.fl'
    file_name2 = '/data/zstatus/normstat.fl'
    file_name = file_name1
    print 'opening file ', file_name
    try:
        fp = open(file_name, "r")
        data = fp.read()
        fp.close()
    except Exception as e:
        print 'exception ', e
    
    with open(file_name, "rb") as f:
        count = 0
        while True:  
            count = count + 1
            data = f.read(data_size)
             
            if not data:
                break 
            else:
                udata = s.unpack(data)
                print count%data_size, udata
            



if __name__ == "__main__":
   #taxirec()

   mytaxi = 9006
   read_taxirec(mytaxi)

   all_zones([])
