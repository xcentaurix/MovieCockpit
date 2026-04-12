# Copyright (C) 2018-2026 by xcentaurix
# License: GNU General Public License v3.0 (see LICENSE file for details)


from Components.config import config
from Plugins.Plugin import PluginDescriptor
from Plugins.SystemPlugins.MountCockpit.MountCockpit import MountCockpit
from Plugins.SystemPlugins.CacheCockpit.FileManager import FileManager
from Screens.InfoBar import InfoBar
from Tools.BoundFunction import boundFunction
from .__init__ import _
from .Debug import logger
from .Version import ID, VERSION
from .SkinUtils import loadPluginSkin
from .ConfigScreenInit import ConfigScreenInit
from .MovieCockpit import MovieCockpit
from .ConfigInit import ConfigInit


def openMovieCockpit(session, **__):
    logger.info("...")
    session.openWithCallback(
        reloadMovieCockpit, MovieCockpit, InfoBar.instance)


def reloadMovieCockpit(session, reload_moviecockpit=False):
    if reload_moviecockpit:
        logger.info("...")
        openMovieCockpit(session)


def autoStart(reason, **kwargs):
    if reason == 0:  # startup
        if "session" in kwargs:
            logger.info("+++ Version: %s starts...", VERSION)
            session = kwargs["session"]
            InfoBar.showMovies = boundFunction(openMovieCockpit, session)
            ConfigScreenInit.setEPGLanguage(
                config.plugins.moviecockpit.epglang)
            MountCockpit.getInstance().registerBookmarks(
                ID, config.plugins.moviecockpit.bookmarks.value)
            loadPluginSkin("skin.xml")
    elif reason == 1:  # shutdown
        logger.info("--- shutdown")
        filemanager = FileManager.getInstance(ID)
        filemanager.purgeTrashcan(config.plugins.moviecockpit.trashcan_retention.value)
        filemanager.archive()


def Plugins(**__):
    ConfigInit()

    descriptors = [
        PluginDescriptor(
            where=[
                PluginDescriptor.WHERE_AUTOSTART,
                PluginDescriptor.WHERE_SESSIONSTART,
            ],
            fnc=autoStart
        ),
        PluginDescriptor(
            name="MovieCockpit",
            description=_("Manage recordings"),
            icon="MovieCockpit.png",
            where=[
                PluginDescriptor.WHERE_PLUGINMENU,
            ],
            fnc=openMovieCockpit
        )
    ]
    return descriptors
