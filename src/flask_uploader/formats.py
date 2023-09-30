"""
Mime-Types
https://www.digipres.org/formats/mime-types/
https://mimetype.io
https://www.sitepoint.com/mime-types-complete-list/
https://www.openoffice.org/framework/documentation/mimetypes/mimetypes.html
https://docs.w3cub.com/http/basics_of_http/mime_types/complete_list_of_mime_types.html
https://help.gnome.org/users/gnumeric/stable/sect-file-formats.html.en
"""

from __future__ import annotations
import typing as t

import mimetypes

from .utils import get_extension


__all__ = (
    'get_format',
    'guess_type',
    'FileFormat',
)


class FileFormat(t.NamedTuple):
    extension: str
    mimetype: str
    comment: str = ''


TXT = FileFormat('txt', 'text/plain')


# MS Office document formats
DOC = FileFormat('doc', 'application/msword')
XLS = FileFormat('xls', 'application/vnd.ms-excel')
PPT = FileFormat('ppt', 'application/vnd.ms-powerpoint')
DOCX = FileFormat(
    'docx',
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
)
XLSX = FileFormat(
    'xlsx',
    'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
)
PPTX = FileFormat(
    'pptx',
    'application/vnd.openxmlformats-officedocument.presentationml.presentation'
)
MS_OFFICE = frozenset((DOC, XLS, PPT, DOCX, XLSX, PPTX))

# Open Office document formats
ODT = FileFormat('odt', 'application/vnd.oasis.opendocument.text')
ODS = FileFormat('ods', 'application/vnd.oasis.opendocument.spreadsheet')
ODP = FileFormat('odp', 'application/vnd.oasis.opendocument.presentation')
ODF = FileFormat('odf', 'application/vnd.oasis.opendocument.formula')
ODC = FileFormat('odc', 'application/vnd.oasis.opendocument.chart')
ODB = FileFormat('odb', 'application/vnd.oasis.opendocument.database')
OPEN_OFFICE = frozenset((ODT, ODS, ODP, ODF, ODC))

# WPS Office document formats
WPS = FileFormat('wps', 'application/wps-office.wps')
ET = FileFormat('et', 'application/wps-office.et')
DPS = FileFormat('dps', 'application/wps-office.dps')
WPS_OFFICE = frozenset((WPS, ET, DPS))

# Other office document formats
RTF = FileFormat('rtf', 'application/rtf')
GNUMERIC = FileFormat('gnumeric', 'application/x-gnumeric')
ABW = FileFormat('abw', 'application/x-abiword')
OTHER_OFFICE = frozenset((RTF, GNUMERIC, ABW))

# Electronic documents file formats
PDF = FileFormat('pdf', 'application/pdf')
DJVU = FileFormat('djvu', 'image/vnd.djvu')
DJV = FileFormat('djv', 'image/vnd.djvu')
EDOCUMENTS = frozenset((PDF, DJVU, DJV))

# Electronic books file formats
EPUB = FileFormat('epub', 'application/epub+zip')
FB2 = FileFormat('fb2', 'application/x-fictionbook+xml')
MOBI = FileFormat('mobi', 'application/x-mobipocket-ebook')
EBOOKS = frozenset((EPUB, FB2, MOBI))

# Image file formats
JPG = FileFormat('jpg', 'image/jpeg')
JPE = FileFormat('jpe', 'image/jpeg')
JPEG = FileFormat('jpeg', 'image/jpeg')
PNG = FileFormat('png', 'image/png')
GIF = FileFormat('gif', 'image/gif')
BMP = FileFormat('bmp', 'image/bmp')
WEBP = FileFormat('webp', 'image/webp')
SVG = FileFormat('svg', 'image/svg+xml')
ODG = FileFormat('odg', 'application/vnd.oasis.opendocument.graphics')
IMAGES = frozenset((JPG, JPE, JPEG, PNG, GIF, BMP, WEBP, SVG, ODG))

# Audio file formats
WAV = FileFormat('wav', 'audio/wav')
WMA = FileFormat('wma', 'audio/x-ms-wma')
MP3 = FileFormat('mp3', 'audio/mpeg')
AAC = FileFormat('aac', 'audio/x-aac')
OGG = FileFormat('ogg', 'audio/ogg')
OGA = FileFormat('oga', 'audio/ogg')
FLAC = FileFormat('flac', 'audio/x-flac')
AUDIO = frozenset((WAV, WMA, MP3, AAC, OGG, OGA, FLAC))

# Structured data file formats
CSV = FileFormat('csv', 'text/csv')
INI = FileFormat('ini', 'text/plain')
CFG = FileFormat('cfg', 'text/plain')
TOML = FileFormat('toml', 'text/plain')
JSON = FileFormat('json', 'application/json')
PLIST = FileFormat('plist', 'application/x-plist')
XML = FileFormat('xml', 'text/xml')
YAML = FileFormat('yaml', 'text/plain')
YML = FileFormat('yml', 'text/plain')
DATA = frozenset((CSV, INI, CFG, TOML, JSON, PLIST, XML, YAML, YML))

# Various script file formats
JS = FileFormat('js', 'text/javascript')
PHP = FileFormat('php', 'application/x-httpd-php')
PL = FileFormat('pl', 'text/plain')
PY = FileFormat('py', 'text/x-python')
RB = FileFormat('rb', 'text/plain')
SH = FileFormat('sh', 'text/x-shellscript')
BAT = FileFormat('bat', 'application/x-msdownload')
PS1 = FileFormat('ps1', 'text/plain')
SCRIPTS = frozenset((JS, PHP, PL, PY, RB, SH, BAT, PS1))

# Archive and compression file formats
TAR = FileFormat('tar', 'application/x-tar')
ZIP = FileFormat('zip', 'application/zip')
_7Z = FileFormat('7z', 'application/x-7z-compressed')
GZ = FileFormat('gz', 'application/gzip')
TGZ = FileFormat('tgz', 'application/x-gzip')
BZ2 = FileFormat('bz2', 'application/x-bzip2')
TXZ = FileFormat('txz', 'application/x-xz')
ARCHIVES = frozenset((TAR, ZIP, _7Z, GZ, TGZ, BZ2, TXZ))

# Non executable source file formats
ADA = FileFormat('ada', 'text/x-ada', comment='Ada source code')
ASM = FileFormat('asm', 'text/x-asm', comment='Assembler source code')
ASM_S = FileFormat('s', 'text/x-asm', comment='Assembler source code')
BAS = FileFormat('bas', 'text/x-basic', comment='Basic source code')
C = FileFormat('c', 'text/x-c', comment='C source code')
H = FileFormat('h', 'text/x-chdr', comment='C source code header')
CPP = FileFormat('cpp', 'text/x-c++src', comment='C++ source code')
CXX = FileFormat('cxx', 'text/x-c++src', comment='C++ source code')
HPP = FileFormat('hpp', 'text/x-c++hdr', comment='C++ source code header')
HXX = FileFormat('hxx', 'text/x-c++hdr', comment='C++ source code header')
CBL = FileFormat('cbl', 'text/x-cobol', comment='COBOL source code')
COB = FileFormat('cob', 'text/x-cobol', comment='COBOL source code')
CS = FileFormat('cs', 'text/x-csharp', comment='C# source code')
D = FileFormat('D', 'text/x-d', comment='D source code')
F = FileFormat('f', 'text/x-fortran', comment='Fortran source code')
FS = FileFormat('fs', 'text/plain', comment='F Sharp compiled source')
GO = FileFormat('go', 'text/x-go', comment='Go source code')
HS = FileFormat('hs', 'text/x-haskell', comment='Haskell source code')
JAVA = FileFormat('java', 'text/x-java-source', comment='Java source code')
PAS = FileFormat('pas', 'text/x-pascal', comment='Pascal source code')
RS = FileFormat('rs', 'text/rust', comment='Rust source code')
SOURCE = frozenset((
    ADA,
    ASM, ASM_S,
    BAS,
    C, H, CPP, CXX, HPP, HXX,
    CBL, COB,
    CS,
    D,
    F,
    FS,
    GO,
    HS,
    JAVA,
    PAS,
    RS,
))

# Shared libraries and executable file formats
SO = FileFormat('so', 'application/octet-stream')
EXE = FileFormat('exe', 'application/x-msdownload')
DLL = FileFormat('dll', 'application/x-msdownload')
EXECUTABLES = frozenset((SO, EXE, DLL))


format_map: t.Dict[str, FileFormat] = {
    value.extension: value
    for name, value in globals().items()
    if isinstance(value, FileFormat)
}


def get_format(path_or_url: str) -> t.Optional[FileFormat]:
    """Returns a FileFormat object for the given file or URL."""
    return format_map.get(
        get_extension(path_or_url).lstrip('.').lower()
    )


def guess_type(
    path_or_url: str,
    use_external: bool = False,
) -> t.Optional[str]:
    """
    Returns a mime type for the given file or URL.

    Arguments:
        path_or_url (str): The path to the file or URL.
        use_external (bool): Use the mimetype package.
    """
    fmt = get_format(path_or_url)

    if fmt is not None:
        return fmt.mimetype

    if use_external:
        mimetype, _ = mimetypes.guess_type(path_or_url)
        return mimetype

    return None
