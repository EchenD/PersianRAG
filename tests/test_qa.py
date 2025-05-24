import pytest
from modules.qa import handle_greeting, handle_meta_question

def test_handle_greeting():
    # Test general salutations
    assert handle_greeting("سلام") != False
    assert handle_greeting("درود بر شما") != False
    assert "سلام" in handle_greeting("سلام")[1] or "درود" in handle_greeting("سلام")[1]

    # Test time-based greetings
    assert "صبح" in handle_greeting("صبح بخیر")[1]
    assert "شب" in handle_greeting("شب بخیر")[1]
    assert "وقت" in handle_greeting("وقت بخیر")[1]

    # Test farewells
    assert "خداحافظ" in handle_greeting("خداحافظ")[1] or "خدانگهدار" in handle_greeting("خداحافظ")[1]
    assert "روز خوش" in handle_greeting("روز خوش")[1]

    # Test non-greetings
    assert handle_greeting("قیمت محصول چنده؟") == False

def test_handle_meta_question():
    # Test meta questions
    assert handle_meta_question("تو کی هستی؟") != False
    assert handle_meta_question("اسمت چیه؟") != False
    assert "مستندات" in handle_meta_question("چه کسی شما را ساخته است؟")[1]

    # Test non-meta questions
    assert handle_meta_question("چطور فایل آپلود کنم؟") == False
    assert handle_meta_question("امروز هوا چطوره؟") == False