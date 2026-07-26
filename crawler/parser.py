from pathlib import Path
import nest_asyncio
import asyncio
from config import (
    REMOVE_TAGS,
    Llama_index_API,
    Gemini_index_API,
)
import io
import google.generativeai as genai
from llama_cloud import AsyncLlamaCloud
import fitz
from PIL import Image
import re
nest_asyncio.apply()

genai.configure(api_key=Gemini_index_API)

gemini = genai.GenerativeModel(
    "gemini-2.5-flash"
)

llama_client = AsyncLlamaCloud(
    api_key=Llama_index_API
)
from bs4 import BeautifulSoup
from markdownify import markdownify


from utils import (
    logger,
)

# promt yêu cầu gemini đọc bảng
TABLE_PROMPT = """
Bạn đang đọc ảnh chụp một hoặc nhiều trang PDF.

Nếu trang chứa bảng:

- KHÔNG xuất markdown table.
- KHÔNG xuất HTML.
- Chuyển bảng thành markdown dạng:

# Tên bảng

## Dòng ...

- Cột A: ...
- Cột B: ...
- Cột C: ...

Nếu có các dòng 2.1, 2.2...
hãy lồng dưới 2.

Giữ nguyên toàn bộ số liệu.

Nếu không chắc thì giữ nguyên.

Nếu không có bảng thì giữ nguyên nội dung.

Chỉ trả về markdown.
"""

def image_to_part(img):
    buf = io.BytesIO()
    img.save(buf, format="PNG")

    return {
        "mime_type": "image/png",
        "data": buf.getvalue(),
    }


# cử lý riêng trang lịch sử truyền thống 
def parse_history_page(soup):

    markdown = []

    titles = soup.select(".title")
    components = soup.select(".component")

    for title, component in zip(titles, components):

        md = markdownify(
            str(component),
            heading_style="ATX",
        )

        markdown.append(
            f"# {title.get_text(strip=True)}\n\n{md}"
        )

    return "\n\n".join(markdown)

# cử lý nhữung file còn lại
def parse_html(html: str):

    soup = BeautifulSoup(html, "lxml")

    # bỏ mấy cáu tag không cần thiết
    for tag_name in REMOVE_TAGS:
        for tag in soup.find_all(tag_name):
            tag.decompose()

    title = ""

    if soup.title:
        title = soup.title.get_text(strip=True)

    # lấy nội dung ở main content
    content = soup.select_one(".main-content")

    if content is None:

        if soup.select_one(".component"):
            return {
                "title": title,
                "text": parse_history_page(soup),
            }

        logger.warning(
            f"Cannot find .main-content: {title}"
        )

        return {
            "title": title,
            "text": "",
        }

    # bỏ mấy tag k cần thiết trong main content

    for tag in content.select(
        "nav,header,footer,script,style,.menu,.sidebar"
    ):
        tag.decompose()

    markdown = markdownify(
        str(content),
        heading_style="ATX",
    )
    return {
        "title": title,
        "text": markdown,
    }


# kiểm tra xem có bảng không
def has_markdown_table(md):

    if "<table" in md.lower():
        return True

    return bool(
        re.search(
            r"\|.*\|\n\|[-:| ]+\|",
            md
        )
    )

# xem có trang liên tiếp có bảng không để gửi gemini xử lý theo nhóm
def group_table_pages(pages):

    groups = []

    start = None

    for i, page in enumerate(pages):

        if has_markdown_table(page.markdown):

            if start is None:
                start = i

        else:

            if start is not None:
                groups.append((start, i - 1))
                start = None

    if start is not None:
        groups.append((start, len(pages) - 1))

    return groups

# hàm 
def parse_file(path: Path):

    try:

        async def run():

            file_obj = await llama_client.files.create(
                file=str(path),
                purpose="parse"
            )

            # dùng llama để chuyển sang markdown
            result = await llama_client.parsing.parse(
                file_id=file_obj.id,
                tier="agentic",
                version="latest",
                expand=["markdown"]
            )

            return result

        result = asyncio.run(run())

        pages = result.markdown.pages

        if path.suffix.lower() != ".pdf":

            return {
                "title": path.stem,
                "text": "\n\n".join(
                    page.markdown
                    for page in pages
                )
            }

        # nếu là pdf 
        doc = fitz.open(str(path))

        output = []
        # tìm trang có bảng
        groups = group_table_pages(pages)
        logger.info(f"Detected table groups: {groups}")

        table_map = {
            i: (s, e)
            for s, e in groups
            for i in range(s, e + 1)
        }

        i = 0

        while i < len(pages):

            # trang thường
            if i not in table_map:

                output.append(pages[i].markdown)

                i += 1

                continue

            # cụm bảng
            start, end = table_map[i]

            logger.info(
                f"Gemini pages {start+1}-{end+1}"
            )

            batch = []

            for p in range(start, end + 1):
                #trang có bảng
                pix = doc[p].get_pixmap(
                    dpi=200,
                    alpha=False
                )

                img = Image.frombytes(
                    "RGB",
                    [pix.width, pix.height],
                    pix.samples
                )

                batch.append(image_to_part(img))

            try:
                # gửi gemini
                print("Before Gemini")
                response = gemini.generate_content(
                    [TABLE_PROMPT] + batch
                )
                print("After Gemini")
                if response.text and response.text.strip():
                    output.append(response.text)
                else:
                    raise ValueError("Gemini returned empty response")

            except Exception as e:

                logger.warning(f"Gemini failed: {e}")

                for p in range(start, end + 1):
                    output.append(pages[p].markdown)

            i = end + 1
        doc.close()
        return {
            "title": path.stem,
            "text": "\n\n".join(output) # gộp lại
        }

    except Exception as e:

        logger.error(e)

        return {
            "title": path.stem,
            "text": ""
        }