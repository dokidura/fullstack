const API = "http://localhost:8000/api/v1";

export async function login(email: string, password: string) {
  const res = await fetch(`${API}/auth/login`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email, password }),
  });

  if (!res.ok) {
    throw new Error("Ошибка авторизации");
  }

  return res.json();
}

export async function register(
  email: string,
  password: string,
  full_name: string,
  role: "student" | "teacher"
) {
  const res = await fetch(`${API}/auth/register`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      email,
      password,
      full_name,
      role,
    }),
  });

  if (!res.ok) {
    const err = await res.json();
    throw new Error(err.detail || "Ошибка регистрации");
  }

  return res.json();
}

import { getToken } from "../auth/token";

export async function getMe() {
  const res = await fetch("http://localhost:8000/api/v1/auth/me", {
    headers: {
      Authorization: `Bearer ${getToken()}`
    }
  });

  if (!res.ok) {
    throw new Error("Не удалось получить текущего пользователя");
  }

  return res.json();
}
