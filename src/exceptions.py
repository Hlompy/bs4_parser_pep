class ParserFindTagException(Exception):
    """Вызывается, когда парсер не может найти тег."""


class ParserGetNoneResponseException(Exception):
    """Вызывается, когда парсер видит пустой ответ"""
