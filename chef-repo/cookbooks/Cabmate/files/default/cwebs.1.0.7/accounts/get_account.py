from gevent import monkey; monkey.patch_all()
import gevent 
import datetime
from bottle import Bottle, view, template, redirect, request, response, static_file, run, abort, route
import json
import sys
import time
import zqqwrap
import smalldb
import socketcli
import socket
import thread
import cwebsconf as Config
import itcli
import format_field
import dblayer
import validpr
import driver
import vehicle
import msgconf
import cabmsg
import struct
import sanity_check
import scap
import errormsg as ErrorMsg
import vehicle_msg
import server_utils as Utils



@app.route('/account/check_subaccount/',  method=['POST', 'GET'])
def check_subaccount():

    sys.stdout.write("%s: check_subaccount %s\n" % (datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT), str(request.environ) ))

    response =  Utils.prepare_header('check_subaccount', "default")
    if  response.status == 401:
            return            

    clen = request.content_length
    request.body.seek(0)
    response.headers["Content-type"] = "application/json"
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

