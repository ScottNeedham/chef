import traceback
import config.cwebsconf as Config

def format_field(source='', sz=0, is_pad_right=True, is_numeric=False):
   
    try:
        res=source
        if is_numeric == False and type(res) not in [int, float]:
            try:
                if Config.lUseUTF8Encoder and isinstance(source, unicode):
                    #print 'encoded source ', source.encode('utf8')

                    res = source.upper().encode('utf8')
                else:
                    #print 'source ', source     
                    res = source.upper()
            except Exception as e:
                print ' Exception in format_field.upper exc=%s src=%s ' % ( str(e)) 
                traceback.print_exc()
                res=source 
                 
        elif Config.lUseUTF8Encoder and isinstance(source, unicode):  
            res = source.encode('utf8')
       
        if type(res) == int :       
            res = str(res)
            
        if type(res) == str :
            if len(res) > sz:
                return res[:sz]
            else: 
                return res.ljust(sz, ' ') if is_pad_right else res.rjust(sz, ' ')
        else:
            return str(res)
    except Exception as e:
        print ' Exception in format_field %s' % ( str(e) )            


def str_field(source=''):
    if Config.lUseUTF8Encoder and isinstance(source, unicode):
        res = source.upper().encode('utf8')
    else:
        res = source.upper()
    return res


def is_numeric(data):
    try:
        if type (data) == int:
            return True
        if type(data) in [ str, unicode] :
            i = int(data)
            return True
    
    except ValueError as e:
        return False

    except Exception as e:
        print ' Exception in is_numeric  %s' % ( str(e) )              
        return False
     
    return False      