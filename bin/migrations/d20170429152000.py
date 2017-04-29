from sqlalchemy import Table, Column, Integer, String, MetaData
from migrate import ChangesetTable


def execute(database, engine):
    meta = MetaData(bind=engine)
    roles = Table('roles', meta,
                  Column('id', Integer, primary_key=True),
                  Column('role_name', String(100)))
    roles.create(engine)
