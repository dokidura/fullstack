import { useEffect, useState } from 'react';
import {
  Upload,
  File,
  Clock,
  CheckCircle,
  XCircle,
  AlertCircle
} from 'lucide-react';
import { fetchSubmissions, uploadSubmission } from '../api/submissions';

type Role = 'student' | 'teacher';

interface User {
  id: number;
  email: string;
  role: Role;
  full_name: string;
}

interface Submission {
  id: number;
  student_id: number;
  exam_id: number;
  file_path: string;
  submission_date: string;
  status: 'submitted' | 'processing' | 'processed' | 'error';
  grade?: number;
}

interface StudentSubmissionsProps {
  user: User;
}

// 📘 Список предметов (exam_id ↔ название)
const EXAMS = [
  { id: 1, name: 'Русский язык' },
  { id: 2, name: 'Математика' },
  { id: 3, name: 'Физика' },
  { id: 4, name: 'Литература' },
  { id: 5, name: 'Химия' },
];

export function StudentSubmissions({ user }: StudentSubmissionsProps) {
  const [submissions, setSubmissions] = useState<Submission[]>([]);
  const [dragActive, setDragActive] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // 🆕 выбранный предмет (по умолчанию первый)
  const [examId, setExamId] = useState<number>(EXAMS[0].id);

  // 🔄 загрузка работ
  useEffect(() => {
    loadSubmissions();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const loadSubmissions = async () => {
    try {
      setLoading(true);
      const data = await fetchSubmissions();
      setSubmissions(data);
    } catch (err: any) {
      setError(err.message || 'Ошибка загрузки работ');
    } finally {
      setLoading(false);
    }
  };

  // 📤 загрузка файла
  const handleFileUpload = async (files: FileList | null) => {
    if (!files || files.length === 0) return;

    try {
      setLoading(true);
      setError(null);

      // 🔥 user.id + выбранный предмет
      await uploadSubmission(user.id, examId, files[0]);

      await loadSubmissions();
    } catch (err: any) {
      setError(err.message || 'Ошибка загрузки файла');
    } finally {
      setLoading(false);
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'submitted':
        return <Clock className="w-5 h-5 text-gray-400" />;
      case 'processing':
        return <AlertCircle className="w-5 h-5 text-blue-500" />;
      case 'processed':
        return <CheckCircle className="w-5 h-5 text-green-500" />;
      case 'error':
        return <XCircle className="w-5 h-5 text-red-500" />;
      default:
        return null;
    }
  };

  const getStatusText = (status: string) => {
    switch (status) {
      case 'submitted':
        return 'Ожидает обработки';
      case 'processing':
        return 'Обрабатывается';
      case 'processed':
        return 'Обработана';
      case 'error':
        return 'Ошибка обработки';
      default:
        return status;
    }
  };

  const examNameById = (id: number) =>
    EXAMS.find((e) => e.id === id)?.name || `Экзамен #${id}`;

  return (
    <div className="space-y-6">
      {/* 🔽 Выбор предмета */}
      {user.role === 'student' && (
        <div className="bg-white border border-gray-200 rounded-lg p-4">
          <label className="block text-gray-700 mb-2">
            Предмет
          </label>
          <select
            value={examId}
            onChange={(e) => setExamId(Number(e.target.value))}
            className="w-full px-4 py-2 border border-gray-300 rounded-lg bg-white focus:ring-2 focus:ring-blue-500"
          >
            {EXAMS.map((exam) => (
              <option key={exam.id} value={exam.id}>
                {exam.name}
              </option>
            ))}
          </select>
        </div>
      )}

      {/* 📤 Загрузка файла */}
      {user.role === 'student' && (
        <div
          className={`border-2 border-dashed rounded-lg p-12 text-center transition-colors ${
            dragActive ? 'border-blue-500 bg-blue-50' : 'border-gray-300 bg-white'
          }`}
          onDragOver={(e) => {
            e.preventDefault();
            setDragActive(true);
          }}
          onDragLeave={() => setDragActive(false)}
          onDrop={(e) => {
            e.preventDefault();
            setDragActive(false);
            handleFileUpload(e.dataTransfer.files);
          }}
        >
          <Upload className="w-12 h-12 text-gray-400 mx-auto mb-4" />
          <p className="text-gray-600 mb-2">
            Перетащите файл сюда или нажмите для выбора
          </p>
          <p className="text-gray-400 mb-4">
            Поддерживаются форматы: PDF, JPG, PNG
          </p>
          <label className="inline-block">
            <input
              type="file"
              className="hidden"
              accept=".pdf,.jpg,.jpeg,.png"
              onChange={(e) => handleFileUpload(e.target.files)}
            />
            <span className="px-6 py-2 bg-blue-600 text-white rounded-lg cursor-pointer hover:bg-blue-700 transition-colors inline-block">
              Выбрать файл
            </span>
          </label>
        </div>
      )}

      {error && (
        <div className="p-4 bg-red-50 border border-red-200 rounded-lg text-red-700">
          {error}
        </div>
      )}

      {/* 📄 Список работ */}
      <div className="bg-white rounded-lg border border-gray-200">
        <div className="px-6 py-4 border-b border-gray-200">
          <h2 className="text-gray-900">
            {user.role === 'student'
              ? 'Загруженные работы'
              : 'Все работы учеников'}
          </h2>
        </div>

        <div className="divide-y divide-gray-200">
          {loading ? (
            <div className="px-6 py-12 text-center text-gray-500">
              Загрузка...
            </div>
          ) : submissions.length === 0 ? (
            <div className="px-6 py-12 text-center text-gray-500">
              <File className="w-12 h-12 text-gray-300 mx-auto mb-3" />
              <p>Нет загруженных работ</p>
            </div>
          ) : (
            submissions.map((submission) => (
              <div
                key={submission.id}
                className="px-6 py-4 hover:bg-gray-50 transition-colors"
              >
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-4 flex-1">
                    <File className="w-8 h-8 text-gray-400" />
                    <div className="flex-1">
                      <p className="text-gray-600">
                        {examNameById(submission.exam_id)}
                      </p>
                      <p className="text-gray-400 text-sm break-all">
                        {submission.file_path}
                      </p>
                    </div>
                  </div>

                  <div className="flex items-center gap-6">
                    <div className="text-right">
                      <p className="text-gray-500">
                        {new Date(
                          submission.submission_date
                        ).toLocaleDateString()}
                      </p>
                    </div>

                    <div className="flex items-center gap-2 min-w-[180px]">
                      {getStatusIcon(submission.status)}
                      <span className="text-gray-700">
                        {getStatusText(submission.status)}
                      </span>
                    </div>

                    {submission.grade !== undefined && (
                      <div className="text-center min-w-[60px]">
                        <div className="inline-flex items-center justify-center w-10 h-10 rounded-full bg-green-100">
                          <span className="text-green-700">
                            {submission.grade}
                          </span>
                        </div>
                      </div>
                    )}
                  </div>
                </div>
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  );
}
