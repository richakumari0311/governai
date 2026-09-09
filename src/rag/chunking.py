import re
from dataclasses import dataclass
from langchain_text_splitters import RecursiveCharacterTextSplitter


@dataclass
class Chunk:
    text: str
    source: str
    chunk_type: str  # "prose" or "table_row"


def split_into_blocks(markdown_text: str) -> list[dict]:
    """Split a markdown document into alternating prose and table blocks."""
    lines = markdown_text.split("\n")
    blocks = []
    current_block: list[str] = []
    current_type = None

    for line in lines:
        is_table_line = line.strip().startswith("|")
        line_type = "table" if is_table_line else "prose"

        if current_type is not None and line_type != current_type:
            blocks.append({"type": current_type, "text": "\n".join(current_block)})
            current_block = []

        current_type = line_type
        current_block.append(line)

    if current_block:
        blocks.append({"type": current_type, "text": "\n".join(current_block)})

    return blocks


def table_block_to_sentences(table_text: str, doc_title: str) -> list[str]:
    """Convert a markdown table into one self-contained sentence per row."""
    rows = [r.strip() for r in table_text.strip().split("\n") if r.strip()]
    if len(rows) < 2:
        return []

    header_cells = [c.strip() for c in rows[0].strip("|").split("|")]
    data_rows = rows[2:]  # rows[1] is the "---|---|---" separator line

    sentences = []
    for row in data_rows:
        cells = [c.strip() for c in row.strip("|").split("|")]
        if len(cells) != len(header_cells):
            continue  # malformed row, skip rather than crash

        # first column is treated as the row's identity (e.g. "Manager", "P1 - Critical")
        subject = cells[0]
        facts = ", ".join(
            f"{header_cells[i]} is {cells[i]}"
            for i in range(1, len(cells))
        )
        sentence = f"In {doc_title}, for {header_cells[0]} '{subject}': {facts}."
        sentences.append(sentence)

    return sentences


def chunk_prose(prose_text: str, chunk_size: int = 500, overlap: int = 75) -> list[str]:
    """Chunk prose using recursive character splitting with overlap."""
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=overlap,
        separators=["\n## ", "\n### ", "\n\n", "\n", " ", ""],
    )
    return [c for c in splitter.split_text(prose_text) if c.strip()]


def chunk_document(markdown_text: str, doc_title: str, source: str) -> list[Chunk]:
    """Full pipeline: split into blocks, chunk each block type appropriately."""
    blocks = split_into_blocks(markdown_text)
    chunks: list[Chunk] = []

    for block in blocks:
        if block["type"] == "table":
            for sentence in table_block_to_sentences(block["text"], doc_title):
                chunks.append(Chunk(text=sentence, source=source, chunk_type="table_row"))
        else:
            for piece in chunk_prose(block["text"]):
                chunks.append(Chunk(text=piece, source=source, chunk_type="prose"))

    return chunks