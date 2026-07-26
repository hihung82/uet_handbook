from dataclasses import dataclass
import re
import uuid

MAX_CHUNK_LENGTH = 2000
MIN_CHUNK_LENGTH = 100


@dataclass
class SectionNode:
    title: str
    chapter: str | None = None
    article: str | None = None

    heading1: str | None = None
    heading2: str | None = None
    heading3: str | None = None
    heading4: str | None = None

    text: str = ""

def is_heading(line):

    return re.match(
        r"^(#{1,6})\s+(.+)$",
        line
    )


def is_chapter_line(line):

    line = re.sub(r"^#{1,3}\s*", "", line)

    return re.match(
        r"^\s*Chương\s+[IVXLCDM\d]+\b",
        line,
        re.I
    )


def is_article_line(line):

    line = line.strip()

    # Bỏ markdown heading (#, ##, ###...)
    line = re.sub(r"^#{1,6}\s*", "", line)

    # Bỏ bullet nếu có
    line = line.strip("* ")

    return re.match(
        r"^Điều\s+\d+([.:]|$|\s)",
        line,
        re.I
    )

# khi sang nội dung mới thì những nội dung trước k còn hiệu lực
def reset_lower_levels(current, level):

    if level <= 1:
        current.heading2 = None
        current.heading3 = None
        current.heading4 = None

    elif level == 2:
        current.heading3 = None
        current.heading4 = None

    elif level == 3:
        current.heading4 = None

def parse_document(document):

    lines = document["text"].splitlines()

    nodes = []

    current = SectionNode(
        title=document["title"]
    )

    def flush():

        nonlocal current

        if current.text.strip():

            nodes.append(current)

        current = SectionNode(
            title=document["title"],
            chapter=current.chapter,
            article=current.article,
            heading1=current.heading1,
            heading2=current.heading2,
            heading3=current.heading3,
            heading4=current.heading4
        )

    for line in lines:

        line = line.strip()

        if not line:
            continue

        # Ưu tiên Chapter
        if is_chapter_line(line):

            flush()
            chapter = re.sub(r"^#{1,3}\s*", "", line).strip()
            current.chapter = chapter
            current.article = None

            current.heading1 = None
            current.heading2 = None
            current.heading3 = None
            current.heading4 = None

            continue

        # Sau đó Article
        if is_article_line(line):

            flush()

            article = re.sub(r"^#{1,6}\s*", "", line)
            article = article.strip("* ").strip()

            current.article = article

            current.heading3 = None
            current.heading4 = None

            continue

        # Cuối cùng mới xử lý Heading
        heading = is_heading(line)

        if heading:

            level = len(heading.group(1))
            text = heading.group(2).strip()

            # Nếu node hiện tại đã có nội dung thì tạo node mới
            if current.text.strip():
                flush()

            reset_lower_levels(current, level)

            if level == 1:
                current.heading1 = text

                # Sang section mới thì article không còn hiệu lực
                current.article = None

            elif level == 2:
                current.heading2 = text

            elif level == 3:
                current.heading3 = text

            elif level >= 4:
                current.heading4 = text

            continue

        current.text += line + "\n"

    flush()

    return nodes

# nếu 1 chunk dài quá thì chia theo mấy cái kiểu 1 2 3 a b c 
def split_long_text(text):

    # Không cần chia
    if len(text) <= MAX_CHUNK_LENGTH:
        return [text]

    paragraphs = re.split(
        r"\n(?=(?:- |\d+\.|[a-z]\)|[IVXLCDM]+\.) )",
        text
    )

    sections = []

    for p in paragraphs:
        p = p.strip()
        if p:
            sections.append(p)

    chunks = []
    current = ""

    for sec in sections:

        sec = sec.strip()

        if not sec:
            continue

        # Ghép nếu còn đủ chỗ
        if len(current) + len(sec) + 2 <= MAX_CHUNK_LENGTH:

            if current:
                current += "\n\n"

            current += sec

        else:

            if current:
                chunks.append(current)

            # section quá lớn -> cắt theo paragraph
            if len(sec) > MAX_CHUNK_LENGTH:

                paragraphs = re.split(
                    r"\n(?=(?:- |\d+\.|[a-z]\)|[IVXLCDM]+\.) )",
                    sec
                )

                tmp = ""

                for para in paragraphs:

                    para = para.strip()

                    if not para:
                        continue

                    if len(tmp) + len(para) + 2 <= MAX_CHUNK_LENGTH:

                        if tmp:
                            tmp += "\n\n"

                        tmp += para

                    else:

                        if tmp:
                            chunks.append(tmp)

                        tmp = para

                if tmp:
                    chunks.append(tmp)

                current = ""

            else:

                current = sec

    if current:
        chunks.append(current)

    return chunks

# thêm ngữ cảnh lên trước nội dung 
def build_prefix(node):

    prefix = []

    prefix.append(
        f"Tiêu đề: {node.title}"
    )

    if node.heading1:
        prefix.append(
            f"# {node.heading1}"
        )

    if node.chapter:
        prefix.append(
            node.chapter
        )

    if node.heading2:
        prefix.append(
            f"## {node.heading2}"
        )

    if node.article:
        prefix.append(
            node.article
        )

    if node.heading3:
        prefix.append(
            f"### {node.heading3}"
        )

    if node.heading4:
        prefix.append(
            f"#### {node.heading4}"
        )

    return "\n".join(prefix)

def create_chunks(document):

    nodes = parse_document(document)

    chunks = []

    for node in nodes:

        pieces = split_long_text(node.text)

        prefix = build_prefix(node)

        for idx, piece in enumerate(pieces):

            piece = piece.strip()

            if len(piece) < MIN_CHUNK_LENGTH:
                continue

            text = prefix + "\n\n" + piece.strip()

            chunks.append({

                "chunk_id": str(uuid.uuid4()),

                "document_id": document["id"],

                "title": document["title"],

                "source": document["source"],

                "type": document["type"],

                "chapter": node.chapter,

                "article": node.article,

                "heading1": node.heading1,

                "heading2": node.heading2,

                "heading3": node.heading3,

                "heading4": node.heading4,

                "chunk_index": idx,

                "char_length": len(piece),

                "text": text

            })

    return chunks