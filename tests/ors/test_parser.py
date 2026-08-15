from datetime import date
from pathlib import Path

from src.ors.parser import parse_response

FIXTURES_DIR = Path(__file__).parent / "fixtures"


def test_parse_response():
    xml = (FIXTURES_DIR / "video_search_success.xml").read_text()

    result = parse_response(xml)

    assert result.page == 1
    assert result.page_size == 1000
    assert result.total_count == 45
    assert len(result.items) == 45

    first = result.items[0]

    assert first.title == "대전 감사합니다 ~숙녀는 격투 게임을 안 해요~ 1기 (1-3화)"
    assert first.original_title == "Young Ladies Don't Play Fighting Games S1"
    assert first.rating_number == "2026-VF02770"
    assert first.rating_date == date(2026, 7, 21)
    assert first.grade == "15세이상관람가"
    assert first.applicant_name == "크런치롤코리아 유한회사"


def test_parse_empty_element_as_none():
    xml = (FIXTURES_DIR / "video_search_success.xml").read_text()

    result = parse_response(xml)

    # 두 번째 item의 <rtCoreHarmRsnNm/>
    assert result.items[1].core_harm_reason is None
