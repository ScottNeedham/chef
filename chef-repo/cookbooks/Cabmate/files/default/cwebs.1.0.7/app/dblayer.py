import datetime
import sys
import config.cwebsconf as Config
import smalldb
import time
import re

def get_corporate_account_querystr(account_no="", customer_no=""):
    try:
        anum = str(account_no).strip()
        cnum = int(customer_no)
    except Exception as e:
        return ""
    sqlstring = ""  
    if anum != "":
        sqlstring  = '''select 
        a.AccountNumber as account_number, 
        a.CustomerNumber as customer_number, 
        a.AccountName as account_name, 
        a.VIPNumberString as vip_number, 
        a.PhoneAccount as phone_account, 
        a.CreationDate as creation_date, 
        a.Active as active, 
        a.ExtraInfo as extra_info,
        e.Caption1 as caption1, 
        e.DefaultValue1 as default_value1, 
        e.Length1 as length1, 
        e.PromptId1 as prompt_id1,  
        e.Required1 as required1, 
        e.Validation1 as validation1,
        v1.Name as name1,  
        e.Caption2 as caption2, 
        e.DefaultValue2 as default_value2, 
        e.Length2 as length2, 
        e.PromptId2 as prompt_id2,  
        e.Required2 as required2, 
        e.Validation2 as validation2,
        v2.Name as name2, 
        e.Caption3 as caption3, 
        e.DefaultValue3 as default_value3, 
        e.Length3  as length3, 
        e.PromptId3 as prompt_id3,  
        e.Required3 as required3, 
        e.Validation3 as validation3,
        v3.Name as name3, 
        e.Caption4 as caption4, 
        e.DefaultValue4 as default_value4, 
        e.Length4  as length4, 
        e.PromptId4 as prompt_id4,  
        e.Required4 as required4, 
        e.Validation4 as validation4,
        v4.Name as name4,  
        e.Caption5 as caption5, 
        e.DefaultValue5 as default_value5, 
        e.Length5  as length5, 
        e.PromptId5 as prompt_id5,  
        e.Required5 as required5, 
        e.Validation5 as validation5,
        v5.Name as name5, 
        e.Caption6 as caption6, 
        e.DefaultValue6 as default_value6, 
        e.Length6  as length6, 
        e.PromptId6 as prompt_id6,  
        e.Required6 as required6, 
        e.Validation6 as validation6,
        v6.Name as name6, 
        e.Caption7 as caption7, 
        e.DefaultValue7 as default_value7, 
        e.Length7  as length7, 
        e.PromptId7 as prompt_id7,  
        e.Required7 as required7, 
        e.Validation7 as validation7,
        v7.Name as name7, 
        e.Caption8 as caption8, 
        e.DefaultValue8 as default_value8, 
        e.Length8  as length8, 
        e.PromptId8 as prompt_id8,  
        e.Required8 as required8, 
        e.Validation8 as validation8, 
        v8.Name as name8
        from account a LEFT JOIN extrainfo e ON a.ExtraInfo = e.id 
        left join validation v1 on v1.id=e.Validation1
        left join validation v2 on v2.id=e.Validation2
        left join validation v3 on v3.id=e.Validation3
        left join validation v4 on v4.id=e.Validation4
        left join validation v5 on v5.id=e.Validation5
        left join validation v6 on v6.id=e.Validation6
        left join validation v7 on v7.id=e.Validation7
        left join validation v8 on v8.id=e.Validation8
        where a.PhoneAccount != 1 and a.AccountNumber = '%s' and a.CustomerNumber = %d limit 1;'''  % (anum, cnum)   
        #tmp = "select v.id, v.Name, vv.ValidID from validation v left join validid vv on vv.Name=v.Name"
    return sqlstring

def get_corporate_account_all_querystr():
    sqlstring  = '''select 
        a.AccountNumber as account_number, 
        a.CustomerNumber as customer_number, 
        a.AccountName as account_name, 
        a.VIPNumberString as vip_number, 
        a.PhoneAccount as phone_account, 
        a.CreationDate as creation_date, 
        a.Active as active, 
        a.ExtraInfo as extra_info,
    a.LastUpdate as last_update, 
        e.Caption1 as caption1, 
        e.DefaultValue1 as default_value1, 
        e.Length1 as length1, 
        e.PromptId1 as prompt_id1,  
        e.Required1 as required1, 
        e.Validation1 as validation1,
        v1.Name as name1,  
        e.Caption2 as caption2, 
        e.DefaultValue2 as default_value2, 
        e.Length2 as length2, 
        e.PromptId2 as prompt_id2,  
        e.Required2 as required2, 
        e.Validation2 as validation2,
        v2.Name as name2, 
        e.Caption3 as caption3, 
        e.DefaultValue3 as default_value3, 
        e.Length3  as length3, 
        e.PromptId3 as prompt_id3,  
        e.Required3 as required3, 
        e.Validation3 as validation3,
        v3.Name as name3, 
        e.Caption4 as caption4, 
        e.DefaultValue4 as default_value4, 
        e.Length4  as length4, 
        e.PromptId4 as prompt_id4,  
        e.Required4 as required4, 
        e.Validation4 as validation4,
        v4.Name as name4,  
        e.Caption5 as caption5, 
        e.DefaultValue5 as default_value5, 
        e.Length5  as length5, 
        e.PromptId5 as prompt_id5,  
        e.Required5 as required5, 
        e.Validation5 as validation5,
        v5.Name as name5, 
        e.Caption6 as caption6, 
        e.DefaultValue6 as default_value6, 
        e.Length6  as length6, 
        e.PromptId6 as prompt_id6,  
        e.Required6 as required6, 
        e.Validation6 as validation6,
        v6.Name as name6, 
        e.Caption7 as caption7, 
        e.DefaultValue7 as default_value7, 
        e.Length7  as length7, 
        e.PromptId7 as prompt_id7,  
        e.Required7 as required7, 
        e.Validation7 as validation7,
        v7.Name as name7, 
        e.Caption8 as caption8, 
        e.DefaultValue8 as default_value8, 
        e.Length8  as length8, 
        e.PromptId8 as prompt_id8,  
        e.Required8 as required8, 
        e.Validation8 as validation8, 
        v8.Name as name8
        from account a LEFT JOIN extrainfo e ON a.ExtraInfo = e.id 
        left join validation v1 on v1.id=e.Validation1
        left join validation v2 on v2.id=e.Validation2
        left join validation v3 on v3.id=e.Validation3
        left join validation v4 on v4.id=e.Validation4
        left join validation v5 on v5.id=e.Validation5
        left join validation v6 on v6.id=e.Validation6
        left join validation v7 on v7.id=e.Validation7
        left join validation v8 on v8.id=e.Validation8
        where a.PhoneAccount != 1 order by last_update DESC ;'''
    return sqlstring

def get_corporate_account_validation_querystr(account_no="", customer_no="", prompts = ["","","","","","","",""]):
    try:
        anum = str(account_no).strip()
        cnum = int(customer_no)
    except Exception as e:
        return ""
    sqlstring = ""
    if anum != "":
        sqlstring  = '''select
        if(vid1.id is null and e.validation1>0, 0,1) as IsGood1, v1.Name as Name1, 
            if(vid2.id is null and e.validation2>0, 0,1) as IsGood2, v2.Name as Name2, 
            if(vid3.id is null and e.validation3>0, 0,1) as IsGood3, v3.Name as Name3,
            if(vid4.id is null and e.validation4>0, 0,1) as IsGood4, v4.Name as Name4,
            if(vid5.id is null and e.validation5>0, 0,1) as IsGood5, v5.Name as Name5,
            if(vid6.id is null and e.validation6>0, 0,1) as IsGood6, v6.Name as Name6, 
            if(vid7.id is null and e.validation7>0, 0,1) as IsGood7, v7.Name as Name7, 
            if(vid8.id is null and e.validation8>0, 0,1) as IsGood8, v8.Name as Name8
        from account a 
        left join cabmate.extrainfo e on e.id=a.extrainfo
            left join cabmate.validation v1 on v1.id=e.Validation1
            left join cabmate.validid vid1 on vid1.name=v1.name  and vid1.validid='%s'
            left join cabmate.validation v2 on v2.id=e.Validation2
            left join cabmate.validid vid2 on vid2.name=v2.name  and vid2.validid='%s'
            left join cabmate.validation v3 on v3.id=e.Validation3
            left join cabmate.validid vid3 on vid3.name=v3.name  and vid3.validid='%s'
            left join cabmate.validation v4 on v4.id=e.Validation4
            left join cabmate.validid vid4 on vid4.name=v4.name  and vid4.validid='%s'
            left join cabmate.validation v5 on v5.id=e.Validation5
            left join cabmate.validid vid5 on vid5.name=v5.name  and vid5.validid='%s'
            left join cabmate.validation v6 on v6.id=e.Validation6
            left join cabmate.validid vid6 on vid6.name=v6.name  and vid6.validid='%s'
            left join cabmate.validation v7 on v7.id=e.Validation7
            left join cabmate.validid vid7 on vid7.name=v7.name  and vid7.validid='%s'
            left join cabmate.validation v8 on v8.id=e.Validation8 
        left join cabmate.validid vid8 on vid8.name=v8.name  and vid8.validid='%s' 
        where a.PhoneAccount != 1 and a.AccountNumber='%s' and a.CustomerNumber = %d limit 1;''' % (
            prompts[0], 
        prompts[1], 
        prompts[2], 
        prompts[3], 
        prompts[4], 
        prompts[5], 
        prompts[6], 
        prompts[7], 
        anum, 
        cnum)
    return sqlstring

def get_fare_number(data_src, fare_num):
    #determine if fare exists   
    lim_fare_exists = False              
    QueuePriority = 0
    sql_stat_im = '''
                  select IBSOrderId as order_id, 
                         Remark4 as remark4, 
                         SequenceNumber as seq_no, 
                         FareNumber as fare_number,
                         QueuePriority as QueuePriority from 
                         farefl 
              where FareNumber = %s limit 1
              ''' % (fare_num)
    lfu_fare_exists = False       
    sql_stat_fu = '''
                  select IBSOrderId as order_id, 
                         Remark4 as remark4,
                         SequenceNumber as seq_no, 
                         FareNumber as fare_number,
                         QueuePriority as QueuePriority from 
                         futfarefl 
          where FareNumber = %s limit 1
          ''' % (fare_num)
    print sql_stat_im
    info = data_src.fetch_many(sql_stat_im)
    for (order_id, remark4, seq_no, fare_number, QueuePriority) in info:
        lim_fare_exists = True
        sys.stdout.write("%s: dispatch modify_book_order imm fare %s exists\n" % (datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT), 
         fare_num))
        break
    print sql_stat_fu 
    print QueuePriority 
    info = data_src.fetch_many(sql_stat_fu)
    for (order_id, remark4, seq_no, fare_number, QueuePriority) in info:
        lfu_fare_exists = True
        sys.stdout.write("%s: dispatch modify_book_order fut fare %s exists\n" % (datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT), 
         fare_num))
        print QueuePriority 
        break  
    return (lim_fare_exists, lfu_fare_exists, QueuePriority)
    
def get_driver_info(data_src, driver_id):
    res_dic = {}
    sql_stat1 = '''SELECT
        d.DriverNumber AS driver_num,
        d.AccountsDisabled AS disable_corporate, 
        d.AllowViewCustPhone as allow_view_cust_phone,
        d.CurrentCombatPoints as current_combat_points, 
        d.CurrentVehicle AS cur_taxi, 
        d.DenyTempBookOff as deny_temp_book_off,
        d.DisCallout as discallout, 
        d.Driver as driver, 
        d.DriverDisabled as disable_driver, 
        d.EndOfShift as end_of_shift, 
        d.MerchantGroup as merchant_group, 
        d.NumberOfTempBookOff as number_of_temp_book_off, 
        d.PremiereDriver as premiere_driver,
        d.StartOfShift as start_of_shift, 
        d.Supervisor as supervisor, 
        d.TotalCombatPoints as total_combat_points,   
        d.UsesDriverSMS as fare_offer_via_sms,  
        d.WakeupDriver as wakeup_driver, 
        d.WakeupTime as wakeup_time, 
        d.DriverPIN as driver_pin, 
        p.Cityname as city, 
        p.Buildingname as building,
        p.DispatchZoneString as zone, 
        p.PostalCodeString as postal, 
        p.StreetName as street, 
        p.StreetNumber as num, 
        p.XPosition as addr_x, 
        p.YPosition as addr_y, 
        p.MobilePhoneNumber as mobile_phone, 
        p.Name as name,       
        p.PhoneNumber as phone, 
        p.PrimaryEmail as primary_email, 
        p.SecondaryEmail as secondary_email
        FROM driver AS d
        LEFT JOIN person AS p ON p.id = d.Driver
        WHERE d.DriverNumber = %s limit 1''' % (str(driver_id))
    info = data_src.fetch_many(sql_stat1)
    for (driver_num,
         disable_corporate,
         allow_view_cust_phone,
         current_combat_points,
         cur_taxi,
         deny_temp_book_off,
         discallout,
         driver,
         disable_driver,
         end_of_shift,
         merchant_group,
         number_of_temp_book_off,
         premiere_driver,
         start_of_shift,
         supervisor,
         total_combat_points,
         fare_offer_via_sms,
         wakeup_driver,
         wakeup_time,
         driver_pin,
         city,
         building,
         zone,
         postal,
         street,
         num,
         addr_x,
         addr_y,
         mobile_phone,
         name,
         phone,
         primary_email,
         secondary_email) in info:
         res_dic["DriverNum"] = driver_id
         try: 
             res_dic["primary_email"] = primary_email.strip() + '\0' if primary_email else '\0'
         except AttributeError:
             res_dic["primary_email"] = '\0' 
         try: 
             res_dic["secondary_email"] = secondary_email.strip() + '\0'  if secondary_email else '\0'
         except AttributeError:
             res_dic["primary_email"] = '\0'

         if phone:
             try:
                 res_dic["phone"] = re.sub("[^0-9]", "", str(phone)) + '\0'
             except AttributeError:
                 res_dic["phone"] = '\0'
         else: 
             res_dic["phone"] = '\0' 

         if mobile_phone:
             try:
                 res_dic["mobile_phone"] = re.sub("[^0-9]", "", str(mobile_phone)) + '\0' 
             except AttributeError:
                 res_dic["mobile_phone"] = '\0'
         else:
             res_dic["mobile_phone"] = '\0'
         
         try:
             res_dic["name"] = name.strip() + '\0' if name else '\0'     
         except AttributeError:
             res_dic["name"] = '\0' 
         
         try:
             res_dic["addr_x"] = int(addr_x) if addr_x else 0 
         except ValueError: 
             res_dic["addr_x"] = 0
         try:
             res_dic["addr_y"] = int(addr_y) if addr_y else 0
         except ValueError: 
             res_dic["addr_y"] = 0 
         try:
             res_dic["zone"] = int(zone) if zone else 0
         except ValueError:
             res_dic["zone"] = 0
         try:
             res_dic["postal"] = str(postal) + '\0' if postal else '\0'
         except ValueError:
             res_dic["postal"] = '\0' 
         try:
             res_dic["num"] = str(num) + '\0' if num else '\0'
         except ValueError:
             res_dic["num"] = '\0'
         try:
             res_dic["street"]  = str(street) + '\0' if street else '\0'
         except ValueError:
             res_dic["street"] = '\0'
         try:
             res_dic["city"] = str(city) + '\0' if city else '\0'
         except ValueError:
             res_dic["city"] = '\0'
         try:
             res_dic["building"] = str(building) + '\0' if building else '\0'
         except ValueError:
             res_dic["building"] = '\0'
         res_dic["disable_driver"] = "Y" if disable_driver == 1 else 'N' 
         
         if start_of_shift:
             lparse = True 
             try:
                 t1 = time.strptime(start_of_shift, '%H:%M:%S')
                 res_dic["start_time"] = t1.tm_hour*3600 + t1.tm_min*60 + tm_sec
             except Exception as e: 
                 lparse = False
             if not lparse:
                 try:
                     t1 = time.strptime(start_of_shift, '%H:%M')
                     res_dic["start_time"] = t1.tm_hour*3600 + t1.tm_min*60
                 except Exception as e:
                     res_dic["start_time"] = 90000
         else:
             res_dic["start_time"] = 90000

         if end_of_shift:
             lparse = True
             try:
                 t1 = time.strptime(end_of_shift, '%H:%M:%S')
                 res_dic["end_time"] = t1.tm_hour*3600 + t1.tm_min*60 + tm_sec
             except Exception as e:
                 lparse = False
             if not lparse:
                 try:
                     t1 = time.strptime(end_of_shift, '%H:%M')
                     res_dic["end_time"] = t1.tm_hour*3600 + t1.tm_min*60
                 except Exception as e:
                     res_dic["end_time"] = 90000
         else:
             #cabwin port
             res_dic["end_time"] = 90000

         res_dic["acct_disabled"] = 'Y' if disable_corporate == 1 else 'N'
         try:
             res_dic["current_combat_points"] = int(current_combat_points) if current_combat_points else 0
         except ValueError:
             res_dic["current_combat_points"] = 0  
         try:
             res_dic["cur_taxi"] = cur_taxi if cur_taxi else 0
         except ValueError:
             res_dic["cur_taxi"] = 0
         res_dic["supervisor"] = 'Y' if supervisor == 1 else 'N'       
         res_dic["discallout"] = 'Y' if discallout == 1 else 'N'
         res_dic["deny_temp_book_off"] = 'Y' if deny_temp_book_off == 1 else 'N'
         res_dic["premiere_driver"] = 'Y' if premiere_driver == 1 else 'N'
         try:
             res_dic["total_combat_points"] = int(total_combat_points) if total_combat_points else 0
         except ValueError:
             res_dic["total_combat_points"] = 0
         res_dic["driver_group"] = merchant_group if (merchant_group and merchant_group != "") else ' ' 
         res_dic["MDT_Display"] = 'Y' if allow_view_cust_phone == 1 else 'N'
         res_dic["fare_offer_via_sms"] = 'Y' if fare_offer_via_sms == 1 else 'N'
         if driver_pin: 
            try:
                res_dic["driver_pin"] = int(driver_pin)
                res_dic["shift_id"] = int(driver_pin) 
            except ValueError: 
                res_dic["driver_pin"] = 0
                res_dic["shift_id"] = 0
         else: 
             res_dic["driver_pin"] = 0 
             res_dic["shift_id"] = 0
         res_dic["wakeup_driver"] = 'Y' if wakeup_driver == 1 else 'N'
         res_dic["number_of_temp_book_off"] = number_of_temp_book_off if number_of_temp_book_off else 0 

    sql_stat2 = '''SELECT
        id,
        DriverNumber as driver_num,  
        type 
        FROM drv_dtypes 
        WHERE DriverNumber = %s''' % (str(driver_id))
    info = data_src.fetch_many(sql_stat2)
    res_dic["user_driver_types"] = []
    for (id, driver_num, type) in info:
        try:
            dtype = int(type)
            if dtype in range(32):
                if dtype not in res_dic["user_driver_types"]:
                    res_dic["user_driver_types"].append(dtype)
        except ValueError:
            pass
    #########################################
    sql_stat3 = '''SELECT 
        id, 
        DriverNum as driver_num, 
        fleet
        FROM drvallowedfleets where DriverNum =  %s''' % (str(driver_id))    
    info = data_src.fetch_many(sql_stat3)
    res_dic["valid_fleets"] = []
    for(id, driver_num, fleet) in info:
        try:
            vfleet = int(fleet) 
            if vfleet > 0: 
                res_dic["valid_fleets"].append(vfleet)
        except ValueError:
            pass

    sql_stat4 = '''SELECT 
        id, 
        fleet, 
        account, 
        custnum, 
        name, 
        driver, 
        vehicle
        FROM disableaccounts where driver = %s''' % (str(driver_id))
    info = data_src.fetch_many(sql_stat4)
    res_dic["disabled_accounts"] = []
    for(id, fleet, account, custnum, name, driver, vehicle) in info:
        try:
            icust = int(custnum)
            if account:
                if account.strip() != "":
                    res_dic["disabled_accounts"].append(account + '\0') 
                    res_dic["disabled_accounts"].append(icust)
        except ValueError:
            pass
    
    sql_stat5 = '''SELECT
        id, 
        DriverNum, 
        vehicle
        FROM drvallowedvehs 
        where DriverNum = %s''' % (str(driver_id))    
    info = data_src.fetch_many(sql_stat5)
    res_dic["taxis"] = []
    for(id, DriverNum, vehicle) in info:
        try: 
            taxi = int(vehicle)
        except ValueError:
            continue 
        if len(res_dic["taxis"]) < 10:
            if not taxi in res_dic["taxis"]:
                res_dic["taxis"].append(taxi)      

    sql_stat6 = '''select z.id, 
                          z.driver, 
                          z.fromzone, 
                          z.tozone, 
                          df.ZoneNumber as zone_from, 
                          dt.ZoneNumber as zone_to 
                          from zonerange z 
                          left join dispatchzone df on z.fromzone = df.id 
                          left join dispatchzone dt on z.tozone = dt.id
                          where driver = %s;''' % (str(driver_id))
    info = data_src.fetch_many(sql_stat6)
    res_dic["from_zone"] = []
    res_dic["to_zone"] = [] 
    for(id, driver, fromzone, tozone, zone_from, zone_to) in info:
        if len(res_dic["from_zone"]) < 32:
            try:
                res_dic["from_zone"].append(int(zone_from))
            except ValueError:
                pass
        if len(res_dic["to_zone"]) < 32:
            try:
                res_dic["to_zone"].append(int(zone_to))
            except ValueError:
                pass          
    #print 'res_dic ', res_dic
    return res_dic

def get_vehicle_info(data_src, vehicle_id):
    res_dic = {"vehicle_number": -1}
    sql_stat1 = '''SELECT
        v.VehicleNumber as vehicle_number,
        v.Alias as alias,
        v.BaseUnit as base_unit, 
        v.Colour as colour,
        v.Financier as financier,
        v.Fleet as fleet,   
        v.InsuranceExpiryDate as insurance_expiry_date,
        v.InsuranceIssueDate as insurance_issue_date, 
        v.Insurer as insurer, 
        v.LicenseExpiryDate as license_expiry_date,  
        v.LicenseIssueDate as license_issue_date,
        v.LicensePlate as license_plate,
        v.LicenseType as license_type, 
        v.LicensingCity as licensing_city, 
        v.MaintenanceMileage as maintenance_mileage, 
        v.Manufacturer as manufacturer,
        v.MaximumPassengers as maximum_passengers, 
        v.Mileage as mileage, 
        v.Model as model,  
        v.Owner as owner, 
        v.RegistrationNumber as registration_number,
        v.Remarks1 as remarks1, 
        v.Remarks2 as remarks2,  
        v.Remarks3 as remarks3,  
        v.Remarks4 as remarks4,   
        v.Sale as sale,     
        v.SerialNumber as serial_number, 
        v.ServiceDate as service_date,  
        v.LongAlias as long_alias,  
        v.TaxExpiryDate as tax_expiry_date, 
        v.TerminalRevision as terminal_revision, 
        v.TerminalType as terminal_type, 
        v.TrainingTerminal as training_terminal, 
        v.VDMMDTControls as VDMMDTControls,  
        v.VDMMDTEnabled as VDMMDTEnabled,   
        v.VehicleDisabled as vehicle_disabled,  
        v.TaxID as tax_id, 
        v.Deactivated as deactivated, 
        v.InsurancePolicyNo as insurance_policy_no, 
        v.medalianowner as medalian_owner, 
        v.medalianmanager as medalian_manager, 
        p.PhoneNumber as phone_number, 
        p.MobilePhoneNumber as mobile_phone, 
        f.Fleetname as fleet_name  
        from vehicle v 
        LEFT JOIN person AS p ON p.id = v.owner
        LEFT JOIN fleet  AS f on f.Fleetnumber = v.fleet
        WHERE v.VehicleNumber = %s limit 1;''' % (str(vehicle_id))
    info = data_src.fetch_many(sql_stat1)
    for (vehicle_number,
        alias,
        base_unit,
        colour,
        financier,
        fleet,
        insurance_expiry_date,
        insurance_issue_date,
        insurer,
        license_expiry_date,
        license_issue_date,
        license_plate,
        license_type,
        licensing_city,
        maintenance_mileage,
        manufacturer,
        maximum_passengers,
        mileage,
        model,
        owner,
        registration_number,
        remarks1,
        remarks2,
        remarks3,
        remarks4,
        sale,
        serial_number,
        service_date,
        long_alias,
        tax_expiry_date,
        terminal_revision,
        terminal_type,
        training_terminal,
        VDMMDTControls,
        VDMMDTEnabled,
        vehicle_disabled,
        tax_id,
        deactivated,
        insurance_policy_no,
        medalian_owner,
        medalian_manager,
        phone_number,
        mobile_phone,
        fleet_name) in info:
        
        try:
            res_dic["vehicle_number"] = int(vehicle_number) if int(vehicle_number) > 0 else -1
        except Exception as e:
            res_dic["vehicle_number"] = -1   
  
        if res_dic["vehicle_number"]  == -1:
            return res_dic        
        res_dic["alias"] = alias +'\0' if alias else "\0"
        res_dic["long_alias"] = long_alias + '\0' if long_alias else "\0"
        try:
            res_dic["training"] = int(training_terminal)
        except Exception as e:
            res_dic["training"] = 0
        try:
            res_dic["maximum_passengers"] = int(maximum_passengers) if maximum_passengers else 0
        except Exception as e:
            res_dic["maximum_passengers"] = 0

        if phone_number:
            try:
                res_dic["phone"] = re.sub("[^0-9]", "", str(phone_number)) + '\0'
            except Exception as e:
                res_dic["phone"] = '\0'
        else:
            res_dic["phone"] = '\0'

        if mobile_phone:
            try:
                res_dic["mobile_phone"] = re.sub("[^0-9]", "", str(mobile_phone)) + '\0'
            except Exception as e:
                res_dic["mobile_phone"] = '\0'
        else:
            res_dic["mobile_phone"] = '\0'
        
        res_dic["fleet_name"] = fleet_name + '\0'  if fleet_name else "\0"
        try:
            res_dic["fleet"] = int(fleet) if int(fleet) > 0 else 0
        except Exception as e:
            res_dic["fleet"] = 0
        res_dic["vehicle_type"] = 0
        res_dic["sys_ftypes"] = 0 
        res_dic["usr_ftypes"] = 0
        res_dic["dtypes"] = 0
        res_dic["vtypes"] = 0
        try:    
             res_dic["baseunit"] = int(base_unit) if base_unit else 0
        except Exception as e:
             res_dic["baseunit"] = 0
        res_dic["voice"] = 'N'
        res_dic["sale"] = 'N'
        try:
            res_dic["sale"] = 'Y' if int(sale) == 1 else 'N'
        except Exception as e:
            res_dic["sale"] = 'N'
         
        try:
            res_dic["VDM_MDTControlEnabled"] = 'Y' if int(VDMMDTEnabled) == 1 else 'N'
        except Exception as e:
            res_dic["VDM_MDTControlEnabled"] = 'N'
        
        res_dic["VDM_MDTControl"] = 0
        try:  
            res_dic["VDM_MDTControl"] = int(VDMMDTControls) if VDMMDTControls else 0
        except Exception as e:
            pass 
 
        res_dic["RearSeatVivotechEnabled"] = 'N'
        try:
            dt = datetime.datetime.strptime(license_expiry_date, '%Y-%m-%d')
            res_dic["license_expiry_date"] = int(time.mktime(dt.timetuple()) )
        except Exception as e: 
            res_dic["license_expiry_date"] = 0
            #dt = datetime.datetime.strptime('2020-01-01', '%Y-%m-%d')
        
        
    sql_stat2 = '''SELECT 
        VehicleNumber, 
        broadcast, 
        manifest, 
        DefaultDriver 
        from veh_termcfg 
        where VehicleNumber = %s''' % (str(vehicle_id))
     
    res_dic["cur_driver"] = 0
    sql_stat3 = '''SELECT 
        id, 
        VehicleNumber, 
        Channel 
        from vehdisallowedchan
        where VehicleNumber = %s''' % (str(vehicle_id))
    
    
    res_dic["disallowedchannels"] = []       
    info = data_src.fetch_many(sql_stat3)
    for (id, VehicleNumber, Channel) in info:
        try:
            if int(Channel) in range(16):
                if int(Channel) not in res_dic["disallowedchannels"]: 
                    res_dic["disallowedchannels"].append(Channel)
        except Exception as e:
            pass
  
    sql_stat4 = '''SELECT 
        id,  
        VehicleNumber as vehicle_id, 
        Type as type
        from veh_vtypes where VehicleNumber = %s''' % (str(vehicle_id))
    info = data_src.fetch_many(sql_stat4)
    res_dic["veh_class_32"] = []
    for (id, vehicle_id, type) in info:
        try:
            vtype = int(type)
            if vtype in range(32):
                if vtype not in res_dic["veh_class_32"]:
                    res_dic["veh_class_32"].append(vtype)
        except Exception as e:
            pass

    sql_stat5 = '''SELECT 
        id, 
        DriverNum, 
        vehicle 
        from drvallowedvehs 
        where vehicle = %s''' % (str(vehicle_id))
    info = data_src.fetch_many(sql_stat5)
    res_dic["drivers"] = []
    for(id, DriverNum, vehicle) in info:
        try:
            driver_num = int(DriverNum)
        except Exception as e:
            continue
        if len(res_dic["drivers"]) < 10:
            if not driver_num in res_dic["drivers"]:
                res_dic["drivers"].append(driver_num)


    sql_stat6 = '''SELECT
        z.id,
        z.driver,
        z.fromzone,
        z.tozone,
        df.ZoneNumber as zone_from,
        dt.ZoneNumber as zone_to
        from zonerange z
        left join dispatchzone df on z.fromzone = df.id
        left join dispatchzone dt on z.tozone = dt.id
        where vehicle = %s;''' % (str(vehicle_id))
    info = data_src.fetch_many(sql_stat6)
    res_dic["from_zone"] = []
    res_dic["to_zone"] = []
    for(id, driver, fromzone, tozone, zone_from, zone_to) in info:
        print id, driver, fromzone, tozone, zone_from, zone_to
        if len(res_dic["from_zone"]) < 32:
            try:
                res_dic["from_zone"].append(int(zone_from))
            except Exception as e:
                pass
        if len(res_dic["to_zone"]) < 32:
            try:
                res_dic["to_zone"].append(int(zone_to))
            except Exception as e:
                pass

    sql_stat7 = '''SELECT 
        id as id, 
        VehicleNumber as vehicle_number, 
        fleet as fleet 
        from vehaltfleets 
        where VehicleNumber = %s;''' % (str(vehicle_id))
    info = data_src.fetch_many(sql_stat7)
    res_dic["alternate_fleet"] = []
    for(id, vehicle_number, fleet) in info:
        if len(res_dic["alternate_fleet"]) < 10:
            try:
                if not int(fleet) in res_dic["alternate_fleet"]:
                    res_dic["alternate_fleet"].append(int(fleet))
            except Exception as e:
                pass
    res_dic["duplicate_alias_vehicle_id"] = -1
    if "fleet" in res_dic and res_dic["fleet"] > 0 and res_dic["alias"].strip("\0").strip() != "":
        sql_stat8 = '''SELECT
            VehicleNumber as vehicle_number,
            fleet as fleet,
            Alias as alias
            from vehicle
            where fleet = %s and alias = '%s' and VehicleNumber != %s
            limit 1;''' % (str(res_dic["fleet"]), res_dic["alias"].strip("\0").strip(), str(vehicle_id))
        print sql_stat8
        info = data_src.fetch_many(sql_stat8)
        for(vehicle_number, fleet, alias) in info:
            res_dic["duplicate_alias_vehicle_id"] = vehicle_number
    print "duplicate_alias_vehicle_id", res_dic["duplicate_alias_vehicle_id"]

    res_dic["duplicate_long_alias_vehicle_id"] = -1
    if "fleet" in res_dic  and res_dic["fleet"] > 0 and res_dic["long_alias"].strip("\0").strip() != "":
        sql_stat9 = '''SELECT
            VehicleNumber as vehicle_number,
            fleet as fleet,
            LongAlias as long_alias
            from vehicle
            where fleet = %s and LongAlias = '%s' and VehicleNumber != %s
            limit 1;''' % (str(res_dic["fleet"]), res_dic["long_alias"].strip("\0").strip(), str(vehicle_id))
        print sql_stat9
        info = data_src.fetch_many(sql_stat9)
        for(vehicle_number, fleet, long_alias) in info:
            res_dic["duplicate_long_alias_vehicle_id"] = vehicle_number
    
    return res_dic

def get_vehicle_by_long_alias(data_src, device_name, medallion, fleet):
    res_dic = {"vehicle_number": -1, "long_alias": "", "alias": "",  "count": 0, "fleet": fleet}
    print 'entering get_vehicle_by_long_alias'
    sql_stat1 = '''SELECT VehicleNumber as vehicle_number, 
        Fleet as fleet, 
        Alias as alias, 
        LongAlias as long_alias 
        from vehicle 
        where (LongAlias = '%s' and fleet = %s);''' % (device_name, fleet)
    print sql_stat1
    print 'executing...' 
    info = data_src.fetch_many(sql_stat1)
    count = 0
    for (vehicle_number, fleet, alias, long_alias) in info:
        count = count + 1
        res_dic["vehicle_number"] = vehicle_number
        res_dic["fleet"] = fleet
        res_dic["long_alias"] = long_alias
        res_dic["alias"] = alias
        res_dic["count"] = count 
    return res_dic

def get_vehicle_by_long_alias2(data_src, device_name, medallion):
    res_dic = {"vehicle_number": -1, "long_alias": "", "alias": "",  "count": 0, "fleet": 0}
    #print 'entering get_vehicle_by_long_alias2'
    sql_stat1 = '''SELECT VehicleNumber as vehicle_number,
        Fleet as fleet,
        Alias as alias,
        LongAlias as long_alias
        from vehicle
        where LongAlias = '%s';''' % (device_name)
    #print sql_stat1
    #print 'executing...'
    info = data_src.fetch_many(sql_stat1)
    count = 0
    for (vehicle_number, fleet, alias, long_alias) in info:
        count = count + 1
        res_dic["vehicle_number"] = vehicle_number
        res_dic["fleet"] = fleet
        res_dic["long_alias"] = long_alias
        res_dic["alias"] = alias
        res_dic["count"] = count
    return res_dic

def get_vehicle_by_ch(data_src, ch):
    res = []
    print 'entering get_vehicle_by_ch'
    sql_stat1 = '''select VehicleNumber as vehicle_number from cabmate.vehicle 
       where VehicleNumber not in 
       (select VehicleNumber from cabmate.vehdisallowedchan where Channel = %s 
        group by VehicleNumber) order by VehicleNumber desc limit 800;''' % (ch)
    print sql_stat1
    print 'executing...'
    info = data_src.fetch_many(sql_stat1)
    count = 0
    for (vehicle_number, ) in info:
        count = count + 1
        res.append(str(vehicle_number))
    return res

def get_max_vehicle(data_src): 
    max_vehicle_number = -1
    sql_stat2 = '''SELECT max(VehicleNumber) as max_vehicle from vehicle;'''
    info = data_src.fetch_many(sql_stat2)
    for (max_vehicle, ) in info:
        max_vehicle_number = max_vehicle
    return max_vehicle_number 



def createLogEntry(dic):
    
    sys.stdout.write("%s: entering %s\n" % (datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT), __name__))
   
    try:
        db = smalldb.DB(Config.DB_HOST, Config.DB_USER, Config.DB_PASSWORD, 'Logs')
        db.connect()
        sql_stat = '''
            INSERT INTO messages
            (
                fromuser,
                date,
                fleet,
                vehicle,
                message
            )
            VALUES (
            \'%u\',
            \'%u\',
            \'%u\',
            \'%u\',
            \'%s\'
            );
            ''' % ( 
                dic["operator_id"] ,
                dic["time"] , 
                dic["fleet"],                 
                dic["vehicle"] ,
                dic["mesg"]
            )

        sys.stdout.write("%s: %s Execution ... %s\n" % (datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT), __name__, sql_stat))

        info = db.insert_update(sql_stat)
    
    except Exception as e:
        sys.stdout.write("%s: createLogEntry exception %s \n" % (datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT), e ))
        
        pass

    db.close()
    



if __name__ == "__main__":
    print 'dblayer main'
    #data_src = smalldb.DB(Config.DB_HOST, Config.DB_USER, Config.DB_PASSWORD, Config.DB_NAME)
    #data_src.connect()

    #db = smalldb.DB('10.2.4.61', 'taxi', 'taxi', 'cabmate')
    db = smalldb.DB('127.0.0.1', 'taxi', 'taxi', 'cabmate')
    db.connect()
    res = get_driver_info(db, 8089)
    #res = get_vehicle_info(db, 9007)
    print res 
    #get_max = get_max_vehicle(db)
    #print 'max vehicle ', get_max 
    #res = get_vehicle_by_ch(db, 3)
    #print ",".join(res)
    #sql_stat1 = "insert into vehdisallowedchan(VehicleNumber, Channel) values"
    #for i in res:
    #    sql_stat1 = sql_stat1 + " (%s,%s)," % (i, "3")
    #print sql_stat1
    db.close() 

    data_src= smalldb.DB('127.0.0.1', 'taxi', 'taxi', "CabmateRepo")
    data_src.connect()
    fare_num="201606090006497"
    a, b, q = get_fare_number(data_src, fare_num)
    print ' Got %d %d %d ' % (  a, b, q )

    data_src.close()

   
