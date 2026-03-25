# Copyright (C) 2018-2026 by xcentaurix
# License: GNU General Public License v3.0 (see LICENSE file for details)


from Components.Button import Button
from Components.Label import Label
from Components.config import config
from Components.ActionMap import HelpableActionMap
from Components.Sources.StaticText import StaticText
from Tools.BoundFunction import boundFunction
from Plugins.SystemPlugins.MountCockpit.MountCockpit import MountCockpit
from .Version import ID
from .Debug import logger
from .__init__ import _


KEY_RED = 0
KEY_GREEN = 1
KEY_YELLOW = 2
KEY_BLUE = 3


KEY_LABEL = 0
KEY_FUNCTION = 1


class Actions():

    def __init__(self, csel):
        self.csel = csel
        self.csel["key_menu"] = StaticText(_("Setup"))
        self.csel["key_red"] = Button()
        self.csel["key_green"] = Button()
        self.csel["key_yellow"] = Button()
        self.csel["key_blue"] = Button()
        self.csel["level"] = Label()
        self.initColorActions(self)
        self.setColorButtons()

    # color button management functions

    def setColorButtons(self):
        self.csel["level"].setText(f"<{self.color_buttons_level + 1}>")

        red = self.color_buttons_matrix[self.color_buttons_level][KEY_RED]
        green = self.color_buttons_matrix[self.color_buttons_level][KEY_GREEN]
        yellow = self.color_buttons_matrix[self.color_buttons_level][KEY_YELLOW]
        blue = self.color_buttons_matrix[self.color_buttons_level][KEY_BLUE]

        self.csel["key_red"].setText(red[KEY_LABEL] if red else "")
        self.csel["key_green"].setText(green[KEY_LABEL] if green else "")
        self.csel["key_yellow"].setText(yellow[KEY_LABEL] if yellow else "")
        self.csel["key_blue"].setText(blue[KEY_LABEL] if blue else "")

    def nextColorButtonsLevel(self):
        self.color_buttons_level = (
            self.color_buttons_level + 1) % len(self.color_buttons_matrix)
        self.setColorButtons()

    def previousColorButtonsLevel(self):
        self.color_buttons_level = self.color_buttons_level - \
            1 if self.color_buttons_level > 0 else len(
                self.color_buttons_matrix) - 1
        self.setColorButtons()

    def resetColorButtonsLevel(self):
        self.color_buttons_level = 0
        self.setColorButtons()

    # key init

    def initActions(self, csel):
        actions = HelpableActionMap(
            csel,
            "CockpitActions",
            {
                "RED": (boundFunction(self.execColorButton, KEY_RED), _("Color key red")),
                "GREEN": (boundFunction(self.execColorButton, KEY_GREEN), _("Color key green")),
                "YELLOW": (boundFunction(self.execColorButton, KEY_YELLOW), _("Color key yellow")),
                "BLUE": (boundFunction(self.execColorButton, KEY_BLUE), _("Color key blue")),
                "OK": (csel.selectedEntry, _("Play")),
                "EXIT": (csel.exit, _("Exit")),
                "FASTFORWARD": (csel.movie_list.nextListContent, _("Next list content")),
                "REWIND": (csel.movie_list.previousListContent, _("Previous list content")),
                "POWER": (csel.exit, _("Exit")),
                "menu": (csel.openContextMenu, _("Context menu")),  # dummy for skin button label
                "MENUS": (csel.openContextMenu, _("Context menu")),
                "MENUL": (csel.openPluginsMenu, _("Plugins menu")),
                "INFOS": (csel.showMovieInfoEPG, _("EPG info")),
                "INFOL": (csel.showMovieInfoTMDB, _("TMDB info")),
                "LEFT": (csel.movie_list.pageUp, _("Cursor page up")),
                "RIGHT": (csel.movie_list.pageDown, _("Cursor page down")),
                "UP": (csel.movie_list.moveUp, _("Cursor up")),
                "DOWN": (csel.movie_list.moveDown, _("Cursor down")),
                "CHANNELUP": (csel.movie_list.moveBouquetPlus, _("Bouquet up")),
                "CHANNELDOWN": (csel.movie_list.moveBouquetMinus, _("Bouquet down")),
                "VIDEOS": (csel.toggleSelection, _("Selection on/off")),
                "VIDEOL": (csel.unselectAll, _("Selection off")),
                "STOP": (csel.stopRecordings, _("Stop recording(s)")),
                "NEXT": (csel.nextColorButtonsLevel, _("Color buttons next")),
                "PREVIOUS": (csel.previousColorButtonsLevel, _("Color buttons previous")),
                "0": (csel.goUp, _("Directory up")),
                "0L": (csel.goHome, _("Home")),
                "8": (csel.showFileManagerProgress, _("File operations progress")),
                "5": (csel.showRecordingInfo, _("Recording Info")),
            },
            prio=-3  # give them a little more priority to win over base class buttons
        )
        actions.csel = csel
        return actions

    def initColorActions(self, csel):
        logger.debug("...")
        self.color_buttons_matrix = [
            [                                                                           # level 0
                [_("Delete"), csel.deleteMovies],                                       # red
                [_("Sort mode"), csel.toggleSortMode],                                  # green
                [_("Move"), csel.moveMovies],                                           # yellow
                [_("Home"), boundFunction(csel.changeDir,
                                          MountCockpit.getInstance().getHomeDir(ID))]   # blue
            ],
            [                                                                           # level 1
                [_("Delete"), csel.deleteMovies],                                       # red
                [_("Sort order"), csel.toggleSortOrder],                                # green
                [_("Copy"), csel.copyMovies],                                           # yellow
                [_("Home"), boundFunction(csel.changeDir,
                                          MountCockpit.getInstance().getHomeDir(ID))]   # blue
            ],
            [                                                                           # level 2
                [_("Reload cache"), csel.reloadCache],                                  # red
                None,                                                                   # green (removed list type toggle)
                [_("Archive"), csel.archiveFiles],                                      # yellow
                [_("Bookmarks"), csel.openBookmarks]                                    # blue
            ],
            [                                                                           # level 3
                [_("Reset progress"), csel.resetProgress],                              # red
                [_("Date/Mount"), csel.toggleDateMount],                                # green
                [_("Timer list"), csel.openTimerList],                                  # yellow
                [_("Open setup"), csel.openConfigScreen],                               # blue
            ],
        ]
        self.color_buttons_matrix[1][KEY_RED] = [
            _("Empty trashcan"), csel.emptyTrashcan]
        if config.plugins.moviecockpit.archive_enable.value:
            self.color_buttons_matrix[2][KEY_YELLOW] = [
                _("Archive"), csel.archiveFiles]

    def setTrashcanActions(self, csel, path):
        logger.debug("path: %s", path)
        if path and "trashcan" in path:
            self.color_buttons_matrix[0][KEY_YELLOW] = [
                _("Restore"), csel.restoreMovies]
            self.color_buttons_matrix[0][KEY_BLUE] = [_("Home"), boundFunction(
                csel.changeDir, MountCockpit.getInstance().getHomeDir(ID))]
        else:
            self.color_buttons_matrix[0][KEY_YELLOW] = [
                _("Move"), csel.moveMovies]
            self.color_buttons_matrix[0][KEY_BLUE] = [
                _("Trashcan"), csel.openTrashcan]
        self.setColorButtons()

    # color button execution function

    def execColorButton(self, key):
        button = self.color_buttons_matrix[self.color_buttons_level][key]
        if button:
            button[KEY_FUNCTION]()
        self.resetColorButtonsLevel()
