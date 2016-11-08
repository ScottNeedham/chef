BASE_URL = ''


class UrlRule(object):

    def __init__(self, url, func, methods='GET', base_url=BASE_URL):
    	if base_url != '':
        	self.url = '%s/%s' % (base_url, url)
        else:
			self.url = url
        self.url_short = url       
        self.func = func
        self.methods = methods
