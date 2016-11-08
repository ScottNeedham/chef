import config.cwebsconf as Config

file_name = "/data/itaxisrv_ip.fl"

def sanity_check():
    sanity_check_response_code = -1
    try:
        fp = open(file_name, "r")
        data = fp.read()
        if Config.BOTTLE_IP_FOR_BROADCAST in data:
            sanity_check_response_code = 0
        else:
            sanity_check_response_code = 1
        fp.close()
        return sanity_check_response_code  
    except Exception as e:
        print 'Exception ', str(e)
        sanity_check_response_code = -1
        return sanity_check_response_code  

if __name__ == "__main__":
    sanity_check = sanity_check() 
    if sanity_check in [1]:
        print 'CWEBS IP is not configured for BROADCAST' 
    elif sanity_check in [0]:
        print 'CWEBS IP might be configured for BROADCAST' 
    else:
        print 'Unable to determine if CWEBS IP configured for BROADCAST' 
