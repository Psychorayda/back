from contextvars import ContextVar
import os

from templates import *


#######################################################################
TITLE = "OCSNAD"
'''
project title
'''
DESCRIPTION = "This demo is for testing building proj using fastapi framework"
'''
project description
'''
VERSION = '0.0.6'
'''
project version
'''
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
'''
project root path
'''


#######################################################################
SITE = ""
'''
teles site
'''
INTERFACE = ""
'''
teles interface
'''


#######################################################################
REQUEST_LOG_RECORD = True
'''
record log for every request
'''
# OPERATION_RECORD = True
# '''
# record operation details for every request
# '''
REQUEST_PROCESS_TIME_RECORD = True
'''
record process time for every request
'''

LOG_LEVEL = "DEBUG"
'''
log level
'''

# user_context = ContextVar("user")
# role_context = ContextVar("role")
request_id_context = ContextVar("request_id")
# host_context = ContextVar("host")
# method_context = ContextVar("method")
# url_context = ContextVar("url")


#######################################################################
MIDDLEWARES = [
    "middlewares.registeProcessTimeRecorder" if REQUEST_PROCESS_TIME_RECORD else None,
    "middlewares.registeRequestLogRecorder" if REQUEST_LOG_RECORD else None,
    # "middlewares.registeOperationRecorder" if OPERATION_RECORD else None,
]
'''
middlewares for project setting up
'''


#######################################################################
# 是否启用跨域
CORS_ORIGIN_ENABLE = True
# 只允许访问的域名列表，* 代表所有
ALLOW_ORIGINS = ["*"]
# 是否支持携带 cookie
ALLOW_CREDENTIALS = True
# 设置允许跨域的http方法，比如 get、post、put等。
ALLOW_METHODS = ["*"]
# 允许携带的headers，可以用来鉴别来源等作用。
ALLOW_HEADERS = ["*"]


#######################################################################
WEBSOCKET_TEST_HTML = websocket_test_html
'''
template for test websocket func
'''


#######################################################################
DB_USER = 'spark'
'''
database user
'''
DB_PWD = 'oneforall'
'''
database password
'''
DB_HOST = 'localhost'
'''
database host
'''
DB_NAME = 'fast_api_db'
'''
database name
'''
DB_INIT_INFO = {
    'user': DB_USER,
    'password': DB_PWD,
    'host': DB_HOST,
    'database': DB_NAME
}
'''
database initialize information
'''
DB_MYSQL_URL = f'mysql+pymysql://{DB_USER}:{DB_PWD}@{DB_HOST}/{DB_NAME}'


#######################################################################
HTTP_200_SUCCESS = 200
HTTP_400_ERROR = 400
HTTP_401_UNAUTHORIZED = 401
HTTP_403_FORBIDDEN = 403
HTTP_404_NOT_FOUND = 404


#######################################################################
symmetry_key = b'QIAnTBAbHs1GVgDspM9lVwnYgSdI0IkAACAjJw9UUvQ='

aes_key = '0CoJUm6Qywm6ts68'
vi = '0102030405060708'

SECRET_KEY = "07108a7d28a4a60d004f5d1ad93bdbc82f8871c2595b19e2d9b24f3e0342fd56"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

#######################################################################
COMMON_THRESHOLD = 5.0
'''
common threshold to all limiter
'''