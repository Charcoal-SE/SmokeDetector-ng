from migrate.changeset.constraint import UniqueConstraint


def execute(database, engine):
    cons = UniqueConstraint(database.SchemaMigration.migration_file, table=database.get_table(database.SchemaMigration))
    cons.create(engine=engine)
