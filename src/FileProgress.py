# Copyright (C) 2018-2026 by xcentaurix
# License: GNU General Public License v3.0 (see LICENSE file for details)


from Components.ActionMap import ActionMap
from Components.Label import Label
from Components.Slider import Slider
from Screens.Screen import Screen
from .__init__ import _
from .Debug import logger


class FileProgress(Screen):

    def __init__(self, session):
        logger.debug("...")
        Screen.__init__(self, session)

        self["slider1"] = Slider(0, 100)

        self["status"] = Label("")
        self["name"] = Label("")
        self["operation"] = Label("")

        self["key_red"] = Label(_("Cancel"))
        self["key_green"] = Label(_("Close"))
        self["key_green"].setText("")
        self["key_yellow"] = Label("")
        self["key_blue"] = Label(_("Hide"))

        self["actions"] = ActionMap(
            ["OkCancelActions", "ColorActions"],
            {"ok": self.exit, "cancel": self.exit, "red": self.cancel, "green": self.exit, "yellow": self.noop, "blue": self.toggleHide}
        )

        self.execution_list = []
        self.total_files = 0
        self.current_files = 0
        self.file_progress = 0
        self.file_name = ""
        self.status = ""
        self.request_cancel = False
        self.cancelled = False
        self.hidden = False

    def noop(self):
        return

    def cancel(self):
        if self.hidden:
            logger.debug("unhide")
            self.toggleHide()
        elif self.cancelled or (self.current_files > self.total_files):
            self.exit()
        else:
            logger.debug("trigger")
            self.request_cancel = True
            self["key_red"].setText("")
            self["key_blue"].setText("")
            self["key_green"].setText("")
            self.status = _("Cancelling, please wait") + " ..."

    def exit(self):
        logger.info("...")
        if self.hidden:
            logger.debug("unhide")
            self.toggleHide()
        elif self.cancelled or (self.current_files > self.total_files):
            logger.debug("close")
            self.close()

    def toggleHide(self):
        if self.hidden:
            self.hidden = False
            self.show()
        else:
            self.hidden = True
            self.hide()

    def updateProgress(self):
        logger.debug("file_name: %s, current_files: %s, total_files: %s, status: %s", self.file_name, self.current_files, self.total_files, self.status)
        current_files = self.current_files if self.current_files <= self.total_files else self.total_files
        msg = _("Processing") + ": " + str(current_files) + " " + _("of") + " " + str(self.total_files) + " ..."
        self["operation"].setText(msg)
        self["name"].setText(self.file_name)
        percent_complete = int(round(float(self.current_files - 1) / float(self.total_files) * 100)) if self.total_files > 0 else 0
        self["slider1"].setValue(percent_complete)
        self["status"].setText(self.status)

    def completionStatus(self):
        return _("Done") + "."

    def doFileOp(self, _afile):
        logger.error("should not be called at all, as overridden by child")

    def nextFileOp(self):
        logger.debug("...")

        self.current_files += 1
        if self.request_cancel and (self.current_files <= self.total_files):
            self.current_files -= 1
            if self.hidden:
                self.toggleHide()
            self["key_red"].setText("")
            self["key_blue"].setText("")
            self["key_green"].setText(_("Close"))
            self.status = _("Cancelled") + "."
            self.cancelled = True
            self.updateProgress()
        elif self.execution_list:
            afile = self.execution_list.pop(0)
            self.status = _("Please wait") + " ..."
            self.doFileOp(afile)
        else:
            logger.debug("done.")
            if self.hidden:
                self.toggleHide()
            self["key_red"].setText("")
            self["key_blue"].setText("")
            self["key_green"].setText(_("Close"))
            if self.cancelled:
                self.status = _("Cancelled") + "."
            else:
                self.status = self.completionStatus()
            self.updateProgress()
