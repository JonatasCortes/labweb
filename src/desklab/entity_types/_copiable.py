from ._entity import Entity
from abc import abstractmethod
from typing import Any, Self


class CopiableEntity(Entity):

    @abstractmethod
    def copy(self, *args: Any, **kwargs: Any) -> Self:
        error = f"ERROR: 'copy' can't be called directly from {self.__class__.__name__}"
        raise NotImplementedError(error)
