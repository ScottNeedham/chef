import datetime
import sys
import dblayer
import config.cwebsconf as Config
import smalldb
import time
import re
import uuid
import format_field


def retrieve_data_for_ibs_mobileorder(data_src, farenum):
    res_dic = {}
    sql_stat = '''
		SELECT 
		pickup_streetnumber, 
		pickup_streetname,
		pickup_cityname,
		pickup_latitude,
		pickup_longitude,
		dest_streetnumber, 
		dest_streetname,
		dest_cityname,
		SequenceNumber,
		fleet,
		driverid,
		pickup_dispatchzone,
		remark1,
		remark2,
		remark3,
		remark4,
		IBSOrderID as orderid
		FROM farefl
		WHERE FareNumber = %s limit 1
		  ''' % (farenum)
    print 'retrieve_data_for_ibs_mobileorder ---> Execute ...', sql_stat
    try:
	info = data_src.fetch_many(sql_stat)
        for ( pickup_streetnumber, 
		pickup_streetname,
		pickup_cityname,
		pickup_latitude,
		pickup_longitude,
		dest_streetnumber, 
		dest_streetname,
		dest_cityname,
		fleet,
		driverid,
		pickup_dispatchzone,
		remark1,
		remark2,
		remark3,
		remark4,
		orderid) in info:
	    res_dic["pickup_streetnumber"] = pickup_streetnumber 
	    res_dic["pickup_streetname"] =  pickup_streetname
	    res_dic["pickup_cityname"] = pcityname
	    res_dic["pickup_latitude"] =  pickup_latitude
	    res_dic["pickup_longitude"] = pickup_longitude
	    res_dic["dest_streetnumber"]  = dest_streetnumber 
	    res_dic["dest_streetname"] = dest_streetname
	    res_dic["dest_cityname"]  = dcityname
	    res_dic["pickup_zone"]  = pickup_dispatchzone
            res_dic["fleet"] = fleet
            res_dic["driverid"] = driverid
	    res_dic["remarks"] = remark1 + ' ' + remark2 + ' ' + remark3 + ' ' + remark4
	    res_dic["orderid"] = orderid
    except Exception as e:
	print 'ERROR accessing database for fare number ', farenum
        res_dic = {}
	return res_dic
	
    try:
        print 'retrieve_data_for_ibs_mobileorder ---> orderid=' , orderid
	if orderid==0:
	    guidstr = str(uuid.uuid4())
            if len(guidstr) != 36:
	        print 'WARNING: ', guidstr, 'has length ' , len(guidstr)
                guid = format_field.format_field(guidstr, 36, True)
                res_dic["guid"] = guid
    except Exception as e:
	guidstr=''

    return res_dic

def updateEntryInIBS(fare, fare_type, farenum):
    orderid=-1
    sys.stdout.write("%s: entering %s\n" % (datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT), __name__))
    res_dic = createJSON(fare, fare_type, farenum)
    try:
	sql_stat = '''
		UPDATE  mobileorder
		SET 
		pickupZone = \'%s\',
		pickupAddressNo = \'%s\', 
		pickupAddressName = \'%s\',
		pickupAddressCity = \'%s\',
		dropoffAddressNo = \'%s\', 
		dropoffAddressName = \'%s\', 
		dropoffAddressCity = \'%s\', 
		FleetNum = \'%s\',
		Remarks = \'%s\',
		pickupLat = %f,
		pickupLon = %f
		WHERE ID=%u;
	''' % ( 
		res_dic["pickup_zone"] ,
                res_dic["pickup_streetnumber"] , 
	        res_dic["pickup_streetname"] ,
	        res_dic["pickup_cityname"] ,
	        res_dic["dest_streetnumber"],   
	        res_dic["dest_streetname"] ,
	        res_dic["dest_cityname"]  ,
                res_dic["fleet"] ,
                res_dic["remarks"], 
	        float(res_dic["pickup_latitude"]) ,
	        float(res_dic["pickup_longitude"]) , 
	        res_dic["orderid"] 
		)
	print 'updateEntryInIBS ---> Execute ...', sql_stat

	db = smalldb.DB(Config.DB_HOST, Config.DB_USER, Config.DB_PASSWORD, 'ibs')
        db.connect()

        info = db.insert_update(sql_stat)
	if info == 1 :
	    print ' SUCCESS ...'
	else:
	    print ' FAILED to update entry in mobileorder in IBS Database'
    except Exception as e:
    	print 'Exception ... ', e 
    	pass

    db.close()


def createJSON(fare, fare_type, farenum=0):
    dic={}
    try:
        sys.stdout.write("%s: entering createJSON \n" % (datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT)))

	dic["pickup_zone"]  = fare.pick_zone
        dic["pickup_streetnumber"] = fare.pick_street_no
	dic["pickup_streetname"] = fare.pick_street_name
	dic["pickup_cityname"]  = fare.pick_city
	dic["dest_streetnumber"]  = fare.dest_street_no 
	dic["dest_streetname"] = fare.dest_street_name
	dic["dest_cityname"]   = fare.dest_city
        dic["fleet"] = fare.fleet_number
        dic["remarks"]  = fare.remarks1 + ' ' + fare.remarks2 + ' ' + fare.remarks3 + ' ' + fare.remarks4
	dic["pickup_latitude"] = fare.pick_y
	dic["pickup_longitude"] = fare.pick_x

	dic["sequence_number"] = fare.SeqNo
	dic["phone"] = fare.phone
	dic["account_number"] = fare.acctno
	dic["resv_date"] = fare.resv_date
	dic["resv_time"] = fare.resv_time
	dic["passengers"] = fare.num_of_passengers

	# farenum =0 ==> create fare  ==> create a GUID
	if farenum == 0:
	    guidstr = str(uuid.uuid4())
            if len(guidstr) != 36:
                print 'WARNING: ', guidstr, 'has length ' , len(guidstr)
                guid = format_field.format_field(guidstr, 36, True)
                dic["guid"] = guid
	    else:
                dic["guid"] = guidstr
	else:
	    orderid=-1
	    # Need order id from the DB
	    if fare_type == 'immediate':
                sql_stat = 'SELECT  IBSOrderID as ID FROM farefl  WHERE FareNumber = \'%s\' ' % (farenum)
	    else:
                sql_stat = 'SELECT  IBSOrderID as ID FROM futfarefl  WHERE FareNumber = \'%s\' ' % (farenum)

    	    db = smalldb.DB(Config.DB_HOST, Config.DB_USER, Config.DB_PASSWORD, 'CabmateRepo')
            db.connect()
            info = db.fetch_many(sql_stat)
	    if info:
	        for (ID, ) in info:
	            orderid = ID
	            dic["orderid"] = ID
                sys.stdout.write("%s: %s orderid %u in IBS \n" % (datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT), __name__, orderid))

    except Exception as e:
        sys.stdout.write("%s: createJSON exception %s \n" % (datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT), e ))
	pass

    return dic

def createEntryInIBS(fare, fare_type):
    orderid=-1
    sys.stdout.write("%s: entering %s\n" % (datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT), __name__))
    res_dic = createJSON(fare, fare_type)
    try:
	db = smalldb.DB(Config.DB_HOST, Config.DB_USER, Config.DB_PASSWORD, 'ibs')
        db.connect()
	sql_stat = '''
		INSERT INTO mobileorder
		(
		pickupZone,
		pickupAddressNo, 
		pickupAddressName,
		pickupAddressCity,
		dropoffAddressNo, 
		dropoffAddressName, 
		dropoffAddressCity, 
		FleetNum,
		Remarks,
		RowGuid,
		pickupLat,
		pickupLon
		)
		VALUES (
		\'%s\',
		\'%s\',
		\'%s\',
		\'%s\',
		\'%s\',
		\'%s\',
		\'%s\',
		\'%s\',
		\'%s\',
		\'%s\',
		%f,
		%f
		);
	    ''' % ( res_dic["pickup_zone"] ,
                res_dic["pickup_streetnumber"] , 
	        res_dic["pickup_streetname"] ,
	        res_dic["pickup_cityname"] ,
	        res_dic["dest_streetnumber"],   
	        res_dic["dest_streetname"] ,
	        res_dic["dest_cityname"]  ,
                res_dic["fleet"] ,
                res_dic["remarks"], 
	        res_dic["guid"],
	        float(res_dic["pickup_latitude"] ),
	        float(res_dic["pickup_longitude"] )
		)

        sys.stdout.write("%s: %s Execution ... %s\n" % (datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT), __name__, sql_stat))

        info = db.insert_update(sql_stat)
	if info == 1:
            sys.stdout.write("%s: %s SUCCESS creating entry in IBS \n" % (datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT), __name__))
	    if res_dic.has_key("guid"):
	        sql_stat = '''SELECT  ID FROM mobileorder WHERE RowGuid = \'%s\' ''' % (res_dic["guid"])
                info = db.fetch_many(sql_stat)
	        if info:
	            for (ID, ) in info:
	   	        orderid = ID
                sys.stdout.write("%s: %s SUCCESS created entry %u entry in IBS \n" % (datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT), __name__, orderid))
	else:
            sys.stdout.write("%s: %s FAILED to create entry in IBS \n" % (datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT), __name__))
    except Exception as e:
        sys.stdout.write("%s: createEntryInIBS exception %s \n" % (datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT), e ))
    	orderid=-1
    	pass

    db.close()
    return orderid


def saveFareToIBS(farenum, fare_type='immediate'):
    print 'saveFareToIBS'
    orderid=0
    found_orderid=False

    db1 = smalldb.DB(Config.DB_HOST, Config.DB_USER, Config.DB_PASSWORD, 'CabmateRepo')
    db1.connect()

    response = retrieve_data_for_ibs_mobileorder(db1, farenum)
    print response

    if response and response.has_key('orderid'):
        found_orderid=True
	orderid = response['orderid']

    db = smalldb.DB(Config.DB_HOST, Config.DB_USER, Config.DB_PASSWORD, 'ibs')
    db.connect()
    orderid = writetodb(db, response, orderid)
    db.close() 

    if orderid==-1:
	print ' ERROR on return from writetodb .....'
        db1.close() 
        return

    print ' from writetodb orderid = ', orderid

'''
    if response.has_key('orderid') and found_orderid == False:
    	# now update cabmaterepo with order id  
    	sql_stat = ' '
    	if fare_type == 'immediate':    
            sql_stat = ' UPDATE farefl SET IBSOrderId = %u  WHERE FareNumber = %s ' % (orderid, farenum)
    	if fare_type == 'future':    
            sql_stat = ' UPDATE futfarefl SET IBSOrderId = %u  WHERE FareNumber = %s ' % (orderid, farenum)
    	print sql_stat
    	info = db1.insert_update(sql_stat)
    	if info:
	    print ' SUCCESS ...'
            sql_stat = 'SELECT  IBSOrderID as found_orderid, FareNumber FROM farefl  WHERE FareNumber = \'%s\' ' % (farenum)
            info = db1.fetch_many(sql_stat)
            if info:
	   	for (found_orderid, FareNumber ) in info:
	            print ' FOUND ==> orderid, farenum ...', found_orderid, FareNumber  
            else:
	         print 'Could not find the entry in the CabmateRepo database'
        else:
	     print ' FAILED to create entry in farefl table in CabmateRepo'

    if found_orderid:
	print 'ORDER ID in DB ....'
    db1.close() 


'''

if __name__ == "__main__":
    print 'db fare test '

    farenum='201512030000276'
    saveFareToIBS(farenum, 'immediate')
