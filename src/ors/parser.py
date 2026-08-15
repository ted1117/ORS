from datetime import date, datetime
from xml.etree import ElementTree

from .schemas import VideoRating, VideoRatingPage


def parse_response(xml: str) -> VideoRatingPage:
    root = ElementTree.fromstring(xml)

    header = root.find("header")
    body = root.find("body")

    if header is None or body is None:
        raise ValueError("Invalid ORS response")

    result_code = header.findtext("resultCode")

    if result_code != "00":
        result_message = header.findtext("resultMsg")
        raise ValueError(f"ORS API error: {result_code} {result_message}")

    items = [_parse_item(element) for element in body.findall("./items/item")]

    return VideoRatingPage(
        items=items,
        page=int(body.findtext("pageNo", "1")),
        page_size=int(body.findtext("numOfRows", "0")),
        total_count=int(body.findtext("totalCount", "0")),
    )


def _parse_item(element: ElementTree.Element) -> VideoRating:
    return VideoRating(
        title=element.findtext("useTitle", ""),
        original_title=_parse_optional_text(element.findtext("oriTitle")),
        rating_number=element.findtext("rtNo", ""),
        rating_date=_parse_date(element.findtext("rtDate")),
        grade=element.findtext("gradeName", ""),
        applicant_name=element.findtext("aplcName", ""),
        producer_name=_parse_optional_text(element.findtext("prodcName")),
        production_country=_parse_optional_text(element.findtext("prodcNatnlName")),
        production_year=_parse_int(element.findtext("prodYear")),
        kind=_parse_optional_text(element.findtext("kindName")),
        running_time=_parse_optional_text(element.findtext("screTime")),
        director_name=_parse_optional_text(element.findtext("direName")),
        lead_actor_name=_parse_optional_text(element.findtext("leadaName")),
        content=_parse_optional_text(element.findtext("workCont")),
        core_harm_reason=_parse_optional_text(element.findtext("rtCoreHarmRsnNm")),
    )


def _parse_optional_text(value: str | None) -> str | None:
    return value or None


def _parse_date(value: str | None) -> date | None:
    if not value:
        return None

    return datetime.strptime(value, "%Y%m%d").date()


def _parse_int(value: str | None) -> int | None:
    return int(value) if value else None
