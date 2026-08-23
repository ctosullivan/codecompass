from codecompass.doc_chunking import DocChunk, chunk_markdown


def test_no_headings_produces_no_chunks() -> None:
    text = "just plain text\nno headings at all\n"
    assert chunk_markdown(text) == []


def test_empty_text_produces_no_chunks() -> None:
    assert chunk_markdown("") == []


def test_single_top_level_heading_produces_one_chunk() -> None:
    text = "# Title\n\nBody text.\n"
    chunks = chunk_markdown(text)
    assert chunks == [
        DocChunk(
            heading_path="Title",
            start_line=1,
            end_line=3,
            content_hash=chunks[0].content_hash,
        )
    ]


def test_leading_content_before_first_heading_gets_its_own_chunk() -> None:
    text = "Intro line.\n\n# Title\n\nBody.\n"
    chunks = chunk_markdown(text)
    assert [(c.heading_path, c.start_line, c.end_line) for c in chunks] == [
        ("", 1, 2),
        ("Title", 3, 5),
    ]


def test_nested_heading_levels_build_a_root_first_path() -> None:
    text = (
        "# Title\n\n"
        "intro\n\n"
        "## Scope\n\n"
        "scope text\n\n"
        "### Covers\n\n"
        "covers text\n\n"
        "## Files\n\n"
        "files text\n"
    )
    chunks = chunk_markdown(text)
    assert [c.heading_path for c in chunks] == [
        "Title",
        "Title > Scope",
        "Title > Scope > Covers",
        "Title > Files",
    ]
    # Popping back from a level-3 heading to a sibling level-2 heading
    # must drop the level-3 title from the path, not append to it.
    assert "Covers" not in chunks[3].heading_path


def test_chunk_boundaries_are_contiguous_and_cover_the_whole_file() -> None:
    text = "# A\n\ntext a\n\n# B\n\ntext b\n\n# C\n\ntext c\n"
    lines = text.splitlines()
    chunks = chunk_markdown(text)
    assert chunks[0].start_line == 1
    assert chunks[-1].end_line == len(lines)
    for prev, nxt in zip(chunks, chunks[1:]):
        assert nxt.start_line == prev.end_line + 1


def test_content_hash_reflects_only_that_chunks_own_text() -> None:
    text_a = "# A\n\nsame body\n\n# B\n\ndifferent in A\n"
    text_b = "# A\n\nsame body\n\n# B\n\ndifferent in B\n"
    chunks_a = chunk_markdown(text_a)
    chunks_b = chunk_markdown(text_b)
    # Chunk "A" is byte-identical across both docs — same hash.
    assert chunks_a[0].content_hash == chunks_b[0].content_hash
    # Chunk "B" differs — different hash. A change confined to one
    # section must not appear to invalidate an unrelated section's hash.
    assert chunks_a[1].content_hash != chunks_b[1].content_hash


def test_heading_with_no_space_after_hash_is_not_treated_as_a_heading() -> None:
    # "#tag" (no space) is common in prose/hashtags, not markdown syntax.
    text = "Some text with a #hashtag in it.\nMore text.\n"
    assert chunk_markdown(text) == []


def test_heading_line_trailing_whitespace_is_trimmed_from_the_title() -> None:
    text = "#   Title with leading/trailing spaces   \n\nbody\n"
    chunks = chunk_markdown(text)
    assert chunks[0].heading_path == "Title with leading/trailing spaces"
