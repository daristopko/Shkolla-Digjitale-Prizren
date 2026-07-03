import datetime
from sqlalchemy import create_engine, Column, Integer, String, Boolean, DateTime, Text
from sqlalchemy.exc import OperationalError
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Define base structure
Base = declarative_base()

class Post(Base):
    __tablename__ = 'posts'
    id = Column(Integer, primary_key=True)
    account_id = Column(String(120), default="default", index=True)
    caption = Column(Text)
    media_type = Column(String(50))
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)

class ScheduledPost(Base):
    __tablename__ = 'scheduled_posts'
    id = Column(Integer, primary_key=True)
    account_id = Column(String(120), default="default", index=True)
    media_paths = Column(Text, default="placeholder.jpg")
    media_type = Column(String(50))
    caption = Column(Text)
    status = Column(String(50), default="scheduled")
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)

class Strategy(Base):
    __tablename__ = 'strategies'
    id = Column(Integer, primary_key=True)
    account_id = Column(String(120), default="default", index=True)
    name = Column(String(100), default="Standard Balanced")
    description = Column(Text, default="Professional AI-assisted engagement loop.")
    brand_voice = Column(String(250), default="helpful, clear, and energetic")
    niche = Column(String(150), default="software development")
    target_audience = Column(String(250), default="developers, founders, and technical creators")
    content_themes = Column(Text, default="Python, automation, AI tools, developer productivity")
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

class EngagementLog(Base):
    __tablename__ = 'engagement_logs'
    id = Column(Integer, primary_key=True)
    account_id = Column(String(120), default="default", index=True)
    type = Column(String(50))         # 'dm' or 'comment'
    username = Column(String(100))
    message_id = Column(String(250))
    input_text = Column(Text)
    response_text = Column(Text)
    status = Column(String(50))       # 'sent', 'failed'
    autopilot = Column(Boolean, default=True)
    responded_at = Column(DateTime, default=datetime.datetime.utcnow)

class AnalyticsSnapshot(Base):
    __tablename__ = 'analytics_snapshots'
    id = Column(Integer, primary_key=True)
    account_id = Column(String(120), default="default", index=True)
    followers = Column(Integer)
    following = Column(Integer)
    posts_count = Column(Integer)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)

class AutopilotRule(Base):
    __tablename__ = 'autopilot_rules'
    id = Column(Integer, primary_key=True)
    account_id = Column(String(120), default="default", index=True)
    name = Column(String(150))
    keyword = Column(String(250))
    scope = Column(String(50), default="both")
    response_template = Column(Text)
    active = Column(Boolean, default=True)

class AccountProfile(Base):
    __tablename__ = 'account_profiles'
    id = Column(Integer, primary_key=True)
    account_id = Column(String(120), unique=True, index=True)
    username = Column(String(150))
    display_name = Column(String(150))
    brand_voice = Column(String(250), default="helpful, clear, and energetic")
    session_mode = Column(String(50), default="sandbox")
    status = Column(String(50), default="active")
    last_error = Column(Text)
    last_verified_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

# Engine setup
DATABASE_URL = "sqlite:///instagram_portal.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    Base.metadata.create_all(bind=engine)
    _ensure_account_scope_columns()
    _ensure_strategy_columns()
    _ensure_scheduled_posts_columns()
    _ensure_autopilot_rules_columns()

def _ensure_account_scope_columns():
    scoped_tables = [
        "posts",
        "scheduled_posts",
        "strategies",
        "engagement_logs",
        "analytics_snapshots",
        "autopilot_rules",
    ]
    with engine.begin() as conn:
        for table in scoped_tables:
            existing = {
                row[1] for row in conn.exec_driver_sql(f"PRAGMA table_info({table})")
            }
            if "account_id" not in existing:
                _add_column(conn, f"ALTER TABLE {table} ADD COLUMN account_id VARCHAR(120) DEFAULT 'default'")

def _ensure_strategy_columns():
    with engine.begin() as conn:
        existing = {
            row[1] for row in conn.exec_driver_sql("PRAGMA table_info(strategies)")
        }
        if "brand_voice" not in existing:
            _add_column(conn,
                "ALTER TABLE strategies "
                "ADD COLUMN brand_voice VARCHAR(250) DEFAULT 'helpful, clear, and energetic'"
            )
        if "niche" not in existing:
            _add_column(conn,
                "ALTER TABLE strategies "
                "ADD COLUMN niche VARCHAR(150) DEFAULT 'software development'"
            )
        if "target_audience" not in existing:
            _add_column(conn,
                "ALTER TABLE strategies "
                "ADD COLUMN target_audience VARCHAR(250) "
                "DEFAULT 'developers, founders, and technical creators'"
            )
        if "content_themes" not in existing:
            _add_column(conn,
                "ALTER TABLE strategies "
                "ADD COLUMN content_themes TEXT "
                "DEFAULT 'Python, automation, AI tools, developer productivity'"
            )
        if "created_at" not in existing:
            _add_column(conn, "ALTER TABLE strategies ADD COLUMN created_at DATETIME")
            conn.exec_driver_sql(
                "UPDATE strategies "
                "SET created_at = CURRENT_TIMESTAMP "
                "WHERE created_at IS NULL"
            )

def _add_column(conn, sql):
    try:
        conn.exec_driver_sql(sql)
    except OperationalError as exc:
        if "duplicate column name" not in str(exc).lower():
            raise

def _ensure_scheduled_posts_columns():
    with engine.begin() as conn:
        existing = {
            row[1] for row in conn.exec_driver_sql("PRAGMA table_info(scheduled_posts)")
        }
        if "status" not in existing:
            conn.exec_driver_sql(
                "ALTER TABLE scheduled_posts "
                "ADD COLUMN status VARCHAR(50) DEFAULT 'scheduled'"
            )
        if "timestamp" not in existing:
            conn.exec_driver_sql(
                "ALTER TABLE scheduled_posts "
                "ADD COLUMN timestamp DATETIME"
            )
            if "scheduled_time" in existing:
                conn.exec_driver_sql(
                    "UPDATE scheduled_posts "
                    "SET timestamp = scheduled_time "
                    "WHERE timestamp IS NULL"
                )

def _ensure_autopilot_rules_columns():
    with engine.begin() as conn:
        existing = {
            row[1] for row in conn.exec_driver_sql("PRAGMA table_info(autopilot_rules)")
        }
        if "name" not in existing:
            conn.exec_driver_sql("ALTER TABLE autopilot_rules ADD COLUMN name VARCHAR(150)")
        if "keyword" not in existing:
            conn.exec_driver_sql("ALTER TABLE autopilot_rules ADD COLUMN keyword VARCHAR(250)")
            if "trigger_keyword" in existing:
                conn.exec_driver_sql(
                    "UPDATE autopilot_rules "
                    "SET keyword = trigger_keyword "
                    "WHERE keyword IS NULL"
                )
        if "scope" not in existing:
            conn.exec_driver_sql(
                "ALTER TABLE autopilot_rules ADD COLUMN scope VARCHAR(50) DEFAULT 'both'"
            )
        if "response_template" not in existing:
            conn.exec_driver_sql("ALTER TABLE autopilot_rules ADD COLUMN response_template TEXT")
            if "static_response_text" in existing:
                conn.exec_driver_sql(
                    "UPDATE autopilot_rules "
                    "SET response_template = static_response_text "
                    "WHERE response_template IS NULL"
                )
        if "active" not in existing:
            conn.exec_driver_sql(
                "ALTER TABLE autopilot_rules ADD COLUMN active BOOLEAN DEFAULT 1"
            )
            if "is_active" in existing:
                conn.exec_driver_sql(
                    "UPDATE autopilot_rules "
                    "SET active = is_active "
                    "WHERE active IS NULL"
                )
