-- USERS TABLE
CREATE TABLE IF NOT EXISTS users (
    id SERIAL NOT NULL,
    email TEXT NOT NULL,
    password_hash TEXT NOT NULL,
    is_active BOOLEAN,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
    PRIMARY KEY (id)
);

CREATE UNIQUE INDEX IF NOT EXISTS users_email_key ON public.users USING btree (email);

CREATE INDEX IF NOT EXISTS ix_users_id ON public.users USING btree (id);

-- URLS TABLE
CREATE TABLE IF NOT EXISTS urls (
    id SERIAL NOT NULL,
    user_id INTEGER,
    original_url TEXT NOT NULL,
    short_code TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now(),
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
    last_accessed TIMESTAMP WITH TIME ZONE,
    is_disabled BOOLEAN NOT NULL,
    is_active BOOLEAN NOT NULL,
    deleted_at TIMESTAMP WITH TIME ZONE,
    deleted_by INTEGER,
    click_count BIGINT,
    PRIMARY KEY (id),
    CONSTRAINT urls_user_id_fkey FOREIGN KEY (user_id) REFERENCES users (id),
    CONSTRAINT urls_deleted_by_fkey FOREIGN KEY (deleted_by) REFERENCES users (id)
);

CREATE UNIQUE INDEX IF NOT EXISTS ix_urls_short_code ON public.urls USING btree (short_code);

CREATE INDEX IF NOT EXISTS ix_urls_user_id ON public.urls USING btree (user_id);

CREATE INDEX IF NOT EXISTS ix_urls_is_active ON public.urls USING btree (is_active);

CREATE INDEX IF NOT EXISTS ix_urls_expires_at ON public.urls USING btree (expires_at);

-- CLICK EVENTS TABLE
CREATE TABLE IF NOT EXISTS click_events (
    id SERIAL NOT NULL,
    event_id UUID NOT NULL,
    short_code TEXT NOT NULL,
    clicked_at TIMESTAMP WITH TIME ZONE NOT NULL,
    ip_address TEXT,
    country TEXT,
    city TEXT,
    browser TEXT,
    os TEXT,
    device_type TEXT,
    referer TEXT,
    is_bot BOOLEAN NOT NULL,
    cache_hit BOOLEAN NOT NULL,
    redirect_latency_ms DOUBLE PRECISION NOT NULL,
    PRIMARY KEY (id)
);

CREATE UNIQUE INDEX IF NOT EXISTS click_events_event_id_key ON public.click_events USING btree (event_id);

CREATE INDEX IF NOT EXISTS ix_click_events_country ON public.click_events USING btree (country);

CREATE INDEX IF NOT EXISTS ix_click_events_is_bot ON public.click_events USING btree (is_bot);

CREATE INDEX IF NOT EXISTS ix_click_events_browser ON public.click_events USING btree (browser);

CREATE INDEX IF NOT EXISTS ix_click_events_device_type ON public.click_events USING btree (device_type);

CREATE INDEX IF NOT EXISTS ix_click_events_short_code ON public.click_events USING btree (short_code);