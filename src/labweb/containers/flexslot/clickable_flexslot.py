from src.labweb.area import ClickableArea
from src.labweb.containers.flexslot.protected_flexslot import ProtectedFlexSlot


class ClickableFlexSlot(ProtectedFlexSlot, ClickableArea):

    def copy(self) -> "ClickableFlexSlot":
        instance = self._copy()
        assert isinstance(instance, self.__class__)
        return instance
