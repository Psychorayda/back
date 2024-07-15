from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

engine = create_engine(
            'mysql+pymysql://spark:oneforall@localhost/fast_db',
            echo=False,
            pool_pre_ping=True
        )

db_session = sessionmaker(bind=engine, autoflush=False, autocommit=False)

def get_session() -> Session:
    return db_session()

