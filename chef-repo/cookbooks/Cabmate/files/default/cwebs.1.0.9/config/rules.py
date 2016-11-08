from base.url_rule import UrlRule

from app.controllers import get_cwebs_version

rules = []

#  url, name, func, methods=None, base_url=BASE_URL
rules = [
    UrlRule('version', 'get_app_version', get_cwebs_version, methods=['GET']),
 
]





