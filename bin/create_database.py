import os.path
import sys
import inspect
from sqlalchemy import create_engine

# Haaaaaaaaaaack.
sys.path.append(os.path.abspath('../src'))
import database

models = []
for name, obj in inspect.getmembers(sys.modules[database.__name__]):
    if inspect.isclass(obj) and obj.__module__ == database.__name__ and database.Base in inspect.getmro(obj):
        models.append(name)

print("Found models: {}".format(', '.join(models)))

print("Creating tables...")
relative_engine = create_engine('sqlite:///../data/database.sqlite3')
database.Base.metadata.create_all(relative_engine)
