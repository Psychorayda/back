import logging
from logging import Filter

from settings import req_id_ctx
from database import engine, get_session
from models import SystemLogModel


class RequestInfoFilter(Filter):
    def filter(self, record):
        record.req_id = req_id_ctx.get("req_id")
        return True

system_logger = logging.getLogger("sys_log")
system_logger.setLevel(logging.DEBUG)
format_str = "%(levelname)s - %(asctime)s - ID:%(req_id)s - FILE:%(filename)s - FUNC:%(funcName)s - LINE:%(lineno)d %(message)s"

stream = logging.StreamHandler() # write to console
stream.addFilter(RequestInfoFilter())
stream.setLevel(logging.WARNING)
stream.setFormatter(logging.Formatter(format_str, datefmt="%Y-%m-%d %H:%M:%S"))


file = logging.FileHandler("./logs/system.log", encoding='UTF-8') # write to file
file.addFilter(RequestInfoFilter())
file.setLevel(logging.INFO)
file.setFormatter(logging.Formatter(format_str, datefmt="%Y-%m-%d %H:%M:%S"))


class SystemLogDBHandler(logging.Handler):
    def __init__(self):
        logging.Handler.__init__(self)
        self.engine = engine

    def emit(self, record):
        session = get_session()
        try:
            system_log = SystemLogModel(
                levelname = record.levelname,
                message = record.message,
                filename = record.filename,
                funcName = record.funcName,
                lineno = record.lineno,
                req_id = record.req_id
            )
            session.add(system_log)
            session.commit()
        except Exception as error_info:
            session.rollback()
            print(f"Failed to write system log to database by error {error_info}")
        finally:
            session.close()

database = SystemLogDBHandler() # write to database
database.addFilter(RequestInfoFilter()) 
database.setLevel(logging.DEBUG)


system_logger.addHandler(stream)
# system_logger.addHandler(file)
# system_logger.addHandler(database)