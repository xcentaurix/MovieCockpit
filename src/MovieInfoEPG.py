# Copyright (C) 2018-2026 by xcentaurix
# License: GNU General Public License v3.0 (see LICENSE file for details)


from Components.Sources.COCServiceEvent import COCServiceEvent
from Components.Button import Button
from Components.ActionMap import ActionMap
from Screens.Screen import Screen
from .__init__ import _
from .SkinUtils import getSkinPath
from .FileUtils import readFile


class MovieInfoEPG(Screen):
    skin = readFile(getSkinPath("MovieInfoEPG.xml"))

    def __init__(self, session, name, service, movie_list, tmdb_plugin=None, mediathek_plugin=None):
        self.service = service
        Screen.__init__(self, session)
        self.setTitle(name)
        self["Service"] = COCServiceEvent(movie_list)
        self["Service"].newService(service)
        self["key_red"] = Button(_("Exit"))
        self["key_green"] = Button("")
        self["key_yellow"] = Button("")
        if tmdb_plugin:
            self["key_yellow"].setText("TMDB" + " " + _("Info"))
        self["key_blue"] = Button("")
        if mediathek_plugin:
            self["key_blue"].setText("Mediathek" + " " + _("Download"))
        self["my_actions"] = ActionMap(
            ["OkCancelActions", "CockpitActions"],
            {
                "cancel": self.close,
                "ok": self.close,
                "RED": self.close,
                "YELLOW": self.yellow,
                "BLUE": self.blue,
            }
        )

    def yellow(self):
        self.close("tmdb")

    def blue(self):
        self.close("mediathek")
