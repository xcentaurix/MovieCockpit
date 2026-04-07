# Copyright (C) 2018-2026 by xcentaurix
# License: GNU General Public License v3.0 (see LICENSE file for details)


import os
import time
from shlex import quote
from enigma import eConsoleAppContainer
from Plugins.SystemPlugins.CacheCockpit.FileManager import FileManager
from .Debug import logger
from .FileUtils import readFile
from .ConfigInit import sort_modes
from .Version import ID


class Sorting():

    def __init__(self):
        self.container = eConsoleAppContainer()

    def updateSortMode(self, adir, sort):
        logger.info("adir: %s, sort: %s", adir, sort)
        sort = f"{int(time.time())},{sort}"
        FileManager.getInstance(ID).update(adir, sort=sort)
        self.writeSortFile(adir, sort)

    def getSortMode(self, adir):
        logger.info("adir: %s", adir)
        return FileManager.getInstance(ID).getSortMode(adir)

    def writeSortFile(self, adir, sort):
        logger.info("adir: %s, sort: %s", adir, sort)
        cmd = f"echo '{sort}' > {os.path.join(quote(adir), '.sort')}"
        self.container.execute(cmd)

    def readSortFile(self, adir):
        logger.info("adir: %s", adir)
        sort = readFile(os.path.join(adir, ".sort"))
        return sort

    def toggleSortMode(self, adir):
        logger.info("adir: %s", adir)
        sort_mode = self.getSortMode(adir)
        sort_mode = str((int(sort_mode) + 2) % len(sort_modes))
        self.updateSortMode(adir, sort_mode)
        return sort_mode

    def toggleSortOrder(self, adir):
        logger.info("adir: %s", adir)
        sort_mode = self.getSortMode(adir)
        mode, order = sort_modes[sort_mode][0]
        order = not order
        for mode_id, sort_mode in list(sort_modes.items()):
            if sort_mode[0] == (mode, order):
                sort_mode = mode_id
                self.updateSortMode(adir, sort_mode)
                break
        return sort_mode
