from math import ceil

from marshmallow import (
    Schema,
    fields,
    validate,
    validates_schema,
    post_load,
    pre_dump,
    ValidationError,
)

from application.lib.validation import custom_fields


ALLOWED_STATUS = (
    "ACTIVE",
    "DISABLED",
)
AVAILABLE_FILTERS = (
    "user_ids",
    "name",
    "email",
    "status",
    "created_at",
    "last_modified",
    "last_login",
)
SEARCHABLE_COLUMNS = (
    "id",
    "name",
    "email",
    "status",
    "created_at",
    "last_modified",
    "last_login",
)
UPDATEABLE_COLUMNS = (
    "name",
    "email",
    "status",
    "password",
)
MAX_SEARCH_LIMIT = 100
PASSWORD_REGEX = r"^(?=.*?[A-Z])(?=.*?[a-z])(?=.*?[0-9]).{10,}$"


class UserSchema(Schema):
    name = fields.String(
        required=True,
        validate=validate.Length(min=1, max=255),
    )
    email = fields.Email(
        required=True,
        validate=validate.Length(max=255),
    )
    status = fields.String(
        validate=validate.OneOf(ALLOWED_STATUS),
    )

    # load_only params
    password = fields.String(
        validate=validate.Regexp(PASSWORD_REGEX), required=True, load_only=True
    )

    # dump_only params
    _id = custom_fields.PositiveInt(attribute="id", data_key="id", dump_only=True)
    last_login = fields.DateTime(required=True, dump_only=True)


class DateTimeRangeSchema(Schema):
    datetime_from = custom_fields.ConvertedAwareDateTime()
    datetime_to = custom_fields.ConvertedAwareDateTime()


class SortBySchema(Schema):
    column = fields.String(
        required=True,
        validate=validate.OneOf(SEARCHABLE_COLUMNS),
        load_only=True,
    )
    order = fields.String(
        validate=validate.OneOf(("ASC", "DESC")),
        load_only=True,
        load_default="ASC",
    )


class UpdateUserRequestSchema(Schema):
    _id = custom_fields.PositiveInt(
        attribute="id", data_key="id", required=True, load_only=True
    )
    name = fields.String(
        validate=validate.Length(min=1),
        load_only=True,
    )
    email = fields.Email(load_only=True)
    status = fields.String(
        validate=validate.OneOf(ALLOWED_STATUS),
        load_only=True,
    )
    password = fields.String(validate=validate.Regexp(PASSWORD_REGEX), load_only=True)

    @validates_schema
    def validate_at_least_one_field(self, data, **kwargs):
        if not set(data).intersection(set(UPDATEABLE_COLUMNS)):
            raise ValidationError("At least one field required")


class SearchUserSchema(Schema):
    # load_only params
    user_ids = fields.List(
        custom_fields.PositiveInt(), validate=validate.Length(min=1), load_only=True
    )
    name = fields.String(load_only=True)
    email = fields.String(load_only=True)
    status = fields.String(
        validate=validate.OneOf(ALLOWED_STATUS),
        load_only=True,
    )
    created = fields.Nested(DateTimeRangeSchema, load_only=True)
    updated = fields.Nested(DateTimeRangeSchema, load_only=True)
    logged_in = fields.Nested(DateTimeRangeSchema, load_only=True)
    sort_by = fields.Nested(
        SortBySchema,
        many=True,
        load_only=True,
    )
    limit = fields.Integer(
        validate=validate.Range(min=1, max=MAX_SEARCH_LIMIT),
        load_only=True,
        load_default=10,
    )
    page = fields.Integer(
        validate=validate.Range(min=0), load_only=True, load_default=0
    )

    # dump_only params
    users = fields.Nested(UserSchema, many=True, dump_only=True)
    pages = custom_fields.PositiveInt(dump_only=True)

    @validates_schema
    def validate_sort_duplicates(self, data, **kwargs):
        sort_by = data.get("sort_by", [])
        used_columns = set([elem["column"] for elem in sort_by])
        if len(used_columns) != len(sort_by):
            raise ValidationError("Duplicated columns for sorting")

    @validates_schema
    def validate_at_least_one_filter(self, data, **kwargs):
        if not set(data).intersection(set(AVAILABLE_FILTERS)):
            raise ValidationError("At least one filter required")

    @post_load
    def calculate_offset(self, data, **kwargs):
        data["offset"] = data["limit"] * data["page"]
        del data["page"]
        return data

    @pre_dump
    def calculate_pages(self, data, **kwargs):
        data["pages"] = ceil(data["users_num"] / data["limit"])

        return data


class LoginUserRequestSchema(Schema):
    email = fields.Email(required=True, load_only=True)
    password = fields.String(required=True, load_only=True)


class DeleteUserRequestSchema(Schema):
    _id = custom_fields.PositiveInt(
        attribute="id", data_key="id", required=True, load_only=True
    )


user_schema = UserSchema()
create_user_request_schema = UserSchema(only=["name", "email", "password"])
update_user_request_schema = UpdateUserRequestSchema()
delete_user_request_schema = DeleteUserRequestSchema()
search_user_request_schema = SearchUserSchema()
login_user_request_schema = LoginUserRequestSchema()
