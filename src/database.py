from sqlalchemy import *
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker


ENGINE = create_engine('sqlite://data/database.sqlite3')
Base = declarative_base()
Session = sessionmaker(bind=ENGINE)
SESSION = Session()


class AutoIgnoredPost(Base):
    __tablename__ = 'auto_ignored_posts'

    id = Column(Integer, primary_key=True)
    post_id = Column(Integer)
    site_url = Column(String(100))
    ignored_date = Column(DateTime)


class BlacklistedUser(Base):
    __tablename__ = 'blacklisted_users'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer)
    site_url = Column(String(100))
    blacklisted_by = Column(String(100))
    blacklisted_for = Column(String(100))


class BodyfetcherMaxId(Base):
    __tablename__ = 'bodyfetcher_max_ids'

    id = Column(Integer, primary_key=True)
    site_url = Column(String(100))
    max_id = Column(Integer)


class BodyfetcherQueueItem(Base):
    __tablename__ = 'bodyfetcher_queue'

    id = Column(Integer, primary_key=True)
    site_url = Column(String(100))
    post_id = Column(Integer)
    enqueued_at = Column(DateTime)


class BodyfetcherQueueTiming(Base):
    __tablename__ = 'bodyfetcher_queue_timings'

    id = Column(Integer, primary_key=True)
    site_url = Column(String(100))
    time_in_queue = Column(Float(precision='12,6'))


class FalsePositive(Base):
    __tablename__ = 'false_positives'

    id = Column(Integer, primary_key=True)
    site_url = Column(String(100))
    post_id = Column(Integer)


class IgnoredPost(Base):
    __tablename__ = 'ignored_posts'

    id = Column(Integer, primary_key=True)
    site_url = Column(String(100))
    post_id = Column(Integer)


class SmokeyMessage(Base):
    __tablename__ = 'smokey_messages'

    id = Column(Integer, primary_key=True)
    chat_site_url = Column(String(100))
    room_id = Column(Integer)
    message_id = Column(Integer)


class Notification(Base):
    __tablename__ = 'notifications'

    id = Column(Integer, primary_key=True)
    chat_user_id = Column(Integer)
    chat_site_url = Column(String(100))
    room_id = Column(Integer)
    site_url = Column(String(100))


class WhitelistedUser(Base):
    __tablename__ = 'whitelisted_users'

    id = Column(Integer, primary_key=True)
    site_url = Column(String(100))
    user_id = Column(Integer)


class WhyDatum(Base):
    __tablename__ = 'why_data'

    id = Column(Integer, primary_key=True)
    site_url = Column(String(100))
    post_id = Column(Integer)
    why = Column(String(1000))
