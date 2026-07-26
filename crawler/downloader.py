from pathlib import Path
from urllib.parse import urlparse, unquote
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from config import (
    HEADERS,
    REQUEST_TIMEOUT,
    MAX_RETRIES,
)

from utils import (
    safe_filename,
    logger,
)

# để mỗi lần get(ủl) không phải 1 lần kết nối mới
def create_session() -> requests.Session:

    session = requests.Session()

    session.headers.update(HEADERS)

    # để nếu lỗi có thể tải lại
    retry = Retry(
        total=MAX_RETRIES,
        backoff_factor=1,
        status_forcelist=[
            500,
            502,
            503,
            504,
        ],
        allowed_methods=["GET", "HEAD"]
    )

    adapter = HTTPAdapter(
        max_retries=retry
    )

    session.mount(
        "http://",
        adapter
    )

    session.mount(
        "https://",
        adapter
    )

    return session


# Session dùng chung cho toàn project
SESSION = create_session()



def download_html(url: str):
    """
    Download HTML page.

    Returns
    -------
    requests.Response | None
    """

    try:

        response = SESSION.get(
            url,
            timeout=REQUEST_TIMEOUT
        )

        response.raise_for_status()

        # lấy cái thuộc htlm
        content_type = response.headers.get(
            "Content-Type",
            ""
        ).lower()

        # nếu không thì không lấy
        if "text/html" not in content_type:

            return None


        response.encoding = "utf-8"


        return response


    except Exception as e:

        logger.error(
            f"HTML download failed: {url}"
        )

        logger.error(str(e))

        return None



def download_file(
    url: str,
    save_dir: Path
):

    # lấy tên file từ url
    filename = Path(
        unquote( # nếu chứa kí tự đặc biệt
            urlparse(url).path # lấy đường dẫn
        )
    ).name # lấy tên cuối cùng đó là tên file

    filename = safe_filename(filename) #sàe filename là sửa làm sạch những tên file lỗi

    if not filename:
        filename = "downloaded_file"

    # tạo đường dẫn để lưu về máy
    save_path = save_dir / filename

    try:

        response = SESSION.get(
            url,
            stream=True,  # để không tải vào ram mà lưu dần vào ổ cứng
            timeout=REQUEST_TIMEOUT
        )

        response.raise_for_status()

        # đọc từng 8kb ghi vào ổ cứng
        with open(save_path, "wb") as f: 

            for chunk in response.iter_content(chunk_size=8192):

                if chunk:

                    f.write(chunk)

    except Exception as e:

        logger.error(
            f"File download failed: {url}"
        )

        logger.error(str(e))

        return None

    logger.info(
        f"Downloaded: {save_path}"
    )

    return save_path


# để xem nó là htlm hay file
def get_content_type(url):

    try:
        r = SESSION.head(
            url,
            allow_redirects=True,
            timeout=REQUEST_TIMEOUT
        )

        if r.status_code >= 400:
            raise Exception()

        return r.headers.get("Content-Type","").lower()

    except Exception:

        try:
            r = SESSION.get(
                url,
                stream=True,
                timeout=REQUEST_TIMEOUT
            )

            return r.headers.get("Content-Type","").lower()

        except Exception:
            return None

# tìm kiểu file
def detect_file_type(
    url: str
):
    lower = url.lower()

    if lower.endswith(".pdf"):
        return "pdf"

    if lower.endswith(".docx"):
        return "docx"

    if lower.endswith(".doc"):
        return "doc"

    content_type = get_content_type(url)

    if not content_type:
        return "unknown"

    if "text/html" in content_type:
        return "html"

    if "application/pdf" in content_type:
        return "pdf"

    if "wordprocessingml" in content_type:
        return "docx"

    if "msword" in content_type:
        return "doc"

    return "unknown"