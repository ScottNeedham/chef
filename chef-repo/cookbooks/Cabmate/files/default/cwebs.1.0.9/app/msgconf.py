# Cabmate defs
MT_SUSP_DRIVER = 600
MT_REIN_DRIVER = 601
MT_CODED_MSG_FROM_SUPERVISOR = 634

MT_UPDATE_DRIVER_PARAMS_FILE = 1034
MT_DELDRIVERREC = 392
MT_MODDRIVERINFO = 284
MT_ADDDRIVERREC = 465
MT_NEW_DRIVER = 391
MT_MODFLEETINFO = 285
MT_VERIFY_ID = 350
MT_GPS_STATUS = 810

MT_DELETE_TAXI = 376
MT_ADD_TAXI = 395
MT_MODTAXINFO = 535
MT_EXTENDED_TAXI_INFO = 1059
MT_SUSP_TAXI = 393
MT_REINST_TAXI = 334

MT_EMERG_CLR = 290
MT_EVENT_MSG = 536
MT_OP_ERR = 538
MT_ADD_QENTRY = 539
MT_YES_ENTRY = 541
MT_NO_ENTRY = 542
MT_CLR_ENTRY = 543
MT_KEEP_ENTRY = 545


DUMP_QUEUES = 39
MT_REMOVE_QENTRY = 544
MT_GET_QENTRY = 546
MT_QUE_HELLO = 547
MT_QUE_GOODBYE = 548
MT_CURRENT_POS = 463

MT_CNCL_QENTRY = 549

MT_YES_ENTRY_STR = "YesEntry"
MT_NO_ENTRY_STR = "NoEntry"
MT_CLR_ENTRY_STR = "ClearEntry"
MT_KEEP_ENTRY_STR = "KeepEntry"
DUMP_QUEUES_STR = "DumpQueues"
MT_CURRENT_POS_STR = "CurrentPos"
MT_ADD_QENTRY_STR = "AddEntry"
MT_EMERG_CLR_STR = "EmergencyClear"
CLEAR_EMERGENCY_EVENT_STR = "ClearEmergencyEvent"


EV_ENTER_FARE = 1 # used in itcli fare creation
EV_REDISPATCH = 4
EV_CNCL_CALL = 28
EV_CB_REQ = 65
EV_EMERG = 18
EV_EMERG_CLR = 19
EV_VEHICLE_MSG = 70
EV_ZONE_MSG = 71
EV_FLEET_MSG = 72  
EV_XNUMREQ	= 78
EV_FLEET1_MSG = 98
EV_FLEET3_MSG = 99
EV_FLEET5_MSG = 100
EV_FLEET2_MSG = 141
EV_FLEET4_MSG = 142

# Local defs
VEHICLE_MSG = 1
FLEET_MSG = 2
DRIVER_MSG = 3


MT_CLIENT_HELLO	= 795
MT_CLIENT_KILL	= 796

MT_CLIENT_HELLO_STR = "ClientHello"
LM_CPU_SPEED = 7
MT_GE_CALL = 389 #  immediate new fare to TFC
MT_MODFAREINFO =  555 #  immediate Mod fare to TFC, Received from DM
MT_ENTER_CALL = 273
MT_HAILED_TRIP = 1037
MT_NEWFARE = 431 # Future new fare to TIME MGR
MT_CANCEL_TIME = 436 # CANCEL sent to TMIMGR
MT_UPD_FARE = 437 # Future Mod Fare to TIME MGR
MT_GET_ZONE_BY_LAT_LONG = 1068

MT_PAYMENT_TYPE_CHANGE = 1090
MT_UPDATE_FARE_AMOUNT = 1092
MT_MODADDRESSFARE = 1117

MT_VEH_MSG = 550

MT_TRIP_UPDATE_ADDRESS = 1128

TC_UN_USED 	= 90000
'''
/* size is 192 bytes (128 + 64 ) this size is the record size for
queue_msg.fl */
struct g_event_msg 
{
	long event_no;   == EV_VEHICLE_MSG, EV_ZONE_MSG, EV_FLEET_MSG 
					== EV_FLEET1_MSG, EV_FLEET2_MSG, EV_FLEET3_MSG, EV_FLEET4_MSG, EV_FLEET5_MSG 			
	long time;				/* time event happened at */
	long fare;				/* fare number if required */
	long other_data;		/* other data if required */
	long qual;              /* qualifier field used by q_proc */
	long fstatus;
	long meter_amount;		/* from longpad[2] */
	long longpad;			/* padding */
	float x ;				/* long xxx.xxxxxx */
	float y ; 				/* lat yyy.yyyyyy */MT_GE	short zone;				/* zone number if required */
	short taxi;				/* taxi number if required */
	short resp_uid;			/* who to send any response to */
	short attribute;        /* used to store parcel/region */
	short qid;              /* uid of who get q mesg */
	short fleet;			/* for fleet access converted from shortpad[0] */
	short redisp_taxi;		/* for now school runs taxi number */
	char merchant_group;	/* convert spare[0] to this for cc_proc */
	char num_sats ;			/* number of satellites 0-4 */
	char mesg[4][33];		/* stores, msgs, forms, xnumreq ...*/
	char rel_queue ; 		/* relative queue, bad comm... */
	unsigned char statusbits;
};


'''

resource_msg = {"suspend": MT_SUSP_DRIVER, "reinstate": MT_REIN_DRIVER}
vehicle_msg = {"add": MT_ADD_TAXI, "update": MT_MODTAXINFO, "modify": MT_MODTAXINFO}

default_susp_duration = 1
ROUT_PRI = 13
#  Unique id numbers for each running process.  These unique numbers are
#  necessary to address each process.  Each time a message is sent from
#  a process to another process, sending process must know the id number
#  of the receiving process.

MT_UID         =  0   # Message task controller
BOSS           =  1   # Boss process
DM             =  2   # dispatch manager
AC             =  3   # again cancel fare controller
Q_PROC         =  4   # queued requests process
TFC            =  5   # taxi fare controller
IVRSRV         =  5   # unix-based ivr callout server
TK_PROC        =  6   # TK_PROC
ITAXISRV       =  7   # ePiNGTaxi srv for internet was UNUSED
TIMEMGR        =  8   # regular runs manager
BI             =  9   # base unit input manager
BO             = 10   # base unit output manager
ITAXISRV1      = 11   # April 5, 2013 RL a separate itaxi server
ITAXISRV2      = 12   # August 27, 2013 RL a separate itaxi server
ES             = 14   # computer send manager
AUTO_CALLTAKER = 16   # This messaging queue is used by
DEBUG_UID      = 19   # used by sysmsg tool
DRIVERSRV      = 22   # for driversrv and windows
IVRDRV         = 22   # Unix-based IVR Callout Driver
IVRCLI         = 23   # ivrcli
DLOADCLI       = 24   # dloadcli
DLOADCCREP     = 25   # dloadccrep
MYSRV          = 26   # mysrv
MAPCLI         = 27   # mapcli
TSSMAP_PROC    = 28   # Tracking Station Server Map_proc
DLOADUPDCLI    = 29   # dloadupdcli for updating the credit card transactions
BODESRV        = 30   # BODE interface server
WINDOWSERVER   = 31   # to serve window spawn requests
MAP_PROC       = 32   # Map proc process
CABMATESRV     = 33   # Cabmate Database Server
MAPDIRSRV      = 34   # MapPoint Direction Server
CC_PROC        = 35   # cc_proc credit card
ER             = 37   # cs/er
CTADDR         = 38   # ctaddr
ADMAN          = 39   # street directory manager
MKC_LOG        = 40   # mkc logging process
AOE_CALLOUT    = 41   # AOE callout feature
AUTO_CALLBACK  = 42   # APEX Auto callback feature
CLISRV         = 43   # Client server parent
ITAXISIM       = 44   # socket based itaxisim simulator
PROG_ACCT_UID  = 46   # progress account server
REPOEVENTFEED  = 46   # Repo event feed Added by KF July 2014
LOGTODB        = 47   # Saves .log data of BI/BO to Cache DB
CABPRNSRV      = 48   # cabprn to print fares instead of acmgr
SRESRV         = 49   # SRE Server
DLOADVEH       = 50   # dloadveh
DLOADVEHSIM    = 51   # dloadvehsim
DLOADSRV       = 52   # dloadsrv
SMSSRV         = 53   # smssrv
SMSMYSRV       = 54   # smsmysrv May 24, 2011 RL
DRVSMSSRV      = 55   # drvsmssrv June 7, 2011 RL
VERIFEYESRV    = 56   # verifeyesrv Feb 13, 2012 RL
MYFAREOFFERTRACKINGSRV = 57  # myFareOfferTracking May 28, 2012 RL
MYDRIVERSHIFT  = 58   # September 24, 2012 RL
MYCABMATESRV   = 59   # October 10, 2012 RL
BSUPROTO       = 65   # bsuproto channel  0
BSUPROTO1      = 66   # bsuproto channel  1
BSUPROTO2      = 67   # bsuproto channel  2
BSUPROTO3      = 68   # bsuproto channel  3
BSUPROTO4      = 69   # bsuproto channel  4
BSUPROTO5      = 70   # bsuproto channel  5
BSUPROTO6      = 71   # bsuproto channel  6
BSUPROTO7      = 72   # bsuproto channel  7
BSUPROTO8      = 73   # bsuproto channel  8
BSUPROTO9      = 74   # bsuproto channel  9
BSUPROTO10     = 75   # bsuproto channel 10
BSUPROTO11     = 76   # bsuproto channel 11
BSUPROTO12     = 77   # bsuproto channel 12
BSUPROTO13     = 78   # bsuproto channel 13
BSUPROTO14     = 79   # bsuproto channel 14
BSUPROTO15     = 80   # bsuproto channel 15
CWEBS          = 99   # CWEBS
MYCABMATEFARESRV = 104
ARCUSBACKEND   = 499  # Arcus Backend Test only
PROTO0         = 400  # proto0
PROTO1         = 401  # proto1
PROTOALL       = 409  # for both proto0 & 1 in scap bsu_msg


MsgQPeerDict = {
	ARCUSBACKEND : 'ARCUSBACKEND',
	TFC : 'TFC',
	DM : 'DM',
	CWEBS : 'CWEBS',
	ITAXISRV : 'ITAXISRV',
	Q_PROC : 'Q_PROC',
	CLISRV : '`CLISRV',
}

MsgEventDict = {
	
	MT_SUSP_DRIVER :  'MT_SUSP_DRIVER',
	MT_REIN_DRIVER : 'MT_REIN_DRIVER' ,
	MT_CODED_MSG_FROM_SUPERVISOR : 'MT_CODED_MSG_FROM_SUPERVISOR'  ,

	MT_UPDATE_DRIVER_PARAMS_FILE : 'MT_UPDATE_DRIVER_PARAMS_FILE' ,
	MT_DELDRIVERREC : 'MT_DELDRIVERREC' ,
	MT_MODDRIVERINFO : 'MT_MODDRIVERINFO',
	MT_ADDDRIVERREC : 'MT_ADDDRIVERREC' ,
	MT_NEW_DRIVER : 'MT_NEW_DRIVER' ,

	MT_VERIFY_ID : 'MT_VERIFY_ID' ,
	MT_GPS_STATUS : 'MT_GPS_STATUS' ,

	MT_DELETE_TAXI : 'MT_DELETE_TAXI' ,
	MT_ADD_TAXI : 'MT_ADD_TAXI' ,
	MT_MODTAXINFO : 'MT_MODTAXINFO' ,
	MT_EXTENDED_TAXI_INFO : 'MT_EXTENDED_TAXI_INFO' ,
	MT_SUSP_TAXI : 'MT_SUSP_TAXI' ,
	MT_REINST_TAXI : 'MT_REINST_TAXI' ,
	MT_EVENT_MSG : 'MT_EVENT_MSG' ,

	MT_MODFLEETINFO : 'MT_MODFLEETINFO_STR',

	MT_CLIENT_HELLO : "MT_CLIENT_HELLO_STR",

}

MAX_ZONES = 32
MAXVEHNUM = 32000

NO_DIRECTIONS = 100
#### Q Messaging constants ... ##
Q_TIMESLOT = .10