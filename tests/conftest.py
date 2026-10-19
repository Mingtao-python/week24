import pytest
from backend import database
from backend.security.rate_limit import requests_log
from backend.utils.tokens import tokens
from backend.utils.hashing import hash_password


@pytest.fixture(autouse=True)
def test_database(tmp_path, monkeypatch):
    # 每个测试使用独立数据库，不修改 database/week24.db
    monkeypatch.setattr(database, "DB_PATH", tmp_path / "week24.db")
    requests_log.clear()
    tokens.clear()
    database.init_db()
    conn = database.get_db()
    for username, role in [
        ("ming", "student"), ("tao", "student"),
        ("teacher", "teacher"), ("admin", "admin"),
        ("teacher2", "teacher"),
    ]:
        conn.execute(
            "INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
            (username, hash_password("123"), role)
        )
    conn.commit()
    conn.close()
    yield
    requests_log.clear()
    tokens.clear()
