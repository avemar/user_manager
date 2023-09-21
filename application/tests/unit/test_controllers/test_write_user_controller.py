import json
from http import HTTPStatus
from unittest.mock import MagicMock

import pytest

from application.controllers.user import UserWriteController
from application.lib.managers.user_manager import UserNotFound
from application.tests.unit.test_controllers.utils import make_controller


@pytest.fixture
def mock_manager_delete_user(mocker, delete_user_exception):
    mock = mocker.patch(
        "application.controllers.user.UserManager.delete_user",
        side_effect=delete_user_exception,
    )
    yield mock


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "raw_request, body_request, delete_user_exception, delete_user_expected_call, expected_write, expected_status",
    [
        (
            # User correctly deleted
            {"id": "123"},
            {},
            None,
            123,
            None,
            HTTPStatus.NO_CONTENT,
        ),
        (
            # Non-existent user
            {"id": "456"},
            {},
            UserNotFound,
            456,
            "User doesn't exist",
            HTTPStatus.NOT_FOUND,
        ),
        (
            # Duplicated arguments
            {"id": "456"},
            {"id": 456},
            None,
            None,
            {"error": "Multiple occurrences of same param/s: {'id'}"},
            HTTPStatus.BAD_REQUEST,
        ),
        (
            # Wrong argument
            {"wrong_arg": "456"},
            {},
            None,
            None,
            {'error': "{'id': ['Missing data for required field.'], 'wrong_arg': ['Unknown field.']}"},
            HTTPStatus.BAD_REQUEST,
        ),
    ],
)
async def test_delete_user(
    mock_manager_delete_user,
    raw_request,
    body_request,
    delete_user_expected_call,
    expected_write,
    expected_status,
):
    mocked_request = MagicMock(method="DELETE", body=json.dumps(body_request))
    controller = make_controller(
        controller_class=UserWriteController,
        application=MagicMock(),
        request=mocked_request,
    )
    await controller.delete(**raw_request)

    if delete_user_expected_call is not None:
        mock_manager_delete_user.assert_awaited_once_with(delete_user_expected_call)
    else:
        mock_manager_delete_user.assert_not_called()

    if expected_write is not None:
        controller.write.assert_called_once_with(expected_write)
    else:
        controller.write.assert_not_called()

    controller.set_status.assert_called_once_with(expected_status)
