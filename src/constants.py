from pathlib import Path

MAIN_DOC_URL = 'https://docs.python.org/3/'
BASE_DIR = Path(__file__).parent
DATETIME_FORMAT = '%Y-%m-%d_%H-%M-%S'
PEP_URL = 'https://peps.python.org/'
EXPECTED_STATUS = {
    'A': ('Active', 'Accepted'),
    'D': ('Deferred',),
    'F': ('Final',),
    'P': ('Provisional',),
    'R': ('Rejected',),
    'S': ('Superseded',),
    'W': ('Withdrawn',),
    '': ('Draft', 'Active'),
}
START = 'Парсер запущен!'
END = 'Парсер завершил работу.'
ARGS_CMD = 'Аргументы командной строки:'
UNDEFINED = 'Неизвестный ключ статуса:'
NOT_FOUND_ANYTHING = 'Ничего не нашлось'
ARCHIVE_SAVED = 'Архив был загружен и сохранён:'
MISMATCHED_STATUSES = 'Несовпадающие статусы:'
STATUS_IN_CARD = 'Статус в карточке:'
SOME_EXP_STATUSES = 'Ожидаемые статусы:'
ALL_VERSIONS = 'All versions'
WHATS_NEW_PART_URL = 'whatsnew/'
DOWNLOAD_DIR_PART = 'downloads'
WHATS_FOR_DICT = 'whats-new'
LATEST_FOR_DICT = 'latest-versions'
DOWNLOAD_FOR_DICT = 'download'
PEP_FOR_DICT = 'pep'
WB = 'wb'
SECTION = 'section'
ID = 'id'
DIV = 'div'
LI = 'li'
H1_TAG = 'h1'
DL = 'dl'
UL = 'ul'
A_TAG = 'a'
CLASS = 'class'
ROLE = 'role'
TBODY = 'tbody'
TR = 'tr'
TD = 'td'
LXML = 'lxml'
HREF = 'href'
MAIN = 'main'
FIELD_EVEN = 'field-even'
SIMPLE = 'rfc2822 field-list simple'
TABLE = 'table'
DOCUTILS = 'docutils'
NUM_INDEX = 'numerical-index'
PEP_CONTENT = 'pep-content'
DD = 'dd'
WHATS_NEW = 'what-s-new-in-python'
TOCTREE_WRAPPER = 'toctree-wrapper'
TOCTREE_L1 = 'toctree-l1'
SIDEBAR = 'sphinxsidebarwrapper'
ARGUMENTS_FOR_WHATS_NEW = ('Ссылка на статью', 'Заголовок', 'Редактор, Автор')
ARGUMENTS_FOR_LATEST_VERSIONS = ('Ссылка на документацию', 'Версия', 'Статус')
TOTAL = 'total'
RESULT = ('Статус', 'Количество')
DOWNLOAD_HTML = 'download.html'
CHOICES = ('pretty', 'file')
FILE = 'file'
PRETTY = 'pretty'
