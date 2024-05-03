import grpc
import pytest

from couchers import errors
from couchers.models import HostingStatus, MeetupStatus, User
from couchers.sql import couchers_select as select
from proto import notifications_pb2
from tests.test_fixtures import db, generate_user, notifications_session, session_scope, testconfig  # noqa


@pytest.fixture(autouse=True)
def _(testconfig):
    pass


def test_GetNotificationSettings(db):
    _, token = generate_user()

    with session_scope() as session:
        user = session.execute(select(User)).scalar_one()
        user.new_notifications_enabled = False

    with notifications_session(token) as notifications:
        res = notifications.GetNotificationSettings(notifications_pb2.GetNotificationSettingsReq())
    assert not res.new_notifications_enabled

    with session_scope() as session:
        user = session.execute(select(User)).scalar_one()
        user.new_notifications_enabled = True

    with notifications_session(token) as notifications:
        res = notifications.GetNotificationSettings(notifications_pb2.GetNotificationSettingsReq())
    assert res.new_notifications_enabled


def test_SetNotificationSettings(db):
    _, token = generate_user()

    with session_scope() as session:
        user = session.execute(select(User)).scalar_one()
        user.new_notifications_enabled = False

    with notifications_session(token) as notifications:
        notifications.SetNotificationSettings(
            notifications_pb2.SetNotificationSettingsReq(enable_new_notifications=False)
        )

    with session_scope() as session:
        user = session.execute(select(User)).scalar_one()
        assert not user.new_notifications_enabled

    with notifications_session(token) as notifications:
        notifications.SetNotificationSettings(
            notifications_pb2.SetNotificationSettingsReq(enable_new_notifications=True)
        )

    with session_scope() as session:
        user = session.execute(select(User)).scalar_one()
        assert user.new_notifications_enabled

    with notifications_session(token) as notifications:
        notifications.SetNotificationSettings(
            notifications_pb2.SetNotificationSettingsReq(enable_new_notifications=False)
        )

    with session_scope() as session:
        user = session.execute(select(User)).scalar_one()
        assert not user.new_notifications_enabled


def test_notifications_do_not_email(db):
    _, token = generate_user()

    with notifications_session(token) as notifications:
        notifications.SetDoNotEmail(notifications_pb2.SetDoNotEmailReq(enable_do_not_email=True))

        with pytest.raises(grpc.RpcError) as e:
            notifications.SetNotificationSettings(
                notifications_pb2.SetNotificationSettingsReq(enable_new_notifications=True)
            )
        assert e.value.code() == grpc.StatusCode.FAILED_PRECONDITION
        assert e.value.details() == errors.DO_NOT_EMAIL_CANNOT_ENABLE_NEW_NOTIFICATIONS


def test_GetDoNotEmail(db):
    _, token = generate_user()

    with session_scope() as session:
        user = session.execute(select(User)).scalar_one()
        user.do_not_email = False

    with notifications_session(token) as notifications:
        res = notifications.GetDoNotEmail(notifications_pb2.GetDoNotEmailReq())
    assert not res.do_not_email_enabled

    with session_scope() as session:
        user = session.execute(select(User)).scalar_one()
        user.do_not_email = True
        user.hosting_status = HostingStatus.cant_host
        user.meetup_status = MeetupStatus.does_not_want_to_meetup
        user.new_notifications_enabled = False

    with notifications_session(token) as notifications:
        res = notifications.GetDoNotEmail(notifications_pb2.GetDoNotEmailReq())
    assert res.do_not_email_enabled


def test_SetDoNotEmail(db):
    _, token = generate_user()

    with session_scope() as session:
        user = session.execute(select(User)).scalar_one()
        user.do_not_email = False
        user.hosting_status = HostingStatus.can_host
        user.meetup_status = MeetupStatus.wants_to_meetup
        user.new_notifications_enabled = True

    with notifications_session(token) as notifications:
        notifications.SetDoNotEmail(notifications_pb2.SetDoNotEmailReq(enable_do_not_email=False))

    with session_scope() as session:
        user = session.execute(select(User)).scalar_one()
        assert not user.do_not_email

    with notifications_session(token) as notifications:
        notifications.SetDoNotEmail(notifications_pb2.SetDoNotEmailReq(enable_do_not_email=True))

    with session_scope() as session:
        user = session.execute(select(User)).scalar_one()
        assert user.do_not_email
        assert user.hosting_status == HostingStatus.cant_host
        assert user.meetup_status == MeetupStatus.does_not_want_to_meetup
        assert user.new_notifications_enabled == False

    with notifications_session(token) as notifications:
        notifications.SetDoNotEmail(notifications_pb2.SetDoNotEmailReq(enable_do_not_email=False))

    with session_scope() as session:
        user = session.execute(select(User)).scalar_one()
        assert not user.do_not_email
