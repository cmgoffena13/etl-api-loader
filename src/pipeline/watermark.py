from typing import Optional

import pendulum
import structlog
from sqlalchemy import text
from sqlalchemy.orm import Session, sessionmaker

from src.utils import retry

logger = structlog.getLogger(__name__)


@retry()
def get_watermark(
    source_name: str, endpoint_name: str, Session: sessionmaker[Session]
) -> Optional[str]:
    logger.info(f"Getting watermark for {source_name}/{endpoint_name}")
    watermark = None
    with Session() as session:
        result = session.execute(
            text(
                "SELECT watermark_value FROM api_watermark WHERE source_name = :source_name AND endpoint_name = :endpoint_name"
            ),
            {"source_name": source_name, "endpoint_name": endpoint_name},
        ).first()
        if result:
            watermark = result[0]
        else:
            logger.warning(
                f"No watermark value found for {source_name}/{endpoint_name}"
            )
        return watermark


@retry()
def set_watermark(
    source_name: str,
    endpoint_name: str,
    watermark_value: str,
    Session: sessionmaker[Session],
) -> None:
    with Session() as session:
        try:
            exists = session.execute(
                text(
                    "SELECT 1 FROM api_watermark WHERE source_name = :source_name AND endpoint_name = :endpoint_name"
                ),
                {"source_name": source_name, "endpoint_name": endpoint_name},
            ).first()

            now = pendulum.now("UTC")
            if exists:
                sql = """
                    UPDATE api_watermark 
                    SET watermark_attempted = :watermark_attempted, etl_updated_at = :etl_updated_at
                    WHERE source_name = :source_name AND endpoint_name = :endpoint_name
                """
                params = {
                    "source_name": source_name,
                    "endpoint_name": endpoint_name,
                    "watermark_attempted": watermark_value,
                    "etl_updated_at": now,
                }
            else:
                sql = """
                    INSERT INTO api_watermark (source_name, endpoint_name, watermark_attempted, etl_created_at)
                    VALUES (:source_name, :endpoint_name, :watermark_attempted, :etl_created_at)
                """
                params = {
                    "source_name": source_name,
                    "endpoint_name": endpoint_name,
                    "watermark_attempted": watermark_value,
                    "etl_created_at": now,
                }

            session.execute(text(sql), params)
            session.commit()
            logger.info(
                f"Set watermark_attempted for {source_name}/{endpoint_name}: {watermark_value}"
            )
        except Exception as e:
            logger.exception(f"Error setting watermark_attempted: {e}")
            session.rollback()
            raise


@retry()
def commit_watermark(
    source_name: str,
    endpoint_name: str,
    Session: sessionmaker[Session],
) -> None:
    with Session() as session:
        try:
            result = session.execute(
                text(
                    """
                    UPDATE api_watermark 
                    SET watermark_value = watermark_attempted, etl_updated_at = :etl_updated_at
                    WHERE source_name = :source_name AND endpoint_name = :endpoint_name
                    AND watermark_attempted IS NOT NULL
                    """
                ),
                {
                    "source_name": source_name,
                    "endpoint_name": endpoint_name,
                    "etl_updated_at": pendulum.now("UTC"),
                },
            )
            session.commit()
            if result.rowcount > 0:
                logger.info(f"Committed watermark for {source_name}/{endpoint_name}")
        except Exception as e:
            logger.exception(f"Error committing watermark: {e}")
            session.rollback()
            raise
