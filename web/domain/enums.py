from enum import Enum

class CompanyFileType(str, Enum):
    PDF = "PDF"
    TXT = "TXT"
    XML = "XML"
    HTML = "HTML"
    DOCX = "DOCX"
    IMAGE = "IMAGE"

class DisclosureFileType(str, Enum):
    HTML = "HTML"
    PDF = "PDF"
    XBRL = "XBRL"


class UserRole(str, Enum):
    USER = "USER"
    ADMIN = "ADMIN"


class UserStatus(str, Enum):
    ACTIVE = "ACTIVE"
    WITHDRAWN = "WITHDRAWN"
    BANNED = "BANNED"
