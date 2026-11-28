-- ============================================================
-- Matcha Database Schema
-- PostgreSQL 16
-- Todas las consultas se escribirán manualmente (sin ORM)
-- Este es uno de los archivos más importantes del proyecto. 
-- Define todas las tablas necesarias para el mandatory + los bonus.
-- ============================================================

-- ============================================================
-- Qué hace este archivo:
-- Crea todas las tablas necesarias para el proyecto completo 
-- (mandatory + bonus de citas). 
-- Se carga automáticamente la primera vez que arranca el contenedor de PostgreSQL.
-- ============================================================

-- Extensiones útiles
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";   -- búsqueda difusa en tags

-- ============================================================
-- USERS (autenticación)
-- ============================================================
CREATE TABLE users (
    id                  SERIAL PRIMARY KEY,
    email               VARCHAR(255) NOT NULL UNIQUE,
    username            VARCHAR(50)  NOT NULL UNIQUE,
    first_name          VARCHAR(100) NOT NULL,
    last_name           VARCHAR(100) NOT NULL,
    password_hash       VARCHAR(255) NOT NULL,

    -- Verificación de email
    is_verified         BOOLEAN NOT NULL DEFAULT FALSE,
    verification_token  VARCHAR(128) UNIQUE,
    verification_sent_at TIMESTAMPTZ,

    -- Reset de contraseña
    reset_token         VARCHAR(128) UNIQUE,
    reset_token_expires TIMESTAMPTZ,

    -- Estado
    is_active           BOOLEAN NOT NULL DEFAULT TRUE,
    is_online           BOOLEAN NOT NULL DEFAULT FALSE,
    last_seen           TIMESTAMPTZ DEFAULT NOW(),

    -- Fame rating (público)
    fame_rating         INTEGER NOT NULL DEFAULT 0,

    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at          TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_username ON users(username);
CREATE INDEX idx_users_fame ON users(fame_rating DESC);
CREATE INDEX idx_users_online ON users(is_online) WHERE is_online = TRUE;

-- ============================================================
-- PROFILES (información extendida)
-- ============================================================
CREATE TABLE profiles (
    user_id             INTEGER PRIMARY KEY REFERENCES users(id) ON DELETE CASCADE,

    gender              VARCHAR(20) CHECK (gender IN ('male', 'female', 'non-binary', 'other')),
    sexual_orientation  VARCHAR(30) DEFAULT 'bisexual'
                            CHECK (sexual_orientation IN ('heterosexual', 'homosexual', 'bisexual', 'other')),

    biography           TEXT,
    birth_date          DATE,

    -- Ubicación
    latitude            DOUBLE PRECISION,
    longitude           DOUBLE PRECISION,
    city                VARCHAR(120),
    neighborhood        VARCHAR(120),
    location_source     VARCHAR(20) DEFAULT 'manual'
                            CHECK (location_source IN ('gps', 'manual', 'ip')),
    location_updated_at TIMESTAMPTZ,

    is_complete         BOOLEAN NOT NULL DEFAULT FALSE,

    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at          TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_profiles_lat_lng ON profiles(latitude, longitude) WHERE latitude IS NOT NULL;

-- ============================================================
-- TAGS (intereses reutilizables)
-- ============================================================
CREATE TABLE tags (
    id              SERIAL PRIMARY KEY,
    name            VARCHAR(50) NOT NULL UNIQUE,  -- sin el #
    usage_count     INTEGER NOT NULL DEFAULT 0,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_tags_name_trgm ON tags USING GIN (name gin_trgm_ops);
CREATE INDEX idx_tags_usage ON tags(usage_count DESC);

-- ============================================================
-- USER_TAGS (relación muchos a muchos)
-- ============================================================
CREATE TABLE user_tags (
    user_id     INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    tag_id      INTEGER NOT NULL REFERENCES tags(id) ON DELETE CASCADE,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    PRIMARY KEY (user_id, tag_id)
);

CREATE INDEX idx_user_tags_tag ON user_tags(tag_id);

-- ============================================================
-- PHOTOS
-- ============================================================
CREATE TABLE photos (
    id              SERIAL PRIMARY KEY,
    user_id         INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    filename        VARCHAR(255) NOT NULL,
    original_name   VARCHAR(255),
    is_profile      BOOLEAN NOT NULL DEFAULT FALSE,
    position        SMALLINT NOT NULL DEFAULT 0,
    width           INTEGER,
    height          INTEGER,
    size_bytes      INTEGER,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_photos_user ON photos(user_id);
CREATE UNIQUE INDEX idx_photos_one_profile ON photos(user_id) WHERE is_profile = TRUE;

-- ============================================================
-- LIKES (😍)
-- ============================================================
CREATE TABLE likes (
    id              SERIAL PRIMARY KEY,
    from_user_id    INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    to_user_id      INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    UNIQUE (from_user_id, to_user_id),
    CHECK (from_user_id <> to_user_id)
);

CREATE INDEX idx_likes_to ON likes(to_user_id);
CREATE INDEX idx_likes_from ON likes(from_user_id);

-- ============================================================
-- MATCHES (likes mutuos)
-- ============================================================
CREATE TABLE matches (
    id          SERIAL PRIMARY KEY,
    user1_id    INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    user2_id    INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    UNIQUE (user1_id, user2_id),
    CHECK (user1_id < user2_id)   -- orden canónico para evitar duplicados
);

CREATE INDEX idx_matches_user1 ON matches(user1_id);
CREATE INDEX idx_matches_user2 ON matches(user2_id);

-- ============================================================
-- PROFILE VIEWS (historial de visitas)
-- ============================================================
CREATE TABLE profile_views (
    id          SERIAL PRIMARY KEY,
    viewer_id   INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    viewed_id   INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    viewed_at   TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    CHECK (viewer_id <> viewed_id)
);

CREATE INDEX idx_views_viewed ON profile_views(viewed_id, viewed_at DESC);
CREATE INDEX idx_views_viewer ON profile_views(viewer_id);

-- ============================================================
-- BLOCKS
-- ============================================================
CREATE TABLE blocks (
    id          SERIAL PRIMARY KEY,
    blocker_id  INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    blocked_id  INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    UNIQUE (blocker_id, blocked_id),
    CHECK (blocker_id <> blocked_id)
);

CREATE INDEX idx_blocks_blocker ON blocks(blocker_id);
CREATE INDEX idx_blocks_blocked ON blocks(blocked_id);

-- ============================================================
-- REPORTS (cuentas falsas)
-- ============================================================
CREATE TABLE reports (
    id          SERIAL PRIMARY KEY,
    reporter_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    reported_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    reason      TEXT,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    UNIQUE (reporter_id, reported_id),
    CHECK (reporter_id <> reported_id)
);

-- ============================================================
-- CONVERSATIONS & MESSAGES (Chat)
-- ============================================================
CREATE TABLE conversations (
    id          SERIAL PRIMARY KEY,
    match_id    INTEGER NOT NULL UNIQUE REFERENCES matches(id) ON DELETE CASCADE,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at  TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE messages (
    id              SERIAL PRIMARY KEY,
    conversation_id INTEGER NOT NULL REFERENCES conversations(id) ON DELETE CASCADE,
    sender_id       INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    content         TEXT NOT NULL,
    is_read         BOOLEAN NOT NULL DEFAULT FALSE,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_messages_conversation ON messages(conversation_id, created_at);
CREATE INDEX idx_messages_unread ON messages(conversation_id, is_read) WHERE is_read = FALSE;

-- ============================================================
-- NOTIFICATIONS
-- ============================================================
CREATE TYPE notification_type AS ENUM (
    'like',
    'unlike',
    'view',
    'message',
    'match',
    'system'
);

CREATE TABLE notifications (
    id          SERIAL PRIMARY KEY,
    user_id     INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    type        notification_type NOT NULL,
    from_user_id INTEGER REFERENCES users(id) ON DELETE SET NULL,
    entity_id   INTEGER,
    content     TEXT,
    is_read     BOOLEAN NOT NULL DEFAULT FALSE,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_notifications_user ON notifications(user_id, created_at DESC);
CREATE INDEX idx_notifications_unread ON notifications(user_id) WHERE is_read = FALSE;

-- ============================================================
-- DATES (Bonus: citas en la vida real)
-- ============================================================
CREATE TABLE dates (
    id              SERIAL PRIMARY KEY,
    match_id        INTEGER NOT NULL REFERENCES matches(id) ON DELETE CASCADE,
    proposed_by     INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    title           VARCHAR(200) NOT NULL,
    description     TEXT,
    location        VARCHAR(255),
    scheduled_at    TIMESTAMPTZ NOT NULL,
    status          VARCHAR(20) NOT NULL DEFAULT 'proposed'
                        CHECK (status IN ('proposed', 'accepted', 'declined', 'cancelled', 'completed')),
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_dates_match ON dates(match_id);
CREATE INDEX idx_dates_scheduled ON dates(scheduled_at);

-- ============================================================
-- TRIGGERS
-- ============================================================
CREATE OR REPLACE FUNCTION update_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER users_updated_at
    BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();

CREATE TRIGGER profiles_updated_at
    BEFORE UPDATE ON profiles
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();

CREATE TRIGGER conversations_updated_at
    BEFORE UPDATE ON conversations
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();

-- Mantener usage_count de tags actualizado
CREATE OR REPLACE FUNCTION update_tag_usage()
RETURNS TRIGGER AS $$
BEGIN
    IF TG_OP = 'INSERT' THEN
        UPDATE tags SET usage_count = usage_count + 1 WHERE id = NEW.tag_id;
    ELSIF TG_OP = 'DELETE' THEN
        UPDATE tags SET usage_count = GREATEST(usage_count - 1, 0) WHERE id = OLD.tag_id;
    END IF;
    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER user_tags_usage
    AFTER INSERT OR DELETE ON user_tags
    FOR EACH ROW EXECUTE FUNCTION update_tag_usage();
