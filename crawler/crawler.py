from collections import deque
from urllib.parse import urljoin, unquote
from downloader import detect_file_type
import time
# dùng để ghi tiếng việt
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(
        encoding="utf-8"
    )
    sys.stderr.reconfigure(
        encoding="utf-8"
    )

from bs4 import BeautifulSoup

from config import (
    BASE_URL,
    ALLOWED_DOMAIN,
    MAX_PAGES,
    REQUEST_DELAY,
    DOWNLOAD_ATTACHMENTS,
    ALLOWED_FILE_EXTENSIONS,
    HTML_DIR,
    FILES_DIR,
    RAW_MD_DIR,
)


from downloader import (
    download_html,
    download_file,
)


from parser import (
    parse_html,
    parse_file,
)


from utils import (
    normalize_url,
    is_valid_url,
    hash_filename,
    logger,
)



# lưu những trang đã crawl
visited = set()
# lưu nhữung file đã tải
downloaded_files = set()



def process_file(url):
   
    if url in downloaded_files:
        return
    # tải 
    downloaded_files.add(url)

    logger.info(f"Download file: {url}")

    file_path = download_file(
        url,
        FILES_DIR
    )

    if file_path is None:
        return

    suffix = file_path.suffix.lower()

    if suffix not in ALLOWED_FILE_EXTENSIONS:
        logger.warning(f"Unsupported file: {file_path}")
        return

    try:
        # chuyển thành markdown
        result = parse_file(file_path)

        md_path = RAW_MD_DIR / hash_filename(url, ".md")

        markdown = f"""---
        title: {result["title"]}
        url: {url}
        type: {suffix[1:]}
        ---

        {result["text"]}
        """

        md_path.write_text(markdown, encoding="utf-8")

    except Exception as e:

        logger.error(
            f"Parse file error {url}: {e}"
        )



def process_page(url):

    # tải htlm
    response = download_html(url)


    if response is None:

        return []



    html = response.text



    # lưu htlm gốc

    filename = hash_filename(
        url,
        ".html"
    )


    html_path = HTML_DIR / filename


    with open(
        html_path,
        "w",
        encoding="utf-8"
    ) as f:

        f.write(html)



    # chuyển thành markdown

    result = parse_html(
        html
    )

    md_path = RAW_MD_DIR / hash_filename(url, ".md")

    markdown = f"""---
    title: {result["title"]}
    url: {url}
    type: html
    ---

    {result["text"]}
    """

    md_path.write_text(markdown, encoding="utf-8")

    soup = BeautifulSoup(
        html,
        "lxml"
    )


    links = []
    # tìm link mới
    for a in soup.find_all("a", href=True):

        href = a["href"].strip()

        if href.startswith(("mailto:", "javascript:")):
            continue

        new_url = normalize_url(urljoin(url, href))

        decoded = unquote(new_url).lower()

        # nếu là file thì tải luôn
        if decoded.endswith((".pdf", ".doc", ".docx")):

            if DOWNLOAD_ATTACHMENTS:
                process_file(new_url)

            continue

        # khác domain thì bỏ
        if not is_valid_url(new_url, ALLOWED_DOMAIN):
            continue

        # bỏ mail
        if "@" in decoded:
            continue

        # nếu là file thì tải
        file_type = detect_file_type(new_url)

        if file_type in ("pdf", "doc", "docx"):

            if DOWNLOAD_ATTACHMENTS:
                process_file(new_url)

            continue

        # còn lại là HTML
        links.append(new_url)

    for tag in soup.find_all(["iframe","embed","object"]):

        src = tag.get("src") or tag.get("data")

        if not src:
            continue

        new_url = normalize_url(urljoin(url, src))

        if detect_file_type(new_url) in ("pdf","doc","docx"):
            process_file(new_url)

    print(f"\n{url}")
    print(f"Found {len(links)} internal links")

    for l in links:
        print("  ", l)

    return links


# BFS
def crawl():

    queue = deque()

    queue.append(
        BASE_URL
    )


    while queue:


        if len(visited) >= MAX_PAGES:

            logger.info(
                "Reached MAX_PAGES"
            )

            break



        url = queue.popleft()


        url = normalize_url(
            url
        )



        if url in visited:

            continue



        visited.add(url)



        print(
            f"Crawl [{len(visited)}]: {url.encode('utf-8', errors='ignore').decode('utf-8')}"
        )


        try:


            # PDF DOCX trực tiếp

            file_type = detect_file_type(url)

            if file_type in ("pdf", "doc", "docx"):

                if DOWNLOAD_ATTACHMENTS:
                    process_file(url)

                continue

            lower = url.lower()

            if lower.endswith(tuple(ALLOWED_FILE_EXTENSIONS)):

                if DOWNLOAD_ATTACHMENTS:
                    process_file(url)

                continue

            # HTML

            new_links = process_page(
                url
            )


            for link in new_links:

                if link not in visited:

                    queue.append(
                        link
                    )


            # tráng spam
            time.sleep(
                REQUEST_DELAY
            )


        except Exception as e:


            logger.error(
                f"Crawler error {url}: {e}"
            )



    print("=" * 50)

    print(
        "DONE"
    )

    print(
        "Pages:",
        len(visited)
    )

    print(
        "Files:",
        len(downloaded_files)
    )
    print("EXITING")
    import os
    os._exit(0)




if __name__ == "__main__":

    crawl()