# Copyright (C) 2018-2026 by xcentaurix
# License: GNU General Public License v3.0 (see LICENSE file for details)


import os
from datetime import datetime
from Screens.Screen import Screen
from Screens.HelpMenu import HelpableScreen
from Components.config import config
from Components.Button import Button
from Components.Sources.List import List
from Components.ActionMap import HelpableActionMap
from .__init__ import _
from .SkinUtils import getSkinPath
from .FileManagerUtils import FILE_IDX_PATH, FILE_IDX_LENGTH, FILE_IDX_EVENT_START_TIME, FILE_IDX_RECORDING_START_TIME, FILE_IDX_RECORDING_STOP_TIME
from .ParserEitFile import ParserEitFile
from .ParserMetaFile import ParserMetaFile
from .FileUtils import readFile


class RecordingInfo(Screen, HelpableScreen):
    skin = readFile(getSkinPath("RecordingInfo.xml"))

    def __init__(self, session, afile):
        self.afile = afile
        Screen.__init__(self, session)
        HelpableScreen.__init__(self)

        self["actions"] = HelpableActionMap(
            self,
            "CockpitActions",
            {
                "OK": (self.exit, _("Exit")),
                "EXIT": (self.exit, _("Exit")),
                "RED": (self.exit, _("Exit")),
                "GREEN": (self.exit, _("Exit")),
            },
            prio=-1
        )

        self.setTitle(_("Recording Info"))
        self["list"] = List()
        self["key_green"] = Button(_("Exit"))
        self["key_red"] = Button(_("Cancel"))
        self["key_yellow"] = Button()
        self["key_blue"] = Button()
        self.onLayoutFinish.append(self.fillList)

    def exit(self):
        self.close()

    def fillList(self):
        path = self.afile[FILE_IDX_PATH]
        meta = ParserMetaFile(path).getMeta()
        epglang = config.plugins.moviecockpit.epglang.value
        eit = ParserEitFile(path, epglang).getEit()
        alist = []
        alist.append(("Path", path))
        alist.append(("Filename", os.path.basename(path)))
        alist.append(("", ""))
        alist.append(("SQL: Length", str(self.afile[FILE_IDX_LENGTH] / 60)))
        alist.append(("SQL: Event start", str(
            datetime.fromtimestamp(self.afile[FILE_IDX_EVENT_START_TIME]))))
        alist.append(("SQL: Recording start", str(
            datetime.fromtimestamp(self.afile[FILE_IDX_RECORDING_START_TIME]))))
        alist.append(("SQL: Recording stop", str(
            datetime.fromtimestamp(self.afile[FILE_IDX_RECORDING_STOP_TIME]))))
        alist.append(("", ""))
        alist.append(("EIT: File exists", str(
            os.path.exists(os.path.splitext(path)[0] + ".eit"))))
        if eit:
            alist.append(("EIT: Event Start", str(
                datetime.fromtimestamp(eit["start"]))))
            alist.append(("EIT: Length", str(eit["length"] / 60)))
        alist.append(("", ""))
        alist.append(("META: File exists", str(
            os.path.exists(path + ".meta"))))
        if meta:
            alist.append(("META: Rec time", str(
                datetime.fromtimestamp(meta["rec_time"]))))
        alist.append(("", ""))
        alist.append(("XMETA: File exists", str(
            os.path.exists(path + ".xmeta"))))
        if meta:
            alist.append(("XMETA: Recording start", str(
                datetime.fromtimestamp(meta["recording_start_time"]))))
            alist.append(("XMETA: Recording stop", str(
                datetime.fromtimestamp(meta["recording_stop_time"]))))
        self["list"].setList(alist)
        self["list"].master.downstream_elements.setSelectionEnabled(0)
