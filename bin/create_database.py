from os import path, getcwd, mkdir
import os.path
import sys
import inspect

# Haaaaaaaaaaack.
sys.path.append(path.abspath('../src'))
import database

if os.path.basename(getcwd()) != 'bin':
    print("E: Can't import database module from {}. Run create_database.py from the bin/ directory."
          .format(getcwd()))

models = []
for name, obj in inspect.getmembers(sys.modules[database.__name__]):
    if inspect.isclass(obj) and obj.__module__ == database.__name__ and database.Base in inspect.getmro(obj):
        models.append(name)

print("Found models: {}".format(', '.join(models)))

if not path.isdir(path.dirname(database.FULL_DB_PATH)):
    mkdir(path.dirname(database.FULL_DB_PATH))
    print("Made directory {}".format(path.dirname(database.FULL_DB_PATH)))

if not path.isfile(database.FULL_DB_PATH):
    with open(database.FULL_DB_PATH, 'w+') as f:
        print("Created database file {}".format(database.FULL_DB_PATH))
        f.close()

print("Creating tables...")
database.Base.metadata.create_all(database.ENGINE)
