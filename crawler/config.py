from pathlib import Path
import os
from dotenv import load_dotenv

load_dotenv()  # Đọc file .env

Llama_index_API = os.getenv("Llama_index_API")
Gemini_index_API = os.getenv("Gemini_index_API")
Hug_API = os.getenv("Hug_API")

# lấy nội dung từ web có
BASE_URL = "https://handbook.uet.vnu.edu.vn"

# Chỉ crawl trong domain này
ALLOWED_DOMAIN = "handbook.uet.vnu.edu.vn"

# Thời gian timeout cho mỗi request 
REQUEST_TIMEOUT = 20

# Giới hạn số trang crawl (để tránh vòng lặp vô hạn)
MAX_PAGES = 5000

# khi lỗi thi được 3 lần làm lại
MAX_RETRIES = 3

# Delay giữa các request
REQUEST_DELAY = 0.2

# Có crawl các file đính kèm hay không
DOWNLOAD_ATTACHMENTS = True

# Các định dạng file được tải
ALLOWED_FILE_EXTENSIONS = {
    ".pdf",
    ".doc",
    ".docx",
}

# tránh việc trang web chặn bot
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/126.0 Safari/537.36"
    )
}


PROJECT_ROOT = Path(__file__).resolve().parent.parent

DATA_DIR = PROJECT_ROOT / "data"

HTML_DIR = DATA_DIR / "html"

FILES_DIR = DATA_DIR / "files"

RAW_DIR = DATA_DIR / "raw"

RAW_MD_DIR = DATA_DIR / "raw" / "markdown"

LOG_DIR = DATA_DIR / "logs"

METADATA_FILE = DATA_DIR / "metadata.json"

CRAWL_LOG = LOG_DIR / "crawler.log"


# Các thẻ HTML không cần lấy nội dung
REMOVE_TAGS = {
    "script",  # này không phải hiện nội dung
    "style",  # này là css
    "noscript",
    "iframe",
    "svg",
    "footer",
    "header",
}


PDF_ENCODING = "utf-8"

DOCX_ENCODING = "utf-8"

# tạo thư mục
for directory in (
    DATA_DIR,
    HTML_DIR,
    FILES_DIR,
    RAW_DIR,
    LOG_DIR,
    RAW_MD_DIR,
):
    directory.mkdir(parents=True, exist_ok=True)
    