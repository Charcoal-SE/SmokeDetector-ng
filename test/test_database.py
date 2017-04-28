import os.path
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime
from src.database import *


def setup_module(module):
    # Initialize the database and actually create tables before we start querying
    module.initialize_new()

    # Add some dummy records we can test on
    records = [
        Notification(chat_user_id=123456, chat_site_url='stackoverflow.com', room_id=33032,
                     site_url='ng-test.stackexchange.com'),
        Notification(chat_user_id=654321, chat_site_url='stackoverflow.com', room_id=99843,
                     site_url='ng-test.stackexchange.com'),
        Notification(chat_user_id=123456, chat_site_url='stackoverflow.com', room_id=33032,
                     site_url='ng-test-dc.stackexchange.com'),
        Notification(chat_user_id=654321, chat_site_url='stackoverflow.com', room_id=99843,
                     site_url='ng-test-dc.stackexchange.com'),
        Notification(chat_user_id=654321, chat_site_url='stackoverflow.com', room_id=99843,
                     site_url='ng-test-ds.stackexchange.com')
    ]
    SESSION.add_all(records)
    SESSION.commit()


def test_basemodel_create():
    aip_before_count = SESSION.query(AutoIgnoredPost).count()
    AutoIgnoredPost.create(post_id=123456, site_url='ng-test.stackexchange.com',
                           ignored_date=datetime(2016, 3, 19, 12, 34, 26))
    aip_after_count = SESSION.query(AutoIgnoredPost).count()
    assert aip_after_count == aip_before_count + 1
    assert aip_after_count > 0

    notification_before_count = SESSION.query(Notification).count()
    Notification.create(chat_user_id=123456, chat_site_url='stackexchange.com', room_id=11540,
                        site_url='ng-test.stackexchange.com')
    notification_after_count = SESSION.query(Notification).count()
    assert notification_after_count == notification_before_count + 1
    assert notification_after_count > 0


def test_basemodel_update_collection():
    col = SESSION.query(Notification).filter(Notification.site_url == 'ng-test.stackexchange.com')
    BaseModel.update_collection(col, room_id=654321)

    col = SESSION.query(Notification).filter(Notification.site_url == 'ng-test.stackexchange.com')
    for notification in col.all():
        assert notification.room_id == 654321


def test_basemodel_update():
    notif = SESSION.query(Notification).filter(Notification.chat_user_id == 123456, Notification.room_id == 33032)\
                   .first()
    notif.update(room_id=30302)

    notif_new = SESSION.query(Notification).filter(Notification.id == notif.id).first()
    assert notif_new.room_id == 30302


def test_basemodel_delete_collection():
    col = SESSION.query(Notification).filter(Notification.site_url == 'ng-test-dc.stackexchange.com')
    BaseModel.delete_collection(col)

    col = SESSION.query(Notification).filter(Notification.site_url == 'ng-test-dc.stackexchange.com')
    assert col.count() == 0


def test_basemodel_delete():
    notif = SESSION.query(Notification).filter(Notification.site_url == 'ng-test-ds.stackexchange.com').first()
    notif.destroy()

    notif_col = SESSION.query(Notification).filter(Notification.id == notif.id)
    assert notif_col.count() == 0
