# Copyright (C) 2018-2026 by xcentaurix
# License: GNU General Public License v3.0 (see LICENSE file for details)


import os
from Components.config import config
from Components.PluginComponent import plugins
from Plugins.SystemPlugins.MountCockpit.MountCockpit import MountCockpit
from Plugins.Plugin import PluginDescriptor
from Screens.ChoiceBox import ChoiceBox
from Tools.BoundFunction import boundFunction
from .Version import ID
from .About import about
from .__init__ import _
from .Debug import logger


MENU_FUNCTIONS = 1
MENU_PLUGINS = 2


class CockpitContextMenu():
    def __init__(self, csel, session):
        self.csel = csel
        self.session = session
        logger.info("...")

    def menu(self, menu_mode, current_dir, service):
        self.menu_mode = menu_mode
        options = []
        if self.menu_mode == MENU_FUNCTIONS:

            if current_dir not in MountCockpit.getInstance().getMountedBookmarks(ID):
                options.append((_("Home"), boundFunction(
                    self.csel.changeDir, MountCockpit.getInstance().getHomeDir(ID))))
                options.append((_("Directory up"), boundFunction(
                    self.csel.changeDir, os.path.dirname(current_dir))))

            options.append((_("Delete"), self.csel.deleteMovies))
            options.append((_("Move"), self.csel.moveMovies))
            options.append((_("Copy"), self.csel.copyMovies))
            options.append((_("Create series directory"), self.csel.createSeriesDir))
            options.append((_("Move to series directory"), self.csel.moveToSeriesDir))

            options.append((_("Empty trashcan"), self.csel.emptyTrashcan))

            options.append((_("Delete cover"), self.csel.deleteCover))
            options.append((_("Bookmarks"), self.csel.openBookmarks))

            if config.plugins.moviecockpit.archive_enable.value:
                options.append((_("Archive"), self.csel.archiveFiles))
            options.append((_("Reload cache"), self.csel.reloadCache))
            options.append(
                (_("Remove all marks"), self.csel.removeCutListMarkers))
            options.append((_("Setup"), self.csel.openConfigScreen))
            options.append(
                (_("About"), boundFunction(about, self.session)))
        elif menu_mode == MENU_PLUGINS:
            if service is not None:
                for plugin in plugins.getPlugins(PluginDescriptor.WHERE_MOVIELIST):
                    options.append(
                        (plugin.description, boundFunction(plugin, self.session, service)))

        self.session.openWithCallback(
            self.menuCallback,
            ChoiceBox,
            title=_("Please select a function") if self.menu_mode == MENU_FUNCTIONS else _("Please select a plugin"),
            list=options,
            keys=[]
        )

    def menuCallback(self, current_entry):
        if current_entry is not None:
            current_entry[1]()  # execute function
