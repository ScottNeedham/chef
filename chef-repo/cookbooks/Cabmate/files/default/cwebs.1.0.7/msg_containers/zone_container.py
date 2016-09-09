import os
import sys

import ..msgconf as msgconf


MAX_x_ENTRY_LEN = 10
MAX_Y_ENTRY_LEN = 10
MAX_FLEET_LEN = 5
SEQNO_LEN = 10

class ZoneContainer(dic):

	def __init__(self):

		self.error = True
        try:
        	self.msgId =  msgconf.MT_GET_ZONE_BY_LAT_LONG

                      

          	'''

          	struct	zonebyLatLongRequest
			{
				char	SeqNo[SEQNO_LEN];		// 10 bytes
				char	FleetNo[5];			// the fleet number 5 bytes
				char	X[10];				// Longitude
				char	Y[10];				// Latitude
			};


			struct	zonebyLatLongResponse
			{
				char	SeqNo[SEQNO_LEN];		// 10 bytes
				char	FleetNo[5];			// the fleet number 5 bytes
				char	X[10];				// Longitude
				char	Y[10];				// Latitude
				char	Zone[5];			// The associated zone
				char	LeadTime[4];			// The lead time
			};



			'''
            
            self.x.append(MAX_x_ENTRY_LEN*' ')
     		self.y.append(MAX_Y_ENTRY_LEN*' ')
     		self.fleet.append(MAX_FLEET_LEN * ' ')

            self.populateObject(dic)


            self.error = False
        except Exception as e:
            self.error = True

	def __str__(self):
		pass



    def getError(self):
        return self.error
		pass



	def sendMsg(self):
		pass


	def convertToTuple(self, dic=None):
		values = (
			self.msgId
			
			)

		return values


	def populateObject(self, dic):

		try:


		except Exception as e:
          	sys.stdout.write("%s: exception %s\n" % (datetime.datetime.strftime(datetime.datetime.now(),  '%Y-%m-%d %H:%M:%S'), str(e) ))            
            self.error = True			
			pass
			


