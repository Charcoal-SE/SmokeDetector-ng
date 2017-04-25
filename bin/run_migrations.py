# This entire script is composed of hacks. Be Ye Not Surprised if it all breaks catastrophically at some point.
from os import path, linesep
import sys
from datetime import datetime
import importlib
from sqlalchemy import MetaData
from sqlalchemy.engine import create_engine


sys.path.append(path.abspath('../src'))
import database


meta = MetaData()
db_path = path.abspath(path.join(path.dirname(__file__), '../data/database.sqlite3'))
migration_engine = create_engine('sqlite:////' + db_path)
meta.bind = migration_engine


def get_table(cls):
    real_table = cls.__table__
    real_table.metadata = meta
    return real_table

setattr(database, 'get_table', get_table)

database.SchemaMigration.populate()

pending_migrations = [x.migration_file for x in database.SchemaMigration.pending()]
print("Pending migrations:")
print(linesep.join([" * {}".format(x) for x in pending_migrations]))

for pending in pending_migrations:
    migrator = importlib.import_module("migrations.{}".format('.'.join(pending.split('.')[0:-1])))
    if not hasattr(migrator, 'execute') or not callable(migrator.execute):
        raise AttributeError("Invalid migration file ({}) - no `execute` method present")

    migrator.execute(database, migration_engine)
    record = database.SESSION.query(database.SchemaMigration).filter(database.SchemaMigration.migration_file == pending)
    record.run_status = True
    record.run_at = datetime.now()
    database.SESSION.commit()

print("Executed {} pending migrations.".format(len(pending_migrations)))
