from http import HTTPStatus
from logging import getLogger
from typing import Dict

from application.lib.decorators.controller import handle_server_errors
from application.lib.tornado.request_handler import ApplicationRequestHandler
from application.lib.validation import validate
from application.lib.managers.user_manager import (
    UserManager,
    UserAlreadyTaken,
    UserNotFound,
    WrongPassword,
)
from application.lib.validation.schemas.user import (
    create_user_request_schema,
    update_user_request_schema,
    delete_user_request_schema,
    search_user_request_schema,
    login_user_request_schema,
    user_schema,
)


logger = getLogger("UserController")


class UserWriteController(ApplicationRequestHandler):
    def initialize(self):
        self.schemas = {
            "create_user_request_schema": create_user_request_schema,
            "update_user_request_schema": update_user_request_schema,
            "delete_user_request_schema": delete_user_request_schema,
            "user_schema": user_schema,
        }

    @handle_server_errors
    @validate(schema_name="create_user_request_schema")
    async def post(self, data: Dict, **kwargs):
        try:
            stored_user_id = await UserManager.insert_user(user_data=data)
        except UserAlreadyTaken:
            self.set_status(HTTPStatus.BAD_REQUEST)
            self.write("User already taken")
            return

        self.set_status(HTTPStatus.CREATED)
        self.write(str(stored_user_id))

    @handle_server_errors
    @validate(schema_name="update_user_request_schema")
    async def patch(self, data: Dict, **kwargs):
        try:
            stored_user = await UserManager.update_user(user_data=data)
        except UserAlreadyTaken:
            self.set_status(HTTPStatus.BAD_REQUEST)
            self.write("One or more fields exist for another users")
        except UserNotFound:
            self.set_status(HTTPStatus.NOT_FOUND)
            self.write("User doesn't exist")
        else:
            self.set_status(HTTPStatus.OK)
            self.write(self.schemas["user_schema"].dump(stored_user))

    @handle_server_errors
    @validate(schema_name="delete_user_request_schema")
    async def delete(self, data: Dict, **kwargs):
        try:
            await UserManager.delete_user(data["id"])
        except UserNotFound:
            self.set_status(HTTPStatus.NOT_FOUND)
            self.write("User doesn't exist")
        else:
            self.set_status(HTTPStatus.NO_CONTENT)


class UserReadController(ApplicationRequestHandler):
    def initialize(self):
        self.schemas = {
            "search_user_request_schema": search_user_request_schema,
        }

    @handle_server_errors
    @validate(schema_name="search_user_request_schema")
    async def post(self, data: Dict, **kwargs):
        stored_users, users_num = await UserManager.search_users(filters=data)
        self.set_status(HTTPStatus.OK)
        self.write(
            self.schemas["search_user_request_schema"].dump(
                {
                    "users": stored_users,
                    "users_num": users_num,
                    "limit": data["limit"],
                }
            )
        )


class UserLoginController(ApplicationRequestHandler):
    def initialize(self):
        self.schemas = {
            "login_user_request_schema": login_user_request_schema,
            "user_schema": user_schema,
        }

    @handle_server_errors
    @validate(schema_name="login_user_request_schema")
    async def post(self, data: Dict, **kwargs):
        try:
            stored_user = await UserManager.login_user(user_data=data)
        except UserNotFound:
            self.set_status(HTTPStatus.BAD_REQUEST)
        except WrongPassword:
            logger.debug(f"User {data['email']} inserted wrong password")
            self.set_status(HTTPStatus.BAD_REQUEST)
        else:
            self.set_status(HTTPStatus.OK)
            self.write(self.schemas["user_schema"].dump(stored_user))
