# coding=utf-8
from gevent import monkey; monkey.patch_all()
import gevent
import datetime
from bottle import Bottle, request, response
import json
import sys
import time
import zqqwrap
import smalldb
import socketcli

import config.cwebsconf as Config

import format_field
import dblayer
import validpr

import msgconf
import cabmsg
import struct

import scap
import errormsg as ErrorMsg

import server_utils as Utils
import supervisor_message as SupervisorMsg


import api_funcs as api_funcs
import scap_funcs

import fares.fare_funcs as fare_funcs
import fares.fare_tfc as fare_tfc
import fares.fare_modify_tfc as fare_modify_tfc
import fares.fare_cancel_tfc as fare_cancel_tfc
import fares.fare_funcs_cabmsg as fare_funcs_cabmsg
from zones.zone_cache import zone_cache
import actions.supervisor_funcs as supervisor_funcs
import fares.fare_redispatch as fare_redispatch
from base.url_rule import UrlRule

import params.sys_funcs

#@app.get('/dispatcher/qtotals/')
def dispatch_qtotals():
    try:

        response = Utils.prepare_header('dispatch_qtotals', "default")
        if response.status == 401:
            return

        if Config.l303Site:
            channel_id_by_fleet_id = {1: 1, 2: 2, 7: 3, 26: 4, 16: 5, 17: 6, 4: 7, 18: 8, 25: 9}
            zone_totals = zqqwrap.get_fleet_zone_totals_303(channel_id_by_fleet_id)
        else:
            print 'getting fleet info...'
            fleet_id_by_channel_id, channel_id_by_fleet_id, zone_number_by_channel_id = zqqwrap.get_fleet_info()
            print 'fleet info is read in...'
            zone_totals = zqqwrap.get_fleet_zone_totals(channel_id_by_fleet_id)
            response.status = 200  
            Utils.set_default_headers(response)
            return zone_totals
    except Exception as e:
        sys.stdout.write("%s: dispatch_qtotals: Exception %s\n" % ( 
            datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT), (str(e) ) ) )
        response.status = 500
        res = {"status": response.status, "result": {"message": ErrorMsg.ERROR_MSG_GENERAL_ERROR}}
        return json.dumps(res)        

#@app.get('/dispatcher/zonestatus/<fleet_id>')
def dispatch_zonestatus(fleet_id):
    try:
        response =  Utils.prepare_header('dispatch_zonestatus', "default")
        if  response.status == 401:
            return
        else:
            print 'dispatch_zonestatus: HMAC is verified...'
            zone_status = {}
            try: 
                fleet_number = int(fleet_id)
            except Exception as e:
                print 'Exception ', str(e)
                response.status = 500
                return zone_status

        lFleetSeparation = scap.is_fleet_separation_on()
        
        if lFleetSeparation: 
            if Config.l303Site: 
                channel_id_by_fleet_id = {1: 1, 2: 2, 7: 3, 26: 4, 16: 5, 17: 6, 4: 7, 18: 8, 25: 9}
                zone_status = zqqwrap.get_fleet_zone_status_by_fleet_id_303(int(fleet_id), channel_id_by_fleet_id)
            else: 
            #fleet_id_by_channel_id, channel_id_by_fleet_id, zone_number_by_channel_id = zqqwrap.get_fleet_info()
            #zone_status = zqqwrap.get_fleet_zone_status_by_fleet_id(int(fleet_id), channel_id_by_fleet_id, zone_number_by_channel_id)
                zone_status = zqqwrap.get_fzstatus(fleet_number)
        else: 
            sql_statement = 'select Fleetnumber, Fleetname, MdtGroup, ZoneSet from fleet;'
            # max fleet number     
            if fleet_number >= 0 and fleet_number <= 100:
                zone_status = Utils.get_zstatus()
            #info = data_src.fetch_many(sql_statement)
            #for (Fleetnumber, Fleetname, MdtGroup, ZoneSet) in info:
            #    fleet_to_zoneset[Fleetnumber] = ZoneSet
 
        response.status = 200   
        Utils.set_default_headers(response)       
        return zone_status  
    except Exception as e:
        sys.stdout.write("%s: dispatch_zonestatus : Exception %s\n" % ( 
            datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT), (str(e) ) ) )             
        response.status = 500
        res = {"status": response.status, "result": {"message": ErrorMsg.ERROR_MSG_GENERAL_ERROR}}
        return json.dumps(res)                
    

#@app.get('/dispatcher/zonesetzones/')
def dispatch_zonesetszones():
    res = {}
    try:
 
        response =  Utils.prepare_header('dispatch_zonesetszones', "default")
        if  response.status == 401:
            return

        if Config.l303Site: 
            sql_statement = 'select Fleetnumber, Fleetname, MdtGroup, ZoneSet from fleet where OffDutyHome = 1;'
        else: 
            sql_statement = 'select Fleetnumber, Fleetname, MdtGroup, ZoneSet from fleet;'
        info = data_src.fetch_many(sql_statement)
        fleet_to_zoneset = {}
        for (Fleetnumber, Fleetname, MdtGroup, ZoneSet) in info:
            fleet_to_zoneset[Fleetnumber] = ZoneSet 
        res = zqqwrap.get_all_zones(fleet_to_zoneset)
        response.status = 200  
        Utils.set_default_headers(response)
        return res  
    except Exception as e:       
        sys.stdout.write("%s: dispatch_zonesetszones : Exception %s\n" % ( 
            datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT), (str(e) ) ) )          
        response.status = 500
        res = {"status": response.status, "result": {"message": ErrorMsg.ERROR_MSG_GENERAL_ERROR}}
        return json.dumps(res)                        
        

#@app.get('/dispatcher/zonevehicles/')
def dispatch_zonevehicles():
    try:
        print __name__
        print 'dispatch_zonevehicles environment: ', request.environ

        response =  Utils.prepare_header('dispatch_zonevehicles', "default")
        if  response.status == 401:
            return

        print 'dispatch_zonevehicles: HMAC is verified...'
        zone_vehicles = zqqwrap.get_vehicles_in_the_zone(Config.fleet_qfolder)
        response.status = 200
        Utils.set_default_headers(response)
        return zone_vehicles
    except Exception as e:
        sys.stdout.write("%s: dispatch_zonevehicles : Exception %s\n" % ( 
            datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT), (str(e) ) ) )            
        response.status = 500
        res = {"status": response.status, "result": {"message": ErrorMsg.ERROR_MSG_GENERAL_ERROR}}
        return json.dumps(res)                
'''
mysql> select rr.Remark4, rr.SequenceNumber, rr.FareNumber, E1.evNumber from (select Remark4, SequenceNumber, FareNumber, LastSQLUpdate from CabmateRepo.farefl  where MOD(FareNumber,1000000)=949 order by LastSQLUpdate DESC limit 1000) rr join CabmateRepo.fareflevents E1 on rr.FareNumber=E1.fareNumber join CabmateRepo.fareflevents E2 on E1.fareNumber=E2.fareNumber where E1.evNumber=0 and E2.evNumber not in (0,8);
Empty set (0.77 sec)
'''

    
#@app.get('/account/corporate/<account_no>/<customer_no>')
def get_corporate_account(account_no="", customer_no=""):
    try:
        sys.stdout.write("%s: entering %s\n" % (datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT), __name__))
        sys.stdout.write("%s: get_corporate_account %s\n" % (
            datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT),
            str(request.environ) ))

        response =  Utils.prepare_header('get_corporate_account', "account")
        if  response.status == 401:
            return            

        Utils.set_default_headers(response)
        response.status = 500
        res = {'status': response.status,
               'result': {
                       'message': 'failure',
                       'number_of_accounts': 0, 
               'account_number': account_no, 
               'customer_number': customer_no}
              }
        qstr = dblayer.get_corporate_account_querystr(account_no, customer_no)
        if qstr != "":
            info = data_src.fetch_many(qstr)
            count = 0
            account_info = {}
            for (account_number, customer_number, account_name, vip_number, phone_account, creation_date, active, extra_info,
                caption1, default_value1, length1, prompt_id1,  required1, validation1, name1, 
                caption2, default_value2, length2, prompt_id2,  required2, validation2, name2, 
                caption3, default_value3, length3, prompt_id3,  required3, validation3, name3, 
                caption4, default_value4, length4, prompt_id4,  required4, validation4, name4, 
                caption5, default_value5, length5, prompt_id5,  required5, validation5, name5, 
                caption6, default_value6, length6, prompt_id6,  required6, validation6, name6, 
                caption7, default_value7, length7, prompt_id7,  required7, validation7, name7, 
                caption8, default_value8, length8, prompt_id8,  required8, validation8, name8) in info:
                count = count + 1
                account_info["account_number"] = account_number
                account_info["customer_number"] = customer_number
                if active == 1:
                    account_info["active"] = True
                else:
                    account_info["active"] = False
                if extra_info > 0:
                    account_info["validate"] = True
                    account_info["prompts"] = []
                    for acap, req, l, n, prompt_number in zip(
                        [caption1, caption2, caption3, caption4, caption5, caption6, caption7, caption8],
                        [required1, required2, required3, required4, required5, required6, required7, required8],
                        [length1, length2, length3, length4, length5, length6, length7, length8], 
                        [name1, name2, name3, name4, name5, name6, name7, name8],
                        range(1, 9)):
                        if not acap or acap == "" or req not in [0,1]:
                            break
                        required = True if req == 1 else False
                        res_dic = {'caption': acap, 'to_be_validated': required, 'prompt_number': prompt_number}      
                        if l > 0: 
                            res_dic["length"] = l
                        if n == "DATE":    
                            res_dic["type"] = "date"
                        elif n == "NUMBERS":
                            res_dic["type"] = "number"
                        else:
                            res_dic["type"] = "string"  
                        account_info['prompts'].append(res_dic)
                else:
                    account_info['validate'] = False
                    account_info['prompts'] = []
            if count == 0:
                response.status = 500               
                msg ='account not found'
                res ['result'] = {
                        'number_of_accounts': 0, 
                        'account_number': account_no,
                        'customer_number': customer_no }
                    
            elif count == 1:
                response.status=200
                msg = 'OK'
                res ['result'] = {
                        'number_of_accounts': 1,
                        'prompts': account_info["prompts"],
                        'account_number': account_number, 
                        'customer_number': str(customer_number)}

            else:
                response.status=500
                msg = 'account is not unique %d' % (count)
                res['result'] =  {
                  'number_of_accounts': count,
                  'account_number': account_no,
                  'customer_number': customer_no}
        else:
            response.status = 500
            msg = "invalid account number %s customer number %s combination" % (account_number, customer_no) 
            res['result'] =  {
                       'number_of_accounts': 0,
                       'account_number': account_no,
                       'customer_number': customer_no}
  
        return Utils.make_error_response(response, response.status, msg, res) 

    except Exception as e:
        sys.stdout.write("%s: returning out of handler get_corporate_accounts...\n" % ( datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT) ))
        print "accounts get_corporate_accounts: Exception %s" % (str(e))
        res['result'] =  {
                       'number_of_accounts': 0,
                       'account_number': account_no,
                       'customer_number': customer_no}

        return Utils.make_error_response(response, 500,'failure', res)    


#@app.get('/account/corporate/all/')
def get_corporate_account_all():
    try:
        sys.stdout.write("%s: entering %s\n" % (datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT), __name__))
        sys.stdout.write("%s: get_corporate_account_all %s\n" % (
            datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT),
            str(request.environ) ))

        response =  Utils.prepare_header('get_corporate_account_all', "account")
        if  response.status == 401:
            return            


        Utils.set_default_headers(response)
        response.status = 500
        res = {'status': response.status,
               'result': {'message': 'failure', 'number_of_accounts': 0}
        }
        qstr = dblayer.get_corporate_account_all_querystr()
        if qstr != "":
            info = data_src.fetch_many(qstr)
            count = 0
            account_list = []
            for (account_number, customer_number, account_name, vip_number, phone_account, creation_date, active, 
            extra_info, last_update, 
                caption1, default_value1, length1, prompt_id1,  required1, validation1, name1, 
                caption2, default_value2, length2, prompt_id2,  required2, validation2, name2, 
                caption3, default_value3, length3, prompt_id3,  required3, validation3, name3, 
                caption4, default_value4, length4, prompt_id4,  required4, validation4, name4, 
                caption5, default_value5, length5, prompt_id5,  required5, validation5, name5, 
                caption6, default_value6, length6, prompt_id6,  required6, validation6, name6, 
                caption7, default_value7, length7, prompt_id7,  required7, validation7, name7, 
                caption8, default_value8, length8, prompt_id8,  required8, validation8, name8) in info:
                account_info = {}
                count = count + 1
                account_info["account_number"] = account_number
                account_info["customer_number"] = customer_number
                if active == 1:
                    account_info["active"] = True
                else:
                    account_info["active"] = False

                #print "accounts get_corporate_accounts: count %d account_number %s, customer_number %s, account_name %s, active %d" \
                #                    % ( count, account_number, customer_number, account_name , active)

                if extra_info > 0:
                    account_info["validate"] = True
                    account_info["prompts"] = []
                    for acap, req, l, n, prompt_number in zip(
                        [caption1, caption2, caption3, caption4, caption5, caption6, caption7, caption8],
                        [required1, required2, required3, required4, required5, required6, required7, required8],
                        [length1, length2, length3, length4, length5, length6, length7, length8], 
                        [name1, name2, name3, name4, name5, name6, name7, name8],
                        range(1, 9)):
                        if not acap or acap == "" or req not in [0,1]:
                            break
                        required = True if req == 1 else False
                        res_dic = {'caption': acap, 'to_be_validated': required, 'prompt_number': prompt_number}      
                        if l > 0: 
                            res_dic["length"] = l
                        if n == "DATE":    
                            res_dic["type"] = "date"
                        elif n == "NUMBERS":
                            res_dic["type"] = "number"
                        else:
                            res_dic["type"] = "string"  
                        account_info['prompts'].append(res_dic)
                else:
                    account_info['validate'] = False
                    account_info['prompts'] = []

                account_list.append({"prompts": account_info['prompts'], 
                             "account_number": account_number, 
                             "customer_number": str(customer_number)})    
            if count == 0:
                response.status = 500
                res = {'status': response.status,
                       'result': {'message': 'account not found','number_of_accounts': 0}
                      }
            else:
                response.status = 200
                res = {'status': response.status,
                       'result': {'message': 'OK', 'number_of_accounts': count},
               'accounts': account_list}
        else:
            response.status = 500
            msg = "invalid sql string"
            res = {'status': response.status,
                   'result': {'message': msg, 'number_of_accounts': 0}}


        #print "JSON DUMP == %s" % (json.dumps(res)) 

        return json.dumps(res)
    except Exception as e:
        sys.stdout.write("%s: returning out of handler get_corporate_accounts...\n" % ( datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT) ))
        print "accounts get_corporate_accounts: Exception %s" % (str(e))
        response.status = 500
        res = {'status': response.status,
               'result': {'message': 'failure', 'number_of_accounts': 0}
        }
        return json.dumps(res)


#@app.post('/account/MDT_check/')
def MDT_Check_Account():

    sys.stdout.write("%s: entering %s\n" % (datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT), __name__))
    sys.stdout.write("%s: MDT check account %s\n" % (datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT), str(request.environ) ))
   

    response =  Utils.prepare_header('MDT_Check_Account', "default")
    if  response.status == 401:
            return            

    clen = request.content_length
    request.body.seek(0)
    Utils.set_default_headers(response)
    response.status = 500
    res = {'status': response.status, 'result': {'message': 'failure'}}

    try:
        MDT_check_dic = json.loads(str(request.body.read(clen)))
        sys.stdout.write("%s: MDT check account %s\n" % (datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT), str(MDT_check_dic) ))
    except Exception as e:
        print 'Exception ', str(e)
        return json.dumps(res)

    if not MDT_check_dic.has_key('account_number'):
        res =  {'status': response.status, 'result': {'message': 'no account_number key'}}  
        return json.dumps(res)
   
    sacc = str(MDT_check_dic["account_number"]).strip()
    if len(sacc) > 12 or len(sacc) < 1: 
        res =  {'status': response.status, 'result': {'message': 'invalid account_number key should be 1..12'}}
        return json.dumps(res)

    if not MDT_check_dic.has_key('customer_number'):
        res =  {'status': response.status, 'result': {'message': 'customer_number key'}}
        return json.dumps(res)
    try:
        scnum = int(MDT_check_dic["customer_number"])
    except Exception as e:
        res =  {'status': response.status, 'result': {'message': 'customer_number is not int'}}
        return json.dumps(res)
    try:
        sqlstr = """SELECT AccountNumber as account_number,
                       AccountName as account_name,
                       CustomerNumber as customer_number,  
                       RemoteVoucher as voucher, 
                       Active as active 
                       FROM account WHERE AccountNumber= '%s' AND CustomerNumber= %s 
                       limit 1;""" % (sacc, str(scnum))    
        info = data_src.fetch_many(sqlstr) 
        account_res = {"message": 'OK', "number_of_accounts": 0}
        for (account_number, account_name, customer_number, voucher, active) in info:
            account_res["number_of_accounts"] = 1
            try:
                account_res["account_name"] = str(account_name) if account_name else ""
            except Exception as e:
                account_res["account_name"] =  "" 
            try:
                account_res["voucher"] = int(voucher) if voucher else 0
            except Exception as e:
                account_res["voucher"] = 0
            try:
                account_res["active"] = int(active) if active else 0
            except Exception as e:
                account_res["active"] = 0
            try:
                account_res["account_number"] = str(account_number) if account_number else ""
            except Exception as e:
                account_res["account_number"] = ""
            try:
                account_res["customer_number"] = int(customer_number) if customer_number else 0
            except Exception as e:
                account_res["customer_number"] = 0
        response.status = 200
        res = {"status": response.status, "result": account_res}
        return json.dumps(res)
    except Exception as e:
        print "Exception ", str(e)
        return json.dumps(res)  

    
#@app.post('/account/validate/')
def validate_account():
    try:
        sys.stdout.write("%s: entering %s\n" % (datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT), __name__))
        sys.stdout.write("%s: validate account %s\n" % (
            datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT),
            str(request.environ) ))
  
        response =  Utils.prepare_header('validate_account', "account")
        if  response.status == 401:
            return            

        clen = request.content_length
        request.body.seek(0)
        Utils.set_default_headers(response)
        response.status = 500
        res = {'status': response.status,
               'result': {
                       'message': 'failure',
                       'number_of_accounts': 0,
                       'account_number': '',
                       'customer_number': ''}
              }
        try:
            validate_dic = json.loads(str(request.body.read(clen)))
            sys.stdout.write("%s: validate account %s\n" % (
            datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT), 
            str(validate_dic) ))
        except Exception as e:
            print 'Exception ', str(e)
            return json.dumps(res) 
        
        if not validate_dic.has_key('account_number') or not validate_dic.has_key('customer_number'):
            return json.dumps(res)
        else:
            print 'account number', validate_dic['account_number']
            print 'customer number', validate_dic['customer_number']
            prompts = ["prompt1", "prompt2", "prompt3", "prompt4", "prompt5", "prompt6", "prompt7", "prompt8"]          
        num_of_incoming_prompts = 0 
        if validate_dic.has_key("prompts"):
            for p, i in zip(validate_dic["prompts"],  range(len(validate_dic["prompts"])) ):
                num_of_incoming_prompts = num_of_incoming_prompts + 1
                prompts[i] = validate_dic["prompts"][i]
                if i == 7:
                    break
        print 'prompts ', prompts 
        qstr = dblayer.get_corporate_account_validation_querystr(
        validate_dic["account_number"], 
        validate_dic["customer_number"],
        prompts) 
        print "qstr", qstr   
#
# mysql> call cabmate.ValidateAcctPrompts('ROBF1', 0, 'prompt1', 'M', 'prompt3', 'prompt4', 'prompt5', 'prompt6', 'prompt7', 'prompt8');
#
        if qstr != "":
            info = data_src.fetch_many(qstr)
            count = 0
            valids = []
            valid = True
            for (IsGood1, Name1, IsGood2, Name2, IsGood3, Name3, IsGood4, Name4,
             IsGood5, Name5, IsGood6, Name6, IsGood7, Name7, IsGood8, Name8) in info:
                print IsGood1, Name1, IsGood2, Name2, IsGood3, Name3, IsGood4, Name4
                print IsGood5, Name5, IsGood6, Name6, IsGood7, Name7, IsGood8, Name8
                count = count + 1
                print 'count = ', count 
                print 'valids append 1' 
                valids.append(validpr.get_if_prompt_is_valid(IsGood1, Name1, prompts[0]))
                print valids
                print 'valids append 2'
                valids.append(validpr.get_if_prompt_is_valid(IsGood2, Name2, prompts[1]))
                print valids
                print 'valids append 3'
                valids.append(validpr.get_if_prompt_is_valid(IsGood3, Name3, prompts[2]))
                print valids 
                print 'valids append 4'
                valids.append(validpr.get_if_prompt_is_valid(IsGood4, Name4, prompts[3]))
                print valids 
                print 'valids append 5'
                valids.append(validpr.get_if_prompt_is_valid(IsGood5, Name5, prompts[4]))
                print valids
                print 'valids append 6'
                valids.append(validpr.get_if_prompt_is_valid(IsGood6, Name6, prompts[5]))
                print valids
                print 'valids append 7' 
                valids.append(validpr.get_if_prompt_is_valid(IsGood7, Name7, prompts[6]))
                print valids
                print 'valids append 8'
                valids.append(validpr.get_if_prompt_is_valid(IsGood8, Name8, prompts[7]))
                print valids 
                if False in valids:
                    valid = False
                if count == 1:
                    break   
            print 'count=', count     
            if count == 0:
                response.status = 500
                res = {'status': response.status,
                    'result': {
                        'message': 'account not found',
                        'number_of_accounts': 0, 
                         'valid': False,
                'account_number': validate_dic["account_number"],
                'customer_number': validate_dic["customer_number"]
                    }}
            elif count == 1:
                response.status = 200
                res = {'status': response.status,
                    'result': {
                        'message': 'OK',
                        'number_of_accounts': 1,
                        'valid': valid,
                    'valid_response': valids[:num_of_incoming_prompts],  
                        'account_number': validate_dic["account_number"], 
                        'customer_number': validate_dic["customer_number"]}}
            else:
                response.status = 500
                msg = 'account is not unique %d' % (count)
                res = {'status': response.status,
                  'result': {
                  'valid': False,
                  'message': 'account not found',
                  'number_of_accounts': 0,
                  'account_number': validate_dic["account_number"],
                  'customer_number': validate_dic["customer_number"]}}
        else:
            response.status = 500
            msg = "invalid account number %s customer number %s combination" % (
               validate_dic["account_number"], 
               validate_dic["customer_number"])
            res = {'status': response.status,
                   'result': {
                       'message': msg,
                       'valid': False,
                       'number_of_accounts': 0,
                       'account_number': validate_dic["account_number"], 
                       'customer_number': validate_dic["customer_number"]}}

        

        return json.dumps(res)
    except Exception as e:
        sys.stdout.write("%s: returning out of handler  validate_account ...\n" % ( datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT) ))
        print "accounts  validate_account : Exception %s" % (str(e))
        return json.dumps(res)



#@app.route('/account/check_subaccount/',  method=['POST', 'GET'])
def check_subaccount():

    sys.stdout.write("%s: check_subaccount %s\n" % (datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT), str(request.environ) ))

    response =  Utils.prepare_header('check_subaccount', "default")
    if  response.status == 401:
            return            

    clen = request.content_length
    request.body.seek(0)
    Utils.set_default_headers(response)
    response.status = 500
    res = {'status': response.status, 'result': {'message': 'failure'}}

    try:
        dic = json.loads(str(request.body.read(clen)))
        sys.stdout.write("%s: check_subaccount %s\n" % (datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT), str(dic) ))
    except Exception as e:
        sys.stdout.write("%s: Exception check_subaccount %s \n"  % (datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT), str(e) ))        
        return json.dumps(res)


    try:
        acc_num = ""
        cus_num = -1
   
        if  'vip_number' in dic:
            sacc = str(dic["vip_number"]).strip()
        elif 'sub_account' in dic:
            sacc = str(dic["sub_account"]).strip() 
        else:
            res =  {'status': response.status, 'result': {'message': 'no vip_number or sub_account key'}}  
            return json.dumps(res)

        if len(sacc) > 12 or len(sacc) < 1: 
            res =  {'status': response.status, 'result': {'message': 'invalid number key should be 1..12'}}
            return json.dumps(res)
    except Exception as e:
        sys.stdout.write("%s: Exception check_subaccount %s \n"  % (datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT), str(e) ))        
        return json.dumps(res)
    
    try:
        if dic.has_key('account_number'):         
            acc_num = str(dic["account_number"]).strip()
            if len(acc_num) > 12 or len(acc_num) < 1: 
                acc_num=""
        if dic.has_key('customer_number'):        
            cus_num = int(dic["customer_number"])
    except Exception as e:
        sys.stdout.write("%s: Exception check_subaccount %s \n"  % (datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT), str(e) ))        
        return json.dumps(res)    

    try:
        if acc_num == "" and cus_num == -1:
            sqlstr = """SELECT AccountNumber as account_number,
                       AccountName as account_name,
                       CustomerNumber as customer_number,  
                       RemoteVoucher as voucher, 
                       Active as active,
                       VIPNumberString as vip_number                       
                       FROM account WHERE VIPNumberString= '%s'  
                       limit 10;""" % (sacc)  


        if acc_num != "" and cus_num == -1 :
            sqlstr = """SELECT AccountNumber as account_number,
                       AccountName as account_name,
                       CustomerNumber as customer_number,  
                       RemoteVoucher as voucher, 
                       Active as active,
                       VIPNumberString as vip_number
                       FROM account WHERE VIPNumberString= '%s' and AccountNumber= '%s'
                       limit 10;""" % (sacc, acc_num)  


        if acc_num != "" and cus_num != -1:
            sqlstr = """SELECT AccountNumber as account_number,
                       AccountName as account_name,
                       CustomerNumber as customer_number,  
                       RemoteVoucher as voucher, 
                       Active as active,
                       VIPNumberString as vip_number
                       FROM account WHERE VIPNumberString= '%s' and AccountNumber= '%s' AND CustomerNumber=%s
                       limit 10;""" % (sacc, acc_num, str(cus_num))  


        if cus_num != -1 and acc_num == "" :
            sqlstr = """SELECT AccountNumber as account_number,
                       AccountName as account_name,
                       CustomerNumber as customer_number,  
                       RemoteVoucher as voucher, 
                       Active as active,
                       VIPNumberString as vip_number
                       FROM account WHERE VIPNumberString= '%s' and CustomerNumber=%s
                       limit 10;""" % (sacc, str(cus_num) )  

        info = data_src.fetch_many(sqlstr) 
        count = 0
        account_res = {"message": 'OK', "number_of_accounts": count}
        for (account_number, account_name, customer_number, voucher, active, vip_number) in info:
            count = 1
    
            try:
                account_res["account_name"] = str(account_name) if account_name else ""
            except Exception as e:
                account_res["account_name"] =  "" 
    
            try:
                account_res["voucher"] = int(voucher) if voucher else 0
            except Exception as e:
                account_res["voucher"] = 0
    
            try:
                account_res["active"] = int(active) if active else 0
            except Exception as e:
                account_res["active"] = 0
    
            try:
                account_res["account_number"] = str(account_number) if account_number else ""
            except Exception as e:
                account_res["account_number"] = ""
    
            try:
                account_res["customer_number"] = int(customer_number) if customer_number else 0
            except Exception as e:
                account_res["customer_number"] = 0

            try:
                account_res["vip_number"] = str(vip_number) if vip_number else ""
            except Exception as e:
                account_res["vip_number"] = 0                
    
        account_res["number_of_accounts"] = 1
        response.status = 200
        res = {"status": response.status, "result": account_res}
        return json.dumps(res)
    except Exception as e:
        sys.stdout.write("%s: Exception check_subaccount %s \n"  % (datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT), str(e) ))
        return json.dumps(res)  



#@app.post('/v1/supervisor/action/')
def supervisor_action():
    try:
        sys.stdout.write("%s: entering %s\n" % (datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT), __name__))
        sys.stdout.write("%s: supervisor action %s\n" % (
            datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT),
            str(request.environ) ))

        response =  Utils.prepare_header('supervisor_action', "default")
        if  response.status == 401:
            return            

        clen = request.content_length
        request.body.seek(0)
        Utils.set_default_headers(response)
        response.status = 500
        res = {'status': response.status,
               'result': { 'message': 'failure'}}
        try:
            action_dic = json.loads(str(request.body.read(clen)))
            sys.stdout.write("%s: action dictionary %s\n" % (
                datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT),
                str(action_dic) ))
        except Exception as e:
            print 'Exception ', str(e)
            return json.dumps(res)

        if not action_dic.has_key('action'):
            res['result']['message'] = 'failure: action field is missing'
            return json.dumps(res)
        
        if not action_dic['action'] in ["suspend", "reinstate", "login", "logout", "coded_msg"]:
            res['result']['message'] = 'failure: invalid action field value'
            return json.dumps(res)

        if not action_dic.has_key('driver_id'):
            res['result']['message'] = 'failure: driver_id field is missing'
            return json.dumps(res)
        try:
            driver_id = int(action_dic['driver_id'])
        except Exception as e:
            res['result']['message'] = 'failure: driver_id field is not int'
            return json.dumps(res)

        if not action_dic.has_key('taxi'):
            res['result']['message'] = 'failure: taxi field is missing'
            return json.dumps(res)
        try:
           taxi = int(action_dic['taxi'])
        except Exception as e:
            res['result']['message'] = 'failure: taxi field is not int'
            return json.dumps(res)

        if not action_dic.has_key('fleet'):
            res['result']['message'] = 'failure: fleet field is missing'
            return json.dumps(res)
        try:
            fleet_num = int(action_dic["fleet"])
        except Exception as e:
            res['result']['message'] = 'failure: fleet is not integer'
            return json.dumps(res)

        if action_dic["action"] in ["suspend", "reinstate"]:
            if not action_dic.has_key('authority_id'):
                res['result']['message'] = 'failure: authority_id field is missing'
                return json.dumps(res)
            try:
                #authority_id = int(action_dic["authority_id"])
                authority_id = msgconf.CWEBS
            except Exception as e:
                res['result']['message'] = 'failure: authority_id is not int'
                return json.dumps(res)
            duration = 0
            if action_dic['action'] == "suspend":
                duration = msgconf.default_susp_duration
                if action_dic.has_key('duration'):
                    try:
                        duration = int(action_dic['duration'])
                    except Exception as e:
                        duration = msgconf.default_susp_duration

            if not action_dic.has_key('msg_for_dispatch'):
                res['result']['message'] = 'failure: message for dispatch is not present'
                return json.dumps(res)
            msg_for_dispatch = str(action_dic["msg_for_dispatch"])
            #msg_for_dispatch = action_dic["msg_for_dispatch"].encode('utf8')
            if len(msg_for_dispatch) > 32:
                msg_for_dispatch = msg_for_dispatch[:32]

            if not action_dic.has_key('msg_for_driver'):
                res['result']['message'] = 'failure: message for driver is not present'
                return json.dumps(res)
            msg_for_driver = str(action_dic["msg_for_driver"])
            if len(msg_for_driver) > 32:
                msg_for_driver = msg_for_driver[:32]
            dData = (driver_id, duration, long(time.time()), authority_id, msg_for_dispatch, msg_for_driver,  '1', '2', taxi, fleet_num, 8*'X')
            print 'dData ', dData
            s = struct.Struct('I I I h 33s 33s c c h h 8s')  #  suspension data
            packed_data = s.pack( *dData)
            data_size = s.size
            #base_fmt = 'I I I I I B B B B'
            ss = struct.Struct(cabmsg.base_fmt + '%ds' % (s.size))  
            #ss = struct.Struct('I I I I I c c c c 96s')
            if action_dic['action'] == "suspend":
                cabmsg.gmsg_send(packed_data, data_size, msgconf.DM, 0, msgconf.MT_SUSP_DRIVER, ss)
            if action_dic['action'] == "reinstate":
                cabmsg.gmsg_send(packed_data, data_size, msgconf.DM, 0, msgconf.MT_REIN_DRIVER, ss)

            #cabmsg.send_supervisor_msg(action_dic['action'], dData)
            response.status = 200
            res = {'status': response.status, 'result': {'message': 'OK'}}
            return json.dumps(res)
        if action_dic["action"] in ["login", "logout"]:
            #s0  = struct.Struct('8I 2f 7h c B 33s 33s 33s 33s B B c c')
            '''
            dData = (56, long(time.time()), 0, driver_id, 0, 0, 0, 0, 0.0, 0.0, 
                     0, taxi, msgconf.BO, 0, msgconf.Q_PROC, fleet_num, 0, 
                     ' ', 3,
                     format_field.format_field("MDT SYNC REQUEST", 33),
                     33*" ", 33*" ", 33*" ", 0, 0, ' ', ' ')
            cabmsg.send_login_msg(data=dData, msgid=1)
            '''
        #
            #dData = (taxi, "MDT SYNC REQUEST                 ", 33*" ", 33*" ", 33*" ",
            #         20, 48, 8, fleet_num, fleet_num, 0, 0, "JUNK************")
            #cabmsg.send_login_msg(data=dData, msgid=2)
        #
            action_char = ' '
            if action_dic["action"] == "login":
                action_char = 'I'  
            elif action_dic["action"] == "logout":
                action_char = 'O' 
            itaxmsgid = '1C0032'
            SeqNo = sockcli.generate_SeqNo()
            taxi_no_str =  format_field.format_field(str(taxi), 5, True)
            driver_id_str = format_field.format_field(str(driver_id), 8, True)  
            message = itaxmsgid + SeqNo + taxi_no_str + driver_id_str + action_char + format_field.format_field(' ', 8, True)
            sys.stdout.write("%s: sending to a socket message %s\n" % (datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT), message))
            sockcli.lock.acquire()
            sockcli.ITaxiSrvReqDic[SeqNo] = {'msg': '', 'msg_type': ''}
            sockcli.lock.release()
            sockcli.send_client_request(message)
            sys.stdout.write("%s: message was sent\n" % ( datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT) ) )

            resp = sockcli.ITaxiSrvReqDic[SeqNo]['msg'].strip()

            sleep_counter = 0
            while resp == '':
                #sys.stdout.write("%s: sleeping...\n" % ( datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT) ) )
                time.sleep(1)
                #sys.stdout.write("%s: back from sleep...\n" % ( datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT) ) )
                resp = sockcli.ITaxiSrvReqDic[SeqNo]['msg'].strip()
                #sys.stdout.write("%s: response=%s\n" % ( datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT), resp) )
                sleep_counter = sleep_counter + 1
                if sleep_counter > 10:
                    break
            if sockcli.ITaxiSrvReqDic[SeqNo]['msg_type'] == '90':
                sockcli.remove_dic_entry(SeqNo)
                response.status = 200
                res = {'status': response.status, 'result': {'message': 'OK'}}                
                return json.dumps(res)
            else:
                if sockcli.ITaxiSrvReqDic[SeqNo]['msg_type'] == '99':
                    msg_text = 'NACK'
                else:
                    msg_text = 'socket timeout' 
                response.status = 500
                res = {'status': response.status, 'result': {'message': 'msg_text'}}
                return json.dumps(res)

        
        if action_dic["action"] == "coded_msg":
            sprv_obj = SupervisorMsg.SupervisorMessage(action_dic)
            if sprv_obj.getError() is True:
                return json.dumps(sprv_obj.getResult())

            return sprv_obj.send_msg( response, action_dic)

    except Exception as e:
        sys.stdout.write("%s: exception is raised in supervisor action\n" % ( datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT) ))
        print "supervisor action: Exception %s" % (str(e))
        Utils.set_default_headers(response)
        response.status = 500
        res = {'status': response.status, 'result': { 'message': 'failure'}}
        return json.dumps(res)
 

#@app.route('/driver/suspend_list/', method=['GET'])
def get_driver_suspend_list():
    try:
        return api_funcs._get_driver_suspend_list(data_src)      
    except Exception as e: 
        response.status = 500
        res = {'status': response.status,
               'result': {'message': 'failure', 'number_of_drivers': 0, 'drivers': []}}
        return json.dumps(res)


#@app.route('/request_fare_details/', method='POST')
def request_fare_details():
    try:
        return fare_funcs.request_fare_details()
    except Exception as e:
        print ' Exception %s ' % ( str(e) )

#@app.error(404)
def error404(error):
    response.status = 404
    return '404 - Sorry, the requested resource is not available'


#@app.route('/cwebs/version/', method='GET')
def get_cwebs_version():
    if Config.MONGO:
        from app.cwebsserv import mydb 
        entry = { "version_access" : datetime.datetime.utcnow() }
        mydb.logs.insert(entry)
    return api_funcs._get_version()
   
#@app.route('/cwebs/hostinfo/', method='GET')
def get_cwebs_hostinfo():
     return api_funcs._get_hostinfo()


#@app.route('/message/send_fleet_msg/', method='POST')
def fleet_send_msg():
    try:
        return api_funcs._fleet_send_msg()
    except Exception as e:
        print ' Exception %s ' % ( str(e) )


#@app.route('/device/clear_emergency/', method='POST')
def clear_device_emergency():
    try:
        return api_funcs._clear_device_emergency()
    except Exception as e:
        print ' Exception %s ' % ( str(e) )

#@app.route('/message/send_vehicle_msg/', method='POST' )
def vehicle_send_msg():
    try:
        return api_funcs._vehicle_send_msg()
    except Exception as e:
        print ' Exception %s ' % ( str(e) )


#@app.route('/message/send_driver_msg/',  method='POST' )
def driver_send_msg():
    try:
        return api_funcs._driver_send_msg()
    except Exception as e:
        print ' Exception %s ' % ( str(e) )


#@app.route( '/dispatcher/queues/', method=['POST', 'GET'] )
def dispatch_queues():
    try:
        return api_funcs._dispatch_queues()
    except Exception as e:
        print ' Exception %s ' % ( str(e) )

#@app.route('/driver/action/',  method='POST' )
def driver_action():
    try:
        return api_funcs._driver_action(data_src)
    except Exception as e:
        print ' Exception %s ' % ( str(e) )

#@app.route('/vehicle/action/', method='POST' )
def vehicle_action():
    try:
        return api_funcs._vehicle_action(data_src)
    except Exception as e:
        print ' Exception %s ' % ( str(e) )

#@app.route('/v1/device/sendmsg/',  method='POST' )
def device_sendmsg():
    global sockcli
    try:
        return api_funcs._device_sendmsg(sockcli)
    except Exception as e:
        print ' Exception %s ' % ( str(e) )

#@app.route('/fleet/action/', method=['POST'])
def modify_fleet():
    try:
        return api_funcs._modify_fleet()
    except Exception as e:
        print ' Exception %s ' % ( str(e) )

#@app.route('/v1/dispatcher/save_book_order/',  method='POST' )
def save_book_order():
    global sockcli
    try:
       return fare_funcs._dispatch_save_book_order(sockcli)
    except Exception as e:
        print ' Exception %s ' % ( str(e) )
 
#@app.route('/dispatcher/save_book_order/',  method='POST')
#@app.route('/v2/dispatcher/save_book_order/',  method='POST')
def save_book_order_cabmsg():
    global sockcli
    global myzonecache
    try:
       return fare_tfc._dispatch_save_book_order_tfc(sockcli,  myzonecache)
    except Exception as e:
        print ' Exception %s ' % ( str(e) )

#@app.route('/v1/dispatcher/modify_book_order/',  method='POST' )
def modify_book_order():
    global sockcli
    try:
        return fare_funcs._dispatch_modify_book_order(sockcli, data_src_repo)
    except Exception as e:
        print ' Exception %s ' % ( str(e) )

#@app.route('/v2/dispatcher/modify_book_order/',  method='POST')
#@app.route('/dispatcher/modify_book_order/',  method='POST')
def modify_book_order_cabmsg():
    global sockcli
    global myzonecache    
    try:
        return fare_modify_tfc._dispatch_modify_book_order_tfc(sockcli, data_src_repo,  myzonecache)
    except Exception as e:
        print ' Exception modify_book_order_tfc %s ' % ( str(e) )


#@app.route('/v1/dispatcher/cancel_book_order/',  method='POST' )
def cancel_book_order():
    global sockcli    
    try:
        return fare_funcs._dispatch_cancel_book_order(sockcli, data_src_repo)
    except Exception as e:
        print ' Exception %s ' % ( str(e) )

#@app.route('/v2/dispatcher/cancel_book_order/',  method='POST' )
#@app.route('/dispatcher/cancel_book_order/',  method='POST' )
def cancel_book_order_cabmsg():
    global sockcli    
    try:
        return fare_cancel_tfc._dispatch_cancel_book_order_tfc(sockcli, data_src_repo)
    except Exception as e:
        print ' Exception %s ' % ( str(e) )


#@app.route('/v1/update_destination/' ,  method='POST')
def update_destination():
    global sockcli    
    try:
        return fare_funcs._update_destination(sockcli, data_src_repo)
    except Exception as e:
        print ' Exception %s ' % ( str(e) )

#@app.route('/v2/update_destination/' ,  method='POST')
#@app.route('/update_destination/' ,  method='POST')
def update_destination_cabmsg():
    global sockcli    
    try:
        return fare_funcs_cabmsg._update_destination(sockcli, data_src_repo)
    except Exception as e:
        print ' Exception %s ' % ( str(e) )


#@app.route('/v1/update_fare_amount/' ,  method='POST')
def update_fare_amount():
    global sockcli    
    try:
        return fare_funcs._update_fare_amount(sockcli, data_src_repo)
    except Exception as e:
        print ' Exception %s ' % ( str(e) )

#@app.route('/v2/update_fare_amount/' ,  method='POST')
#@app.route('/update_fare_amount/' ,  method='POST')
def update_fare_amount_cabmsg():
    global sockcli    
    try:
        return  fare_funcs_cabmsg._update_fare_amount(sockcli, data_src_repo)
    except Exception as e:
        print ' Exception %s ' % ( str(e) )

#@app.route('/v1/update_payment_type/' ,  method='POST')
def update_payment_type():
    global sockcli    
    try:
        return fare_funcs._update_payment_type(sockcli, data_src_repo)
    except Exception as e:
        print ' Exception %s ' % ( str(e) )

#@app.route('/v2/update_payment_type/' ,  method='POST')
#@app.route('/update_payment_type/' ,  method='POST')
def update_payment_type_cabmsg():
    global sockcli    
    try:
        return fare_funcs_cabmsg._update_payment_type(sockcli, data_src_repo)
    except Exception as e:
        print ' Exception %s ' % ( str(e) )


#@app.route('/settings/fleet_separation', method=['GET'])   
def get_param_fleet(): 
    try:
        return scap_funcs._get_fleet_separation()
    except Exception as e:
        print ' Exception %s ' % ( str(e) )


#@app.route('/settings/system_params/', method=['GET', 'POST'])   
#@app.route('/settings/system_params', method=['GET', 'POST'])   
def get_sys_param(): 
    try:
        return scap_funcs._get_sys_params()
    except Exception as e:
        print ' Exception %s ' % ( str(e) )


#@app.route('/v2/zone_by_gps/',  method=['POST', 'GET'])
#@app.route('/zone_latlon/',  method=['POST', 'GET'])
#@app.route('/zone_by_gps/',  method=['POST', 'GET'])
def zone_by_latlon():
    global sockcli
    global myzonecache
    try:
        from zones.get_zone import _get_zone
        return _get_zone(sockcli, myzonecache)    
    except Exception as e:
        sys.stdout.write("%s: Exception %s\n" % ( datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT), str(e) ) )
        response.status = 500
        res = {"status": response.status, "result": {"message": ErrorMsg.ERROR_MSG_GENERAL_ERROR}}
        return json.dumps(res)


#@app.route('/v1/zone_by_gps/',  method=['POST', 'GET'])
def zone_by_gps():
    global sockcli
    try:
        return api_funcs._zone_by_gps(sockcli)    
    except Exception as e:
        sys.stdout.write("%s: Exception %s\n" % ( datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT), str(e) ) )        
        response.status = 500
        res = {"status": response.status, "result": {"message": ErrorMsg.ERROR_MSG_GENERAL_ERROR}}
        return json.dumps(res)

#@app.route('/v2/supervisor/action/',  method=['POST', 'GET'])
#@app.route('/supervisor/action/',  method=['POST', 'GET'])
def supervisor_action_cabmsg():
    try:
        return supervisor_funcs._supervisor_action()    
    except Exception as e:
        sys.stdout.write("%s: Exception %s\n" % ( datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT), str(e) ) )        
        response.status = 500
        res = {"status": response.status, "result": {"message": ErrorMsg.ERROR_MSG_GENERAL_ERROR}}
        return json.dumps(res)    


#@app.route('/v2/device/sendmsg/',  method='POST' )
#@app.route('/device/sendmsg/',  method='POST' )
def device_sendmsg_q():  
    try:
        return supervisor_funcs._device_sendmsg_q()
    except Exception as e:
        sys.stdout.write("%s: Exception %s\n" % ( datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT), str(e) ) )        
        response.status = 500
        res = {"status": response.status, "result": {"message": ErrorMsg.ERROR_MSG_GENERAL_ERROR}}
        return json.dumps(res)            

#@app.route('/v2/dispatcher/redispatch_book_order/',  method='POST' )
#@app.route('/dispatcher/redispatch_book_order/',  method='POST' )
def redispatch_job():
    global sockcli
    global myzonecache
    try:
       return fare_redispatch._redispatch_order(sockcli,  myzonecache)
    except Exception as e:
        print ' Exception %s ' % ( str(e) )

######################### Move this elsewhere #####################

all_rules = []


# UrlRule (url, func, methods=None, base_url=BASE_URL)
all_rules.extend([

    # Account
    UrlRule('/account/corporate/<account_no>/<customer_no>', get_corporate_account, methods = 'GET'),
    UrlRule('/account/corporate/all/', get_corporate_account_all, methods='GET'),
    UrlRule('/account/MDT_check/', MDT_Check_Account, methods='POST'),
    UrlRule('/account/validate/', validate_account, methods='POST'),
    UrlRule('/account/check_subaccount/', check_subaccount, methods=['POST', 'GET']),
    UrlRule('/cwebs/version/', get_cwebs_version, methods='GET'),
    UrlRule('/cwebs/hostinfo/', get_cwebs_hostinfo, methods='GET'),

    # Dispatcher:

    UrlRule('/dispatcher/save_book_order/', save_book_order_cabmsg, methods='POST'),
    UrlRule('/dispatcher/modify_book_order/', modify_book_order_cabmsg, methods='POST'),
    UrlRule('/dispatcher/cancel_book_order/', cancel_book_order_cabmsg, methods='POST') ,
    UrlRule('/dispatcher/queues/', dispatch_queues, methods=['GET', 'POST']),
    UrlRule('/dispatcher/redispatch_book_order/', redispatch_job, methods='POST'),
    UrlRule('/dispatcher/qtotals/', dispatch_qtotals, methods='GET'),
    UrlRule('/dispatcher/zonestatus/<fleet_id>', dispatch_zonestatus, methods='GET'),
    UrlRule('/dispatcher/zonesetzones/', dispatch_zonesetszones, methods='GET'),
    UrlRule('/dispatcher/zonevehicles/', dispatch_zonevehicles, methods='GET'),

    # device, driver, fleet
    UrlRule('/device/clear_emergency/', clear_device_emergency, methods='POST'),
    UrlRule('/device/sendmsg/', device_sendmsg_q, methods='POST'),
    UrlRule('/driver/suspend_list/', get_driver_suspend_list, methods='GET'),
    UrlRule('/driver/action/', driver_action, methods='POST'),

    UrlRule('/fleet/action/', modify_fleet, methods='POST'),

    # messages to v/d/f
    UrlRule('/message/send_fleet_msg/', fleet_send_msg, methods='POST'),
    UrlRule('/message/send_vehicle_msg/', vehicle_send_msg, methods='POST'),
    UrlRule('/message/send_driver_msg/', driver_send_msg, methods='POST'),

    # should be part of dispatcher
    UrlRule('/request_fare_details/', request_fare_details, methods='POST'),

    # settings : fleet_sepration is in
    UrlRule('/settings/fleet_separation/', get_param_fleet, methods='GET'),
    UrlRule('/settings/system_params/', get_sys_param, methods=['GET', 'POST']),


    UrlRule('/settings/system_limits/', params.sys_funcs._get_sys_limit_param, methods=['GET', 'POST']),

    UrlRule('/supervisor/action/', supervisor_action_cabmsg, methods='POST'),

    # dispatcher like
    UrlRule('/update_destination/', update_destination_cabmsg, methods='POST'),
    UrlRule('/update_fare_amount/', update_fare_amount_cabmsg, methods='POST'),
    UrlRule('/update_payment_type/', update_payment_type_cabmsg, methods='POST'),

    # actions
    UrlRule('/vehicle/action/', vehicle_action, methods='POST'),

    # zone info
    UrlRule('/zone_latlon/', zone_by_latlon, methods=['GET', 'POST']),
    UrlRule('/zone_by_gps/', zone_by_latlon,  methods=['GET', 'POST'])

])

def setup_routing(app):  
    try:
        for i in all_rules:
            app.route( i.url, i.methods, i.func)  
    except Exception as e:
        sys.stdout.write("%s: Exception %s\n" % ( datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT), (str(e) ) ) )        

#Version v1 talks to MSGQ
def setup_routing_msgq(app, ver):
    app.route('/{0}/supervisor/action/'.format ( ver) , 'POST', supervisor_action_cabmsg)
    app.route('/{0}/device/sendmsg/'.format ( ver),  'POST', device_sendmsg_q)    
    app.route('/{0}/dispatcher/save_book_order/'.format ( ver),  'POST' , save_book_order_cabmsg)     
    app.route('/{0}/dispatcher/modify_book_order/'.format ( ver),  'POST' ,modify_book_order_cabmsg)
    app.route('/{0}/dispatcher/cancel_book_order/'.format ( ver),  'POST' , cancel_book_order_cabmsg)  
    app.route('/{0}/update_destination/'.format ( ver) ,  'POST', update_destination_cabmsg)
    app.route('/{0}/update_fare_amount/'.format ( ver) ,  'POST', update_fare_amount_cabmsg)
    app.route('/{0}/update_payment_type/'.format ( ver) ,  'POST', update_payment_type_cabmsg)
    app.route('/{0}/zone_by_gps/'.format ( ver),  ['GET', 'POST'], zone_by_latlon)
 

#Version v2 talks to ITAXISRV
def setup_routing_itaxisrv(app, ver):   
    app.route('/{0}/supervisor/action/'.format ( ver ), 'POST', supervisor_action)
    app.route('/{0}/device/sendmsg/'.format ( ver ),  'POST', device_sendmsg)    
    app.route('/{0}/dispatcher/save_book_order/'.format ( ver ),  'POST' , save_book_order)     
    app.route('/{0}/dispatcher/modify_book_order/'.format ( ver ),  'POST' , modify_book_order)
    app.route('/{0}/dispatcher/cancel_book_order/'.format ( ver ),  'POST' , cancel_book_order)  
    app.route('/{0}/update_destination/'.format ( ver ) ,  'POST', update_destination)
    app.route('/{0}/update_fare_amount/'.format ( ver ) ,  'POST', update_fare_amount)
    app.route('/{0}/update_payment_type/'.format ( ver ) ,  'POST', update_payment_type)
    app.route('/{0}/zone_by_gps/'.format ( ver ), ['GET', 'POST'], zone_by_gps)

def setup_routing_version(app, version='cabmsg'):
    if version == 'itaxisrv':
        setup_routing_itaxisrv (app, 'v1')
    if version == 'cabmsg':
        setup_routing_msgq (app, 'v2')


def create_services():
    try:
        app = Bottle()

        # cabmate schema
        data_src = smalldb.DB(Config.DB_HOST, Config.DB_USER, Config.DB_PASSWORD, Config.DB_NAME)
        data_src.connect()

        # CabmateRepo schema
        data_src_repo = smalldb.DB(Config.DB_HOST_REPO, Config.DB_USER_REPO, Config.DB_PASSWORD_REPO, Config.DB_NAME_REPO)
        data_src_repo.connect()

        # Logs schema
        data_logs_src = smalldb.DB(Config.DB_LOGS_HOST, Config.DB_LOGS_USER, Config.DB_LOGS_PASSWORD, Config.DB_LOGS_NAME)
        data_logs_src.connect()
        # socket server config

        setup_routing(app)

        setup_routing_version(app, version='cabmsg')

        sockcli = socketcli.sClient(Config.SocketServerHost, Config.SocketServerPort, gevent.lock.Semaphore())     

        myzonecache = zone_cache()

        return app, data_src, data_src_repo, data_logs_src, myzonecache, sockcli   
    except Exception as e:
        sys.stdout.write("%s: Exception %s\n" % ( datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT), (str(e) ) ) )

    return None, None, None, None, None, None

app, data_src, data_src_repo, data_logs_src, myzonecache, sockcli  = create_services()