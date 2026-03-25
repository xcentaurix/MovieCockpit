# Copyright (C) 2018-2026 by xcentaurix
# License: GNU General Public License v3.0 (see LICENSE file for details)


import os
from Components.config import config, ConfigSet, ConfigDirectory, ConfigNumber, ConfigSelection, ConfigSelectionNumber, ConfigYesNo, ConfigSubsection, ConfigNothing, NoSave
from Components.Language import language
from .Debug import logger, log_levels, initLogging
from .__init__ import _
from .LanguageSelection import LanguageSelection
from .MovieCoverDownloadUtils import choices_cover_source


# date format is implemented using datetime.strftime
choices_date = [
    ("%d.%m.%Y", _("DD.MM.YYYY")),
    ("%a %d.%m.%Y", _("WD DD.MM.YYYY")),

    ("%d.%m.%Y %H:%M", _("DD.MM.YYYY HH:MM")),
    ("%a %d.%m.%Y %H:%M", _("WD DD.MM.YYYY HH:MM")),

    ("%d.%m. %H:%M", _("DD.MM. HH:MM")),
    ("%a %d.%m. %H:%M", _("WD DD.MM. HH:MM")),

    ("%Y/%m/%d", _("YYYY/MM/DD")),
    ("%a %Y/%m/%d", _("WD YYYY/MM/DD")),

    ("%Y/%m/%d %H:%M", _("YYYY/MM/DD HH:MM")),
    ("%a %Y/%m/%d %H:%M", _("WD YYYY/MM/DD HH:MM")),

    ("%m/%d %H:%M", _("MM/DD HH:MM")),
    ("%a %m/%d %H:%M", _("WD MM/DD HH:MM"))
]


choices_dir_info = [
    ("", _("off")),
    ("D", _("Description")),  # Description
    ("C", _("(#)")),  # Count
    ("CS", _("(#/GB)")),  # Count/Size
    ("S", _("(GB)"))  # Size
]


# pylint: disable=consider-using-namedtuple-or-dataclass
sort_modes = {
    "0": (("date", False), _("Date sort down")),
    "1": (("date", True), _("Date sort up")),
    "2": (("alpha", False), _("Alpha sort up")),
    "3": (("alpha", True), _("Alpha sort down"))
}


choices_sort = [(k, v[1]) for k, v in list(sort_modes.items())]


choices_color_recording = [
    ("#ff1616", _("red")),
    ("#ff3838", _("light red")),
    ("#8B0000", _("dark red"))
]


choices_color_selection = [
    ("#ffffff", _("white")),
    ("#cccccc", _("light grey")),
    ("#bababa", _("grey")),
    ("#666666", _("dark grey")),
    ("#000000", _("black"))
]


choices_color_mark = [
    ("#cccc00", _("dark yellow")),
    ("#ffff00", _("yellow"))
] + choices_color_selection


def initBookmarks():
    logger.info("...")
    bookmarks = []
    for video_dir in config.movielist.videodirs.value:
        bookmarks.append(os.path.normpath(video_dir))
    logger.debug("bookmarks: %s", bookmarks)
    return bookmarks


class ConfigInit(LanguageSelection):

    def __init__(self):
        logger.info("...")
        LanguageSelection.__init__(self)
        lang = language.getActiveLanguage()
        logger.debug("lang: %s", lang)
        lang_choices = self.getLangChoices(lang)
        config.plugins.moviecockpit = ConfigSubsection()
        config.plugins.moviecockpit.fake_entry = NoSave(ConfigNothing())
        config.plugins.moviecockpit.timer_autoclean = ConfigYesNo(
            default=False)
        config.plugins.moviecockpit.cover_auto_download = ConfigYesNo(
            default=False)
        config.plugins.moviecockpit.cover_fallback = ConfigYesNo(default=True)
        config.plugins.moviecockpit.cover_source = ConfigSelection(
            default="tvs_id", choices=choices_cover_source)
        config.plugins.moviecockpit.epglang = ConfigSelection(
            default=lang[:2], choices=lang_choices)
        config.plugins.moviecockpit.list_start_home = ConfigYesNo(default=True)
        config.plugins.moviecockpit.movie_description_delay = ConfigNumber(
            default=200)
        config.plugins.moviecockpit.list_show_mount_points = ConfigYesNo(
            default=False)
        config.plugins.moviecockpit.movie_watching_percent = ConfigSelectionNumber(
            0, 30, 1, default=10)
        config.plugins.moviecockpit.movie_finished_percent = ConfigSelectionNumber(
            50, 100, 1, default=90)
        config.plugins.moviecockpit.movie_date_format = ConfigSelection(
            default="%d.%m.%Y %H:%M", choices=choices_date)
        config.plugins.moviecockpit.movie_resume_at_last_pos = ConfigYesNo(
            default=True)
        config.plugins.moviecockpit.movie_start_position = ConfigSelection(default="event_start", choices=[(
            "beginning", _("beginning")), ("first_mark", _("first mark")), ("event_start", _("event start"))])
        config.plugins.moviecockpit.trashcan_clean = ConfigYesNo(default=True)
        config.plugins.moviecockpit.trashcan_retention = ConfigSelectionNumber(
            0, 30, 1, default=3)
        config.plugins.moviecockpit.trashcan_show = ConfigYesNo(default=True)
        config.plugins.moviecockpit.trashcan_info = ConfigSelection(
            default="CS", choices=choices_dir_info)
        config.plugins.moviecockpit.list_content = ConfigNumber(default=1)
        config.plugins.moviecockpit.directories_info = ConfigSelection(
            default="CS", choices=choices_dir_info)
        config.plugins.moviecockpit.color = ConfigSelection(
            default="#bababa", choices=choices_color_selection)
        config.plugins.moviecockpit.color_sel = ConfigSelection(
            default="#ffffff", choices=choices_color_selection)
        config.plugins.moviecockpit.recording_color = ConfigSelection(
            default="#ff1616", choices=choices_color_recording)
        config.plugins.moviecockpit.recording_color_sel = ConfigSelection(
            default="#ff3838", choices=choices_color_recording)
        config.plugins.moviecockpit.selection_color = ConfigSelection(
            default="#cccc00", choices=choices_color_mark)
        config.plugins.moviecockpit.selection_color_sel = ConfigSelection(
            default="#ffff00", choices=choices_color_mark)
        config.plugins.moviecockpit.list_sort = ConfigSelection(
            default="0", choices=choices_sort)
        config.plugins.moviecockpit.debug_log_level = ConfigSelection(
            default="INFO", choices=list(log_levels.keys()))
        config.plugins.moviecockpit.archive_enable = ConfigYesNo(default=False)
        config.plugins.moviecockpit.archive_source_dir = ConfigDirectory(
            default="/media/hdd/movie")
        config.plugins.moviecockpit.archive_target_dir = ConfigDirectory(
            default="/media/hdd/movie")
        config.plugins.moviecockpit.database_directory = ConfigDirectory(
            default="/etc/enigma2")
        config.plugins.moviecockpit.piconspath = ConfigDirectory(default="/usr/share/enigma2/picon")

        config.plugins.moviecockpit.bookmarks = ConfigSet([], [])
        if not config.plugins.moviecockpit.bookmarks.value:
            config.plugins.moviecockpit.bookmarks.value = initBookmarks()
            config.plugins.moviecockpit.bookmarks.save()

        initLogging()
