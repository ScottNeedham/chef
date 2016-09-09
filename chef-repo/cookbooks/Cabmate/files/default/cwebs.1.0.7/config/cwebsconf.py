BOTTLE_DEBUG = True
BOTTLE_AUTO_RELOAD = False
BOTTLE_SERVER = 'gevent'
SECRET = "I_L@VE_BEE!"
AP_SECRET = "T!?_asF"
SERVER_DATE_FORMAT = '%Y-%m-%d %H:%M:%S'
l303Site = False
fleet_qfolder = "/data/export/"
normtots = "/data/fzstatus/normtots.fl"
normstat = "/data/fzstatus/normstat.fl"
normtots_nofleet = "/data/zstatus/normtots.fl"
normstat_nofleet = "/data/zstatus/normstat.fl"
sys_filename = "/data/params/spparams.fl"
app_filename = "/data/params/apparams.fl"
chan_filename = "/data/params/chparams.fl"
DB_HOST = '127.0.0.1'
DB_USER = 'taxi'
DB_PASSWORD = 'taxi'
DB_NAME = 'cabmate'
SocketServerHost = '127.0.0.1'
SocketServerPort = 1232
DB_HOST_REPO = '127.0.0.1'
DB_USER_REPO = 'taxi'
DB_PASSWORD_REPO = 'taxi'
DB_NAME_REPO = 'CabmateRepo'

DB_HOST_IBS = '127.0.0.1'
DB_USER_IBS = 'taxi'
DB_PASSWORD_IBS = 'taxi'
DB_NAME_IBS = 'ibs'

DB_LOGS_HOST = '127.0.0.1'
DB_LOGS_USER = 'taxi'
DB_LOGS_PASSWORD = 'taxi'
DB_LOGS_NAME = 'Logs'

BOTTLE_IP_FOR_BROADCAST = '127.0.0.1' 
DateFormat_SaveOrder_Input = '%Y-%m-%d %H:%M'
LOG_DATETIME_FORMAT = '%Y-%m-%d %H:%M:%S'
validate_corporate_account_date = '%Y-%m-%d %H:%M'
lDisplayAttribute = True
EnableCancelByFareType = True
EnableIdentificationAsArcus = True
#lNewFareData= True
lNewFareData= False

PaymentTypeDic = {"cash": "CA",
                  "1": "CA",
                  "account": "AC",
                  "2": "AC",
                  "credit": "CC",
                  "3": "CC",
                  "crew": "CR",
                  "4": "CR",
                  "incar": "PI",
                  "6": "PI",
                  "cof": "CO",
                  "7": "CO",
                  "8": "AC",
                  "other": "OT"}

SocketTimeoutDic = {"default": 30}
QueueTimeoutDic =  { "default" : 3 }

lUseUTF8Encoder = True

lDebugTrace = True

lTryZoneItaxisrv = False

DefaultZoneTimeout = 30

lTryZoneTfc = False

CheckZoneCache = False
