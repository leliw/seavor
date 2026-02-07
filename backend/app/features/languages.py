
from enum import StrEnum, auto


class Language(StrEnum):
    EN = auto()
    DE = auto()
    ES = auto()
    FR = auto()
    IT = auto()
    PL = auto()
    UK = auto()
    RU = auto()
    ZH = auto()
    AR = auto()



LANGUAGE_NAMES = {
    Language.EN: "English",
    Language.DE: "German",
    Language.ES: "Spanish",
    Language.FR: "French",
    Language.IT: "Italian",
    Language.PL: "Polish",
    Language.UK: "Ukrainian",
    Language.RU: "Russian",
    Language.ZH: "Chinese",
    Language.AR: "Arabic",
}
