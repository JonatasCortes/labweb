from typing import Any, Optional

import pygame
from pygame import Surface
from src.labweb.entities import Entity, DimensionableEntity
from src.labweb.text import Text
from src.labweb.color import Color
from src.labweb.containers.clickable_flexbox import ClickableFlexBox
from src.labweb.containers.flexbox import FlexBox
from src.labweb.system.mouse import Mouse
from src.labweb.system.keyboard import KeyBoard
from src.labweb.system.clipboard import ClipBoard
import time


class _TextInputCell(FlexBox):

    def __init__(self, value: str | Text, max_width: int, max_height: int, background_color: Color | tuple[int, int, int] | str, text_color: Color | tuple[int, int, int] | str) -> None:
        text = value if isinstance(value, Text) else Text(value,
                                                          color=text_color)
        text = text.maximize(max_width, max_height)
        super().__init__(text.get_width(), text.get_height(), 0, 0, "ROW",
                         "CENTER", "CENTER", 0, background_color, True)
        self.__text = text
        self.add(text)
        self.__is_selected = False
        self.__defauld_background_color = background_color
        self.__default_text_color = text_color

    def is_selected(self) -> bool:
        return self.__is_selected

    def switch_selection_status(self) -> None:
        self.__is_selected = not self.__is_selected

    def handle_selection(self) -> None:
        if self.is_selected():
            self.set_color("BLUE")
            self.__text.set_color("WHITE")
            return
        self.set_color(self.__defauld_background_color)
        self.__text.set_color(self.__default_text_color)


class _TextInputContainer(FlexBox):

    def __init__(self,
                 width: int,
                 height: int,
                 corners_radius: tuple[int, int, int, int] | int,
                 color: Color | tuple[int, int, int] | str,
                 text_color: Color | tuple[int, int, int] | str) -> None:

        super().__init__(width, height, 0, 0, "ROW", "LEFT",
                         "CENTER", corners_radius, color, True)
        self.set_text_color(text_color)

    def set_text_color(self, color: Color | tuple[int, int, int] | str):
        self.__text_color = color if isinstance(color, Color) else Color(color)

    def get_text_color(self) -> Color:
        return self.__text_color

    def add_cell(self, text: str) -> None:
        cell = _TextInputCell(text, self.get_width(),
                              self.get_height(),
                              self.get_color(),
                              self.get_text_color())
        self.add(cell)

    def force_cell_append(self, text: str):
        while True:
            try:
                self.add_cell(text)
                return
            except ValueError:
                new_cells_list = self.get_children()[1::]
                self.set_children(new_cells_list)

    def delete_last_word(self):
        while len(self.get_children()) > 0:
            removed_cell = self.pop()
            char = self.__retrieve_character_from_cell(removed_cell)
            if char == " ":
                break

    def __retrieve_character_from_cell(self, cell: Optional[Entity]) -> Optional[str]:
        if not isinstance(cell, _TextInputCell):
            return

        removed_text_instance = cell.pop()
        if not isinstance(removed_text_instance, Text):
            return

        return removed_text_instance.get_text()


class TextInput(ClickableFlexBox):

    __HORIZONTAL_PADDING_PERCENTAGE = 5
    __VERTICAL_PADDING_PERCENTAGE = 33
    __CURSOR_HIDING_DELAY = 0.5

    def __init__(self,
                 width: int,
                 height: int,
                 corners_radius: tuple[int, int, int, int] | int = 0,
                 background_color: Color | tuple[int,
                                                 int, int] | str = "WHITE",
                 text_color: Color | tuple[int, int, int] | str = "BLACK") -> None:

        super().__init__(width, height, 0, 0, "ROW", "CENTER", "CENTER",
                         corners_radius, background_color, True)
        self.__set_text_container(text_color)
        self.__is_focused = False
        self.__text = ""
        self.__cursor_index = 0
        self.__display_cursor = False
        self.__last_key_press_time = time.time()

    def is_focused(self) -> bool:
        return self.__is_focused

    def __get_cursor_rect(self) -> tuple[int, ...]:

        cursor_y = self.__text_container.get_y()
        cursor_x = self.__text_container.get_x()
        for letter in self.__text_container.get_children()[:self.__cursor_index+1]:
            if isinstance(letter, DimensionableEntity):
                cursor_x += letter.get_width()
        cursor_width = 2
        cursor_height = self.__text_container.get_height()

        return (cursor_x, cursor_y, cursor_width, cursor_height)

    def __set_text_container(self, text_color: Color | tuple[int, int, int] | str) -> None:
        self.__text_container = _TextInputContainer(self.get_width() - self.__calcuate_horizontal_padding(),
                                                    self.get_height() - self.__calculate_vertical_padding(),
                                                    self.get_corners_radius(), self.get_color(), text_color)
        self._add(self.__text_container)

    def __calcuate_horizontal_padding(self) -> int:
        return self.__HORIZONTAL_PADDING_PERCENTAGE*self.get_width()//100

    def __calculate_vertical_padding(self) -> int:
        return self.__VERTICAL_PADDING_PERCENTAGE*self.get_height()//100

    def handle_event(self, *args: Any, **kwargs: Any):
        super().handle_event(*args, **kwargs)

        mouse = kwargs.get("mouse")
        keyboard = kwargs.get("keyboard")
        clipboard = kwargs.get("clipboard")

        if not isinstance(mouse, Mouse) or not isinstance(keyboard, KeyBoard) or not isinstance(clipboard, ClipBoard):
            raise RuntimeError(f"Expected a {Mouse.__name__} instance in kwargs with key 'mouse'",
                               f"Expected a {KeyBoard.__name__} instance in kwargs with key 'keyboard'",
                               f"Expected a {ClipBoard.__name__} instance in kwargs with key 'clipboard'")

        self.__add_focus_listener(mouse)
        self.__add_typing_listener(keyboard)
        self.__add_delete_listener(keyboard)
        self.__add_cursor_move_listener(keyboard)
        self.__add_cursor_display_listener(keyboard)

    def __add_focus_listener(self, mouse: Mouse):
        if self.is_clicked():
            self.__is_focused = True
            return
        elif mouse.is_clicked():
            self.__is_focused = False

    def __add_typing_listener(self, keyboard: KeyBoard):
        if not self.is_focused():
            return
        if keyboard.any_text_input():
            text = keyboard.last_input()
            if not text:
                return
            self.__text_container.force_cell_append(text)
            self.__text += text
            self.__cursor_index += len(text)

    def __add_delete_listener(self, keyboard: KeyBoard):

        if not self.is_focused() or not keyboard.key_down("backspace"):
            return
        elif not keyboard.ctrl_active() and not keyboard.meta_active():
            self.__text_container.pop()
            self.__text = self.__text[:-1]
            self.__cursor_index -= 1
        else:
            last_word = self.__text.split(" ")[-1]
            self.__cursor_index -= len(last_word)
            self.__text = " ".join(self.__text.split(" ")[:-1])
            self.__text_container.delete_last_word()

    def __add_cursor_move_listener(self, keyboard: KeyBoard):
        if not self.is_focused():
            return
        if keyboard.key_down("left"):
            self.__cursor_index -= 1
        elif keyboard.key_down("right"):
            self.__cursor_index += 1

    def __add_cursor_display_listener(self, keyboard: KeyBoard):
        current_time = time.time()

        if not self.is_focused():
            self.__display_cursor = False
            return

        if keyboard.any_key_pressed():
            self.__last_key_press_time = current_time
            self.__display_cursor = True
            return

        time_since_last_press = current_time - self.__last_key_press_time

        if time_since_last_press <= self.__CURSOR_HIDING_DELAY:
            self.__display_cursor = True
            return

        self.__display_cursor = int(current_time * 1.5) % 2 == 0

    def display(self, screen: Surface) -> None:
        super().display(screen)
        if self.__display_cursor:
            pygame.draw.rect(screen, (0, 0, 0), self.__get_cursor_rect())
