import time

import config.cwebsconf as Config

try:
    
    import MySQLdb as mdb   
except ImportError:
    import mysql.connector as mdb

 

class DB:

    def __init__(self, DB_HOST, DB_USER, DB_PASSWORD, DB_NAME):
        self.DB_HOST = DB_HOST
        self.DB_USER = DB_USER
        self.DB_PASSWORD = DB_PASSWORD
        self.DB_NAME = DB_NAME
        self.db_session = None

    def connect(self):
        try:
            self.db_session = mdb.connect(host=self.DB_HOST, db=self.DB_NAME, user=self.DB_USER, passwd=self.DB_PASSWORD)
        except mdb.Error as e:
            raise e

    def fetch_many(self, sql_statement):
        results = []
	try:
	    self.db_session.commit()
            cursor = self.db_session.cursor()
            cursor.execute(sql_statement);
        except mdb.Error as e:
            self.connect()
	    self.db_session.commit()
            cursor = self.db_session.cursor()
            cursor.execute(sql_statement);
	for res in cursor:
	    results.append(res)            
        cursor.close()
	return results

    def sp_execute(self, proc_name, proc_params):
    ###############################################
    ## to be tested... 
    ###############################################
        results = []
	try:
	    self.db_session.commit()
            cursor = self.db_session.cursor()
            cursor.callproc(proc_name, proc_params)
        except mdb.Error as e:
            self.connect()
	    self.db_session.commit()
            cursor = self.db_session.cursor()
            cursor.callproc(proc_name, proc_params)
        for res in cursor:
            results.append(res)
	    print res
        return results	   

    def insert_update(self, sql_statement):            
        try:
            self.db_session.commit()
            cursor = self.db_session.cursor()
            cursor.execute(sql_statement)
        except mdb.Error as e:
            self.connect()
            self.db_session.commit()
            cursor = self.db_session.cursor()
            cursor.execute(sql_statement)
        result = cursor.rowcount
        self.db_session.commit()
        cursor.close()
        return result

    def close(self):
        try:
            self.db_session.close()
        except Exception as e:
            print 'exception %s' % (str(e))
        return

      	
if __name__ == "__main__":
    db_inst = DB('127.0.0.1', 'root', 'mkc_ser', 'cabmate')
    db_inst.connect()
    db_inst.sp_execute('ValidateAcctPrompts', ('ROBF1', 0, "Prompt1", "Prompt2", "Prompt3", "Prompt4", "Prompt5", "Prompt6", "Prompt7", "Prompt8"))
#    info = db_inst.fetch_many(sql_statement)
#    for (Fleetnumber, Fleetname, MdtGroup, ZoneSet) in info:
#        print Fleetnumber, Fleetname, MdtGroup, ZoneSet
    
    
