class ORSError(Exception):
    """ORS API 관련 예외의 기본 클래스"""


class ORSHTTPError(ORSError):
    """ORS API HTTP 요청 실패"""


class ORSTimeoutError(ORSError):
    """ORS API 요청 시간 초과"""


class ORSResponseError(ORSError):
    """ORS API 유효하지 않은 응답 발생"""
