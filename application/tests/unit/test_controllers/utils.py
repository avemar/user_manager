from unittest.mock import MagicMock


def make_controller(controller_class, application, request, **kwargs):
    controller_kwargs = {"application": application, "request": request}
    if kwargs:
        controller_kwargs.update(kwargs)

    controller = controller_class(**controller_kwargs)

    controller.write = MagicMock()
    controller.set_status = MagicMock()

    return controller
