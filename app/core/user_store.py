# app/core/user_store.py
"""
User store backed by SQLite (app.db) + in-memory cache (fake_users_db).

Почему так:
- Твой проект уже использует fake_users_db во многих местах (например, для получения имени студента).
- Чтобы не переписывать половину кода, мы оставляем fake_users_db как "кеш",
  но источник истины — SQLite.
"""

from __future__ import annotations

import os
import sqlite3
from datetime import datetime
from typing import Dict, Any, Optional, List

from app.core.config import settings

# Старая структура остаётся: другие части проекта всё ещё могут импортировать fake_users_db
fake_users_db: Dict[str, Dict[str, Any]] = {}

# Путь до SQLite файла (создастся автоматически)
DB_PATH = os.getenv("USER_DB_PATH", "app.db")


def _connect() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def _create_tables() -> None:
    with _connect() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT NOT NULL UNIQUE,
                full_name TEXT NOT NULL,
                role TEXT NOT NULL,
                hashed_password TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
            """
        )
        conn.commit()


def _load_all_users() -> None:
    """Загружает всех пользователей из БД в fake_users_db (кеш)."""
    fake_users_db.clear()
    with _connect() as conn:
        rows = conn.execute(
            "SELECT id, email, full_name, role, hashed_password, created_at FROM users"
        ).fetchall()

    for r in rows:
        fake_users_db[r["email"]] = {
            "id": int(r["id"]),
            "email": r["email"],
            "full_name": r["full_name"],
            "role": r["role"],
            "hashed_password": r["hashed_password"],
            # created_at храним как строку ISO — pydantic нормально переварит при необходимости,
            # но для простоты в кеш можно оставить строкой
            "created_at": r["created_at"],
        }


def get_user_by_email(email: str) -> Optional[Dict[str, Any]]:
    return fake_users_db.get(email)


def get_user_by_id(user_id: int) -> Optional[Dict[str, Any]]:
    for u in fake_users_db.values():
        if int(u.get("id", -1)) == int(user_id):
            return u
    return None


def create_user(email: str, full_name: str, role: str, hashed_password: str) -> Dict[str, Any]:
    """Создаёт пользователя в БД и в кеше. Возвращает user_dict."""
    created_at = datetime.utcnow().isoformat()

    with _connect() as conn:
        try:
            cur = conn.execute(
                """
                INSERT INTO users (email, full_name, role, hashed_password, created_at)
                VALUES (?, ?, ?, ?, ?)
                """,
                (email, full_name, role, hashed_password, created_at),
            )
            conn.commit()
        except sqlite3.IntegrityError:
            # email уникален
            raise ValueError("User already exists")

        user_id = int(cur.lastrowid)

    user_dict = {
        "id": user_id,
        "email": email,
        "full_name": full_name,
        "role": role,
        "hashed_password": hashed_password,
        "created_at": created_at,
    }
    fake_users_db[email] = user_dict
    return user_dict


def update_user_role(user_id: int, new_role: str) -> Dict[str, Any]:
    """Меняет роль пользователя в БД и кеше. Возвращает обновлённого пользователя."""
    with _connect() as conn:
        cur = conn.execute("SELECT email FROM users WHERE id = ?", (user_id,))
        row = cur.fetchone()
        if not row:
            raise ValueError("User not found")
        email = row["email"]

        conn.execute("UPDATE users SET role = ? WHERE id = ?", (new_role, user_id))
        conn.commit()

    # обновляем кеш
    u = fake_users_db.get(email)
    if u:
        u["role"] = new_role
        return u

    # если по какой-то причине кеш был пуст — перезагрузим
    _load_all_users()
    u2 = fake_users_db.get(email)
    if not u2:
        raise ValueError("User not found after reload")
    return u2


def _seed_default_users() -> None:
    """
    Засеиваем дефолтные учетки, если таблица пустая.
    Пароли можно поменять, но для демонстрации удобно одинаковые.
    """
    from app.core.security import get_password_hash  # импорт здесь, чтобы не было циклов

    # admin-teacher: email берём из settings.ADMIN_EMAILS[0]
    admin_email = settings.ADMIN_EMAILS[0] if getattr(settings, "ADMIN_EMAILS", None) else "admin@mail.com"

    defaults = [
        ("student1@mail.com", "Student One", "student", "123456"),
        ("student2@mail.com", "Student Two", "student", "123456"),
        ("teacher@mail.com", "Teacher", "teacher", "123456"),
        (admin_email, "Admin Teacher", "teacher", "123456"),
    ]

    with _connect() as conn:
        count = conn.execute("SELECT COUNT(*) AS c FROM users").fetchone()["c"]
        if int(count) > 0:
            return

    for email, full_name, role, password in defaults:
        try:
            create_user(
                email=email,
                full_name=full_name,
                role=role,
                hashed_password=get_password_hash(password),
            )
        except ValueError:
            # уже есть — пропускаем
            pass


def init_user_store() -> None:
    """
    Вызывается при старте приложения:
    - создаёт таблицы
    - сидит дефолтных пользователей (если таблица пустая)
    - загружает всех пользователей в fake_users_db
    """
    _create_tables()
    _seed_default_users()
    _load_all_users()
