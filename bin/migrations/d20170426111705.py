from sqlalchemy import Table, Column, Integer, String, MetaData, ForeignKey
from migrate import ChangesetTable, ForeignKeyConstraint


def execute(database, engine):
    meta = MetaData(bind=engine)
    report = Table('reports', meta,
                   Column('id', Integer, primary_key=True),
                   Column('message_id', Integer, ForeignKey(database.SmokeyMessage.id), nullable=False),
                   Column('site_url', String(100)),
                   Column('post_id', Integer)
                  )
    report.create(engine)
