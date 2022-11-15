import logging

# Импорт базового класса ошибок библиотеки request.
from requests import RequestException

from exceptions import ParserFindTagException

# Перехват ошибки RequestException.
def get_response(session, url):
    try:
        response = session.get(url)
        response.encoding = 'utf-8'
        return response
    except RequestException:
        logging.exception(
            f'Возникла ошибка при загрузке страницы {url}',
            stack_info=True
        )

def find_tag(soup, tag, attrs=None, text=None):
    searched_tag = soup.find(tag, attrs=(attrs or {}), text=text)
    if searched_tag is None:
        error_msg = f'Не найден тег {tag} {attrs}'
        logging.error(error_msg, stack_info=True)
        raise ParserFindTagException(error_msg)
    return searched_tag

def is_int(s):
    try:
        int(s)
        return True
    except ValueError:
        return False
