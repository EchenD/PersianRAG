import pytest
from modules.utils import clean_text, sanitize_input, build_context
from langchain_core.documents import Document

def test_clean_text():
    input_text = "سلام! این یک متن نمونه است با @#$ و اعداد ۱۲۳."
    expected = "سلام این یک متن نمونه است با و اعداد ۱۲۳"
    assert clean_text(input_text) == expected

    # Test empty input
    assert clean_text("") == ""

def test_sanitize_input():
    valid_input = "سلام، این یک سوال فارسی است؟"
    assert sanitize_input(valid_input) == valid_input

    # Test HTML tags
    assert "<script>" not in sanitize_input("<script>سلام</script>")

    # Test max length
    long_input = "ا" * 1001
    with pytest.raises(ValueError, match="طول ورودی بیش از حد مجاز است"):
        sanitize_input(long_input)

    # Test non-Persian input
    with pytest.raises(ValueError, match="متن ورودی فاقد حروف فارسی است"):
        sanitize_input("Hello, this is English!")

def test_build_context():
    docs = [
        Document(page_content="متن نمونه ۱", metadata={"chunk_index": 1}),
        Document(page_content="متن نمونه ۲", metadata={"chunk_index": 2})
    ]
    context_chunks, context_html = build_context(docs)
    assert "[Chunk 1]" in context_chunks
    assert "متن نمونه ۱" in context_chunks
    assert "<br>" in context_html
    assert "متن نمونه ۱" in context_html

    # Test empty input
    context_chunks, context_html = build_context([])
    assert context_chunks == ""
    assert "هیچ متنی یافت نشد" in context_html