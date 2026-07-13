# Copyright (C) 2018-2026 by xcentaurix
# License: GNU General Public License v3.0


from enigma import eServiceCenter, eServiceEvent
from Tools.ISO639 import LanguageCodes
from .Debug import logger
from .ServiceUtils import getService


def _to_iso639_3(alpha):
    """Normalise a 2- or 3-letter language code to the lowercase 3-letter
    ISO 639-2 form eServiceEvent.setEPGLanguage() expects.

    eServiceEvent matches this against the DVB descriptor's own 3-letter
    code with a plain substring check LICENSE eServiceEvent::loadLanguage) - a
    bare 2-letter code like "en" is never a match for the "eng" the
    descriptor actually carries, so this must resolve to 3 letters first.
    An empty/unrecognised input passes through as-is, which reproduces
    core's own "no preference, use whichever language appears first" path.
    """
    key = alpha.lower()[:2]
    if key in LanguageCodes:
        target = LanguageCodes[key]
        for code, name in LanguageCodes.items():
            if name == target and len(code) == 3:
                return code.lower()
    return alpha.lower()


class ParserEitFile():
    """Reads a recording's .eit sidecar file (the raw DVB-SI EIT event
    descriptor enigma2 writes next to a recording).

    Thin wrapper around enigma2's own EIT parser (eServiceEvent, reached via
    iStaticServiceInformation.getEvent() exactly the way MovieList.py and
    friends do) instead of hand-decoding MJD dates, BCD time and DVB-SI
    descriptor bytes ourselves - eStaticServiceDVBPVRInformation.getEvent()
    (servicedvb.cpp) / eStaticServiceMP3Info.getEvent() (servicemp3.cpp)
    already do exactly that for a non-URL service reference, including
    genre/parental/linkage descriptors this file never actually implemented
    (content_descriptor here used to be a stub that just appended "n/a").

    eServiceEvent's language selection is process-global static state, not a
    per-call parameter - setEPGLanguage() below changes it for every EPG
    lookup in the process, not just this one, until something else (e.g. the
    system EPG language setting) changes it again. There's no getter to save
    and restore the previous value around this call. In practice this only
    matters if the caller's *epglang* genuinely differs from the box's
    system EPG language.
    """

    def __init__(self, path, epglang):
        self.eit = {}
        try:
            serviceref = getService(path)
            info = eServiceCenter.getInstance().info(serviceref)
            if info is None:
                return
            eServiceEvent.setEPGLanguage(_to_iso639_3(epglang or ""))
            event = info.getEvent(serviceref)
        except Exception as exc:
            logger.error("exception: %s", exc)
            return
        if event is None:
            return

        self.eit["event_id"] = event.getEventId()
        self.eit["start"] = event.getBeginTime()
        self.eit["length"] = event.getDuration()
        running_status = event.getRunningStatus()
        if running_status in {1, 2}:
            self.eit["when"] = "NEXT"
        elif running_status in {3, 4}:
            self.eit["when"] = "NOW"
        self.eit["content"] = event.getGenreDataList()
        self.eit["name"] = event.getEventName()
        self.eit["short_description"] = event.getShortDescription()
        self.eit["description"] = event.getExtendedDescription()

    def getEit(self):
        if self.eit:
            if self.eit["short_description"].startswith(self.eit["name"]):
                self.eit["short_description"] = self.eit["short_description"][len(self.eit["name"]) + 1:]
            self.eit["short_description"] = self.eit["short_description"].replace("\n", ", ")
        return self.eit
