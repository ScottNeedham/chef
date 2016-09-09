import hashlib
import hmac
import base64
# 
# header environment dic goes in here...
#
def get_hmac_from_header(header, secret, lIncludeMD5=False):
    hmac_dic = {} 
    hmac_dic['CLIENT_HMAC'] = ''
    hmac_dic['CLIENT_METHOD'] = ''
    hmac_dic['CLIENT_MD5'] = '=='
    hmac_dic['CLIENT_PATH'] = ''
    hmac_dic['CLIENT_DATE'] = ''
    hmac_dic['CLIENT_NAME'] = ''
    if header.has_key('HTTP_AUTHORIZATION'):
        #HMAC Hashed Message Authentication Code
        if len(header['HTTP_AUTHORIZATION'].split(':')) == 2:
	    hmac_dic['CLIENT_NAME'] = header['HTTP_AUTHORIZATION'].split(':')[0]
            hmac_dic['CLIENT_HMAC'] = header['HTTP_AUTHORIZATION'].split(':')[1]
    if header.has_key('REQUEST_METHOD'): 
        hmac_dic['CLIENT_METHOD'] = header['REQUEST_METHOD']
    if header.has_key('HTTP_CONTENT_MD5'):
	hmac_dic['CLIENT_MD5'] = header['HTTP_CONTENT_MD5']
    if header.has_key('PATH_INFO'):
        hmac_dic['CLIENT_PATH'] = header['PATH_INFO']
    if header.has_key('HTTP_DATE'):
        #Tue, 15 Nov 1994 08:12:31 GMT
        hmac_dic['CLIENT_DATE']	 = header['HTTP_DATE']

    str_to_hash = hmac_dic['CLIENT_METHOD'] 
    if lIncludeMD5:
        str_to_hash = str_to_hash + hmac_dic['CLIENT_MD5'][:-2] 
    str_to_hash = str_to_hash + hmac_dic['CLIENT_PATH'] 
    str_to_hash = str_to_hash + hmac_dic['CLIENT_DATE']
    hmacvar = hmac.new(secret, str_to_hash, hashlib.sha1).digest()
    print 'string to hash ', str_to_hash
    print 'hex digest ', hmac.new(secret, str_to_hash, hashlib.sha1).hexdigest()
    return (str_to_hash.strip(), base64.b64encode(hmacvar), hmac_dic['CLIENT_HMAC'], hmac_dic['CLIENT_MD5'][:-2], hmac_dic['CLIENT_NAME'])
