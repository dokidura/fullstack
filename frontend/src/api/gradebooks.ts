import { getToken } from "../auth/token";

const API = "http://localhost:8000/api/v1";

export async function fetchGradebooks() {
  const res = await fetch(`${API}/gradebooks/`, {
    headers: {
      Authorization: `Bearer ${getToken()}`,
    },
  });

  if (!res.ok) {
    throw new Error("Ошибка загрузки ведомостей");
  }

  return res.json();
}

export async function exportGradebook(examId: number) {
  const res = await fetch(`${API}/gradebooks/export/${examId}`, {
    headers: {
      Authorization: `Bearer ${getToken()}`,
    },
  });

  if (!res.ok) {
    throw new Error("Ошибка экспорта ведомости");
  }

  const blob = await res.blob();
  const url = window.URL.createObjectURL(blob);

  const a = document.createElement("a");
  a.href = url;
  a.download = `gradebook_exam_${examId}.csv`;
  document.body.appendChild(a);
  a.click();

  a.remove();
  window.URL.revokeObjectURL(url);
}
