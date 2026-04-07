# Copyright (C) 2018-2026 by xcentaurix
# License: GNU General Public License v3.0 (see LICENSE file for details)


import pickle
from Plugins.SystemPlugins.CacheCockpit.FileManager import FileManager
from .Debug import logger
from .CutListUtils import packCutList, replaceLast, removeMarks
from .FileUtils import writeFile
from .FileManagerUtils import FILE_IDX_CUTS
from .Version import ID


class CutList():

    def __init__(self):
        return

    def updateCutList(self, path, last):
        logger.info("path: %s, last: %s", path, last)
        cut_list = replaceLast(self.readCutList(path), last)
        self.writeCutList(path, cut_list)

    def removeCutListMarks(self, path):
        cut_list = removeMarks(self.readCutList(path))
        logger.info("path: %s, cut_list: %s", path, cut_list)
        self.writeCutList(path, cut_list)

    def readCutList(self, path):
        cut_list = []
        afile = FileManager.getInstance(ID).getFile("table1", path)
        if afile and afile[FILE_IDX_CUTS]:
            cut_list = pickle.loads(afile[FILE_IDX_CUTS])
        logger.info("cut_list: %s", cut_list)
        return cut_list

    def writeCutList(self, path, cut_list):
        logger.info("path: %s, cut_list: %s", path, cut_list)
        data = packCutList(cut_list)
        writeFile(path + ".cuts", data)
        data = pickle.dumps(cut_list)
        FileManager.getInstance(ID).update(path, cuts=data)
