import os
import os.path
import typing
from sqlalchemy import *
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound
import inspect

DB_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__)), '../data/database.sqlite3')

ENGINE = create_engine('sqlite:////' + DB_PATH)
Base = declarative_base()
Session = sessionmaker(bind=ENGINE)
SESSION = Session()


def initialize_new():
    if not os.path.isdir(os.path.dirname(DB_PATH)):
        os.mkdir(os.path.dirname(DB_PATH))

    if not os.path.isfile(DB_PATH):
        with open(DB_PATH, 'w+') as f:
            f.close()

    Base.metadata.create_all(ENGINE)


class BaseModel:
    @classmethod
    def create(cls, **kwargs):
        instance = cls(**kwargs)
        SESSION.add(instance)
        SESSION.commit()

    @classmethod
    def update_all(cls, ids, **kwargs):
        SESSION.query(cls).filter(cls.id.in_(ids)).update(kwargs)
        SESSION.commit()

    @staticmethod
    def update_collection(col, **kwargs):
        if not hasattr(col, 'update') or not callable(col.update):
            raise AttributeError('Invalid ORM collection passed to update_collection')

        col.update(kwargs)
        SESSION.commit()

    def __repr__(self):
        field_names = [x for x in dir(self.__class__) if x[0] != '_' and not
                       inspect.ismethod(getattr(self.__class__, x))]
        field_values = [getattr(self, x).__repr__() for x in field_names]
        fields = dict(zip(field_names, field_values))
        field_str = ", ".join(["{}={}".format(k, v) for k, v in fields.items()])
        return "<{}: {}>".format(self.__class__.__name__, field_str)

    def update(self, **kwargs):
        for field, val in kwargs.items():
            setattr(self, field, val)

        SESSION.commit()


class SchemaMigration(Base, BaseModel):
    __tablename__ = 'schema_migrations'

    id = Column(Integer, primary_key=True)
    migration_file = Column(String(255), nullable=False)
    run_status = Column(Boolean, default=False, nullable=False)
    run_at = Column(DateTime)

    @staticmethod
    def pending():
        return SESSION.query(SchemaMigration).filter(SchemaMigration.run_status == False).all()

    @staticmethod
    def is_run(filename):
        migration = SESSION.query(SchemaMigration).filter(SchemaMigration.migration_file == filename)
        if migration.count() > 1:
            raise MultipleResultsFound('Multiple migration files found with specified name.')

        return migration.first().run_status


class AutoIgnoredPost(Base, BaseModel):
    __tablename__ = 'auto_ignored_posts'

    id = Column(Integer, primary_key=True)
    post_id = Column(Integer)
    site_url = Column(String(100))
    ignored_date = Column(DateTime)


class BlacklistedUser(Base, BaseModel):
    __tablename__ = 'blacklisted_users'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer)
    site_url = Column(String(100))
    blacklisted_by = Column(String(100))
    blacklisted_for = Column(String(100))

    """
    Given a site URL and user ID, finds out whether the user represented by the combination is blacklisted or not.
    
    :param site_url: a string containing the SE site URL, as it would have been inserted into the database.
    :param  user_id: an int containing the ID of the user to check on the specified site.
    :returns: Two return values: a boolean indicating 'blacklisted or not', and either a BlacklistedUser instance 
              for the checked user, or None if the user is not blacklisted.
    """
    @staticmethod
    def is_blacklisted(site_url: str, user_id: int) -> (bool, typing.Optional['BlacklistedUser']):
        try:
            return True, SESSION.query(BlacklistedUser)\
                                .filter(BlacklistedUser.site_url == site_url, BlacklistedUser.user_id == user_id)\
                                .one()
        except NoResultFound:
            return False, None
        except MultipleResultsFound:
            return True, SESSION.query(BlacklistedUser)\
                                .filter(BlacklistedUser.site_url == site_url, BlacklistedUser.user_id == user_id)\
                                .order_by(desc(BlacklistedUser.id)).first()


class BodyfetcherMaxId(Base, BaseModel):
    __tablename__ = 'bodyfetcher_max_ids'

    id = Column(Integer, primary_key=True)
    site_url = Column(String(100))
    max_id = Column(Integer)

    """
    Given a site URL, retrieves the latest max ID record for the site.
    
    :param site: a string containing the SE site URL, as it would have been inserted into the database.
    :returns: A BodyfetcherMaxId instance representing the latest max ID record for the specified site, or None if no 
              record was found.
    """
    @staticmethod
    def by_site(site: str) -> typing.Optional['BodyfetcherMaxId']:
        return SESSION.query(BodyfetcherMaxId).filter(BodyfetcherMaxId.site_url == site)\
                      .order_by(desc(BodyfetcherMaxId.id)).first()


class BodyfetcherQueueItem(Base, BaseModel):
    __tablename__ = 'bodyfetcher_queue'

    id = Column(Integer, primary_key=True)
    site_url = Column(String(100))
    post_id = Column(Integer)
    enqueued_at = Column(DateTime)

    """
    Given a site URL, retrieves all items currently in the bodyfetcher queue for the site.
    
    :param site: a string containing the SE site URL, as it would have been inserted into the database.
    :returns: A list of BodyfetcherQueueItem instances, each representing a queue entry for the specified site.
    """
    @staticmethod
    def by_site(site: str) -> list:
        return SESSION.query(BodyfetcherQueueItem).filter(BodyfetcherQueueItem.site_url == site).all()


class BodyfetcherQueueTiming(Base, BaseModel):
    __tablename__ = 'bodyfetcher_queue_timings'

    id = Column(Integer, primary_key=True)
    site_url = Column(String(100))
    time_in_queue = Column(Float(precision='12,6'))

    """
    Given a site URL, retrieves a list of times that posts for the specified site have been in the bodyfetcher queue.
    
    :param site: a string containing the SE site URL, as it would have been inserted into the database.
    :returns: A list of floats, each representing the length of time a post on the specified site was in the queue.
    """
    @staticmethod
    def by_site(site: str) -> list:
        # We're returning the floats rather than the BodyfetcherQueueTiming instances because there's really no other
        # useful data on this model - the times are the only thing you're going to want.
        return [x.time_in_queue for x in
                SESSION.query(BodyfetcherQueueTiming).filter(BodyfetcherQueueTiming.site_url == site).all()]


class FalsePositive(Base, BaseModel):
    __tablename__ = 'false_positives'

    id = Column(Integer, primary_key=True)
    site_url = Column(String(100))
    post_id = Column(Integer)


class IgnoredPost(Base, BaseModel):
    __tablename__ = 'ignored_posts'

    id = Column(Integer, primary_key=True)
    site_url = Column(String(100))
    post_id = Column(Integer)


class SmokeyMessage(Base, BaseModel):
    __tablename__ = 'smokey_messages'

    id = Column(Integer, primary_key=True)
    chat_site_url = Column(String(100))
    room_id = Column(Integer)
    message_id = Column(Integer)


class Notification(Base, BaseModel):
    __tablename__ = 'notifications'

    id = Column(Integer, primary_key=True)
    chat_user_id = Column(Integer)
    chat_site_url = Column(String(100))
    room_id = Column(Integer)
    site_url = Column(String(100))


class WhitelistedUser(Base, BaseModel):
    __tablename__ = 'whitelisted_users'

    id = Column(Integer, primary_key=True)
    site_url = Column(String(100))
    user_id = Column(Integer)


class WhyDatum(Base, BaseModel):
    __tablename__ = 'why_data'

    id = Column(Integer, primary_key=True)
    site_url = Column(String(100))
    post_id = Column(Integer)
    why = Column(String(1000))
