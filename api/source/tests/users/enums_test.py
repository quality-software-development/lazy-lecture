from source.app.users.enums import Roles, Sort, Order


def test_roles_values():
    assert Roles.ADMIN.value == "admin"
    assert Roles.USER.value == "user"


def test_sort_values():
    assert Sort.ID.value == "id"
    assert Sort.USERNAME.value == "username"
    assert Sort.CREATE_DATE.value == "create_date"
    assert Sort.UPDATE_DATE.value == "update_date"


def test_order_values():
    assert Order.ASC.value == "asc"
    assert Order.DESC.value == "desc"
