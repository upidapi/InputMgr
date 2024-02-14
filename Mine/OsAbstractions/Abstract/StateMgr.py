from Mine.ViritallKeys.VkEnum import KeyData
from abc import ABC, abstractmethod


class AbsStateMgr(ABC):
    @classmethod
    @abstractmethod
    def get_pressed_keys(cls) -> set[KeyData]:
        """
        gets the currently pressed keys

        this should include mouse buttons
        """

    @classmethod
    @abstractmethod
    def get_mouse_pos(cls) -> tuple[int, int]:
        """
        gets the current mouse pos
        """
