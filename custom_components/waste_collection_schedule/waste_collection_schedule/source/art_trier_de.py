import logging
from urllib.parse import quote

import requests
from waste_collection_schedule import Collection  # type: ignore[attr-defined]
from waste_collection_schedule.service.ICS import ICS

TITLE = "ART Trier (Depreciated)"
DESCRIPTION = "Source for waste collection of ART Trier."
URL = "https://www.art-trier.de"
TEST_CASES = {
    "Trier": {
        "zip_code": "54296",
        "district": "Stadt Trier, Universitätsring",
    },  # # https://www.art-trier.de/ics-feed/54296_trier_universitaetsring_1-1800.ics
    "Schweich": {
        "zip_code": "54338",
        "district": "Schweich (inkl. Issel)",
    },  # https://www.art-trier.de/ics-feed/54338_schweich_inkl_issel_1-1800.ics
    "Dreis": {
        "zip_code": "54518",
        "district": "Dreis",
    },  # https://www.art-trier.de/ics-feed/54518_dreis_1-1800.ics
    "Wittlich Marktplatz": {
        "zip_code": "54516",
        "district": "Wittlich, Marktplatz",
    },  # https://www.art-trier.de/ics-feed/54516_wittlich_marktplatz_1-1800.ics
    "Wittlich Wengerohr": {
        "zip_code": "54516",
        "district": "Wittlich-Wengerohr",
    },  # https://www.art-trier.de/ics-feed/54516_wittlich%2Dwengerohr_1-1800.ics
}

API_URL = "https://www.art-trier.de/ics-feed"
REMINDER_DAY = (
    "0"  # The calendar event should be on the same day as the waste collection
)
REMINDER_TIME = "0600"  # The calendar event should start on any hour of the correct day, so this does not matter much
ICON_MAP = {
    "Altpapier": "mdi:package-variant",
    "Restmüll": "mdi:trash-can",
    "Gelber Sack": "mdi:recycle",
}
SPECIAL_CHARS = str.maketrans(
    {
        " ": "_",
        "ä": "ae",
        "ü": "ue",
        "ö": "oe",
        "ß": "ss",
        "(": None,
        ")": None,
        ",": None,
        ".": None,
    }
)
LOGGER = logging.getLogger(__name__)

PARAM_TRANSLATIONS = {
    "de": {
        "zip_code": "PLZ",
        "district": "Ort",
    }
}


class Source:
    def __init__(self, district: str, zip_code: str):
        self._district = quote(
            district.lower().removeprefix("stadt ").translate(SPECIAL_CHARS).strip()
        )
        self._zip_code = zip_code
        self._ics = ICS(regex=r"^A.R.T. Abfuhrtermin: (.*)", split_at=r" & ")

    def fetch(self):
        LOGGER.warning(
            "The ART Trier source is deprecated and might not work with all addresses anymore."
            " Please use the ICS instead: https://github.com/mampfes/hacs_waste_collection_schedule/blob/master/doc/ics/art_trier_de.md"
        )
        url = f"{API_URL}/{self._zip_code}:{self._district}::@{REMINDER_DAY}-{REMINDER_TIME}.ics"

        res = requests.get(url)
        res.raise_for_status()

        schedule = self._ics.convert(res.text)

        return [
            Collection(date=entry[0], t=entry[1], icon=ICON_MAP.get(entry[1]))
            for entry in schedule
        ]
