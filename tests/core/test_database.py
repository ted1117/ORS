import asyncio

from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_db_session


def test_get_db_session_yields_async_session():
    async def exercise_dependency() -> None:
        dependency = get_db_session()
        session = await anext(dependency)

        assert isinstance(session, AsyncSession)

        await dependency.aclose()

    asyncio.run(exercise_dependency())
