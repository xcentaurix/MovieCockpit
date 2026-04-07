# Copyright (C) 2018-2026 by xcentaurix
# License: GNU General Public License v3.0 (see LICENSE file for details)


from Screens.MessageBox import MessageBox
from .Version import PLUGIN, VERSION, COPYRIGHT, LICENSE
from .__init__ import _


def about(session):
    message = (
        f"{_('Plugin')}: {PLUGIN}\n\n"
        f"{_('Version')}: {VERSION}\n\n"
        f"{_('Copyright')}: {COPYRIGHT}\n\n"
        f"{_('License')}: {LICENSE}"
    )
    session.open(
        MessageBox,
        message,
        MessageBox.TYPE_INFO
    )
