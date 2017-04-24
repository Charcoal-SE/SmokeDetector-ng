import os.path
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime
from src.database import *


def setup_module(module):
    # Initialize the database and actually create tables before we start querying
    module.initialize_new()


def test_basemodel_create():
    aip_before_count = SESSION.query(AutoIgnoredPost).count()
    AutoIgnoredPost.create(post_id=123456, site_url='sitecore.stackexchange.com',
                           ignored_date=datetime(2016, 3, 19, 12, 34, 26))
    aip_after_count = SESSION.query(AutoIgnoredPost).count()
    assert aip_after_count == aip_before_count + 1
    assert aip_after_count > 0

    notification_before_count = SESSION.query(Notification).count()
    Notification.create(chat_user_id=123456, chat_site_url='stackexchange.com', room_id=11540,
                        site_url='unix.stackexchange.com')
    notification_after_count = SESSION.query(Notification).count()
    assert notification_after_count == notification_before_count + 1
    assert notification_after_count > 0
