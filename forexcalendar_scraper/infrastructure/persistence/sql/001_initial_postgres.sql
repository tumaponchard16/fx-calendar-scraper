CREATE TABLE IF NOT EXISTS calendar_events (
    id BIGSERIAL PRIMARY KEY,
    source_event_key TEXT NOT NULL UNIQUE,
    date_param TEXT NOT NULL,
    source_detail_id TEXT NOT NULL DEFAULT '',
    event_date TEXT NOT NULL DEFAULT '',
    event_time TEXT NOT NULL DEFAULT '',
    currency TEXT NOT NULL DEFAULT '',
    impact TEXT NOT NULL DEFAULT '',
    event_name TEXT NOT NULL DEFAULT '',
    actual TEXT NOT NULL DEFAULT '',
    forecast TEXT NOT NULL DEFAULT '',
    previous TEXT NOT NULL DEFAULT '',
    output_file TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_calendar_events_date_param
    ON calendar_events (date_param);

CREATE INDEX IF NOT EXISTS idx_calendar_events_currency
    ON calendar_events (currency);

CREATE INDEX IF NOT EXISTS idx_calendar_events_detail_id
    ON calendar_events (source_detail_id);

CREATE TABLE IF NOT EXISTS event_details (
    event_id BIGINT PRIMARY KEY REFERENCES calendar_events(id) ON DELETE CASCADE,
    detail_id TEXT NOT NULL DEFAULT '',
    event_date TEXT NOT NULL DEFAULT '',
    event_time TEXT NOT NULL DEFAULT '',
    event_currency TEXT NOT NULL DEFAULT '',
    event_name TEXT NOT NULL DEFAULT '',
    full_details_url TEXT NOT NULL DEFAULT '',
    specs_json JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_event_details_detail_id
    ON event_details (detail_id);

CREATE TABLE IF NOT EXISTS event_history_records (
    id BIGSERIAL PRIMARY KEY,
    event_id BIGINT NOT NULL REFERENCES calendar_events(id) ON DELETE CASCADE,
    detail_id TEXT NOT NULL DEFAULT '',
    event_name TEXT NOT NULL DEFAULT '',
    event_date TEXT NOT NULL DEFAULT '',
    event_currency TEXT NOT NULL DEFAULT '',
    release_date TEXT NOT NULL DEFAULT '',
    date_url TEXT NOT NULL DEFAULT '',
    actual TEXT NOT NULL DEFAULT '',
    forecast TEXT NOT NULL DEFAULT '',
    previous TEXT NOT NULL DEFAULT '',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_event_history_records_event_id
    ON event_history_records (event_id);

CREATE INDEX IF NOT EXISTS idx_event_history_records_detail_id
    ON event_history_records (detail_id);

CREATE TABLE IF NOT EXISTS event_news_items (
    id BIGSERIAL PRIMARY KEY,
    event_id BIGINT NOT NULL REFERENCES calendar_events(id) ON DELETE CASCADE,
    detail_id TEXT NOT NULL DEFAULT '',
    event_name TEXT NOT NULL DEFAULT '',
    event_date TEXT NOT NULL DEFAULT '',
    event_currency TEXT NOT NULL DEFAULT '',
    title TEXT NOT NULL DEFAULT '',
    url TEXT NOT NULL DEFAULT '',
    snippet TEXT NOT NULL DEFAULT '',
    link_type TEXT NOT NULL DEFAULT 'related',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_event_news_items_event_id
    ON event_news_items (event_id);

CREATE INDEX IF NOT EXISTS idx_event_news_items_detail_id
    ON event_news_items (detail_id);