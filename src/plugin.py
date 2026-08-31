# Copyright (C) 2018-2026 by xcentaurix
# License: GNU General Public License v3.0


from Components.config import config
from Plugins.Plugin import PluginDescriptor
from Plugins.SystemPlugins.MountCockpit.MountCockpit import MountCockpit
from Screens.InfoBar import InfoBar
from Tools.BoundFunction import boundFunction
from .__init__ import _
from .Debug import logger
from .SkinUtils import loadPluginSkin
from .Version import ID, VERSION
from .SetupScreen import SetupScreen
from .MovieCockpit import MovieCockpit
from . import ConfigInit  # noqa: F401, pylint: disable=unused-import

loadPluginSkin()


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
            SetupScreen.setEPGLanguage(
                config.plugins.moviecockpit.epglang)
            MountCockpit.getInstance().registerBookmarks(
                ID, config.plugins.moviecockpit.bookmarks.value)
    elif reason == 1:  # shutdown
        logger.info("--- shutdown")


def Plugins(**__):
    descriptors = [
        PluginDescriptor(
            where=[
                PluginDescriptor.WHERE_AUTOSTART,
                PluginDescriptor.WHERE_SESSIONSTART,
            ],
            # StartEnigma.py runs WHERE_SESSIONSTART plugins in ascending
            # PluginDescriptor.weight order (default 0); a positive weight
            # here guarantees our InfoBar.showMovies patch below is applied
            # after other movie-list plugins (e.g. EnhancedMovieCenter, which
            # patches the same hook at weight 0), so PVR/Video always opens
            # MovieCockpit regardless of Plugins/Extensions scan order.
            weight=1,
            fnc=autoStart,
            needsRestart=True
        ),
        PluginDescriptor(
            name="MovieCockpit",
            description=_("Manage recordings"),
            icon="MovieCockpit.png",
            where=[
                PluginDescriptor.WHERE_PLUGINMENU,
            ],
            fnc=openMovieCockpit,
            needsRestart=True
        )
    ]
    return descriptors
