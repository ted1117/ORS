# Progress: PRD-003 주기적 ORS 데이터 동기화

## Goal

- Celery worker와 Beat가 `ORSClient`를 사용해 ORS 등급분류정보를 주기적으로 조회한다.
- 여러 페이지의 조회 결과를 페이지 단위 트랜잭션으로 PostgreSQL에 저장한다.
- `rating_number`를 기준으로 중복 생성을 막고 변경된 데이터를 갱신한다.
- 일시적인 외부 API 및 DB 오류에는 재시도 정책을 적용하고 처리 결과를 로그로 남긴다.
- 동기화 업무 로직을 FastAPI 또는 향후 다른 웹 프레임워크와 독립된 서비스 계층으로 구성한다.

## Current Status

- Status: In progress
- Branch: `feature/celery-integration`
- HEAD: `3e5dbc9` (`develop`, `origin/develop`과 동일한 commit)
- Current PRD: `docs/PRD-003.md`
- Current focus: 3단계 완료, HTTP 오류 재시도 분류 준비
- 현재 브랜치에는 Redis·worker·Beat의 Compose 실행 구성이 추가되었고, Sync Service·`upsert_many()` 및 동기화 task는 아직 구현되지 않았다.

## Scope

### Included

- Celery application, worker 및 Beat 설정
- Redis broker 개발 환경
- 프레임워크 독립 Sync Service
- 페이지 단위 다건 저장을 위한 `upsert_many()`
- 업체 목록, 실행 주기, 페이지 크기 및 rolling window 설정
- ORS 전체 페이지 순회
- task retry, 중복 실행 방지 및 오류 로깅
- 동기화 단위 테스트, PostgreSQL 통합 테스트 및 Redis/worker smoke test

### Excluded

- FastAPI에서 Litestar로의 전환
- 사용자용 조회 API
- 동기화 이력 조회 화면 및 운영자 관리 화면
- Celery 관리자 UI
- 대규모 과거 데이터 백필

## Decisions

- 동기화 task는 FastAPI 조회 라우터를 거치지 않고 `ORSClient`를 직접 호출한다.
- Sync Service는 웹 프레임워크의 라우터와 의존성 주입에 결합하지 않는다.
- ORS 응답의 `total_count`와 페이지 정보를 이용해 마지막 페이지까지 순회한다.
- 한 페이지의 데이터는 하나의 DB 트랜잭션으로 저장한다.
- 저장 멱등성은 `rating_number` unique constraint와 PostgreSQL upsert를 이용해 보장한다.
- 동기화는 월~금 09:00~18:40, 20분 간격으로 실행한다.
- 시간대는 `Asia/Seoul`을 사용하고, MVP에서는 공휴일을 별도 판별하지 않는다.
- 동기화 대상 업체는 환경변수로 관리하며 최대 5개로 제한한다.
- 조회 기간은 2일 rolling window를 사용한다.
- 동기화 이력과 마지막 성공 cursor는 이번 PRD에서 제외하고 후속 PRD로 분리한다.
- Redis DB 0은 broker, Redis DB 1은 result backend로 사용하고 기존 Compose에 함께 구성한다.
- timeout, HTTP 5xx, 일시적인 네트워크 오류 및 DB 연결 오류만 재시도 대상으로 삼는다.
- 최대 3회 재시도하고 backoff 상한은 900초로 둔다.
- 업체·조회 기간별 Redis lock TTL은 1800초로 둔다.
- 일일 ORS 호출 예산은 800회로 둔다.
- task soft timeout은 900초, hard timeout은 1200초로 둔다.
- 입력·응답 형식 오류는 무한 재시도하지 않고 실패 원인을 기록한다.

## Open Decisions

- 없음. 구현 중 세부 운영값이 변경되면 이 문서에 기록한다.

## Current Gaps

- ORS 조회 결과와 Repository를 연결하는 Sync Service가 없다.
- Repository는 단건 `upsert()`만 제공하며 페이지 단위 `upsert_many()`가 없다.
- 현재 `ORSHTTPError`는 HTTP 4xx와 5xx를 같은 예외로 변환하므로 재시도 대상을 구조적으로 구분할 수 없다.
- SyncService·task 관련 테스트가 아직 없다.

## Implementation Steps

1. [x] `Open Decisions`의 설정값과 실행 정책을 확정한다.
2. [x] Celery·Redis 의존성과 애플리케이션 설정을 추가한다.
3. [x] Docker Compose에 Redis, Celery worker 및 Beat 실행 구성을 추가한다.
4. [ ] HTTP 오류의 재시도 가능 여부를 구분할 수 있도록 ORS 예외 정보를 보완한다.
5. [ ] 한 페이지의 여러 항목을 한 트랜잭션으로 저장하는 `upsert_many()`를 구현한다.
6. [ ] 업체별 rolling window와 다중 페이지 순회를 담당하는 Sync Service를 구현한다.
7. [ ] Celery task, Beat 스케줄, retry, 호출량 보호, 중복 실행 방지 및 로깅을 연결한다.
8. [ ] Sync Service와 task 단위 테스트를 작성한다.
9. [ ] PostgreSQL 통합 테스트와 Redis/worker smoke test를 작성하고 실행한다.
10. [ ] 전체 테스트를 실행한 뒤 이 문서를 갱신한다.

## In Progress

- Celery·Redis 의존성과 PRD-003 실행 설정을 구현했다.
- Docker Compose에 Redis, worker 및 Beat 실행 구성을 구현했다.
- 다음 단계로 ORS HTTP 오류의 재시도 가능 여부를 구분한다.

## Changed Areas

### Current

- `docs/PRD-003.md`: 현재 작업 요구사항과 미결정 항목
- `docs/PROGRESS.md`: 현재 브랜치의 진행 상태
- `pyproject.toml`, `uv.lock`: Celery와 Redis 의존성
- `src/core/config.py`: Celery·동기화·retry·timeout 설정
- `tests/core/test_config.py`: 업체 목록 파싱 및 설정값 검증
- `docker-compose.yml`: Redis, Celery worker 및 Beat 서비스
- `Dockerfile`, `.dockerignore`: worker·Beat 공통 실행 이미지
- `src/celery_app.py`: Celery 애플리케이션 진입점과 timezone 설정

### Planned

- `src/ors/client.py`, `src/ors/exceptions.py`: HTTP 오류의 재시도 가능 여부 구분
- `src/repositories/video_rating.py`: 페이지 단위 다건 upsert
- Service/worker 모듈: 페이지 순회, 저장, task 및 Beat 구성
- `tests/`: Sync Service, task, retry, PostgreSQL 및 Redis/worker 검증

## Test Status

- SyncService·task 관련 테스트는 아직 작성되지 않았다.
- 설정 관련 PRD-003 테스트 7개가 통과했다.
- `docker compose config --quiet`와 worker·Beat 이미지 build가 통과했다.
- 빌드된 worker 이미지에서 Celery 앱 진입점 import smoke test가 통과했다.
- Redis/worker 실행 smoke test와 task 통합 테스트는 아직 실행하지 않았다.
- 구현 완료 후 관련 테스트를 먼저 실행하고, 작업 완료 전 `uv run pytest`로 전체 테스트를 실행한다.
