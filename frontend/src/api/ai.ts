import { getToken } from "../auth/token";

const API = "http://localhost:8000/api/v1";

export async function startAI(submissionId: number) {
  const res = await fetch(`${API}/ai/process`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${getToken()}`,
    },
    body: JSON.stringify({ submission_id: submissionId }),
  });

  if (!res.ok) throw new Error("Ошибка запуска ИИ");
  return res.json();
}

export async function getAIResult(submissionId: number) {
  const res = await fetch(`${API}/ai/results/${submissionId}`, {
    headers: {
      Authorization: `Bearer ${getToken()}`,
    },
  });

  if (!res.ok) throw new Error("Ошибка получения результата ИИ");
  return res.json();
}
