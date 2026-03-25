# Copyright (C) 2018-2026 by xcentaurix
# License: GNU General Public License v3.0 (see LICENSE file for details)


from enigma import eTimer
from Components.Sources.COCDiskSpace import COCDiskSpace
from Plugins.SystemPlugins.CacheCockpit.FileManager import FileManager
from Plugins.SystemPlugins.MountCockpit.MountCockpit import MountCockpit
from .FileProgress import FileProgress
from .FileManagerUtils import FILE_OP_DELETE, FILE_OP_LOAD, file_op_msg
from .Debug import logger
from .__init__ import _
from .Version import ID
from .SkinUtils import getSkinPath
from .FileUtils import readFile


FILE_OP_MGR_TIMER_DELAY = 1000
CACHE_LOAD_TIMER_DELAY = 500


class FileManagerProgress(FileProgress):
    skin = readFile(getSkinPath("FileManagerProgress.xml"))

    def __init__(self, session, file_op=FILE_OP_DELETE):
        logger.debug("...")
        self.file_op = file_op
        FileProgress.__init__(self, session)
        self.setTitle(_("File operation(s)") + " ...")
        self["DiskSpace"] = COCDiskSpace(self)
        self.activity_timer = eTimer()
        self.activity_timer.callback.append(self.doActivityTimer)
        self.activity_timer_delay = CACHE_LOAD_TIMER_DELAY if self.file_op == FILE_OP_LOAD else FILE_OP_MGR_TIMER_DELAY
        self.onShow.append(self.onDialogShow)
        self.request_cancel = False
        self.cancelled = False

    def onDialogShow(self):
        logger.debug("...")
        self.execFileManagerProgress()

    def cancel(self):
        logger.debug("...")
        self.request_cancel = True
        if self.file_op == FILE_OP_LOAD:
            FileManager.getInstance(ID).cancelLoading()
        else:
            FileManager.getInstance(ID).cancelJobs()

    def exit(self):
        logger.debug("...")
        if self.cancelled or not self.total_files:
            self.close(True)
        else:
            self.close(False)

    def toggleHide(self):
        if self.total_files and not self.request_cancel:
            self.close()

    def checkJobs(self):
        file_name = ""
        progress = 0
        if self.file_op == FILE_OP_LOAD:
            jobs, file_name, file_op, progress = FileManager.getInstance(ID).getProgress()
        else:
            jobs, file_name, file_op, progress = FileManager.getInstance(ID).getJobsProgress()
        logger.debug("jobs: %d, file_name: %s, file_op: %d, progress: %d", jobs, file_name, file_op, progress)
        return jobs, file_name, file_op, progress

    def updateProgress(self):
        logger.debug("...")
        self["operation"].setText(self.msg)
        self["name"].setText(self.op_msg)
        self["slider1"].setValue(self.file_progress)
        self["status"].setText(self.status)

    def doActivityTimer(self):
        logger.debug("...")
        self.total_files, self.file_name, self.file_op, self.file_progress = self.checkJobs()
        self.msg = _("Remaining files") + f": {self.total_files}"
        if self.request_cancel:
            self["key_red"].setText("")
            self["key_blue"].setText("")
            if self.total_files:
                self["key_green"].setText("")
                self.status = _("Cancelling, please wait") + "..."
                self.activity_timer.start(self.activity_timer_delay, True)
            else:
                self["key_green"].setText(_("Close"))
                self.op_msg = ""
                self.status = _("Cancelled") + "."
                self.request_cancel = False
                self.cancelled = True
        elif self.total_files:
            self.status = _("Please wait") + " ..."
            self.op_msg = file_op_msg[self.file_op]
            self.op_msg += ": " + self.file_name if self.file_name else ""
            self.activity_timer.start(self.activity_timer_delay, True)
        else:
            self["key_red"].setText("")
            self["key_blue"].setText("")
            self["key_green"].setText(_("Close"))
            self.op_msg = ""
            self.status = _("Done") + "."
            self.op_msg = _("No file operation in process")
        self.updateProgress()

    def execFileManagerProgress(self):
        self.doActivityTimer()

    def getBookmarksSpaceInfo(self):
        return MountCockpit.getInstance().getBookmarksSpaceInfo(ID)
