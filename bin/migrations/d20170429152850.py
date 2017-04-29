from sqlalchemy import Table, Column, Integer, MetaData, ForeignKey, PrimaryKeyConstraint
from migrate import ChangesetTable, ForeignKeyConstraint, PrimaryKeyConstraint


def execute(database, engine):
    meta = MetaData(bind=engine)
    users_roles = Table('users_roles', meta,
                        Column('user_id', Integer, ForeignKey(database.User.id), nullable=False),
                        Column('role_id', Integer, ForeignKey(database.Role.id), nullable=False),
                        PrimaryKeyConstraint('user_id', 'role_id'))
    users_roles.create(engine)
