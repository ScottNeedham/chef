import sys
import format_field
import re
import config.cwebsconf as Config
import datetime
import time
import fare_const as FareConstant
import errormsg as ErrMsg
import msgconf
import scap

import config.local_settings as LocalSettings

BIDINFO_ENTRY_LEN=33
BIDINFO_NUM_ENTRIES=4
BIDINFO_TOTAL_LEN=BIDINFO_ENTRY_LEN*BIDINFO_NUM_ENTRIES
DEFAULT_OPERATOR_ID='1000'
DEFAULT_OPERATOR_ID_INT = 1000
DEFAULT_EXPIRY_TIME='23:59'

ONE_YEAR_AHEAD = 31622400 

# Flag container
# Bit 0 ==> signature required indicator
DEFAULT_SIGNATURE_VALUE=0
SIGNATURE_ON = 1 
FLAT_RATE_ON = 2
SIGNATURE_OFF = DEFAULT_SIGNATURE_VALUE

POSTAL_STRING_FORMAT = '7s B'
ZIP_INT_FORMAT = 'I I'


class Fare():

    # Update to order id
    def updateFare(self, dic ):
        try:
            if dic.has_key("order_id") and dic["order_id"] != "":
             self.IBSorderID = format_field.format_field(str(dic["order_id"]), 11, trim_it=True)
        except Exception as e:
            self.IBSorderID= 11*' '

    # Update to operator id
    def updateOperator(self, dic ):
        try:
            if dic.has_key("operator_id") and dic["operator_id"] != "":
                if dic["operator_id"] > 99 :
                    self.OperatorID = format_field.format_field(str(dic["operator_id"]), 4, trim_it=True)
                    self.operator_id = int(self.OperatorID)
        except Exception as e:
            self.OperatorID= DEFAULT_OPERATOR_ID
            self.operator_id = DEFAULT_OPERATOR_ID_INT

    # Update to Expiration 
    def updateExpiration(self, dic ):
        try:
            if dic.has_key("will_call_expiry_date"):
                my_date = datetime.datetime.strptime(dic["will_call_expiry_date"], '%Y-%m-%d')
                my_date += datetime.timedelta(days=1)
                self.expiry_date = my_date.strftime('%Y%m%d')
                self.resv_date = self.expiry_date
                self.reginfo_disp_time = int( time.mktime( my_date.timetuple()))
                self.reginfo_expire_time = int( time.mktime(my_date.timetuple()))
        except Exception as e:
            self.expiry_date = 8*' '
            self.reginfo_disp_time = 0
        try:
            if dic.has_key("will_call_expiry_time"):
                self.expiry_time = dic["will_call_expiry_time"]
            else:
                self.expiry_time = DEFAULT_EXPIRY_TIME
        except Exception as e:
            self.expiry_time = 5*' '

        try:
            if dic.has_key("will_call_expiry_datetime"):
                my_datetime = datetime.datetime.strptime(dic["will_call_expiry_datetime"], '%Y-%m-%d %H:%M')
                self.expiry_date = my_datetime.strftime('%Y%m%d')
                self.expiry_time = my_datetime.strftime('%H:%M')
                self.resv_date = self.expiry_date
                self.resv_time = self.expiry_time
                self.reginfo_disp_time = int( time.mktime( my_datetime.timetuple()))
                self.reginfo_expire_time = int( time.mktime(my_datetime.timetuple()))
        except Exception as e:
            self.expiry_date = 8*' '
            self.expiry_time = 5*' '
            self.reginfo_disp_time = 0

        try:
            if "will_call_expiry_date" not in dic and "will_call_expiry_datetime" not in dic and "will_call_expiry_time" not in dic:
                dt = datetime.datetime.now() + datetime.timedelta(days=300)
                self.expiry_date = dt.strftime('%Y%m%d')
                self.resv_date = self.expiry_date
                self.reginfo_disp_time = int( time.mktime(dt.timetuple()))
                self.reginfo_expire_time = int( time.mktime(dt.timetuple()))
        except Exception as e:
            self.expiry_date = 8*' '
            self.resv_date = 8*' '
            self.reginfo_disp_time = 0

        try:
            if "pickup_datetime" in dic:
                pickup_datetime = datetime.datetime.strptime(dic["pickup_datetime"], Config.DateFormat_SaveOrder_Input)
                self.resv_date = pickup_datetime.strftime('%Y%m%d')
                self.resv_time = pickup_datetime.strftime('%H:%M')
                self.reginfo_disp_time = int( time.mktime(pickup_datetime.timetuple()))                          
        except Exception as e:
            self.expiry_date = 8*' '
            self.resv_date = 8*' '
            self.reginfo_disp_time = 0

        #sys.stdout.write("%s: *** updateExpiration  *** expiry date:%d %d %d %d  \n" % (datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT), self.expiry_date,  self.expiry_time,  self.reginfo_disp_time , self.reginfo_expire_time ))

    # 
    def updateBuildingType(self, dic):
        self.pick_building_type = ' '
        self.dest_building_type = ' '
        try:
            if dic.has_key("pick_up_building_type") and dic["pick_up_building_type"] != '':
                self.pick_building_type = dic["pick_up_building_type"] 
            if dic.has_key("dest_building_type") and dic["dest_building_type"] != '':
                self.dest_building_type = dic["dest_building_type"] 
        except Exception as e:
            self.pick_building_type = ' '
            self.dest_building_type = ' '
            pass
        #print ' pickup building type ', self.pick_building_type, ' dest ', self.dest_building_type

    def serializeBuildingType(stream):
        stream  += self.pick_building_type + self.dest_building_type 
        return stream
    

    def updatePaymentDetails(self, dic):
        self.flag_container = DEFAULT_SIGNATURE_VALUE
        try:
            if 'signature_required' in dic and dic['signature_required'] in ('Y', 'y', 'T', 't') :
                self.flag_container = SIGNATURE_ON  
            if 'is_flat_rate' in dic and dic['is_flat_rate'] in ('Y', 'y', 'T', 't') :  
                self.flag_container += FLAT_RATE_ON             
                #print '###flat rate is on ###'
        except Exception as e:
            self.flag_container = DEFAULT_SIGNATURE_VALUE
            pass
        
        self.flag_container =  chr(self.flag_container)

   
    def get_fleet_number(self):
        return int (self.fleet_number)
        
    def fare_future(self):
        return self.is_future

    def fare_set_future(self, flag, pickup_time=None):
        if pickup_time != None and flag == True:
            pickup_datetime = pickup_time
            self.resv_date = pickup_datetime.strftime('%Y%m%d')
            self.resv_time = pickup_datetime.strftime('%H:%M')
            self.reginfo_disp_time = int( time.mktime(pickup_datetime.timetuple()))   
            if self.reginfo_expire_time == 0:
                self.reginfo_expire_time =self.reginfo_disp_time         
        self.is_future = True if flag else False

    #TODO
    def trim(self):
        if self.pbuildingname == 32*' ':
            self.pbuildingname = 32*b'\x00'
        if self.dbuildingname == 32*' ':
            self.dbuildingname = 32*b'\x00'
        if self.dest_apartment == 7*' ':
            self.dest_apartment = 7*b'\x00'
        if self.dest_code == 7*' ':
            self.dest_code = 7*b'\x00'
        if self.pick_apartment == 7*' ':
            self.pick_apartment = 7*b'\x00'
        if self.pick_code == 7*' ':
            self.pick_code = 7*b'\x00'
        if self.pcityname == 32*' ':
            self.pcityname = 32*b'\x00'
        if self.dcityname == 32*' ':
            self.dcityname = 32*b'\x00'
        if self.passengername == 32*' ' :
            self.passengername = 32*b'\x00'  
        if self.phone == 19*' ' :
            self.phone = 19*b'\x00'   
        if self.dest_zip == 6*' ':
            self.dest_zip = 6*b'\x00'
        if self.pick_zip == 6*' ':
            self.pick_zip =  6*b'\x00'
        #if self.fleet_number == 4*' ':
        #    self.fleet_number = 4*b'\x00'

    def __init__(self, fare_dic, zone, SeqNo, fn=''):
        self.Flag1 =0
        self.Flag2=0
        self.sys_ftypes1 = 0
        self.mtype = msgconf. MT_GE_CALL
        self.reginfo_disp_time = 0
        self.acctno = 12*' '  # Account  Number
        lCorporateAccount = False
        self.flag_container = 0

        self.reginfo_expire_time =0        
        self.reginfo_lead_time = 0
        self.reginfo_orig_time = 0
        self.reginfo_uid = 0
        self.xphones = [20*b'\x00' for i in range(6)]     

        #print 'inside Fare constructor'
        self.is_future = False
        if fare_dic.has_key("is_future") and  fare_dic["is_future"]  in ['Y', 'y']:
            self.is_future = True      
        if fare_dic.has_key("will_call") and  fare_dic["will_call"]  in ['Y', 'y']:
            self.is_future = True             
        if "account_number" in fare_dic:
            self.acctno = format_field.format_field(fare_dic["account_number"], 12, trim_it=True)
            #print 'self.acctno ', self.acctno
        if fare_dic.has_key("customer_number"):
            if fare_dic["customer_number"] != "":
                try:
                    custno = int(fare_dic["customer_number"])
                    self.custno = format_field.format_field(fare_dic["customer_number"], 10)
                    lCorporateAccount = True
                except Exception as e:
                    self.custno = 10*' '
                #raise Exception("customer_number is not int")   
            else:
                self.custno = 10*' '                
        else:    
            # Customer Number
            self.custno = 10*' '
        #print 'self.custno ', self.custno
        self.acctname = 20*' ' 
        if lCorporateAccount:
            if fare_dic.has_key('account_name'):
                self.acctname = 20*' ' if fare_dic['account_name'] == '' else format_field.format_field(fare_dic['account_name'], 20, trim_it=True)
            else:
                self.acctname = 20*' ' 
        else:
            if "account_number" in fare_dic:
                self.acctname = format_field.format_field("TEL" + fare_dic["account_number"], 20, trim_it=True) 
            #print 'self.acctname ', self.acctname
        # Telephone Number
        self.phone = 19*' '  
        try:
            if "phone" in fare_dic:
                self.phone = format_field.format_field(fare_dic["phone"], 19, trim_it=True)
        except Exception as e:
            self.phone = 19*' '               
        # Passenger Number
        try:
            self.passengername = format_field.format_field(fare_dic["passenger_name"], 32, trim_it=True)
        except Exception as e:
            self.passengername = 32*' '      
        # pickup Street Number
        try:
            self.pick_street_no = format_field.format_field(fare_dic["pick_up_street_number"], 6, trim_it=True)
        except Exception as e:
            self.pick_street_no = 6*' '
        try:
            self.pick_street_name = format_field.format_field(fare_dic["pick_up_street_name"], 32, trim_it=True)
        except Exception as e:
            self.pick_street_name = 32*' '  
        self.pick_street_type = 2*' '   
        
        try: 
            self.pick_city = format_field.format_field(fare_dic["pick_up_city"], 4, trim_it=True)
        except Exception as e:
            self.pick_city = 4 *' '
        try:
            self.pick_apartment = format_field.format_field(fare_dic["pick_up_apartment_number"], 7, trim_it=True)
        except Exception as e:
            self.pick_apartment = 7*' '
        # this is access code 
        try:
            self.pick_code = format_field.format_field(fare_dic["pick_up_apartment_code"], 7, trim_it=True)
        except Exception as e:
            self.pick_code = 7*' '


        try:
            self.pick_zip = 6*' '
            self.dest_zip = 6*' '  
            self.postcode_or_zip = 'Y'  

            if fare_dic.has_key("pick_up_zip_code"):
                #isnum =  format_field.is_numeric (fare_dic["pick_up_zip_code"] )
                #print ' isnum %d  type=%s' % ( isnum ,  type(fare_dic["pick_up_zip_code"]) )
                isnum=False
                self.pick_zip = format_field.format_field(fare_dic["pick_up_zip_code"], 6, True, isnum)
                if type(fare_dic["pick_up_zip_code"]) in [ str, unicode] and not isnum:
                    self.postcode_or_zip = 'Y'
                try:
                    if fare_dic.has_key("destination_zip_code"):                
                        self.dest_zip = format_field.format_field(fare_dic["destination_zip_code"], 6, True, isnum)
                except Exception as e:
                    print ' Exception %s ' % (str(e)) 
                    self.dest_zip = 6*' '               
        except Exception as e:
            print ' __init__ Exception %s ' % (str(e)) 
            self.pick_zip = 6*' '
            self.dest_zip = 6*' '
            self.postcode_or_zip = 'Y'
       
        sys.stdout.write("%s: ispostal=%s self.pick_zip=%s self.dest_zip=%s \n" % (datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT), \
                            self.postcode_or_zip, self.pick_zip , self.dest_zip ) )      

        self.pick_zone = format_field.format_field(str(zone), 4, False)
        # pickup building name
        try:
            self.pbuildingname = format_field.format_field(fare_dic["pick_up_building_name"], 32, trim_it=True)
        except Exception as e:
            self.pbuildingname = 32*' '

        # Destination Street Number
        try:
            self.dest_street_no = format_field.format_field(fare_dic["destination_street_number"], 6, trim_it=True)
        except Exception as e:
            self.dest_street_no = format_field.format_field(' ', 6, trim_it=True)
        try:
            self.dest_street_name = format_field.format_field(fare_dic["destination_street_name"], 32, trim_it=True)
        except Exception as e:
            self.dest_street_name = format_field.format_field(' ', 32, trim_it=True)    
        self.dest_street_type = 2*' '
        try:
            self.dest_city = format_field.format_field(fare_dic["destination_city"], 4, trim_it=True)
        except Exception as e:
            self.dest_city = 4*' '    
      
         
        self.dest_zone = 4*' '
        if fare_dic.has_key('dest_zone') and fare_dic['dest_zone'] != '':
            self.dest_zone = format_field.format_field(str(fare_dic['dest_zone']), 4, False)
        # drop-off building name
        #self.dbuildingname = 32*' ' 
        try:
            self.dbuildingname = format_field.format_field(fare_dic["destination_building_name"], 32, trim_it=True)
        except Exception as e:
            self.dbuildingname = 32*' '
    
    # Number of passengers
        try:
            self.num_of_passengers = format_field.format_field(str(fare_dic["pick_up_passengers"]), 2, False)
        except Exception as e:
            self.num_of_passengers = 2*' ' 
        try:
            self.remarks1 = 32*' ' # Remarks line 1-4
            self.remarks2 = 32*' ' # Remarks line 1-4
            self.remarks3 = 32*' ' # Remarks line 1-4
            self.remarks4 = 32*' ' # Remarks line 1-4

            #print 'remarks ', fare_dic["remarks"]
            if len(fare_dic["remarks"]) > 0:
                #print 'length of remarks array', len(fare_dic["remarks"])
                #print 'remarks ', fare_dic["remarks"]
                for rem, i in zip(fare_dic["remarks"], range(len(fare_dic["remarks"])) ):
                    if i == 0:
                        self.remarks1 = format_field.format_field(rem, 32, trim_it=True)
                    elif i == 1:
                        self.remarks2 = format_field.format_field(rem, 32, trim_it=True)
                    elif i == 2:
                        self.remarks3 = format_field.format_field(rem, 32, trim_it=True)
                    elif i == 3:
                        self.remarks4 = format_field.format_field(rem, 32, trim_it=True)
                    else:    
                        break
 
        except Exception as e:    
            self.remarks1 = 32*' ' # Remarks line 1-4
            self.remarks2 = 32*' ' # Remarks line 1-4
            self.remarks3 = 32*' ' # Remarks line 1-4
            self.remarks4 = 32*' ' # Remarks line 1-4

        self.extra_info = 80*' ' # for Line 1-8, was [8][16]
        
        self.resv_date = 8*' ' # YYYYMMDD, reservation Date
        self.resv_time = 5*' ' # HH:MM(24 hour format),Time

        self.expiry_date = 8*' '
        self.expiry_time = 5*' ' 
        self.will_call = ' '
        lWillCall = False
        if fare_dic.has_key("will_call"):
            if fare_dic["will_call"] == 'Y':
                lWillCall = True
                self.will_call = 'Y' 
        if not lWillCall:
            try:
                pickup_datetime = datetime.datetime.strptime(fare_dic["pickup_datetime"], Config.DateFormat_SaveOrder_Input)
                self.resv_date = pickup_datetime.strftime('%Y%m%d')
                self.resv_time = pickup_datetime.strftime('%H:%M')
                self.reginfo_disp_time = int( time.mktime(pickup_datetime.timetuple()))                              
            except Exception as e:
                self.reginfo_disp_time = 0
                pass
        else:
            self.updateExpiration(fare_dic)

        self.pick_x = 10*' '
        self.pick_y = 10*' '     
        self.dest_x = 10*' '
        self.dest_y = 10*' '         

        if 'pick_up_lng' and 'pick_up_lat' in fare_dic:
            self.pick_x =  format_field.format_field( str(int(fare_dic["pick_up_lng"] * 1000000)), 10, True);
            self.pick_y =  format_field.format_field( str(int(fare_dic["pick_up_lat"] * 1000000)), 10, True);
            try:
                self.dest_x = format_field.format_field( str(int(fare_dic["destination_lng"] * 1000000)), 10, True);
                self.dest_y = format_field.format_field( str(int(fare_dic["destination_lat"] * 1000000)), 10, True);
            except Exception as e:
                self.dest_x = 10*' ' # ex. (-75.922478,45.345203)
                self.dest_y = 10*' ' # we put "-7592478 45345203"        



        self.payment_method = 2*' ' # method of payments
        try:
            pay_meth = str(fare_dic["payment_method"])
             
            if Config.PaymentTypeDic.has_key(pay_meth):         
                self.payment_method = Config.PaymentTypeDic[pay_meth]
                if self.payment_method == 'AC' and lCorporateAccount == False:
                    self.payment_method = 2*' '    
            else:
                print 'key ', pay_meth, ' is not found...'
        except Exception as e:
            self.payment_method = 2*' '  
        
        tmp = 32*['N'] # VCLASS_NUMRECS increased to 32 from 8 (Cabmate 8.x)    
        self.vehicle_preference = 32*'N'
        try:
            for vp in fare_dic["vehicle_preference"]:
                tmp[vp - 1] = 'Y' 
            self.vehicle_preference = "".join(tmp)  
        except Exception as e:
            self.vehicle_preference = 32*'N'
        
        tmp = 32*['N'] 
        self.driver_preference = 32*'N'
    
        try:
            for dp in fare_dic["driver_preference"]:
                tmp[dp - 1] = 'Y' 
            self.driver_preference = "".join(tmp)   
        except Exception as e:
            self.driver_preference = 32*'N'
    
        self.fleet_number = 4*' '
        try:
            if 'fleet_number' in fare_dic:
                #print 'setting fleet_number...' , fare_dic["fleet_number"]                
                self.fleet_number = format_field.format_field(str(fare_dic["fleet_number"]), 4, True);
        except Exception as e:
            self.fleet_number =  4*' '

        self.sequence_number = SeqNo
        self.directions = [32*' ' for i in range(8)]
        self.curb_dispatch = ' ' # Y to allow curb dispatch;
        self.direction = ' ' # '1' if there is a direction from
        # driver id for pre assignment
        try: 
            self.driverid = 8*' '
            self.driverid = format_field.format_field(fare_dic["driver_id"], 8, True);
        except Exception as e:
            self.driverid = 8*' '
        
        self.driver_name = 23*' ' # 23 characters for driver name
        try:
            self.vehicle_number = format_field.format_field(fare_dic["vehicle_number"], 4, True);
        except Exception as e:
            self.vehicle_number = 4*' ' # vehicle number
        
        self.charter_flag = ' ' # Is it a chartered moves? Y/N or
        self.charter_hours = 8*' ' # charter hours
        self.charter_miles = 8*' ' # charter miles
        self.fare_amount = 8*' ' # in cents, FIS orig_rate
        try:                   
            
            self.fare_amount_i = int(str(fare_dic["flat_rate"]))                        
            self.fare_amount = format_field.format_field(("%2.2f" % (self.fare_amount_i / 100.0)), 8, trim_it=True)
        except Exception as e:
            self.fare_amount = 8*' '
            self.fare_amount_i = 0
    
        #print ' fare amount = ', self.fare_amount

        self.airline = 16*' ' #
        self.flight = 6*' ' #
        self.flightorgcity = 10*' '
        self.flight_arrtime = 8*' '
        self.flight_instruction = 15*' '
        self.room_number = 8*' '
        try:
            self.contact_name = format_field.format_field(fare_dic["contact_name"], 20, trim_it=True)
        except Exception as e:
            self.contact_name = 20*' ' # used in dest address passenger name                 
    
        self.fare_num = 6*' ' # used for modifying a job
        if fn != '':
            self.fare_num = format_field.format_field(fn, 6, True);   

        self.taxi_x = 10*' ' 
        self.taxi_y = 10*' ' 
        self.reason = 16*' '
        self.newSeqno = 10*' '
        self.Run_number = 6*' '
        self.pup_sequence = 2*' ' 
        self.drop_sequence = 2*' ' 
        self.run_fare_sequence_number = 2*' ' 
        self.total_number_fares_in_run = 2*' ' 
        self.routable = ' ' 
        self.taxi_gpsdate = 8*' ' # YYYYMMDD, last date taxi gps was received
        self.taxi_gpstime = 5*' ' # HH:MM(24 hour format), last time axi gps was received
           
    
        try:
            self.pcityname = format_field.format_field(fare_dic["pick_up_city"], 32, trim_it=True)
        except KeyError:
            self.pcityname = 32*' '

        try:
            self.dcityname = format_field.format_field(fare_dic["destination_city"], 32, trim_it=True)
        except KeyError:
            self.dcityname = 32*' '
        
        self.authorization_number = 10*' '            
        self.dispatch_priority = 4*' '
        if fare_dic.has_key("dispatch_priority"):
            try:
                dispatch_priority = int(fare_dic["dispatch_priority"])
                if dispatch_priority in range(10):
                    self.dispatch_priority = format_field.format_field(str(dispatch_priority), 4, trim_it=True)   
            except Exception as e:
                pass     
        print 'self.dispatch_priority= %s ' % ( self.dispatch_priority)
        try:
            self.dest_apartment = format_field.format_field(fare_dic["destination_apartment_number"], 7, trim_it=True)
        except Exception as e:
            self.dest_apartment = 7*' '

        self.dest_code = 7*' '                            
        if lCorporateAccount:
            self.account_type = 'C'
            self.dest_code = 7*' '            
        else:
            self.account_type = 'T'
        
        try:
            self.dest_code = format_field.format_field(fare_dic["destination_apartment_code"], 7, trim_it=True) 
        except Exception as e:
            self.dest_code = 7*' '  

        self.add_account = ' '
        if fare_dic.has_key("add_account"):
            if fare_dic["add_account"]:
                self.add_account = 'Y' 
        if fn != "" or lCorporateAccount:
            self.add_account = ' '    
        self.hailed_trip = ' '
        try:
            self.SMS_Enabled = 'Y' if fare_dic["txt_back"] else ' '
            print 'SMS_Enabled is', self.SMS_Enabled 
        except KeyError:
            self.SMS_Enabled = ' '

        self.InOut = ' '
        try:
            if fare_dic.has_key("quick_return"):
                self.InOut = 'Y' if fare_dic["quick_return"] == 'Y' else ' '
        except Exception as e:
            self.InOut = ' '

        self.AppointmentTime = 5*' '
        self.VIPNumber = 12*' '

        self.Quantity = ' ' 
        self.num_of_jobs = 1
        if fare_dic.has_key("number_of_jobs") and fn == '':
            try:
                self.num_of_jobs = int(fare_dic["number_of_jobs"])
                if self.num_of_jobs > 1 and self.num_of_jobs < 256:
                    self.Quantity = chr(self.num_of_jobs)
            except Exception as e:
                self.num_of_jobs = 1
            


        self.special_data = 80*' '
    
        self.special_data_id = [' ' for i in range(8)]
        self.ei_Conf_Length = [' ' for i in range(8)] 
        self.ei_Conf_Prompt = [13*' ' for i in range(8)]           
        if lCorporateAccount:     
            special_data = ''  
        if "prompts" in fare_dic :
            for p, i in zip(fare_dic["prompts"], range(len(fare_dic["prompts"]))):
                plen = p["length"] if p["length"] < 13 else 0
                #plen = len(p) if len(p) < 13 else 12
                print 'prompt i', i, 'length ', plen
                if plen > 0 and plen < 10:
                    self.ei_Conf_Length[i] = str(plen)
                elif plen == 10:
                    self.ei_Conf_Length[i] = 'A'
                elif plen == 11:
                    self.ei_Conf_Length[i] = 'B'
                elif plen == 12:
                    self.ei_Conf_Length[i] = 'C'
                else:
                    self.ei_Conf_Length[i] = ' '    
                #does not work ... self.ei_Conf_Length[i] = chr(plen)
                #this works ... self.ei_Conf_Length[i] = '9'
                self.ei_Conf_Prompt[i] = format_field.format_field(p["response"], 13, trim_it=True)
                special_data = special_data + format_field.format_field(p["response"], p["length"], trim_it=True) 
                self.special_data = format_field.format_field(special_data, 80, trim_it=True)  
        try:
            self.CalloutNotAllowed = 'Y' if fare_dic["callout_not_allowed"] == 'Y' else ' '
        except Exception as e:
            self.CalloutNotAllowed = ' '
        #print 'CalloutNotAllowed#', self.CalloutNotAllowed, '#'
        if Config.EnableIdentificationAsArcus:
            self.Taxihail = 'A'
        else:
            self.Taxihail = ' '
        try:
            self.LocalCall = 'Y' if fare_dic["local_call"] in ['Y','y'] else 'N'
            #print 'LocalCall is#', self.LocalCall, '#'
        except Exception as e:
            self.LocalCall = ' '

        try:
            self.Priority= 'Y' if fare_dic["priority_call"] in ['Y','y'] else 'N'
            #print 'Priority is#', self.Priority, '#'
        except KeyError:
            self.Priority= ' '

        try:
            self.Restricted = 'Y' if fare_dic["restricted_code"] in ['Y','y'] else 'N'
            #print 'Restricted is#', self.Restricted, '#'
        except KeyError:
            self.Restricted= ' '

        try:
            self.Bid= 'Y' if fare_dic["bid_call"] in ['Y','y'] else 'N'
            #print 'Bid#', self.Bid, '#'
        except KeyError:
            self.Bid= ' '

        try:
            self.ForceZone= 'Y' if fare_dic["force_zone"] in ['Y','y'] else 'N'
        except KeyError:
            self.ForceZone= ' '

        try:
            self.ExcludeIVR= 'Y' if fare_dic["exclude_ivr"] in ['Y','y'] else 'N'
        except KeyError:
            self.ExcludeIVR= ' ' 

        try:
            self.NoService= 'Y' if fare_dic["no_service"] in ['Y','y'] else ' '
            print 'No Service#', self.NoService, '#'
        except KeyError:
            self.NoService= ' '

        self.dest_passengername = 32*' '
        
        try:
            self.IBSorderID = 11*' '
            if fare_dic.has_key("order_id") and fare_dic["order_id"] != "":
                self.IBSorderID = format_field.format_field(str(fare_dic["order_id"]), 11, trim_it=True)
        except Exception as e:
            self.IBSorderID = 11*' '
        try:
            self.mobile_phone = format_field.format_field(fare_dic["mobile"], 18, trim_it=True)
        except Exception as e:
            self.mobile_phone = 18*' '
   
        self.display_attribute = '  '
        try:
            if Config.lNewFareData:
                if fare_dic["tip_amount"]:
                    self.tipamount= fare_dic["tip_amount"] 
                else:
                    self.tipamount= 11*' '
        except KeyError:
            self.tipamount = 11*' ' # was 13

    

        self.OperatorID= DEFAULT_OPERATOR_ID
        self.operator_id = DEFAULT_OPERATOR_ID_INT
        #self.spare = 1*' '
        if Config.lNewFareData:
            try:
                self.bid_info = []
                i=0
                while i < BIDINFO_NUM_ENTRIES:
                    self.bid_info.append(BIDINFO_ENTRY_LEN*' ')
                    i +=1
                    if fare_dic.has_key("bid_info") and self.Bid == 'Y':
                        if len(fare_dic["bid_info"]) > 0:
                            for rem , i in zip(fare_dic["bid_info"], range(len(fare_dic["bid_info"])) ):
                                self.bid_info[i] = format_field.format_field(rem, BIDINFO_ENTRY_LEN, trim_it=True)
            except KeyError:    
                pass
            self.filler= 329*' '
            self.reserved= 2118*' ' #2120*' '

        self.updateOperator(fare_dic)

        self.updateBuildingType(fare_dic)

        self.updatePaymentDetails(fare_dic)

        self.createPadding(fare_dic)

        self.create_space_saver_struct()
        print ' Returning from fare creation'

    def createPadding(self, dic):
        self.xforminfo = 396 * b'\x00'
        self.xjobinfo_filling = 1338* b'\x00' # (1536-198)

    
        # H B B I I
        self.ss_uid = msgconf.CWEBS
        self.ss_count = 1
        self.ss_evno = msgconf.EV_ENTER_FARE
        self.ss_time = time.mktime(datetime.datetime.now().timetuple())
        self.ss_val = 0
        self.ss = 468*b'\x00' 

        #self.user_data = 95*' ' + b'\x00'

        self.point_val = 4 * b'\x00'
        self.rflt = 22 * b'\x00'

        #'3b B 20s 3s 8s 9s 20s I I I H H I I I 100s ' = '192s'
        self.payment_ct = 0
        self.payment_cp = 0
        self.payment_dis = 0 
        self.payment_f3 = 0
        self.payment_cn = 20 * b'\x00'
        self.payment_att = 3 * b'\x00'
        self.payment_pai = 8 * b'\x00'
        self.payment_cr1 = 9 * b'\x00'
        self.payment_cr2 = 20 * b'\x00'
        self.payment_exp = 0
        self.payment_vid = 0
        self.payment_order = 0
        self.payment_tipper = 0
        self.payment_to = 0
        self.payment_meter = 0
        self.payment_tipinc = 0
        self.payment_tipamount = 0
        self.payment_data = 100 * b'\x00'
         
        self.code_9_event = 16 * b'\x00' # seems to be unused
       
        self.regtrack = 16 * b'\x00'

        return

    def create_space_saver_struct(self):        
        
      
        ss = (  (0, ) * 16, (0, 0 ,
                            0, 0,
                            0, 0,
                            0, 0,), 
                            ( self.reginfo_expire_time, self.reginfo_disp_time,  self.reginfo_lead_time, 0,),  
                            ( self.reginfo_uid,) ,( 0,  self.reginfo_orig_time,), (0, ) * 80, (b'\x00', ) * 194 )
        self.ss_data = sum(ss, ())
        self.ss_fmt = '24I 7I 10H I 69H 194c'
       
       


    def to_msg(self):
        data = ''
        data = data + self.acctno         
        data = data + self.custno     
        data = data + self.acctname
        data = data + self.phone     
        data = data + self.passengername
        data = data + self.pick_street_no        
        data = data + self.pick_street_name         
        data = data + self.pick_street_type 
        data = data + self.pick_city    
        data = data + self.pick_apartment 
        data = data + self.pick_code   
        data = data + self.pick_zip 
        data = data + self.pick_zone    
        data = data + self.pbuildingname
        data = data + self.dest_street_no + self.dest_street_name + self.dest_street_type + self.dest_city + self.dest_zip + self.dest_zone + self.dbuildingname     
        data = data + self.num_of_passengers + self.remarks1 + self.remarks2 + self.remarks3 + self.remarks4 + self.extra_info
        data = data + self.resv_date + self.resv_time + self.pick_x + self.pick_y + self.dest_x + self.dest_y
        
        print 'fleet_number:' +  self.fleet_number + '->' + data + '<-'
        try:
            data = data + self.payment_method + self.vehicle_preference + self.driver_preference + self.fleet_number + self.sequence_number
        
            for direc in self.directions:
                data = data + direc
            data = data + self.postcode_or_zip + self.curb_dispatch + self.direction
        except Exception as e:
            sys.stdout.write("%s: Error *** 1  *** %s \n" % (datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT), str(e)))                                  
        
        try:      
            data = data + self.driverid + self.driver_name + self.vehicle_number + self.charter_flag
        except Exception as e:
            sys.stdout.write("%s: Error *** 2  *** %s \n" % (datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT), str(e)))                                  

        data = data + self.charter_hours + self.charter_miles + self.fare_amount + self.airline + self.flight + self.flightorgcity + self.flight_arrtime + self.flight_instruction
        data = data + self.room_number + self.contact_name + self.fare_num + self.taxi_x + self.taxi_y + self.reason + self.newSeqno
        data = data + self.Run_number + self.pup_sequence + self.drop_sequence + self.run_fare_sequence_number + self.total_number_fares_in_run + self.routable
     
        data = data + self.taxi_gpsdate + self.taxi_gpstime + self.pcityname + self.dcityname + self.authorization_number + self.dispatch_priority + self.dest_apartment + self.account_type    
        data = data + self.dest_code + self.add_account + self.hailed_trip + self.SMS_Enabled + self.expiry_date + self.expiry_time + self.will_call + self.InOut + self.AppointmentTime + self.VIPNumber + self.Quantity + self.special_data
      
        for it in self.special_data_id:
            data = data + it
        for it in self.ei_Conf_Length:
            data = data + it
        for it in self.ei_Conf_Prompt:
            data = data + it        

        if not Config.lNewFareData:
            if not Config.lDisplayAttribute:                             
                data = data + self.CalloutNotAllowed + self.LocalCall + self.Taxihail + self.dest_passengername + self.IBSorderID + self.mobile_phone + self.display_attribute + self.ForceZone + self.ExcludeIVR + self.Priority + self.Bid + self.Restricted + self.NoService + self.OperatorID + self.pick_building_type + self.dest_building_type + self.flag_container
            else:
                data += self.CalloutNotAllowed + self.LocalCall + self.Taxihail + self.dest_passengername + self.IBSorderID + self.display_attribute + self.mobile_phone + self.ForceZone + self.ExcludeIVR + self.Priority + self.Bid + self.Restricted + self.NoService + self.OperatorID +   self.pick_building_type + self.dest_building_type + self.flag_container
                #print 'fare [',data, ']'
        if Config.lNewFareData:
            #print 'new fare amount ', self.fare_amount 
            data += self.CalloutNotAllowed + self.LocalCall + self.Taxihail + self.dest_passengername + self.IBSorderID + self.display_attribute + self.mobile_phone + self.ForceZone + self.ExcludeIVR + self.filler + self.Priority + self.Bid + self.Restricted + self.NoService 
            for i in range(len(self.bid_info)):
                data += self.bid_info[i]
             
            data += self.OperatorID
            data += self.pick_building_type + self.dest_building_type 
            data += self.reserved
        
        return data


    

    def fare_to_bin(self, pzone=None, seqno=None, packit=True):
        from socketcli import sClient  

        errmsg = None
        vehicle_number=0

        port_number=LocalSettings.BOTTLE_PORT
        sspare=0
        requester_ip= LocalSettings.BOTTLE_IP  
       
        self.flag=0

        self.fdvt_sys_ftypes = 0
        self.fdvt_usr_ftypes = 0
        self.fdvt_dtypes_32 = 0
        self.fdvt_vtypes = 0
        self.reg_marks=0


        self.que_priority = 0

        self.landmark = 33* b'\x00'    #self.landmark, #33s
        self.borough =  3* b'\x00'    #self.borough,

      
        #not used in cwebs 
        try:
            self.rgev_pup_sequence=0
            self.rgev_drop_sequence=0
            self.rgev_run_fare_sequence_num=0
            self.rgev_total_number_fares_in_run=0
            self.rgev_manifest=0
            self.rgev_run_number=0
            self.rgev_fare=0
            self.veh_class_32 = 0
            self.xjobinfo =  198 * b'\x00'
            self.ei_conf_length = [ 0 for i in range(8)]
            self.ei_conf_prompt = [ 12 * b'\x00' for i in range(8)]
        except Exception as e:            
            sys.stdout.write("%s: Error while encoding unused fields %s \n" % (datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT), str(e)))               

        try:
            # 'Y' ==> is postal code
            pick_postcode = 7*b'\x00'
            dest_postcode = 7*b'\x00'
            sys.stdout.write("%s: ispostal=%s self.pick_zip=%s self.dest_zip=%s \n" % (datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT), \
                            self.postcode_or_zip, self.pick_zip , self.dest_zip ) )  
            if hasattr(Config, 'USE_POSTAL_CODE') and Config.USE_POSTAL_CODE:
                    pick_postcode = self.pick_zip 
                    dest_postcode = self.dest_zip               
                    postcode_format = POSTAL_STRING_FORMAT          
            else:
                if self.postcode_or_zip == 'Y':
                    pick_postcode = self.pick_zip 
                    dest_postcode = self.dest_zip               
                    postcode_format = POSTAL_STRING_FORMAT            
                elif self.postcode_or_zip == 'N':
                    print ' type pick_zip = %s  dest_zip = %s' % ( type(self.pick_zip), type(self.dest_zip)  )
                    if self.pick_zip != 6*' ' :   
                        pick_postcode = long ( self.pick_zip)
                    else:
                        pick_postcode = 0
                    if type(self.dest_zip) in [str, unicode]  and self.dest_zip != 6*' ':
                        try:
                            dest_postcode = long (self.dest_zip)
                        except Exception as e:                        
                            dest_postcode = 0                        
                    else:                   
                        dest_postcode = 0
                    postcode_format = ZIP_INT_FORMAT
                    self.sys_ftypes1 |= FareConstant.ZIPCODE_JOB
                else:
                    pick_postcode = 7*b'\x00'
                    dest_postcode = 7*b'\x00'
                    postcode_format = POSTAL_STRING_FORMAT
            
        except Exception as e:
            print ' fare_to_bin Exception postcode_or_zip %s ' % ( str(e) )
            pick_postcode = 7*b'\x00'
            dest_postcode = 7*b'\x00'           
            postcode_format = POSTAL_STRING_FORMAT    

        sys.stdout.write("%s: ispostal=%s fmt=%s self.sys_ftypes1=%x\n" % (datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT), self.postcode_or_zip, postcode_format, self.sys_ftypes1)  )      

        #TRIM 
        self.trim()

        try:          
            if type(self.custno) in  [str, unicode] :
                self.custno = self.custno.rstrip('\x00')
            custno = long(self.custno)
        except ValueError as e:
            sys.stdout.write("%s: fare_to_bin custno Exception  %s \n" % (datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT), str(e)))                       
            custno=0

        if self.routable == 'Y':
            self.flag |= FareConstant.ROUTABLE;

        if self.curb_dispatch == 'Y':
            self.flag |= FareConstant.CURB_DISPATCHING_ALLOWED
     
        if self.SMS_Enabled == 'Y' :
            self.Flag1 |=  FareConstant.SMS_ENABLED  
            
        # if no mobile phone
        if self.mobile_phone != 18*' ':
            self.xphones[3] = self.mobile_phone
        elif  self.phone == 19*' ':
            self.xphones[3] = self.acctno
        else:
            self.xphones[3] = self.phone

        try:
            if self.direction != ' ':
                mydic = zip( ('0', '1', '2', '3'), (FareConstant.NO_COMMENTS, FareConstants.COMMENTS_AVAILABLE, FareConstants.DIRECTION_AVAILABLE, FareConstant.COMMENTS_FROM_JOB))
                if self.direction in mydic.keys():
                    self.flag |= mydic[self.direction]
                if self.direction != '0':
                    self.xjobinfo = ''.join( [ i for i in self.directions],  b'\x00' )
        except Exception as e:
            sys.stdout.write("%s: Error while encoding direction %s \n" % (datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT), str(e)))               


        if self.charter_flag == 'Y':
            self.flag |= FareConstant.CHARTER_FLIGHT

        if self.display_attribute != '  ' :
            self.fdvt_sys_ftypes |= FareConstant.FARE_OFFER_ATTRIBUTE;

        if self.will_call == 'Y':
             self.reg_marks |= FareConstant.WILL_CALL 
             self.fdvt_sys_ftypes |= FareConstant.FUTURE

        #IN OUT flag = 1078
        if self.InOut == 'Y' and self.remarks1 != 32*' ':
            if scap.read_parameter(1078) > 0:
                self.Flag1 |= FareConstant.IN_OUT 

        if self.Taxihail == 'Y':
            self.Flag1 |= FareConstant.TAXIHAIL
        elif self.Taxihail in [ 'A', 'a']:
            self.Flag2 |= FareConstant.ARCUS_FARE
            try:
                self.que_priority = int(self.dispatch_priority)
            except ValueError:
                self.que_priority  =  0x0 # default
        elif self.Taxihail == 'R':
                self.Flag2 |= FareConstant.ARRO_FARE

        try:           
            try:
                if self.LocalCall == 'Y':
                    self.fdvt_sys_ftypes |= FareConstant.LOC_CALL       
                if self.Priority == 'Y':
                    self.fdvt_sys_ftypes |= FareConstant.PRIORITY_CALL
                if self.Restricted == 'Y':
                    self.fdvt_sys_ftypes |= FareConstant.RESTRICT_CODE
                if self.Bid == 'Y':
                    self.fdvt_sys_ftypes |= FareConstant.BID_CALL
            except Exception as e:  
                self.fdvt_sys_ftypes  = 0
                sys.stdout.write("%s: Error while encoding  fdvt_sys_ftypes  %s \n" \
                         % (datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT), str(e) ) )

            try:
                vehicle_number = 0
                if self.vehicle_number  != None and self.vehicle_number != 4*' ':
                    vehicle_number = int(self.vehicle_number )              
                if  vehicle_number > 0:
                    self.sys_ftypes1 |= FareConstant.ASSIGN_TAXI
            except ValueError as e:
                vehicle_number=0 
                sys.stdout.write("%s: Error while encoding vehicle_number %s \n" \
                         % (datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT), str(e))  )      

            try:    
                if self.CalloutNotAllowed == 'Y':
                    self.fdvt_usr_ftypes |= FareConstant.SKAD_DIS_CALLOUT
            except Exception as e:           
                sys.stdout.write("%s: Error while encoding  flag computations %s \n" \
                         % (datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT), str(e) ) )
                                             

            try:          
                my_flag_container = ord ( self.flag_container)
                if my_flag_container is not None:
                    if my_flag_container & SIGNATURE_ON > 0: 
                        self.Flag2 |= FareConstant.SIGNATURE_REQUIRED

                    if my_flag_container & FLAT_RATE_ON > 0:
                        self.Flag1 |=  FareConstant.FLAT_RATE_DISPATCH_TRIP  
     
            except Exception as e:           
                sys.stdout.write("%s: Error while encoding  flag computations *** %s type=%s Flag1=%d Flag2=%d \n" \
                         % (datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT), str(e), \
                            type(self.flag_container) ,
                            self.Flag1, self.Flag2))                  

        except Exception as e:           
            sys.stdout.write("%s: Error while encoding  flag computations %s type=%s Flag1=0x%x Flag2=0x%x fdvt_sys_ftypes=0x%x \n" \
                         % (datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT), str(e), \
                            type(self.flag_container) ,
                            self.Flag1, self.Flag2, self.fdvt_sys_ftypes ))                  

        try:
            passengers = long(self.num_of_passengers)
        except ValueError:
            passengers=0            

        try:
            driverid = long(self.driverid)
            if driverid > 0:
                self.sys_ftypes1 |= FareConstant.ASSIGN_DRIVERID
        except ValueError:
            driverid=0       

        try:
            pick_x = long(self. pick_x )
        except ValueError:
             pick_x =0    

        try:
            pick_y = long(self. pick_y )
        except ValueError:
             pick_y =0    
        
        try:
            pick_zone = int(self. pick_zone )
        except ValueError:
             pick_zone =0    
        

        try:
            dest_x = long(self. dest_x )
        except ValueError:
             dest_x =0    

        try:
            dest_y = long(self. dest_y )
        except ValueError:
             dest_y =0    
        
        try:
            dest_zone = int(self. dest_zone )
        except ValueError:
             dest_zone =0    


        try:
            #Could be a fare created to update parts of the fare only such as update destination
            print ('***FLEET NUMBER*** {0} type{1}'.format (self.fleet_number, type(self.fleet_number) ))
            if self.fleet_number != 4*' ' :
                fleet = int(self.fleet_number )
            else:
                fleet = 0
            if fleet > FareConstant.MAX_FLEET or fleet < 0:
                errmsg = ErrMsg.ERROR_MSG_INVALID_FLEET_NUMBER
                return None, 0, errmsg                    
        except ValueError as e:
            sys.stdout.write("%s: Error while encoding fleet Exception [%s] [%s]\n" % (datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT), str(e), self.fleet_number ))                             
            fleet =0  

        print ' fare_to_bin ==> fleet = ', fleet, ' <=='

        if self.account_type == 'T':
            self.fdvt_sys_ftypes |= FareConstant.PHONE_INFO_ACCNT
            #self.que_priority |= 0x80
    
        elif self.account_type  in [ 'C', 'A', ' ']:            
            self.que_priority  = 0x20
            self.fdvt_sys_ftypes |= FareConstant. ACCNT_FARE
            if self.account_type == 'T':
                self.fdvt_sys_ftypes |= FareConstant.AUTHORIZE_ACCNT
        else:
            self.fdvt_sys_ftypes |= FareConstant.ACCNT_FARE
            self.que_priority  = 0x20  

        startmask =1
        for i in range(FareConstant.NUM_DRIVER_TYPES):
            if self.driver_preference[i] == 'Y':
                self.fdvt_dtypes_32 |= (startmask << i)

        startmask =1
        for i in range(FareConstant.VCLASS_NUMRECS):
            if self.vehicle_preference[i] == 'Y':
                self.veh_class_32 |= (startmask << i)

        try:
            for i in range(8):
                if self.ei_Conf_Length[i] != ' ':
                    self.ei_conf_length [i] = int(self.ei_Conf_Length[i])
                else:
                    self.ei_conf_length [i] = 0
                self.ei_conf_prompt[i] = ''.join( [self.ei_Conf_Prompt[i][:12], b'\x00' ])
        except Exception as e:
            sys.stdout.write("%s: Error while encoding ei_Conf_Prompt %s\n" % (datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT), str(e)))    
      
 
        try:
            self.payment_order = int (self.IBSorderID)
        except ValueError:
            self.payment_order = 0            
                   
        try:                
            payment = self.payment_method[:2] + b'\x00' + self.sequence_number[:10] + b'\x00' + self.payment_data [14:]
            self.payment_data = payment
        except Exception as e:            
            sys.stdout.write("%s: Error while encoding data buffer in payment %s\n" % (datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT), str(e)))    
   
        try:
            if scap.is_fleet_separation_on() > 0 and scap.multi_fleet_zoning_on() > 0 :
                def_fleet =  scap.default_fleet() 
                if def_fleet >= 0:
                    self.fleet = def_fleet 

            lflat_rate_tag_in_fare_details = scap.flat_rate_tag_in_fare_details() 
            if lflat_rate_tag_in_fare_details > 0:
                self.Flag1 |= FareConstant.FLAT_RATE_DISPATCH_TRIP
        except Exception as e:
            sys.stdout.write("%s: Error while verifying scap parameters %s\n" % (datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT), str(e)))                

        try:
            self.orig_time = int (time.time()) #time.mktime(datetime.datetime.now().timetuple())
            reg_disp_time = self.orig_time
        except Exception as e:
            self.orig_time = 0
            sys.stdout.write("%s: Error while computing orig_time %s\n" % (datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT), str(e)))                

        try:
            if self.hailed_trip == 'Y' and  vehicle_number > 0:
                self.mtype = msgconf. MT_HAILED_TRIP
        except Exception as e:
            pass

        try:
            fare_num = int(self.fare_num )
        except Exception as e:
            fare_num = 0

        self.fdvt_sys_ftypes |= FareConstant.STANDARD_CALL
        self.sys_ftypes1 |= FareConstant.CABWEB_FARE



        #TEST ONLY ====      
        if self.is_future == True:
            self.fdvt_sys_ftypes |= FareConstant.FUTURE
            self.reginfo_uid = msgconf.CWEBS
            self.create_space_saver_struct()

        if self.is_future == False:
            self.reginfo_disp_time = 0
            self.reginfo_expire_time =0 
            self.reginfo_lead_time = 0
            self.reginfo_orig_time = 0
            self.reginfo_uid = 0
            self.create_space_saver_struct()
        
        if pzone is not None:
            pick_zone = pzone
        if seqno != None:
            self.sequence_number = seqno

        sys.stdout.write("%s: Sending ... pick_zone=%d, fleet=%d is_future=%d reginfo_disp_time =%d\n" % (datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT), pick_zone, fleet, self.is_future, self.reginfo_disp_time ))    

        d1 = (
        fare_num,
        0,                  #fstatus
        0,                  #dm_fstatus      
        custno,
        self.fare_amount_i, #original fare amount as it came in the dic                          
        driverid,         
        0,                  #self.vip_num,
        0,                  #self.reg_fare_num,                         
        reg_disp_time,
        0,                  #self.pass_on_brd,                           
        self.orig_time,                           
        self.sys_ftypes1,                      
        passengers,
        0,  #self.fstatus1,
        self.fare_amount_i,                          
        0,              #self.webId,                  
     
        # Pickup
        pick_x,
        pick_y,  
        pick_zone ,                # zone
        0,                          # map_page
        4* b'\x00',                      # map_ref
        pick_postcode,                             #self.pick_zip + b'\x00', # postal code   
        0,                                    #filler for zip code end char
        self.pick_street_no + b'\x00',        # num street 8
        self.pick_street_name + b'\x00',      # street name 34
        self.pcityname + b'\x00',             # city name  34
        self.pbuildingname + b'\x00',         # building name 34
        0,                                   # short junk
        self.pick_apartment+ b'\x00' ,     # apt
        self.pick_code + b'\x00',      # code 
        self.passengername + b'\x00',               
        b'\x00',                                    # data source
        b'\x00',                                    # building type
        b'\x00',                                   # pad
      
        # Destination  
        dest_x,
        dest_y,        
        dest_zone ,                # zone
        0,                          # map_page
        4 * b'\x00',                      # map_ref                 
        dest_postcode,               # postal code  
        0,                                     #filler for zip code end char
        self.dest_street_no + b'\x00',        # num street 8
        self.dest_street_name + b'\x00',      # street name 34
        self.dcityname + b'\x00',             # city name  34
        self.dbuildingname + b'\x00',         # building name 34
        0,                                   # short junk
        self.dest_apartment + b'\x00',     # apt
        self.dest_code + b'\x00',      # code 
        self.dest_passengername + b'\x00',          
        b'\x00',                                    # data source
        b'\x00',                                    # building type
        b'\x00',
     
        66 * b'\x00',                         #forminfo
        66 * b'\x00',
        self.phone[:19] + b'\x00',
        self.extra_info[:79] + b'\x00',         # special_data 80s
        b'\x00' ,                 # special_data 8H   [0 for i in range(8)]
        self.fdvt_sys_ftypes,
        self.fdvt_usr_ftypes,
        self.fdvt_dtypes_32,
        self.fdvt_vtypes,

        self.point_val,       
        self.rflt,
    
   
        #self.payment,
        self.payment_ct,
        self.payment_cp ,
        self.payment_dis ,
        self.payment_f3 ,
        self.payment_cn ,
        self.payment_att ,
        self.payment_pai ,
        self.payment_cr1 , 
        self.payment_cr2,         
        self.payment_exp , 
        self.payment_vid ,
        self.payment_order ,
        self.payment_tipper ,
        self.payment_to ,
        self.payment_meter ,
        self.payment_tipinc, 
        self.payment_tipamount ,
        self.payment_data,


        self.veh_class_32,
        self.code_9_event,

        #rgev : 16 bytes *** not used in cwebs ***
        self.rgev_pup_sequence,
        self.rgev_drop_sequence,
        self.rgev_run_fare_sequence_num,
        self.rgev_total_number_fares_in_run,
        self.rgev_manifest,
        self.rgev_run_number,
        self.rgev_fare,
        )

       
        d2=(
        self.xjobinfo,
        self.xjobinfo_filling,
        self.xforminfo,
        self.regtrack,
      
        self.que_priority,
        2,  # prior_incr_time
        0,  # amount_type
        0,  # authorization_num
        vehicle_number,  # fi_taxi
        fleet,  # fleet
        0,  # taxi_dest_zone
        0,  # going_home_code
        fleet,  # fare_fleet
        0,  # offer_taxi
        0,  # reserv_count
        0,  # reserv_manifest
        port_number,  # port_number
        self.operator_id, # msgconf.CWEBS,  # orig_id
        0,  # reg_lead_time
        self.reg_marks,
        0,  # reg_upd_time
        0,  # reg_sign
        self.flag,

        self.remarks1 + b'\x00',
        self.remarks2 + b'\x00',
        self.remarks3 + b'\x00',
        self.remarks4 + b'\x00',
       
        132 * b'\x00',

        
        self.acctno[:11] + b'\x00' ,        
        self.acctname[:19] + b'\x00',       
 
        0,                                  
        self.num_of_jobs,
        0,                                  

        self.driver_name[:23] + b'\x00', 
        self.Flag2,

        0,                          
        0,                          
        0,                          
        self.Flag1,
        self.landmark + b'\x00',    
        self.borough + b'\x00',     
        0, #self.cc_rec_num,
        self.ei_conf_length[0], self.ei_conf_length[0], self.ei_conf_length[2], self.ei_conf_length[3], 
        self.ei_conf_length[4], self.ei_conf_length[5], self.ei_conf_length[6], self.ei_conf_length[7],
        ''.join([i for i in self.ei_conf_prompt]),  
        ''.join([i for i in self.xphones]),  
        160 * b'\x00', 
   

        4 * b'\x00',          
        2 * b'\x00',          
        60 * b'\x00',         
        0,                    
        port_number, sspare, requester_ip, self.sequence_number, 0)
        
        
        data = (d1, self.ss_data, d2)
        data = sum(data, ())

        fmts = [
        '16I ' ,
        '2i h H 4s ', postcode_format , ' 8s 34s 34s 34s 1H 8s 8s 33s 3c',       
        '2i h H 4s ', postcode_format , ' 8s 34s 34s 34s 1H 8s 8s 33s 3c',       
        '66s 66s' ,  
        ' 20s'  ,  
        ' 80s 16s' ,  
        ' 4I ' ,  
        ' 4s ' ,  
        ' 22s ' ,  
        ' 3b B 20s 3s 8s 9s 20s I I I H H I I I 100s ' ,  
        ' I' , 
        ' 16s' , 
        ' 1B 1B H H H I I ' ,   
        self.ss_fmt,             
        '198s 1338s ',           
        '396s 16s' ,      

        ' 4h H 4h H 2h H h 2H I 2B 33s 33s 33s 33s 132s 12s 20s 3B 24s 5B 33s 3s 1I' ,
        '8b 104s', #         
        ' 120s' , 
        ' 160s' ,  
        ' 4s' ,   
        ' 2s' , 
        ' 60s ' , 
        ' H' ,  
        ' H H 64s 10s H' ,
        ]

        try:           
            if packit:
                import struct      
                f = ''.join(fmts)
                s = struct.Struct(f);
                print '*****fare_to_bin structure size ', s.size
                packed_data = s.pack(*data)
                return packed_data, s.size, errmsg
            else:
                return data, fmts, errmsg
        except Exception as e:
            sys.stdout.write("%s: Error in fare_to_bin structure  %s\n" % (datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT), str(e)))                

        return None, None, None

