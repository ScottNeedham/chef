#include <Python.h>
#include "zqqlib.h"
/*
 * 
 * Author: Eugene Kadantsev (ekadantsev@mobile-knowledge.com)
 * x86_64 architecture is assumed, for 32 ints have to be changed to long
 *
 #define MAX_STRING_LENGTH (100)
char sNFleetStatus[MAX_STRING_LENGTH] = "/data/fzstatus/normstat.fl\0"; 
char sNFleetStatusTots[MAX_STRING_LENGTH] = "/data/fzstatus/normtots.fl\0"; 
 *
 */

static PyObject *pGetFleetNumber(PyObject *self, PyObject *args)
{
    int i, itmp;
    FILE *fptr_sNFleetStatus = NULL;
    StdStat *tmpstdptr = NULL;
    int FleetNumber = 0;
    /* printf("...entering pGetFleetNumber...\n"); */ 
    if(!PyArg_ParseTuple(args, "")) {
       PyErr_SetString(PyExc_TypeError, "function does not accept args"); 
       return NULL;   
    }
    fptr_sNFleetStatus = fopen(sNFleetStatus, "r");
    if (!fptr_sNFleetStatus) { 
       PyErr_SetString(PyExc_IOError, "can not open normstat"); 
       return NULL;   
    }    
    tmpstdptr = (StdStat *) malloc(NUM_OF_STANDS_PER_RECORD*sizeof(StdStat));
    if (tmpstdptr == NULL) return PyErr_NoMemory();
    fread(tmpstdptr, sizeof(StdStat), NUM_OF_STANDS_PER_RECORD, fptr_sNFleetStatus);
    for(i = 0; i < NUM_OF_STANDS_PER_RECORD; i++)
        if(tmpstdptr[i].veh_size > 0) FleetNumber++;
    free(tmpstdptr);
    fclose(fptr_sNFleetStatus);
    /* printf("...exiting pGetFleetNumber...\n"); */  
    return Py_BuildValue("i", FleetNumber);
}

/* this returns Fleet info
   per each fleet, number of zones and fleet_id 
   (known as fleetNumber in cabmate...) */ 
static PyObject *pGetFleetInfo(PyObject *self, PyObject *args)
{
    int i, FleetNumber, zones, fleet_id;
    FILE *fptr_sNFleetStatus = NULL;
    StdStat *tmpstdptr = NULL;
    PyObject* FleetInfo; 
    if (!PyArg_ParseTuple(args, "")) { 
       PyErr_SetString(PyExc_TypeError, "function does not accept args"); 
       return NULL;   
    }     	  
    fptr_sNFleetStatus = fopen(sNFleetStatus, "r");
    if (!fptr_sNFleetStatus) { 
       PyErr_SetString(PyExc_IOError, "can not open normstat"); 
       return NULL;   
    }    
    tmpstdptr = (StdStat *) malloc(NUM_OF_STANDS_PER_RECORD*sizeof(StdStat));
    if (!tmpstdptr) return PyErr_NoMemory();     
    fread(tmpstdptr, sizeof(StdStat), NUM_OF_STANDS_PER_RECORD, fptr_sNFleetStatus);

    FleetNumber = 0; 
    for(i = 0; i < NUM_OF_STANDS_PER_RECORD; i++) 
        if(tmpstdptr[i].veh_size > 0) FleetNumber++;
       
    FleetInfo = PyList_New(FleetNumber); 
    FleetNumber = 0; 
    for(i = 0; i < NUM_OF_STANDS_PER_RECORD; i++) {
        if(tmpstdptr[i].veh_size > 0) {
	   /* number of zones */ 
           zones = tmpstdptr[i].standnum;  
	   /* fleet number */ 
           fleet_id = tmpstdptr[i].veh_size % NUM_MOD;  
	   PyList_SetItem(FleetInfo, FleetNumber, Py_BuildValue("(i,i,i)", i, zones, fleet_id));  
	   FleetNumber++;   
        }   
    } 
    free(tmpstdptr);
    fclose(fptr_sNFleetStatus);
    return FleetInfo;
}  

static PyObject *pGetFleetZoneStatus(PyObject *self, PyObject *args)
{ 
    int i, j, FleetNumber, FleetZone;
    int tz1, tz2; 
    int index, zones, vehicles, fares, dests;  
    int mdt_by_fleet_order[NUM_OF_STANDS_PER_RECORD];
    FILE *fptr_sNFleetStatus = NULL;
    StdStat *tmpstdptr = NULL;
    PyObject* ZoneStatusInfo;
    printf("entering C API\n");  
    if (!PyArg_ParseTuple(args, "")) { 
       PyErr_SetString(PyExc_TypeError, "function does not accept args"); 
       return NULL;   
    }     	  
    
    fptr_sNFleetStatus = fopen(sNFleetStatus, "r");
    if (!fptr_sNFleetStatus) { 
       PyErr_SetString(PyExc_IOError, "can not open normstat"); 
       return NULL;   
    }    
    for(i = 0; i < NUM_OF_STANDS_PER_RECORD; i++) mdt_by_fleet_order[i] = 0;
    tmpstdptr = (StdStat *) malloc(NUM_OF_STANDS_PER_RECORD*sizeof(StdStat));
    if (tmpstdptr == NULL) return PyErr_NoMemory();
    fread(tmpstdptr, sizeof(StdStat), NUM_OF_STANDS_PER_RECORD, fptr_sNFleetStatus);
    FleetNumber = 0; 
    tz2 = 0; 
    for(i = 0; i < NUM_OF_STANDS_PER_RECORD; i++) {
        if(i == 0) tz1 = tmpstdptr[i].standnum; 
        printf("%4d %4d %4d\n", i, tmpstdptr[i].standnum, tmpstdptr[i].veh_size % NUM_MOD);
        if(tmpstdptr[i].veh_size > 0) { 
            FleetNumber++;
	    mdt_by_fleet_order[FleetNumber] = i;
            if (tmpstdptr[i].standnum > tz2) tz2 = tmpstdptr[i].standnum; 
        }
    }
    free(tmpstdptr);
    /*  
    if ((tz1 != tz2) || (tz1 < 1) || (tz2 < 1)) { 
        PyErr_SetString(PyExc_TypeError, "can not verify number of zones");       
        return NULL;
    } */ 
    /* we will just go with tz2 for number of zones 
       FleetNumber for a number of fleets */ 
    /* printf("tz2=%d\n", tz2); */  
    tmpstdptr = (StdStat *) malloc((int)(NUM_OF_STANDS_PER_RECORD)*tz2*sizeof(StdStat));
    if (tmpstdptr == NULL) return PyErr_NoMemory();
    fread(tmpstdptr, sizeof(StdStat), (int)(NUM_OF_STANDS_PER_RECORD)*tz2, fptr_sNFleetStatus);
    FleetZone = 0; 
    ZoneStatusInfo = PyList_New(FleetNumber*tz2); 
    for(i = 0; i < tz2; i++) {
       for(j = 1; j <= FleetNumber; j++) {
          index = i*(int)(NUM_OF_STANDS_PER_RECORD) + mdt_by_fleet_order[j]; 
          zones = tmpstdptr[index].standnum;
          vehicles = tmpstdptr[index].veh_size % NUM_MOD; 
          fares = tmpstdptr[index].fare_size % NUM_MOD; 
          dests = tmpstdptr[index].dest_size % NUM_MOD;
          PyList_SetItem(ZoneStatusInfo, FleetZone, 
	      Py_BuildValue("(i,i,i,i,i)", mdt_by_fleet_order[j], zones, vehicles, fares, dests));   
          FleetZone++; 
       } 
    }
    free(tmpstdptr); 
    fclose(fptr_sNFleetStatus);
    printf("exiting C API\n"); 
    return ZoneStatusInfo;
}

static PyObject *pGetFleetZoneTotals(PyObject *self, PyObject *args)
{ 
    int i, j, FleetNumber, FleetZone;
    int tz1, tz2;    
    FILE *fptr_sNFleetTotals = NULL;
    QueTotals *tmpqptr = NULL;
    PyObject* ZoneTotalsInfo; 
    printf("entering C API\n"); 
    if (!PyArg_ParseTuple(args, "")) { 
       PyErr_SetString(PyExc_TypeError, "function does not accept args"); 
       return NULL;   
    }   
 
    fptr_sNFleetTotals = fopen(sNFleetStatusTots, "r");
    if (!fptr_sNFleetTotals) { 
       PyErr_SetString(PyExc_IOError, "can not open normtots"); 
       return NULL;   
    }    
    
    tmpqptr = (QueTotals *) malloc(NUM_OF_STANDS_PER_RECORD*sizeof(QueTotals));
    if (tmpqptr == NULL) return PyErr_NoMemory();
    fread(tmpqptr, sizeof(QueTotals), NUM_OF_STANDS_PER_RECORD, fptr_sNFleetTotals);
    ZoneTotalsInfo = PyList_New(NUM_OF_STANDS_PER_RECORD);
    /*
    FleetInfo = PyList_New(FleetNumber); 
    FleetNumber = 0; 
    for(i = 0; i < NUM_OF_STANDS_PER_RECORD; i++) {
        if(tmpstdptr[i].veh_size > 0) {
           zones = tmpstdptr[i].standnum; 
           fleet_id = tmpstdptr[i].veh_size % NUM_MOD;  
	   PyList_SetItem(FleetInfo, FleetNumber, Py_BuildValue("(i,i,i)", i, zones, fleet_id));  
	   FleetNumber++;   
        }   
    } 
    free(tmpstdptr);
    fclose(fptr_sNFleetStatus);
    */   
    for(i = 0; i < NUM_OF_STANDS_PER_RECORD; i++) {
      PyList_SetItem(ZoneTotalsInfo,i, 
         Py_BuildValue("(i,i,i,i,i,i,i,i,i,i,i,i,i)", i,
              tmpqptr[i].taxi_queue, 
              tmpqptr[i].fare_queue,  
	      tmpqptr[i].bid_queue,
	      tmpqptr[i].offer_queue, 
              tmpqptr[i].accept_queue,
              tmpqptr[i].dest_queue, 
              tmpqptr[i].local_queue, 
              tmpqptr[i].pickup_queue,
              tmpqptr[i].total_taxis,  
              tmpqptr[i].sfree_queue, 
	      tmpqptr[i].cvd_queue, 
	      tmpqptr[i].num_queue)); 
 
      printf("%4d %4d %4d %4d %4d %4d %4d %4d %4d %4d %4d %4d %4d\n", i, 
              tmpqptr[i].taxi_queue, 
              tmpqptr[i].fare_queue,  
	      tmpqptr[i].bid_queue,
	      tmpqptr[i].offer_queue, 
              tmpqptr[i].accept_queue,
              tmpqptr[i].dest_queue, 
              tmpqptr[i].local_queue, 
              tmpqptr[i].pickup_queue,
              tmpqptr[i].total_taxis,  
              tmpqptr[i].sfree_queue, 
	      tmpqptr[i].cvd_queue, 
	      tmpqptr[i].num_queue);  

    }
    free(tmpqptr);
    printf("exiting C API\n"); 
    return ZoneTotalsInfo;
}

static PyMethodDef zqqlib_methods[] = {
    {"get_fleet_number", pGetFleetNumber, METH_VARARGS, "Gets fleet number."},
    {"get_fleet_info", pGetFleetInfo, METH_VARARGS, "Gets fleet info."}, 
    {"get_fleet_zone_status", pGetFleetZoneStatus, METH_VARARGS, "Gets fleet zone status."},
    {"get_fleet_zone_totals", pGetFleetZoneTotals, METH_VARARGS, "Gets fleet zone totals."}, 
    {NULL, NULL, 0, NULL}     /* Sentinel */
};

PyMODINIT_FUNC initzqqlib(void) 
{
    (void) Py_InitModule("zqqlib", zqqlib_methods);
}



