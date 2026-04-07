# Copyright (C) 2018-2026 by xcentaurix
# License: GNU General Public License v3.0 (see LICENSE file for details)


from .__init__ import _
from .Debug import logger
from .PluginUtils import getPlugin, WHERE_COVER_DOWNLOAD


choices_cover_source = [
    ("tvh_id", "HÖRZU"),
    ("tvfa_id", "TV Für Alle"),
    ("tvs_id", "TVSpielfilm"),
    ("tvm_id", "TVMovie"),
    ("auto", _("automatic"))
]


def downloadCover(target_path, service_str, event_start_time, event_duration, source_id, callback):
    plugin = getPlugin(WHERE_COVER_DOWNLOAD)
    if plugin:
        logger.debug("plugin.name: %s", plugin.name)
        plugin(
            target_path,
            service_str,
            event_start_time,
            event_duration,
            source_id,
            callback
        )
