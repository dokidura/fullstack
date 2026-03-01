import { getToken } from "../auth/token";

const API = "http://localhost:8000/api/v1";

export async function fetchSubmissions() {
  const res = await fetch(`${API}/submissions/`, {
    headers: {
      Authorization: `Bearer ${getToken()}`,
    },
  });

  if (!res.ok) throw new Error("Ошибка загрузки работ");
  return res.json();
}

export async function uploadSubmission(
  studentId: number,
  examId: number,
  file: File
) {
  const form = new FormData();
  form.append("student_id", String(studentId));
  form.append("exam_id", String(examId));
  form.append("file", file);

  const res = await fetch(`${API}/submissions/`, {
    method: "POST",
    headers: {
      Authorization: `Bearer ${getToken()}`,
    },
    body: form,
  });

  if (!res.ok) throw new Error("Ошибка загрузки файла");
  return res.json();
}

export async function fetchAllSubmissions() {
  const res = await fetch("http://localhost:8000/api/v1/submissions/", {
    headers: {
      Authorization: `Bearer ${getToken()}`,
    },
  });

  if (!res.ok) throw new Error("Ошибка загрузки работ");
  return res.json();
}
