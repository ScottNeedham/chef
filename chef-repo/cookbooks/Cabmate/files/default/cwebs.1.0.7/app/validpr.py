import datetime
import config.cwebsconf as Config

def get_if_prompt_is_valid(is_good, nm, prompt_val="prompt"):
    print 'is_good', is_good, 'nm', nm, 'prompt_val', prompt_val
    l_prompt = False
    if is_good == 0:
        if nm == 'NUMBERS':
            print 'nm is NUMBERS'
	    try:
	        tmp = float(prompt_val)
                print 'conversion to float is success'
                l_prompt = True
                print 'l_prompt', l_prompt  
            except Exception as e:
                print 'exception' 
                l_prompt = False
                print 'l_prompt', l_prompt  
        elif nm  == 'DATE': 
            print 'nm is DATE' 
	    try:
                print 'converting to date ', prompt_val 
	        tmp = datetime.datetime.strptime(prompt_val, 
                    Config.validate_corporate_account_date) 
                print 'conversion to date is success'
		l_prompt = True
                print 'l_prompt', l_prompt
            except Exception as e:
                print 'exception'
	        l_prompt = False
                print 'l_prompt', l_prompt
        else:
            print 'nm is not NUMBERS or DATE'
	    l_prompt = False
    else:
        l_prompt = True
    return l_prompt 

if __name__ == "__main__":
    print get_if_prompt_is_valid(0, 'DATE', prompt_val="29/09")

