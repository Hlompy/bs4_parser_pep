import re
import logging
from urllib.parse import urljoin

import requests_cache
from bs4 import BeautifulSoup
from tqdm import tqdm as bar

from constants import BASE_DIR, MAIN_DOC_URL, PEP_URL, EXPECTED_STATUS
from configs import configure_argument_parser, configure_logging
from outputs import control_output
from utils import get_response, find_tag


def whats_new(session):
    whats_new_url = urljoin(MAIN_DOC_URL, 'whatsnew/')
    response = get_response(session, whats_new_url)
    if response is None:
        return
    soup = BeautifulSoup(response.text, features='lxml')
    main_div = find_tag(soup, 'section', attrs={'id': 'what-s-new-in-python'})
    div_with_ul = find_tag(main_div, 'div', attrs={'class': 'toctree-wrapper'})
    sections_by_python = div_with_ul.find_all('li', attrs={
        'class': 'toctree-l1'
    })

    results = [('Ссылка на статью', 'Заголовок', 'Редактор, Автор')]
    for section in bar(sections_by_python):
        version_a_tag = section.find('a')
        version_link = urljoin(whats_new_url, version_a_tag['href'])
        response = get_response(session, version_link)
        if response is None:
            continue
        soup = BeautifulSoup(response.text, features='lxml')
        h1 = find_tag(soup, 'h1')
        dl = find_tag(soup, 'dl')
        dl_text = dl.text.replace('\n', ' ')
        results.append(
            (version_link, h1.text, dl_text)
        )
    return results


def latest_versions(session):
    response = get_response(session, MAIN_DOC_URL)
    if response is None:
        return
    soup = BeautifulSoup(response.text, features='lxml')
    sidebar = find_tag(soup, 'div', attrs={'class': 'sphinxsidebarwrapper'})
    ul_tags = sidebar.find_all('ul')
    for ul in ul_tags:
        if 'All versions' in ul.text:
            a_tags = ul.find_all('a')
            break
    else:
        raise Exception('Ничего не нашлось')

    results = [('Ссылка на документацию', 'Версия', 'Статус')]
    pattern = r'Python (?P<version>\d\.\d+) \((?P<status>.*)\)'
    for a_tag in a_tags:
        link = a_tag['href']
        current = re.search(pattern, a_tag.text)
        if current is not None:
            version, status = current.groups()
        else:
            version, status = a_tag.text, ''
        results.append((link, version, status))
    return results


def download(session):
    downloads_url = urljoin(MAIN_DOC_URL, 'download.html')
    response = get_response(session, downloads_url)
    if response is None:
        return
    soup = BeautifulSoup(response.text, features='lxml')
    main_tag = find_tag(soup, 'div', attrs={'role': 'main'})
    table_tag = find_tag(main_tag, 'table', attrs={'class': 'docutils'})

    pdf_a4_tag = find_tag(table_tag, 'a', {
        'href': re.compile(r'.+pdf-a4\.zip$')
    })
    link = pdf_a4_tag['href']
    archive_url = urljoin(downloads_url, link)

    filename = archive_url.split('/')[-1]
    downloads_dir = BASE_DIR / 'downloads'
    downloads_dir.mkdir(exist_ok=True)
    archive_path = downloads_dir / filename
    arch_response = session.get(archive_url)

    with open(archive_path, 'wb') as file:
        file.write(arch_response.content)
        print(archive_path)
        logging.info(f'Архив был загружен и сохранён: {archive_path}')


def pep(session):
    response = get_response(session, PEP_URL)
    if response is None:
        return
    soup = BeautifulSoup(response.text, features='lxml')
    main_tag = find_tag(soup, 'section', attrs={'id': 'numerical-index'})
    tbody_tag = find_tag(main_tag, 'tbody')
    tr_tags = tbody_tag.find_all('tr')
    counter = 0
    results = {}
    for tr_tag in tr_tags:
        status_key = find_tag(tr_tag, 'td').text[1:]
        expected_status = EXPECTED_STATUS.get(status_key, [])
        if not expected_status:
            logging.info(f'Неизвестный ключ статуса: \'{status_key}\'')
        a_link = find_tag(tr_tag, 'a')
        pep_link = urljoin(PEP_URL, a_link['href'])
        response = get_response(session, pep_link)
        if response is None:
            continue
        soup = BeautifulSoup(response.text, features='lxml')
        section_tag = find_tag(soup, 'section', attrs={'id': 'pep-content'})
        dl_tag = find_tag(section_tag, 'dl', attrs={
            'class': 'rfc2822 field-list simple'
        })
        status = find_tag(dl_tag, 'dd', attrs={'class': 'field-even'}).text
        if status not in expected_status:
            logging.info(
                f'\nНесовпадающие статусы:\n {pep_link}\n'
                f'Статус в карточке: {status}\n'
                f'Ожидаемые статусы: {expected_status}')
        if status in expected_status:
            results[status] = results.get(status, 0) + 1
            counter += 1
    return (
        [('Статус', 'Количество')]
        + sorted(results.items())
        + [('Total', counter)]
    )


MODE_TO_FUNCTION = {
    'whats-new': whats_new,
    'latest-versions': latest_versions,
    'download': download,
    'pep': pep,
}


def main():
    configure_logging()
    logging.info('Парсер запущен!')
    arg_parser = configure_argument_parser(MODE_TO_FUNCTION.keys())
    args = arg_parser.parse_args()
    logging.info(f'Аргументы командной строки: {args}')

    session = requests_cache.CachedSession()
    if args.clear_cache:
        session.cache.clear()
    parser_mode = args.mode
    results = MODE_TO_FUNCTION[parser_mode](session)

    if results is not None:
        control_output(results, args)
    logging.info('Парсер завершил работу.')


if __name__ == '__main__':
    main()
