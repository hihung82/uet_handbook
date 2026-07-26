from __future__ import annotations
from urllib.parse import urlparse
import hashlib
import json
import logging
import re
from pathlib import Path
from urllib.parse import (
    urlparse,
    urldefrag,
    unquote,
)

from config import CRAWL_LOG

logging.basicConfig(
    filename=CRAWL_LOG,
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    encoding="utf-8",
)

logger = logging.getLogger("crawler")


from urllib.parse import (
    urlparse,
    urldefrag,
    quote,
    unquote
)

# chuẩn hoá lại url
def normalize_url(url: str) -> str:

    # bỏ #
    url, _ = urldefrag(url)


    parsed = urlparse(url)


    # decode trước
    path = unquote(parsed.path)


    # encode lại đúng 1 lần
    path = quote(
        path,
        safe="/"
    )


    return parsed._replace(
        path=path,
        query=""
    ).geturl()

# kiểu tra xem có hợp lệ không
def is_valid_url(url: str, allowed_domain: str) -> bool:

    if not url:
        return False

    parsed = urlparse(url)

    if parsed.scheme not in ("http", "https"):
        return False

    return parsed.hostname == allowed_domain



INVALID_CHARS = r'[<>:"/\\|?*]'

# chuyển tên file thàng kiêu hợp lệ tránh mấy kí tự bên trên
def safe_filename(filename: str) -> str:

    filename = unquote(filename)

    filename = re.sub(INVALID_CHARS, "_", filename)

    filename = filename.strip()

    return filename

# sinh tên file duy nhất bằng md5 tránh trùng
def hash_filename(url: str, suffix: str = ".html") -> str:

    md5 = hashlib.md5(url.encode("utf-8")).hexdigest()

    return md5 + suffix



def save_json(path: Path, data) -> None:
    """
    Ghi object thành JSON.
    """

    with open(path, "w", encoding="utf-8") as f:

        json.dump(
            data,
            f,
            ensure_ascii=False,
            indent=2,
        )


def load_json(path: Path):

    with open(path, "r", encoding="utf-8") as f:

        return json.load(f)


# ==========================================================
# JSONL
# ==========================================================

def append_jsonl(path: Path, obj: dict) -> None:
    """
    Ghi thêm một document vào file JSONL.
    """

    with open(path, "a", encoding="utf-8") as f:

        f.write(
            json.dumps(
                obj,
                ensure_ascii=False,
            )
        )

        f.write("\n")


# ==========================================================
# File
# ==========================================================

def ensure_directory(path: Path):
    """
    Tạo thư mục nếu chưa tồn tại.
    """

    path.mkdir(
        parents=True,
        exist_ok=True,
    )


def file_extension(path: str) -> str:
    """
    Trả về phần mở rộng.

    abc.pdf

    -->

    .pdf
    """

    return Path(path).suffix.lower()


# ==========================================================
# HTML
# ==========================================================

def clean_text(text: str):

    text = text.replace("\xa0", " ")

    text = text.replace("\r", "")

    # bỏ khoảng trắng cuối dòng
    text = re.sub(r"[ \t]+\n", "\n", text)

    # nhiều space -> 1 space
    text = re.sub(r"[ \t]+", " ", text)

    # giữ tối đa 2 dòng trống
    text = re.sub(r"\n{3,}", "\n\n", text)

    return text.strip()


def normalize_markdown(md: str) -> str:
    """
    Chuẩn hóa Markdown để phục vụ chunking.
    """

    md = clean_text(md)

    # Phần
    md = re.sub(
        r'^(PHẦN\s+[IVXLC\d]+.*)$',
        r'# \1',
        md,
        flags=re.MULTILINE | re.IGNORECASE,
    )

    # Chương
    md = re.sub(
        r'^(Chương\s+[IVXLC\d]+.*)$',
        r'# \1',
        md,
        flags=re.MULTILINE | re.IGNORECASE,
    )

    # Điều
    md = re.sub(
        r'^(Điều\s+\d+.*)$',
        r'## \1',
        md,
        flags=re.MULTILINE | re.IGNORECASE,
    )

    # Khoản
    md = re.sub(
        r'^(Khoản\s+\d+.*)$',
        r'### \1',
        md,
        flags=re.MULTILINE | re.IGNORECASE,
    )

    # Điểm a), b), c)...
    md = re.sub(
        r'^([a-z]\).*)$',
        r'- \1',
        md,
        flags=re.MULTILINE,
    )

    return md
