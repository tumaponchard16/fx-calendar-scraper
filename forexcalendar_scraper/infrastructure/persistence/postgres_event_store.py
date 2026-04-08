"""PostgreSQL-backed event store used by the API and dual-write workflows."""

from __future__ import annotations

import re
from collections import defaultdict
from collections.abc import Iterable, Sequence
from pathlib import Path
from typing import Any

import psycopg
from psycopg.rows import dict_row
from psycopg.types.json import Jsonb

from forexcalendar_scraper.domain.entities import (
    CalendarEvent,
    DetailBlock,
    HistoryRecord,
    NewsItem,
    StoredCalendarEvent,
    StoredEventAggregate,
)

_WHITESPACE_RE = re.compile(r"\s+")


def _normalize_key_part(value: str) -> str:
    return _WHITESPACE_RE.sub(" ", value.strip().lower())


def build_source_event_key(
    date_param: str,
    event_date: str,
    event_time: str,
    currency: str,
    event_name: str,
    detail_id: str,
) -> str:
    return "|".join(
        [
            _normalize_key_part(date_param),
            _normalize_key_part(event_date),
            _normalize_key_part(event_time),
            _normalize_key_part(currency),
            _normalize_key_part(event_name),
            _normalize_key_part(detail_id),
        ]
    )


def _timestamp_to_text(value: object) -> str:
    if hasattr(value, "isoformat"):
        return value.isoformat()
    return str(value) if value is not None else ""


class PostgresEventStore:
    """Persist events and related data in PostgreSQL."""

    _schema_sql: str | None = None

    def __init__(self, dsn: str) -> None:
        self.dsn = dsn
        self.ensure_schema()

    def is_enabled(self) -> bool:
        return True

    def ensure_schema(self) -> None:
        with self._connect() as connection:
            connection.execute(self._load_schema_sql())

    def upsert_events(
        self,
        date_param: str,
        events: Iterable[CalendarEvent],
        output_file: str | None = None,
    ) -> None:
        event_list = list(events)
        if not event_list:
            return

        with self._connect() as connection:
            with connection.cursor() as cursor:
                for event in event_list:
                    self._upsert_event_row(cursor, date_param, event, output_file=output_file)

    def upsert_detail_blocks(
        self,
        date_param: str,
        detail_results: Iterable[tuple[CalendarEvent, DetailBlock]],
    ) -> None:
        detail_rows = list(detail_results)
        if not detail_rows:
            return

        with self._connect() as connection:
            with connection.cursor() as cursor:
                for event, detail_block in detail_rows:
                    event_id = self._upsert_event_row(cursor, date_param, event)
                    specs = dict(detail_block.fields)
                    full_details_url = specs.pop("full_details_url", "")
                    cursor.execute(
                        """
                        INSERT INTO event_details (
                            event_id,
                            detail_id,
                            event_date,
                            event_time,
                            event_currency,
                            event_name,
                            full_details_url,
                            specs_json
                        )
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                        ON CONFLICT (event_id) DO UPDATE SET
                            detail_id = EXCLUDED.detail_id,
                            event_date = EXCLUDED.event_date,
                            event_time = EXCLUDED.event_time,
                            event_currency = EXCLUDED.event_currency,
                            event_name = EXCLUDED.event_name,
                            full_details_url = EXCLUDED.full_details_url,
                            specs_json = EXCLUDED.specs_json,
                            updated_at = NOW()
                        """,
                        (
                            event_id,
                            detail_block.detail_id,
                            detail_block.event_date,
                            detail_block.event_time,
                            detail_block.event_currency,
                            detail_block.event_name,
                            full_details_url,
                            Jsonb(specs),
                        ),
                    )

    def replace_history_records(
        self,
        date_param: str,
        history_results: Iterable[tuple[CalendarEvent, Sequence[HistoryRecord]]],
    ) -> None:
        grouped_rows = self._prepare_grouped_history_rows(date_param, history_results)
        if not grouped_rows:
            return

        with self._connect() as connection:
            with connection.cursor() as cursor:
                event_ids = list(grouped_rows.keys())
                cursor.execute(
                    "DELETE FROM event_history_records WHERE event_id = ANY(%s)",
                    (event_ids,),
                )
                insert_rows = [
                    row
                    for event_rows in grouped_rows.values()
                    for row in event_rows
                ]
                if insert_rows:
                    cursor.executemany(
                        """
                        INSERT INTO event_history_records (
                            event_id,
                            detail_id,
                            event_name,
                            event_date,
                            event_currency,
                            release_date,
                            date_url,
                            actual,
                            forecast,
                            previous
                        )
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                        """,
                        insert_rows,
                    )

    def replace_news_items(
        self,
        date_param: str,
        news_results: Iterable[tuple[CalendarEvent, Sequence[NewsItem]]],
    ) -> None:
        grouped_rows = self._prepare_grouped_news_rows(date_param, news_results)
        if not grouped_rows:
            return

        with self._connect() as connection:
            with connection.cursor() as cursor:
                event_ids = list(grouped_rows.keys())
                cursor.execute(
                    "DELETE FROM event_news_items WHERE event_id = ANY(%s)",
                    (event_ids,),
                )
                insert_rows = [
                    row
                    for event_rows in grouped_rows.values()
                    for row in event_rows
                ]
                if insert_rows:
                    cursor.executemany(
                        """
                        INSERT INTO event_news_items (
                            event_id,
                            detail_id,
                            event_name,
                            event_date,
                            event_currency,
                            title,
                            url,
                            snippet,
                            link_type
                        )
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                        """,
                        insert_rows,
                    )

    def list_events(
        self,
        date_param: str | None = None,
        currency: str | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> list[StoredCalendarEvent]:
        query = [
            """
            SELECT
                id,
                source_event_key,
                date_param,
                event_date,
                event_time,
                currency,
                impact,
                event_name,
                actual,
                forecast,
                previous,
                source_detail_id,
                output_file,
                created_at,
                updated_at
            FROM calendar_events
            """
        ]
        filters: list[str] = []
        params: list[Any] = []

        if date_param:
            filters.append("date_param = %s")
            params.append(date_param)
        if currency:
            filters.append("UPPER(currency) = UPPER(%s)")
            params.append(currency)

        if filters:
            query.append("WHERE " + " AND ".join(filters))

        query.append("ORDER BY created_at DESC, id DESC LIMIT %s OFFSET %s")
        params.extend([limit, offset])

        with self._connect() as connection:
            rows = connection.execute("\n".join(query), params).fetchall()

        return [self._row_to_stored_event(row) for row in rows]

    def get_event(self, event_id: int) -> StoredEventAggregate | None:
        with self._connect() as connection:
            event_row = connection.execute(
                """
                SELECT
                    id,
                    source_event_key,
                    date_param,
                    event_date,
                    event_time,
                    currency,
                    impact,
                    event_name,
                    actual,
                    forecast,
                    previous,
                    source_detail_id,
                    output_file,
                    created_at,
                    updated_at
                FROM calendar_events
                WHERE id = %s
                """,
                (event_id,),
            ).fetchone()
            if event_row is None:
                return None

            detail_row = connection.execute(
                """
                SELECT
                    event_id,
                    detail_id,
                    event_date,
                    event_time,
                    event_currency,
                    event_name,
                    full_details_url,
                    specs_json
                FROM event_details
                WHERE event_id = %s
                """,
                (event_id,),
            ).fetchone()
            history_rows = connection.execute(
                """
                SELECT
                    detail_id,
                    event_name,
                    event_date,
                    event_currency,
                    release_date,
                    date_url,
                    actual,
                    forecast,
                    previous
                FROM event_history_records
                WHERE event_id = %s
                ORDER BY id ASC
                """,
                (event_id,),
            ).fetchall()
            news_rows = connection.execute(
                """
                SELECT
                    detail_id,
                    event_name,
                    event_date,
                    event_currency,
                    title,
                    url,
                    snippet,
                    link_type
                FROM event_news_items
                WHERE event_id = %s
                ORDER BY id ASC
                """,
                (event_id,),
            ).fetchall()

        return StoredEventAggregate(
            event=self._row_to_stored_event(event_row),
            details=self._row_to_detail_block(detail_row) if detail_row else None,
            history=[self._row_to_history_record(row) for row in history_rows],
            news=[self._row_to_news_item(row) for row in news_rows],
        )

    def _connect(self) -> psycopg.Connection[Any]:
        return psycopg.connect(self.dsn, row_factory=dict_row)

    @classmethod
    def _load_schema_sql(cls) -> str:
        if cls._schema_sql is None:
            schema_file = Path(__file__).resolve().parent / "sql" / "001_initial_postgres.sql"
            cls._schema_sql = schema_file.read_text(encoding="utf-8")
        return cls._schema_sql

    def _upsert_event_row(
        self,
        cursor: psycopg.Cursor[Any],
        date_param: str,
        event: CalendarEvent,
        output_file: str | None = None,
    ) -> int:
        source_event_key = build_source_event_key(
            date_param,
            event.date,
            event.time,
            event.currency,
            event.name,
            event.detail_id,
        )
        cursor.execute(
            """
            INSERT INTO calendar_events (
                source_event_key,
                date_param,
                source_detail_id,
                event_date,
                event_time,
                currency,
                impact,
                event_name,
                actual,
                forecast,
                previous,
                output_file
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (source_event_key) DO UPDATE SET
                date_param = EXCLUDED.date_param,
                source_detail_id = EXCLUDED.source_detail_id,
                event_date = EXCLUDED.event_date,
                event_time = EXCLUDED.event_time,
                currency = EXCLUDED.currency,
                impact = EXCLUDED.impact,
                event_name = EXCLUDED.event_name,
                actual = EXCLUDED.actual,
                forecast = EXCLUDED.forecast,
                previous = EXCLUDED.previous,
                output_file = COALESCE(EXCLUDED.output_file, calendar_events.output_file),
                updated_at = NOW()
            RETURNING id
            """,
            (
                source_event_key,
                date_param,
                event.detail_id,
                event.date,
                event.time,
                event.currency,
                event.impact,
                event.name,
                event.actual,
                event.forecast,
                event.previous,
                output_file,
            ),
        )
        row = cursor.fetchone()
        return int(row["id"])

    def _prepare_grouped_history_rows(
        self,
        date_param: str,
        history_results: Iterable[tuple[CalendarEvent, Sequence[HistoryRecord]]],
    ) -> dict[int, list[tuple[object, ...]]]:
        grouped_results = list(history_results)
        if not grouped_results:
            return {}

        prepared_rows: dict[int, list[tuple[object, ...]]] = defaultdict(list)
        with self._connect() as connection:
            with connection.cursor() as cursor:
                for event, records in grouped_results:
                    event_id = self._upsert_event_row(cursor, date_param, event)
                    prepared_rows[event_id] = [
                        (
                            event_id,
                            record.detail_id,
                            record.event_name,
                            record.event_date,
                            record.event_currency,
                            record.date,
                            record.date_url,
                            record.actual,
                            record.forecast,
                            record.previous,
                        )
                        for record in records
                    ]
        return prepared_rows

    def _prepare_grouped_news_rows(
        self,
        date_param: str,
        news_results: Iterable[tuple[CalendarEvent, Sequence[NewsItem]]],
    ) -> dict[int, list[tuple[object, ...]]]:
        grouped_results = list(news_results)
        if not grouped_results:
            return {}

        prepared_rows: dict[int, list[tuple[object, ...]]] = defaultdict(list)
        with self._connect() as connection:
            with connection.cursor() as cursor:
                for event, items in grouped_results:
                    event_id = self._upsert_event_row(cursor, date_param, event)
                    prepared_rows[event_id] = [
                        (
                            event_id,
                            item.detail_id,
                            item.event_name,
                            item.event_date,
                            item.event_currency,
                            item.title,
                            item.url,
                            item.snippet,
                            item.link_type,
                        )
                        for item in items
                    ]
        return prepared_rows

    def _row_to_stored_event(self, row: dict[str, object]) -> StoredCalendarEvent:
        return StoredCalendarEvent(
            id=int(row["id"]),
            source_event_key=str(row["source_event_key"]),
            date_param=str(row["date_param"] or ""),
            date=str(row["event_date"] or ""),
            time=str(row["event_time"] or ""),
            currency=str(row["currency"] or ""),
            impact=str(row["impact"] or ""),
            name=str(row["event_name"] or ""),
            actual=str(row["actual"] or ""),
            forecast=str(row["forecast"] or ""),
            previous=str(row["previous"] or ""),
            detail_id=str(row["source_detail_id"] or ""),
            output_file=str(row["output_file"] or ""),
            created_at=_timestamp_to_text(row.get("created_at")),
            updated_at=_timestamp_to_text(row.get("updated_at")),
        )

    def _row_to_detail_block(self, row: dict[str, object]) -> DetailBlock:
        fields = dict(row.get("specs_json") or {})
        full_details_url = str(row.get("full_details_url") or "")
        if full_details_url:
            fields["full_details_url"] = full_details_url

        return DetailBlock(
            detail_id=str(row.get("detail_id") or ""),
            event_date=str(row.get("event_date") or ""),
            event_time=str(row.get("event_time") or ""),
            event_currency=str(row.get("event_currency") or ""),
            event_name=str(row.get("event_name") or ""),
            fields={str(key): str(value) for key, value in fields.items()},
        )

    def _row_to_history_record(self, row: dict[str, object]) -> HistoryRecord:
        return HistoryRecord(
            detail_id=str(row.get("detail_id") or ""),
            date=str(row.get("release_date") or ""),
            date_url=str(row.get("date_url") or ""),
            actual=str(row.get("actual") or ""),
            forecast=str(row.get("forecast") or ""),
            previous=str(row.get("previous") or ""),
            event_name=str(row.get("event_name") or ""),
            event_date=str(row.get("event_date") or ""),
            event_currency=str(row.get("event_currency") or ""),
        )

    def _row_to_news_item(self, row: dict[str, object]) -> NewsItem:
        return NewsItem(
            detail_id=str(row.get("detail_id") or ""),
            title=str(row.get("title") or ""),
            url=str(row.get("url") or ""),
            snippet=str(row.get("snippet") or ""),
            link_type=str(row.get("link_type") or "related"),
            event_name=str(row.get("event_name") or ""),
            event_date=str(row.get("event_date") or ""),
            event_currency=str(row.get("event_currency") or ""),
        )