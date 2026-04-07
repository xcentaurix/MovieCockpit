# Copyright (C) 2018-2026 by xcentaurix
# License: GNU General Public License v3.0 (see LICENSE file for details)


import os
import struct
import time
import datetime
from Tools.ISO639 import LanguageCodes
from .Debug import logger
from .FileUtils import readFile


class ParserEitFile():

    def __init__(self, path, epglang):
        self.epglang = epglang
        self.eit = {}
        self.name_event_descriptor = []
        self.name_event_descriptor_multi = []
        self.name_event_codepage = None
        self.short_event_descriptor = []
        self.short_event_descriptor_multi = []
        self.short_event_codepage = None
        self.extended_event_descriptor = []
        self.extended_event_descriptor_multi = []
        self.extended_event_codepage = None
        self.component_descriptor = []
        self.content_descriptor = []
        self.linkage_descriptor = []
        self.parental_rating_descriptor = []
        self.programme_delivery_control_descriptor = []
        self.prev1_ISO_639_language_code = "x"
        self.prev2_ISO_639_language_code = "x"

        path = os.path.splitext(path)[0]
        data = readFile(path + ".eit", "rb")
        if len(data) >= 12:
            self.__parse(data)

    def getEit(self):
        if self.eit:
            if self.eit["short_description"].startswith(self.eit["name"]):
                self.eit["short_description"] = self.eit["short_description"][len(self.eit["name"]) + 1:]
            self.eit["short_description"] = self.eit["short_description"].replace("\n", ", ")
        return self.eit

    def __parse(self, data):
        EIT_LINKAGE_DESCRIPTOR = 0x4a
        EIT_SHORT_EVENT_DESCRIPTOR = 0x4d
        EIT_EXTENDED_EVENT_DESCRIPTOR = 0x4e
        EIT_COMPONENT_DESCRIPTOR = 0x50
        EIT_CONTENT_DESCRIPTOR = 0x54
        EIT_PARENTAL_RATING_DESCRIPTOR = 0x55
        EIT_PDC_DESCRIPTOR = 0x69

        def parseMJD(mjd):
            # parse 16 bit unsigned int containing modified Julian Date as per DVB-SI spec
            # returning year, month, day
            yy = int((mjd - 15078.2) / 365.25)
            mm = int((mjd - 14956.1 - int(yy * 365.25)) / 30.6001)
            d = mjd - 14956 - int(yy * 365.25) - int(mm * 30.6001)
            k = 0
            if mm in {14, 15}:
                k = 1
            return (1900 + yy + k), (mm - 1 - k * 12), d

        def unBCD(byte):
            return (byte >> 4) * 10 + (byte & 0xf)

        def language_iso639_2to3(alpha2):
            if alpha2 in LanguageCodes:
                language = LanguageCodes[alpha2]
                for alpha, name in list(LanguageCodes.items()):
                    if name == language:
                        if len(alpha) == 3:
                            return alpha
            return alpha2

        def determineCodepage(byte):
            codepage = None
            if byte == "1":
                codepage = 'iso-8859-5'
            elif byte == "2":
                codepage = 'iso-8859-6'
            elif byte == "3":
                codepage = 'iso-8859-7'
            elif byte == "4":
                codepage = 'iso-8859-8'
            elif byte == "5":
                codepage = 'iso-8859-9'
            elif byte == "6":
                codepage = 'iso-8859-10'
            elif byte == "7":
                codepage = 'iso-8859-11'
            elif byte == "9":
                codepage = 'iso-8859-13'
            elif byte == "10":
                codepage = 'iso-8859-14'
            elif byte == "11":
                codepage = 'iso-8859-15'
            elif byte == "21":
                codepage = 'utf-8'
            return codepage

        def parseHeader(data, pos):
            e = struct.unpack(">HHBBBBBBH", data[pos:pos + 12])
            self.eit["event_id"] = e[0]
            y, mo, d = parseMJD(e[1])				  # Y, M, D
            h, mi, s = unBCD(e[2]), unBCD(e[3]), unBCD(e[4])	  # HH, MM, SS
            try:
                dt = datetime.datetime(y, mo, d, h, mi, s)
                logger.debug("dt: %s", str(dt))
                start_seconds = int(time.mktime(dt.timetuple()))
                self.eit["start"] = start_seconds - time.timezone + time.localtime(start_seconds).tm_isdst * 3600  # daylight savings time
            except Exception as e:
                logger.error("exception: %s", e)
                self.eit["start"] = 0

            self.eit["length"] = unBCD(e[5]) * 3600 + unBCD(e[6]) * 60 + unBCD(e[7])

            # free_CA_mode = e[8] & 0x1000
            # descriptors_loop_length = e[8] & 0x0fff

            running_status = (e[8] & 0xe000) >> 13
            if running_status in {1, 2}:
                self.eit['when'] = "NEXT"
            elif running_status in {3, 4}:
                self.eit['when'] = "NOW"

        def parseShortEventDescriptor(data, pos):
            ISO_639_language_code = data[pos + 2:pos + 5].decode('latin-1', errors='ignore').upper()
            event_name_length = data[pos + 5]

            # Decode name - check for codepage indicator
            name_start = pos + 6
            name_end = name_start + event_name_length
            name_bytes = data[name_start:name_end]

            # Check if first byte is codepage indicator
            encoding = 'iso-8859-1'
            decode_start = 0
            if event_name_length > 0 and name_bytes[0] < 0x20:
                codepage = determineCodepage(str(name_bytes[0]))
                if codepage:
                    encoding = codepage
                    decode_start = 1  # Skip the indicator byte in decoding

            name_event_description = name_bytes[decode_start:].decode(encoding, errors='ignore')
            # Decode short description
            text_length_pos = pos + 6 + event_name_length
            text_length = data[text_length_pos] if text_length_pos < pos + length else 0
            text_start = text_length_pos + 1
            text_end = text_start + text_length
            text_bytes = data[text_start:text_end]

            # Check if first byte is codepage indicator
            desc_encoding = 'iso-8859-1'
            desc_decode_start = 0
            if text_length > 0 and len(text_bytes) > 0 and text_bytes[0] < 0x20:
                codepage = determineCodepage(str(text_bytes[0]))
                if codepage:
                    desc_encoding = codepage
                    desc_decode_start = 1  # Skip the indicator byte in decoding

            short_event_description = text_bytes[desc_decode_start:].decode(desc_encoding, errors='ignore')

            if ISO_639_language_code == lang:
                self.short_event_descriptor.append(short_event_description)
                self.name_event_descriptor.append(name_event_description)
            if self.prev1_ISO_639_language_code in {ISO_639_language_code, "x"}:
                self.short_event_descriptor_multi.append(short_event_description)
                self.name_event_descriptor_multi.append(name_event_description)
            else:
                self.short_event_descriptor_multi.append("\n\n" + short_event_description)
                self.name_event_descriptor_multi.append(" " + name_event_description)
            self.prev1_ISO_639_language_code = ISO_639_language_code

        def parseExtendedEventDescriptor(data, pos):
            ISO_639_language_code = data[pos + 3:pos + 6].decode('latin-1', errors='ignore').upper()

            # Skip descriptor_number (pos+2), ISO_639 (pos+3-5), length_of_items (pos+6)
            length_of_items = data[pos + 6]
            text_length = data[pos + 7 + length_of_items]
            desc_start = pos + 8 + length_of_items

            # Decode extended description - check for codepage indicator
            encoding = 'iso-8859-1'
            if text_length > 0 and desc_start < pos + length:
                first_byte = data[desc_start]
                if first_byte < 0x20:
                    # Codepage indicator present
                    codepage = determineCodepage(str(first_byte))
                    if codepage:
                        encoding = codepage
                        desc_start += 1

            desc_bytes = data[desc_start:pos + length]
            extended_event_description = desc_bytes.decode(encoding, errors='ignore')

            if ISO_639_language_code == lang:
                self.extended_event_descriptor.append(extended_event_description)
            if self.prev2_ISO_639_language_code in {ISO_639_language_code, "x"}:
                self.extended_event_descriptor_multi.append(extended_event_description)
            else:
                self.extended_event_descriptor_multi.append("\n\n" + extended_event_description)
            self.prev2_ISO_639_language_code = ISO_639_language_code

        def parseContentDescriptor(_data, _pos):
            logger.debug("...")
            self.content_descriptor.append("n/a")

        lang = language_iso639_2to3(self.epglang.lower()[:2]).upper()

        pos = 0
        parseHeader(data, pos)
        pos += 12

        while pos < len(data) - 2:
            rec = data[pos]
            length = data[pos + 1] + 2

            if rec == EIT_SHORT_EVENT_DESCRIPTOR:
                parseShortEventDescriptor(data, pos)

            elif rec == EIT_EXTENDED_EVENT_DESCRIPTOR:
                parseExtendedEventDescriptor(data, pos)

            elif rec == EIT_COMPONENT_DESCRIPTOR:
                self.component_descriptor.append(data[pos + 8:pos + length])

            elif rec == EIT_CONTENT_DESCRIPTOR:
                parseContentDescriptor(data, pos)

            elif rec == EIT_LINKAGE_DESCRIPTOR:
                self.linkage_descriptor.append(data[pos + 8:pos + length])

            elif rec == EIT_PARENTAL_RATING_DESCRIPTOR:
                self.parental_rating_descriptor.append(data[pos + 2:pos + length])

            elif rec == EIT_PDC_DESCRIPTOR:
                self.programme_delivery_control_descriptor.append(data[pos + 5:pos + length])

            else:
                logger.debug("unsupported descriptor: %x %x", rec, length)
                logger.debug("%s", (data[pos:pos + length]))

            pos += length

        self.eit['content'] = self.content_descriptor

        if self.name_event_descriptor:
            self.name_event_descriptor = "".join(self.name_event_descriptor)
        else:
            self.name_event_descriptor = ("".join(self.name_event_descriptor_multi)).strip()
        self.eit['name'] = self.name_event_descriptor

        if self.short_event_descriptor:
            self.short_event_descriptor = "".join(self.short_event_descriptor)
        else:
            self.short_event_descriptor = ("".join(self.short_event_descriptor_multi)).strip()
        self.eit['short_description'] = self.short_event_descriptor

        if self.extended_event_descriptor:
            self.extended_event_descriptor = "".join(self.extended_event_descriptor)
        else:
            self.extended_event_descriptor = ("".join(self.extended_event_descriptor_multi)).strip()
        self.eit['description'] = self.extended_event_descriptor
