from datetime import datetime
from sqlalchemy import or_
from src.database import *


def setup_module(module):
    # Initialize the database and actually create tables before we start querying
    module.initialize_new()

    # Add some dummy records we can test on.
    # If you add records to this, make sure to delete them in teardown_module too.
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
                     site_url='ng-test-ds.stackexchange.com'),
        SchemaMigration(migration_file='ng_test_d20170429021826.py', run_status=False, run_at=None),
        SchemaMigration(migration_file='ng_test_d20170429021856.py', run_status=True,
                        run_at=datetime(2017, 4, 29, 2, 19, 26)),
        User(cso_user_id=-999, cse_user_id=-999, cmse_user_id=-999),
        Role(role_name='ng-test-admin')
    ]
    SESSION.add_all(records)
    SESSION.commit()

    # Annoyingly, we have to do this twice so that we have access to the id attribute for link models.
    test_user = SESSION.query(User).filter(User.cso_user_id == -999).first()
    test_role = SESSION.query(Role).filter(Role.role_name == 'ng-test-admin').first()
    link_records = [
        UserRole(user_id=test_user.id, role_id=test_role.id)
    ]
    SESSION.add_all(link_records)
    SESSION.commit()


def teardown_module(module):
    SESSION.query(Notification).filter(Notification.site_url.like('ng-test%')).delete(synchronize_session=False)
    SESSION.query(SchemaMigration).filter(SchemaMigration.migration_file.like('ng_test%'))\
           .delete(synchronize_session=False)

    user_ids = [x.id for x in SESSION.query(User).filter(User.cso_user_id == -999).all()]
    role_ids = [x.id for x in SESSION.query(Role).filter(Role.role_name.like('ng-test%')).all()]
    SESSION.query(UserRole).filter(or_(UserRole.user_id.in_(user_ids), UserRole.role_id.in_(role_ids)))\
           .delete(synchronize_session=False)

    SESSION.query(User).filter(User.id.in_(user_ids)).delete(synchronize_session=False)
    SESSION.query(Role).filter(Role.id.in_(role_ids)).delete(synchronize_session=False)

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


def test_schema_migration_pending():
    pending = SchemaMigration.pending()

    # SchemaMigration.pending returns sqlalchemy Query.all() (list), so use len() instead of Query.count().
    assert len(pending) == 1
    assert pending[0].migration_file == 'ng_test_d20170429021826.py'


def test_schema_migration_is_run():
    assert SchemaMigration.is_run('ng_test_d20170429021856.py') is True
    assert SchemaMigration.is_run('ng_test_d20170429021826.py') is False


def test_user_role_names():
    user = SESSION.query(User).filter(User.cso_user_id == -999).first()
    assert user.role_names() == ['ng-test-admin']


def test_user_has_role():
    user = SESSION.query(User).filter(User.cso_user_id == -999).first()
    assert user.has_role('ng-test-admin')


def test_user_add_role():
    user = SESSION.query(User).filter(User.cso_user_id == -999).first()
    user.add_role('ng-test-role', create_if_missing=True)
    assert user.has_role('ng-test-role', reload=True)


def test_user_add_role_exception():
    user = SESSION.query(User).filter(User.cso_user_id == -999).first()
    try:
        user.add_role('ng-test-nonexistent')
        raise AssertionError('Expected AttributeError from user.add_role call, got no exception')
    except AttributeError:
        pass


def test_has_role_caching():
    user = SESSION.query(User).filter(User.cso_user_id == -999).first()
    assert user.has_role('ng-test-caching') is False
    user.add_role('ng-test-caching', create_if_missing=True)
    assert user.has_role('ng-test-caching') is False
    assert user.has_role('ng-test-caching', reload=True)


def test_role_users():
    role = SESSION.query(Role).filter(Role.role_name == 'ng-test-admin').first()
    user = SESSION.query(User).filter(User.cso_user_id == -999).first()
    assert role.users() == [user]
