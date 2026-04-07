# Copyright (C) 2018-2026 by xcentaurix
# License: GNU General Public License v3.0 (see LICENSE file for details)


import os
import pickle
from time import time
from datetime import datetime
from Components.config import config
from Components.GUIComponent import GUIComponent
from Components.MultiContent import MultiContentEntryText, MultiContentEntryPixmapAlphaBlend, MultiContentEntryProgress
from Tools.LoadPixmap import LoadPixmap
from enigma import eListbox, eListboxPythonMultiContent
from enigma import RT_HALIGN_LEFT, RT_HALIGN_RIGHT, RT_VALIGN_CENTER
from Plugins.SystemPlugins.MountCockpit.MountCockpit import MountCockpit
from Plugins.SystemPlugins.CacheCockpit.FileManager import FileManager
from skin import parseColor, parseFont, parseSize
from .Debug import logger
from .Version import ID
from .__init__ import _
from .CutListUtils import ptsToSeconds, getCutListLast
from .SkinUtils import getSkinPath
from .FileManagerUtils import FILE_TYPE_FILE, FILE_TYPE_DIR, FILE_TYPE_LINK
from .FileManagerUtils import FILE_IDX_TYPE, FILE_IDX_DIR, FILE_IDX_PATH, FILE_IDX_FILENAME, FILE_IDX_NAME, FILE_IDX_EVENT_START_TIME, FILE_IDX_LENGTH, FILE_IDX_SERVICE_REFERENCE, FILE_IDX_CUTS
from .FileManagerUtils import file_op_msg
from .ConfigInit import sort_modes
from .Sorting import Sorting
from .ServiceCenter import ServiceCenter
from .ServiceUtils import getPicon
from .RecordingUtils import isRecording, isDownloadRecording
from .JobUtils import getPendingJob


class MovieList(GUIComponent, Sorting, ServiceCenter):

    COMPONENT_ID = ""
    GUI_WIDGET = eListbox

    def __init__(self):
        logger.debug("...")
        GUIComponent.__init__(self)
        Sorting.__init__(self)
        ServiceCenter.__init__(self, self)
        self.file_list = []
        self.selection_list = []
        self.lock_list = {}
        self.file_list_index = {}
        self.load_dir = ""
        self.skinAttributes = None

        # Initialize the list
        self.l = eListboxPythonMultiContent()  # noqa: E741
        self.l.setBuildFunc(self.buildMovieListEntry)

        self.show_dirs = False
        self.insert_dirs = False
        self.recursive = False
        self.list_content = config.plugins.moviecockpit.list_content.value
        self.setListContent()

        self.color = parseColor(config.plugins.moviecockpit.color.value).argb()
        self.color_sel = parseColor(
            config.plugins.moviecockpit.color_sel.value).argb()
        self.recording_color = parseColor(
            config.plugins.moviecockpit.recording_color.value).argb()
        self.recording_color_sel = parseColor(
            config.plugins.moviecockpit.recording_color_sel.value).argb()
        self.selection_color = parseColor(
            config.plugins.moviecockpit.selection_color.value).argb()
        self.selection_color_sel = parseColor(
            config.plugins.moviecockpit.selection_color_sel.value).argb()

        self.pic_back = LoadPixmap(getSkinPath(
            "images/back.svg"), cached=True)
        self.pic_directory = LoadPixmap(getSkinPath(
            "images/dir.svg"), cached=True)
        self.pic_link = LoadPixmap(getSkinPath(
            "images/link.svg"), cached=True)
        self.pic_movie_default = LoadPixmap(getSkinPath(
            "images/movie_default.svg"), cached=True)
        self.pic_movie_watching = LoadPixmap(getSkinPath(
            "images/movie_watching.svg"), cached=True)
        self.pic_movie_finished = LoadPixmap(getSkinPath(
            "images/movie_finished.svg"), cached=True)
        self.pic_movie_rec = LoadPixmap(getSkinPath(
            "images/movie_rec.svg"), cached=True)
        self.pic_bookmark = LoadPixmap(getSkinPath(
            "images/bookmark.svg"), cached=True)
        self.pic_trashcan = LoadPixmap(getSkinPath(
            "images/trashcan.svg"), cached=True)
        self.pic_movie_deleted = LoadPixmap(getSkinPath(
            "images/deleted.svg"), cached=True)

        self.onSelectionChanged = []

    def postWidgetCreate(self, instance):
        instance.setWrapAround(True)
        instance.setContent(self.l)
        instance.selectionChanged.get().append(self.selectionChanged)

    def preWidgetRemove(self, instance):
        instance.setContent(None)

    def setListContent(self):
        config.plugins.moviecockpit.list_content.value = self.list_content
        config.plugins.moviecockpit.list_content.save()
        self.show_dirs = self.recursive = self.insert_dirs = False
        if self.list_content == 0:
            self.show_dirs = False
            self.recursive = False
            self.insert_dirs = False
        elif self.list_content == 1:
            self.show_dirs = True
            self.recursive = False
            self.insert_dirs = False
        elif self.list_content == 2:
            self.show_dirs = False
            self.recursive = True
            self.insert_dirs = False
        elif self.list_content == 3:
            self.show_dirs = False
            self.recursive = False
            self.insert_dirs = True
        logger.debug("list_content: %s, show_dirs: %s, recursive: %s",
                     self.list_content, self.show_dirs, self.recursive)

    def nextListContent(self):
        self.list_content = self.list_content + 1 if self.list_content < 3 else 0
        self.setListContent()
        self.loadList()

    def previousListContent(self):
        self.list_content = self.list_content - 1 if self.list_content else 3
        self.setListContent()
        self.loadList()

    def selectionChanged(self):
        logger.debug("...")
        for function in self.onSelectionChanged:
            function()

    # move functions

    def moveUp(self, n=1):
        for _i in range(int(n)):
            self.instance.moveSelection(self.instance.moveUp)

    def moveDown(self, n=1):
        for _i in range(int(n)):
            self.instance.moveSelection(self.instance.moveDown)

    def pageUp(self):
        self.instance.moveSelection(self.instance.pageUp)

    def pageDown(self):
        self.instance.moveSelection(self.instance.pageDown)

    def moveTop(self):
        self.instance.moveSelection(self.instance.moveTop)

    def moveEnd(self):
        self.instance.moveSelection(self.instance.moveEnd)

    def moveToIndex(self, index):
        self.instance.moveSelectionTo(index)

    def moveToPath(self, path):
        index = self.getFileIndex(path)
        self.moveToIndex(index)
        return index

    def moveBouquetPlus(self):
        self.moveTop()

    def moveBouquetMinus(self):
        self.moveEnd()

    def moveToInitialSelection(self, selection_path):
        logger.info("selection_path: %s", selection_path)
        index = self.moveToPath(selection_path)
        if index < 0:
            if self.list_content == 3:
                if config.plugins.moviecockpit.trashcan_show.value:
                    index = 1
                else:
                    index = 0
                self.moveToIndex(index)
            else:
                while index < len(self.file_list) - 1:
                    if self.file_list[index][FILE_IDX_TYPE] != FILE_TYPE_FILE:
                        index += 1
                    else:
                        self.moveToIndex(index)
                        break
                else:
                    afile = self.getCurrentSelection()
                    if afile and afile[FILE_IDX_FILENAME] == ".." and len(self.file_list) > 1:
                        self.moveToIndex(1)

    # selection functions

    def getSelectionList(self):
        if not self.selection_list:
            # if no selections were made, add the current cursor position
            path = self.getCurrentPath()
            if path and not path.endswith("..") and path not in self.lock_list:
                self.selectPath(path)
        selection_list = self.selection_list[:]
        return selection_list

    def selectPath(self, path):
        logger.debug("path: %s", path)
        if path and not path.endswith("..") and path not in self.selection_list:
            self.selection_list.append(path)
            index = self.getFileIndex(path)
            if index > -1:
                self.invalidateEntry(index)

    def unselectPath(self, path):
        logger.debug("path: %s", path)
        if path in self.selection_list:
            self.selection_list.remove(path)
            index = self.getFileIndex(path)
            if index > -1:
                self.invalidateEntry(index)

    def selectAll(self):
        logger.debug("...")
        for afile in self.file_list:
            self.selectPath(afile[FILE_IDX_PATH])

    def unselectAll(self):
        logger.debug("...")
        selection_list = self.selection_list[:]
        for path in selection_list:
            self.unselectPath(path)

    def toggleSelection(self):
        path = self.getCurrentPath()
        logger.debug("path: %s", path)
        logger.debug("selection_list: %s", self.selection_list)
        if path in self.selection_list and path not in self.lock_list:
            self.unselectPath(path)
        else:
            self.selectPath(path)
        self.moveDown()

    # list functions

    def getCurrentPath(self):
        path = ""
        current_selection = self.l.getCurrentSelection()
        if current_selection:
            path = current_selection[FILE_IDX_PATH]
        return path

    def getCurrentDir(self):
        directory = ""
        current_selection = self.l.getCurrentSelection()
        if current_selection:
            directory = current_selection[FILE_IDX_DIR]
        logger.debug("directory: %s", directory)
        return directory

    def getFile(self, path):
        afile = []
        if not path:
            path = self.getCurrentPath()
        index = self.getFileIndex(path)
        if index > -1:
            afile = self.file_list[index]
        return afile

    def getFileIndex(self, path):
        logger.info("path: %s", path)
        index = self.file_list_index.get(path, -1)
        return index

    def getCurrentIndex(self):
        return self.instance.getCurrentIndex()

    def getCurrentSelection(self):
        return self.l.getCurrentSelection()

    def invalidateList(self):
        self.lock_list = FileManager.getInstance(ID).getLockList()
        self.l.invalidate()

    def invalidateEntry(self, i):
        if i > -1:
            self.l.invalidateEntry(i)

    def filterDirList(self, dir_list):
        logger.info("...")
        filtered_list = []
        for adir in dir_list:
            path = adir[FILE_IDX_PATH]
            if self.list_content == 3 and not path.endswith("..") and "trashcan" not in path:
                if FileManager.getInstance(ID).getCountSize(path)[0] == 0:
                    logger.debug("skipping: %s", path)
                    continue
                if FileManager.getInstance(ID).getCountSize(path)[0] == 1:
                    alist = FileManager.getInstance(ID).getFileList(path)
                    if alist:
                        filtered_list.append(alist[0])
                        continue
            filtered_list.append(adir)
        return filtered_list

    def sortList(self, file_list, sort_mode, sort_order):
        logger.debug("sort_mode: %s, sort_order: %s", sort_mode, sort_order)

        if sort_mode == "date":
            if not sort_order:
                file_list.sort(key=lambda x: (
                    x[FILE_IDX_EVENT_START_TIME], x[FILE_IDX_NAME].lower()), reverse=True)
            else:
                file_list.sort(key=lambda x: (
                    x[FILE_IDX_EVENT_START_TIME], x[FILE_IDX_NAME].lower()))

        elif sort_mode == "alpha":
            if not sort_order:
                file_list.sort(key=lambda x: (
                    x[FILE_IDX_NAME].lower(), -x[FILE_IDX_EVENT_START_TIME]))
            else:
                file_list.sort(key=lambda x: (
                    x[FILE_IDX_NAME].lower(), x[FILE_IDX_EVENT_START_TIME]), reverse=True)

        return file_list

    def createListIndex(self, load_dir, file_list):
        all_load_dirs = MountCockpit.getInstance(
        ).getVirtualDirs(ID, [load_dir])
        file_list_index = {}
        for index, afile in enumerate(file_list):
            if afile[FILE_IDX_TYPE] == FILE_TYPE_DIR:
                for adir in all_load_dirs:
                    file_list_index[os.path.join(
                        adir, afile[FILE_IDX_FILENAME])] = index
            else:
                file_list_index[afile[FILE_IDX_PATH]] = index
        return file_list_index

    def loadList(self, load_dir=None, selection_path=None):
        logger.info("load_dir: %s, selection_path: %s",
                    load_dir, selection_path)
        if load_dir is None:
            load_dir = self.getCurrentDir()
        if self.recursive and "trashcan" not in load_dir:
            load_dir = MountCockpit.getInstance().getHomeDir(ID)
        if selection_path is None:
            selection_path = self.getCurrentPath()

        logger.info("load_dir: %s, selection_path: %s",
                    load_dir, selection_path)
        self.lock_list = FileManager.getInstance(ID).getLockList()
        self.selection_list = []
        header_list = []
        file_list = []
        dir_list = []
        if load_dir in MountCockpit.getInstance().getMountedBookmarks(ID):
            if config.plugins.moviecockpit.trashcan_show.value:
                trashcan_dir = os.path.join(load_dir, "trashcan")
                trashcan_file = list(FileManager.getInstance(
                    ID).newDirData(trashcan_dir, FILE_TYPE_DIR))
                trashcan_file[FILE_IDX_NAME] = _("trashcan")
                header_list.append(tuple(trashcan_file))
        elif load_dir:
            up_dir = os.path.join(load_dir, "..")
            up = FileManager.getInstance(ID).newDirData(up_dir, FILE_TYPE_DIR)
            header_list.append(up)
        if self.show_dirs:  # or os.path.basename(load_dir) == "trashcan":
            dir_list = FileManager.getInstance(ID).getDirList(load_dir)
            header_list += self.sortList(dir_list, "alpha", False)
        file_list = FileManager.getInstance(
            ID).getFileList(load_dir, self.recursive)
        if self.insert_dirs:
            file_list += self.filterDirList(
                FileManager.getInstance(ID).getDirList(load_dir))

        current_sort_mode = self.getSortMode(load_dir)
        sort_mode, sort_order = sort_modes[current_sort_mode][0]
        self.file_list = header_list + \
            self.sortList(file_list, sort_mode, sort_order)
        self.l.setList(self.file_list)
        self.file_list_index = self.createListIndex(load_dir, self.file_list)
        self.moveToInitialSelection(selection_path)
        self.load_dir = load_dir

    # skin functions

    def applySkin(self, desktop, parent):
        attribs = []
        value_attributes = [
            "row_height",
            "start",
            "spacer",
            "date_width",
        ]
        size_attributes = [
            "bar_size",
            "icon_size",
            "picon_size"
        ]
        font_attributes = [
            "font0",
            "font1",
            "font2"
        ]
        color_attributes = [
        ]

        if self.skinAttributes:
            for (attrib, value) in self.skinAttributes:
                if attrib in value_attributes:
                    setattr(self, attrib, int(value))
                elif attrib in size_attributes:
                    setattr(self, attrib, parseSize(value, ((1, 1), (1, 1))))
                elif attrib in font_attributes:
                    setattr(self, attrib, parseFont(value, ((1, 1), (1, 1))))
                elif attrib in color_attributes:
                    setattr(self, attrib, parseColor(value).argb())
                else:
                    attribs.append((attrib, value))
        self.skinAttributes = attribs

        logger.debug("self.skinAttributes: %s", self.skinAttributes)
        rc = GUIComponent.applySkin(self, desktop, parent)

        # Get widget width from instance
        self.width = self.instance.size().width()

        # Load progress bar images
        self.pic_progress_bar = LoadPixmap(getSkinPath(
            "images/progcl.svg"), cached=True)
        self.pic_rec_progress_bar = LoadPixmap(getSkinPath(
            "images/rec_progcl.svg"), cached=True)

        self.l.setItemHeight(self.row_height)

        # Set fonts if specified in template
        # self.l.setFont(i, gFont("Regular", size))
        self.l.setFont(0, self.font0)
        self.l.setFont(1, self.font1)
        self.l.setFont(2, self.font2)

        return rc

    # list build function

    def buildMovieListEntry(self, *args):
        afile = args  # args is the tuple containing all file info

        def getDateText(path, file_type, date):
            logger.debug("path: %s, file_type: %s, date: %s",
                         path, file_type, date)
            count = 0
            date_text = ""
            if path in self.lock_list:
                file_op = self.lock_list[path]
                date_text = file_op_msg[file_op]
            elif file_type in [FILE_TYPE_FILE]:
                if config.plugins.moviecockpit.list_show_mount_points.value:
                    words = path.split("/")
                    if len(words) > 3 and words[1] == "media":
                        date_text = words[2]
                elif date:
                    date_text = datetime.fromtimestamp(date).strftime(
                        config.plugins.moviecockpit.movie_date_format.value)
            else:
                if os.path.basename(path) == "trashcan":
                    info_value = config.plugins.moviecockpit.trashcan_info.value
                else:
                    info_value = config.plugins.moviecockpit.directories_info.value
                if os.path.basename(path) == "..":
                    date_text = _("up")
                elif info_value == "D":
                    if os.path.basename(path) == "trashcan":
                        date_text = _("trashcan")
                    else:
                        date_text = _("directory")
                else:
                    count, size = FileManager.getInstance(
                        ID).getCountSize(path)
                    count_text = f"{count:d}"

                    size /= (1024 * 1024 * 1024)  # GB
                    size_text = f"{size:.0f} GB"
                    if size >= 1024:
                        size_text = f"{size / 1024:.1f} TB"

                    if info_value == "C":
                        date_text = f"({count_text})"
                    elif info_value == "S":
                        date_text = f"({size_text})"
                    elif info_value == "CS":
                        date_text = f"({count_text}/{size_text})"
            logger.debug("count: %s, date_text: %s", count, date_text)
            return date_text

        def getProgress(is_recording, path, event_start_time, length, cuts):
            logger.debug("path: %s", path)
            progress = 0
            try:
                if isDownloadRecording(path):
                    job = getPendingJob("MTC", path)
                    progress = job.getProgress()
                else:
                    if is_recording:
                        last = time() - event_start_time
                    else:
                        # get last position from cut file
                        cut_list = pickle.loads(cuts) if cuts else []
                        logger.debug("cut_list: %s", cut_list)
                        last = ptsToSeconds(getCutListLast(cut_list))
                        logger.debug("last: %s", last)

                    if length > 0 and last > 0:
                        last = min(last, length)
                        progress = int(round(float(last) / float(length), 2) * 100)
            except Exception as e:
                logger.error("Error calculating progress for %s: %s", path, e)
                progress = 0

            logger.debug("progress: %s, path: %s, length: %s, is_recording: %s",
                         progress, path, length, is_recording)
            return progress

        def getFileIcon(path, file_type, progress, is_recording):
            pixmap = None
            if file_type == FILE_TYPE_FILE:
                pixmap = self.pic_movie_default
                if is_recording:
                    pixmap = self.pic_movie_rec
                elif progress >= int(config.plugins.moviecockpit.movie_finished_percent.value):
                    pixmap = self.pic_movie_finished
                elif progress >= int(config.plugins.moviecockpit.movie_watching_percent.value):
                    pixmap = self.pic_movie_watching
            elif file_type == FILE_TYPE_LINK:
                pixmap = self.pic_link
            elif file_type == FILE_TYPE_DIR:
                pixmap = self.pic_directory
                if os.path.basename(path) == "trashcan":
                    pixmap = self.pic_trashcan
                elif os.path.basename(path) == "..":
                    pixmap = self.pic_back
            return pixmap

        def getColor(path, _file_type, is_recording):
            color = self.color
            color_sel = self.color_sel
            if path in self.selection_list or path in self.lock_list:
                color = self.selection_color
                color_sel = self.selection_color_sel
            elif is_recording:
                color = self.recording_color
                color_sel = self.recording_color_sel
            return color, color_sel

        path = afile[FILE_IDX_PATH]
        file_type = afile[FILE_IDX_TYPE]
        event_start_time = afile[FILE_IDX_EVENT_START_TIME]
        name = afile[FILE_IDX_NAME]
        length = afile[FILE_IDX_LENGTH]
        service_reference = afile[FILE_IDX_SERVICE_REFERENCE]
        cuts = afile[FILE_IDX_CUTS]

        self.lock_list = FileManager.getInstance(ID).getLockList()

        is_recording = isRecording(path)
        color, color_sel = getColor(path, file_type, is_recording)
        progress = getProgress(is_recording, path, event_start_time,
                               length, cuts) if file_type in [FILE_TYPE_FILE] else -1
        progress_bar = self.pic_rec_progress_bar if is_recording else self.pic_progress_bar

        # Get picon with error handling
        picon = None
        if file_type in [FILE_TYPE_FILE]:
            try:
                picon = getPicon(service_reference)
            except Exception as e:
                logger.error("Error getting picon for %s: %s", path, e)

        name = _(name) if name == "trashcan" else name
        date_text = getDateText(path, file_type, event_start_time)
        file_icon = getFileIcon(path, file_type, progress, is_recording)

        res = [afile]

        # Calculate positions for compact single line: icon | picon | name | progress bar | date
        x_pos = self.start

        # Single line: icon | picon | name | progress bar | date

        # file icon
        if file_icon:
            res.append(MultiContentEntryPixmapAlphaBlend(
                pos=(x_pos, (self.row_height - self.icon_size.height()) // 2),
                size=(self.icon_size.width(), self.icon_size.height()), png=file_icon, flags=4))  # BT_SCALE = 4
            x_pos += self.icon_size.width() + self.spacer

        # picon
        if picon and file_type == FILE_TYPE_FILE:
            res.append(MultiContentEntryPixmapAlphaBlend(
                pos=(x_pos, (self.row_height - self.picon_size.height()) // 2),
                size=(self.picon_size.width(), self.picon_size.height()),
                png=picon, flags=4))  # BT_SCALE = 4
            x_pos += self.picon_size.width() + self.spacer

        # name
        res.append(MultiContentEntryText(
            pos=(x_pos, 0),
            size=(self.width - x_pos - self.bar_size.width() - self.date_width - self.spacer * 3, self.row_height),
            font=1, flags=RT_HALIGN_LEFT | RT_VALIGN_CENTER, text=name, color=color, color_sel=color_sel))

        # progress bar - always show for movie files
        if file_type == FILE_TYPE_FILE and progress_bar:
            res.append(MultiContentEntryProgress(
                pos=(self.width - self.bar_size.width() - self.date_width - 2 * self.spacer, (self.row_height - self.bar_size.height()) // 2),
                size=(self.bar_size.width(), self.bar_size.height()), percent=max(0, progress), borderWidth=1, foreColor=color))

        # date
        res.append(MultiContentEntryText(
            pos=(self.width - self.date_width - self.spacer, 0),
            size=(self.date_width, self.row_height),
            font=2, flags=RT_HALIGN_RIGHT | RT_VALIGN_CENTER, text=date_text, color=color, color_sel=color_sel))

        return res
