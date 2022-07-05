"""
Script for initializing the Google Cloud SQL MySQL tables.
"""
import logging
import os
import sys

from dotenv import load_dotenv
load_dotenv()

from google.cloud.sql.connector import Connector, IPTypes
from sqlalchemy.engine import create_engine
from sqlalchemy.orm import declarative_base
# SQL types
from sqlalchemy import (
    BigInteger,
    Boolean,
    CHAR,
    Column,
    Date,
    DateTime,
    Integer,
    SmallInteger,
    VARCHAR
)
# SQL Contraints
from sqlalchemy import (
    ForeignKey
)
import pymysql

logging.basicConfig(stream=sys.stdout, level=logging.INFO)


def get_connection() -> pymysql.Connection:
    # https://github.com/GoogleCloudPlatform/cloud-sql-python-connector/blob/main/README.md
    with Connector(
        ip_type=IPTypes.PUBLIC,
        enable_iam_auth=False,
        timeout=30
    ) as connector:
        connector: Connector
        conn: pymysql.Connection = connector.connect(
            "{project}:{region}:{instance}".format(
                project=os.getenv('GOOGLE_CLOUD_PROJECT_NAME'),
                region=os.getenv('GOOGLE_CLOUD_PROJECT_REGION'),
                instance=os.getenv('GOOGLE_CLOUD_INSTANCE_NAME')
            ),
            driver="pymysql",
            user=os.getenv('GOOGLE_CLOUD_SQL_USER'),
            password=os.getenv('GOOGLE_CLOUD_SQL_PASSWORD'),
            db="production"
        )
    return conn

logging.info("Connecting to Google Cloud SQL database")
engine = create_engine(
    "mysql+pymysql://",
    creator=get_connection
)
Base = declarative_base(bind=engine)


class ViewLog(Base):
    __tablename__ = 'view_logs'

    id = Column(BigInteger, autoincrement=True, primary_key=True)
    server_time = Column(DateTime)
    device_type = Column(VARCHAR(16))
    session_id = Column(Integer)
    user_id = Column(Integer, ForeignKey('user_accounts.id'))
    item_id = Column(Integer, ForeignKey('items.id'))


class Item(Base):
    __tablename__ = 'items'

    id = Column(Integer, primary_key=True)
    price = Column(Integer)
    category_1 = Column(SmallInteger)
    category_2 = Column(SmallInteger)
    category_3 = Column(SmallInteger)
    product_type = Column(Integer)


class UserAccount(Base):
    __tablename__ = 'user_accounts'

    id = Column(Integer, primary_key=True)
    country = Column(CHAR(2))
    created_at = Column(DateTime)
    date_of_birth = Column(Date)


class Impression(Base):
    __tablename__ = 'impressions'

    id = Column(CHAR(32), primary_key=True)
    shown_at = Column(DateTime)
    user_id = Column(Integer, ForeignKey('user_accounts.id'))
    app_code = Column(SmallInteger)
    os_version = Column(VARCHAR(16))
    is_4G = Column(Boolean)
    is_click = Column(Boolean)


if __name__ == '__main__':
    Base.metadata.create_all(checkfirst=True)
