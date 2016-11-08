import traceback
import config.cwebsconf as Config

def format_field(source='', sz=0, is_pad_right=True, is_numeric=False, to_upper=True, trim_it=False):
   
    try:
        res=source
        if is_numeric == False and type(res) not in [int, float] and to_upper:
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
            
        if type(res) in  [str, unicode] :
            if len(res) > sz:
                return res[:sz]
            else: 
                if not trim_it:
                    return res.ljust(sz, ' ') if is_pad_right else res.rjust(sz, ' ')
                else:
                    return res.ljust(sz, b'\x00')
        else:
            return str(res)
    except Exception as e:
        print ' Exception in format_field %s' % ( str(e) )            


def str_field(source=''):
    if type(source) not in [int, float]:
        if Config.lUseUTF8Encoder and isinstance(source, unicode):
            res = source.upper().encode('utf8')
        else:
            res = source.upper()
        return res
    return source


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
