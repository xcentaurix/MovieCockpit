# Copyright (C) 2018-2026 by xcentaurix
# License: GNU General Public License v3.0


from enigma import eServiceEvent
from Components.config import config
from Screens.Setup import Setup
from .__init__ import _
from .Version import PLUGIN
from .Debug import logger, log_levels, setLogLevel


class SetupScreen(Setup):

    def __init__(self, session):
        Setup.__init__(self, session, setup="moviecockpit", plugin="Extensions/MovieCockpit", PluginLanguageDomain=PLUGIN)
        self.setTitle(PLUGIN + " - " + _("Setup"))

    def keySave(self):
        setLogLevel(log_levels[config.plugins.moviecockpit.debug_log_level.value])
        SetupScreen.setEPGLanguage(config.plugins.moviecockpit.epglang)
        Setup.keySave(self)

    @staticmethod
    def setEPGLanguage(element):
        logger.debug("epglang: %s", element.value)
        eServiceEvent.setEPGLanguage(element.value)
