from sqlalchemy import Column, Boolean
from migrate.changeset import ChangesetColumn


def execute(database, engine):
    is_report = Column('is_report', Boolean)
    is_report.create(database.get_table(database.SmokeyMessage))
