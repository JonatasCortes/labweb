from typing import Callable, Any
from src.labweb.system import KeyBoard
from ._protected_interface import ProtectedListener
from src.labweb._utils import camel_case_to_snake_case


class _KeyboardListener(ProtectedListener):
    _condition_func: str = ""

    def __init_subclass__(cls, **kwargs: Any) -> None:
        super().__init_subclass__(**kwargs)
        if not cls._condition_func:
            base_name = cls.__name__.replace("Listener", "")
            cls._condition_func = camel_case_to_snake_case(base_name)

    def __init__(self, actions: Callable[..., Any] | list[Callable[..., Any]], **kwargs: Any) -> None:
        super().__init__(lambda: self.__check_keyboard_condition(**kwargs), actions)

    def __check_keyboard_condition(self, **kwargs: Any) -> bool:
        keyboard = kwargs.get("keyboard")
        if not isinstance(keyboard, KeyBoard):
            self._raise_for_missing_parameter("keyboard", KeyBoard.__name__)

        method = getattr(keyboard, self._condition_func)
        try:
            return bool(method(**kwargs))
        except TypeError:
            return bool(method())

    def get_actions(self) -> list[Callable[..., Any]]:
        return self._get_actions()

    def set_actions(self, actions: Callable[..., Any] | list[Callable[..., Any]]) -> None:
        return self._set_actions(actions)

    def add_actions(self, actions: Callable[..., Any] | list[Callable[..., Any]]) -> None:
        return self._add_actions(actions)


class KeyPressedListener(_KeyboardListener):
    def __init__(self, key: str, actions: Callable[..., Any] | list[Callable[..., Any]]) -> None:
        super().__init__(actions, key=key)


class KeyDownListener(_KeyboardListener):
    def __init__(self, key: str, actions: Callable[..., Any] | list[Callable[..., Any]]) -> None:
        super().__init__(actions, key=key)


class KeyUpListener(_KeyboardListener):
    def __init__(self, key: str, actions: Callable[..., Any] | list[Callable[..., Any]]) -> None:
        super().__init__(actions, key=key)


class CtrlActiveListener(_KeyboardListener):
    pass


class ShiftActiveListener(_KeyboardListener):
    pass


class AltActiveListener(_KeyboardListener):
    pass


class MetaActiveListener(_KeyboardListener):
    pass


class AnyKeyPressedListener(_KeyboardListener):
    pass


class AnyKeyDownListener(_KeyboardListener):
    pass


class AnyKeyUpListener(_KeyboardListener):
    pass


class AnyTextInputListener(_KeyboardListener):
    pass
