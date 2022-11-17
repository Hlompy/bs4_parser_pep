import logging
import re
from urllib.parse import urljoin

import requests_cache
from bs4 import BeautifulSoup
from tqdm import tqdm as bar

from configs import configure_argument_parser, configure_logging
from constants import (A_TAG, ALL_VERSIONS, ARCHIVE_SAVED, ARGS_CMD,
                       ARGUMENTS_FOR_LATEST_VERSIONS, ARGUMENTS_FOR_WHATS_NEW,
                       BASE_DIR, CLASS, DD, DIV, DL, DOCUTILS,
                       DOWNLOAD_DIR_PART, DOWNLOAD_FOR_DICT, DOWNLOAD_HTML,
                       END, EXPECTED_STATUS, FIELD_EVEN, H1_TAG, HREF, ID,
                       LATEST_FOR_DICT, LI, LXML, MAIN, MAIN_DOC_URL,
                       MISMATCHED_STATUSES, NOT_FOUND_ANYTHING, NUM_INDEX,
                       PEP_CONTENT, PEP_FOR_DICT, PEP_URL, RESULT, ROLE,
                       SECTION, SIDEBAR, SIMPLE, SOME_EXP_STATUSES, START,
                       STATUS_IN_CARD, TABLE, TBODY, TD, TOCTREE_L1,
                       TOCTREE_WRAPPER, TOTAL, TR, UL, UNDEFINED, WB,
                       WHATS_FOR_DICT, WHATS_NEW, WHATS_NEW_PART_URL)
from exceptions import ParserFindTagException
from outputs import control_output
from utils import find_tag, get_response


def whats_new(session):
    whats_new_url = urljoin(MAIN_DOC_URL, WHATS_NEW_PART_URL)
    response = get_response(session, whats_new_url)
    soup = BeautifulSoup(response.text, features=LXML)
    main_div = find_tag(soup, SECTION, attrs={ID: WHATS_NEW})
    div_with_ul = find_tag(main_div, DIV, attrs={CLASS: TOCTREE_WRAPPER})
    sections_by_python = div_with_ul.find_all(LI, attrs={
        CLASS: TOCTREE_L1
    })

    results = [ARGUMENTS_FOR_WHATS_NEW]
    for section in bar(sections_by_python):
        version_a_tag = section.find(A_TAG)
        version_link = urljoin(whats_new_url, version_a_tag[HREF])
        response = session.get(version_link)
        if response is None:
            continue
        inside = BeautifulSoup(response.text, features=LXML)
        h1 = find_tag(inside, H1_TAG)
        dl = find_tag(inside, DL)
        dl_text = dl.text.replace('\n', ' ')
        results.append(
            (version_link, h1.text, dl_text)
        )
    return results


def latest_versions(session):
    response = get_response(session, MAIN_DOC_URL)
    soup = BeautifulSoup(response.text, features=LXML)
    sidebar = find_tag(soup, DIV, attrs={CLASS: SIDEBAR})
    ul_tags = sidebar.find_all(UL)
    for ul in ul_tags:
        if ALL_VERSIONS in ul.text:
            a_tags = ul.find_all(A_TAG)
            break
    else:
        raise ParserFindTagException(NOT_FOUND_ANYTHING)

    results = [ARGUMENTS_FOR_LATEST_VERSIONS]
    pattern = r'Python (?P<version>\d\.\d+) \((?P<status>.*)\)'
    for a_tag in a_tags:
        link = a_tag[HREF]
        current = re.search(pattern, a_tag.text)
        version, status = current.groups() if current else a_tag.text, ''
        results.append((link, version, status))
    return results


def download(session):
    downloads_url = urljoin(MAIN_DOC_URL, DOWNLOAD_HTML)
    response = get_response(session, downloads_url)
    soup = BeautifulSoup(response.text, features=LXML)
    main_tag = find_tag(soup, DIV, attrs={ROLE: MAIN})
    table_tag = find_tag(main_tag, TABLE, attrs={CLASS: DOCUTILS})

    pdf_a4_tag = find_tag(table_tag, A_TAG, {
        HREF: re.compile(r'.+pdf-a4\.zip$')
    })
    link = pdf_a4_tag[HREF]
    archive_url = urljoin(downloads_url, link)

    filename = archive_url.split('/')[-1]
    downloads_dir = BASE_DIR / DOWNLOAD_DIR_PART
    downloads_dir.mkdir(exist_ok=True)
    archive_path = downloads_dir / filename
    arch_response = session.get(archive_url)

    with open(archive_path, WB) as file:
        file.write(arch_response.content)
        print(archive_path)
        logging.info(ARCHIVE_SAVED, archive_path)


def pep(session):
    response = get_response(session, PEP_URL)
    soup = BeautifulSoup(response.text, features=LXML)
    main_tag = find_tag(soup, SECTION, attrs={ID: NUM_INDEX})
    tbody_tag = find_tag(main_tag, TBODY)
    tr_tags = tbody_tag.find_all(TR)
    counter = 0
    results = {}
    for tr_tag in tr_tags:
        status_key = find_tag(tr_tag, TD).text[1:]
        expected_status = EXPECTED_STATUS.get(status_key, [])
        if not expected_status:
            logging.info(f'{UNDEFINED} \'{status_key}\'')
        a_link = find_tag(tr_tag, A_TAG)
        pep_link = urljoin(PEP_URL, a_link[HREF])
        response = session.get(pep_link)
        if response is None:
            continue
        soup = BeautifulSoup(response.text, features=LXML)
        section_tag = find_tag(soup, SECTION, attrs={ID: PEP_CONTENT})
        dl_tag = find_tag(section_tag, DL, attrs={
            CLASS: SIMPLE
        })
        status = find_tag(dl_tag, DD, attrs={CLASS: FIELD_EVEN}).text
        if status not in expected_status:
            logging.info(
                f'\n{MISMATCHED_STATUSES}\n {pep_link}\n'
                f'{STATUS_IN_CARD} {status}\n'
                f'{SOME_EXP_STATUSES} {expected_status}')
        results[status] = results.get(status, 0) + 1
        counter += 1
    return (
        [RESULT]
        + sorted(results.items())
        + [(TOTAL, counter)]
    )


MODE_TO_FUNCTION = {
    WHATS_FOR_DICT: whats_new,
    LATEST_FOR_DICT: latest_versions,
    DOWNLOAD_FOR_DICT: download,
    PEP_FOR_DICT: pep,
}


def main():
    configure_logging()
    logging.info(START)
    arg_parser = configure_argument_parser(MODE_TO_FUNCTION.keys())
    args = arg_parser.parse_args()
    logging.info(ARGS_CMD, args)

    session = requests_cache.CachedSession()
    if args.clear_cache:
        session.cache.clear()
    parser_mode = args.mode
    results = MODE_TO_FUNCTION[parser_mode](session)

    if results is not None:
        control_output(results, args)
    logging.info(END)


if __name__ == '__main__':
    main()
