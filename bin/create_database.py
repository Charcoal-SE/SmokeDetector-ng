import os.path
import sys
import inspect

# Haaaaaaaaaaack.
sys.path.append(os.path.abspath('../src'))
import database

models = []
for name, obj in inspect.getmembers(sys.modules[database.__name__]):
    if inspect.isclass(obj) and obj.__module__ == database.__name__ and database.Base in inspect.getmro(obj):
        models.append(name)

print("Found models: {}".format(', '.join(models)))

if not os.path.isdir(database.basedir):
    os.mkdir(database.basedir)
    print("Made directory {}".format(database.basedir))

if not os.path.isfile(database.DB_PATH):
    with open(database.DB_PATH, 'w+') as f:
        print("Created database file {}".format(database.DB_PATH))
        f.close()

print("Creating tables...")
database.Base.metadata.create_all(database.ENGINE)
