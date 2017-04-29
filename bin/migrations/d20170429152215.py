from sqlalchemy import Table, Column, Integer, MetaData, UniqueConstraint
from migrate import ChangesetTable, UniqueConstraint


def execute(database, engine):
    meta = MetaData(bind=engine)
    users = Table('users', meta,
                  Column('id', Integer, primary_key=True),
                  Column('cso_user_id', Integer),
                  Column('cse_user_id', Integer),
                  Column('cmse_user_id', Integer),
                  UniqueConstraint('cso_user_id', 'cse_user_id', 'cmse_user_id'))
    users.create(engine)
