#ifndef _ZQQLIB_H_
#define _ZQQLIB_H_

#define sNFleetStatus "/data/fzstatus/normstat.fl"
#define sNFleetStatusTots "/data/fzstatus/normtots.fl"
#define NUM_OF_STANDS_PER_RECORD (16)
#define NUM_MOD (65536)

typedef struct tStdStat { 
    int standnum; 
    int veh_size; 
    int fare_size; 
    int dest_size; 
} StdStat; 

typedef struct tQueTotals { 
    int taxi_queue; 
    int fare_queue; 
    int bid_queue; 
    int offer_queue; 
    int accept_queue; 
    int dest_queue; 
    int local_queue; 
    int pickup_queue; 
    int total_taxis; 
    int sfree_queue; 
    /* these 2 additional queues are not present */
    int cvd_queue; 
    int num_queue; 
} QueTotals; 

typedef struct tfarefileinfo {
        int    farenumber;
        int    lastbackup;
        int    lastfareofday;
        int    firstfareofday;
        int    oncearound;
        int    chargeauthor;
        int    last_download;
        int    last_fare_in_aux;
        int    firstfareofyday;
        char   spare[4220];
} farefileinfo;

#endif
