# Copyright (C) 2018-2026 by xcentaurix
# License: GNU General Public License v3.0 (see LICENSE file for details)


import os
from datetime import datetime
from enigma import iServiceInformation
from Components.config import config
from Plugins.SystemPlugins.CacheCockpit.FileManager import FileManager
from .Debug import logger
from .FileManagerUtils import (
    FILE_TYPE_FILE, FILE_IDX_TYPE, FILE_IDX_NAME, FILE_IDX_EVENT_START_TIME,
    FILE_IDX_RECORDING_START_TIME, FILE_IDX_LENGTH, FILE_IDX_DESCRIPTION, FILE_IDX_EXTENDED_DESCRIPTION,
    FILE_IDX_SERVICE_REFERENCE, FILE_IDX_SIZE, COVER_IDX_COVER)
from .SkinUtils import getSkinPath
from .FileUtils import stripCutNumber, readFile
from .Version import ID


class ServiceCenter():

    def __init__(self, movie_list):
        self.movie_list = movie_list
        logger.debug("...")

    def info(self, service):
        logger.debug("...")
        return ServiceInfo(service, self.movie_list)


class ServiceInfo():

    def __init__(self, service, movie_list=None):
        logger.debug("service.getPath(): %s",
                     service.getPath() if service else None)
        self.info = Info(service, movie_list)

    def getLength(self, _service=None):
        logger.debug("..")
        return self.info.getLength()

    def getInfoString(self, _service=None, info_type=None):
        logger.debug("info_type: %s", info_type)
        if info_type == iServiceInformation.sServiceref:
            return self.info.getServiceReference()
        if info_type == iServiceInformation.sDescription:
            return self.info.getShortDescription()
        if info_type == iServiceInformation.sTags:
            return self.info.getTags()
        return None

    def getInfo(self, _service=None, info_type=None):
        logger.debug("info_type: %s", info_type)
        if info_type == iServiceInformation.sTimeCreate:
            return self.info.getEventStartTime()
        return None

    def getInfoObject(self, _service=None, info_type=None):
        logger.debug("info_type: %s", info_type)
        if info_type == iServiceInformation.sFileSize:
            return self.info.getSize()
        return None

    def getName(self, _service=None):
        logger.debug("...")
        return self.info.getName()

    def getEvent(self, _service=None):
        logger.debug("...")
        return self.info

    def getCover(self):
        logger.debug("...")
        return self.info.getCover()


class Info():

    def __init__(self, service, movie_list=None):
        logger.info("...")
        self.path = service.getPath()
        self.afile = movie_list and movie_list.getCurrentSelection()

    def getName(self):
        # EventName NAME
        name = ""
        if self.afile:
            name = self.afile[FILE_IDX_NAME]
        logger.debug("name: %s", name)
        return name

    def getServiceReference(self):
        logger.debug("...")
        service_reference = ""
        if self.afile:
            service_reference = self.afile[FILE_IDX_SERVICE_REFERENCE]
        return service_reference

    def getTags(self):
        logger.debug("...")
        tags = ""
        if self.afile:
            # tags = self.afile[FILE_IDX_TAGS]
            tags = ""
        return tags

    def getEventId(self):
        logger.debug("...")
        return 0

    def getEventName(self):
        logger.debug("...")
        return self.getName()

    def getShortDescription(self):
        logger.debug("...")
        # EventName SHORT_DESCRIPTION
        short_description = ""
        if self.afile:
            short_description = self.afile[FILE_IDX_DESCRIPTION]
        return short_description

    def getExtendedDescription(self):
        logger.debug("...")
        # EventName EXTENDED_DESCRIPTION
        extended_description = ""
        if self.afile:
            extended_description = self.afile[FILE_IDX_EXTENDED_DESCRIPTION]
        return extended_description

    def getBeginTimeString(self):
        logger.debug("...")
        stime = ""
        event_start_time = self.getEventStartTime()
        if event_start_time:
            movie_date_format = config.plugins.moviecockpit.movie_date_format.value
            stime = datetime.fromtimestamp(
                event_start_time).strftime(movie_date_format)
        return stime

    def getEventStartTime(self):
        logger.debug("...")
        event_start_time = 0
        if self.afile:
            event_start_time = self.afile[FILE_IDX_EVENT_START_TIME]
        return event_start_time

    def getRecordingStartTime(self):
        logger.debug("...")
        recording_start_time = 0
        if self.afile:
            recording_start_time = self.afile[FILE_IDX_RECORDING_START_TIME]
        return recording_start_time

    def getDuration(self):
        logger.debug("...")
        duration = 0
        if self.afile:
            duration = self.afile[FILE_IDX_LENGTH]
        return duration

    def getLength(self):
        return self.getDuration()

    def getSize(self):
        logger.debug("...")
        size = 0
        if self.afile and self.afile[FILE_IDX_TYPE] == FILE_TYPE_FILE:
            size = self.afile[FILE_IDX_SIZE]
        else:
            _count, size = FileManager.getInstance(ID).getCountSize(self.path)
        return size

    def getCover(self):
        logger.debug("...")
        cover = ""
        if self.afile:
            path = stripCutNumber(self.path)
            logger.debug("trying path: %s", path)
            bfile = FileManager.getInstance(ID).getFile(
                "table2", os.path.basename(path))
            if bfile:
                cover = bfile[COVER_IDX_COVER]
            if not cover:
                adir = os.path.dirname(path)
                adir_name = os.path.basename(adir)
                logger.debug("trying path: %s", os.path.join(adir, adir_name))
                bfile = FileManager.getInstance(
                    ID).getFile("table2", adir_name)
                if bfile:
                    cover = bfile[COVER_IDX_COVER]
            if not cover and config.plugins.moviecockpit.cover_fallback.value:
                cover = readFile(getSkinPath("images/no_cover.png"))
        return cover
