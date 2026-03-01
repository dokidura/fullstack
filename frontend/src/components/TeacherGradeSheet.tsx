import { useEffect, useState } from 'react';
import { Download, Search, TrendingUp, Users, Eye } from 'lucide-react';
import { ResultModal } from './ResultModal';
import { fetchGradebooks, exportGradebook } from '../api/gradebooks';
import { examNameById } from '../constants/exams';

interface Answer {
  questionNumber: number;
  recognizedText: string;
  correctAnswer: string;
  isCorrect: boolean;
  confidence: number;
}

interface GradebookEntry {
  id: number;
  student_id: number;
  student_name?: string; // ← НОВОЕ
  exam_id: number;
  submission_id: number;
  grade: number;
  comments?: string;
  created_at: string;
  processed_data?: {
    answers: Answer[];
    correct_answers: number;
    total_questions: number;
  };
}

export function TeacherGradeSheet() {
  const [grades, setGrades] = useState<GradebookEntry[]>([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedExam, setSelectedExam] = useState<number | 'all'>('all');
  const [selectedGrade, setSelectedGrade] = useState<GradebookEntry | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadGradebooks();
  }, []);

  const loadGradebooks = async () => {
    try {
      const data = await fetchGradebooks();
      setGrades(data);
    } catch (err: any) {
      setError(err.message || 'Ошибка загрузки ведомостей');
    }
  };

  const exams = Array.from(new Set(grades.map((g) => g.exam_id)));

  const filteredGrades = grades.filter((g) => {
    const studentLabel = g.student_name ?? `ID ${g.student_id}`;

    const matchesSearch = studentLabel
      .toLowerCase()
      .includes(searchTerm.toLowerCase());

    const matchesExam =
      selectedExam === 'all' || g.exam_id === selectedExam;

    return matchesSearch && matchesExam;
  });

  const averageGrade =
    filteredGrades.length > 0
      ? (
          filteredGrades.reduce((sum, g) => sum + g.grade, 0) /
          filteredGrades.length
        ).toFixed(2)
      : '—';

  return (
    <div className="space-y-6">
      {error && (
        <div className="p-4 bg-red-50 border border-red-200 rounded-lg text-red-700">
          {error}
        </div>
      )}

      {/* Statistics */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <StatCard
          icon={<Users />}
          label="Всего записей"
          value={filteredGrades.length}
        />
        <StatCard
          icon={<TrendingUp />}
          label="Средняя оценка"
          value={averageGrade}
        />
        <StatCard
          icon={<TrendingUp />}
          label="Экзаменов"
          value={exams.length}
        />
      </div>

      {/* Filters & Export */}
      <div className="bg-white rounded-lg border border-gray-200 p-4 flex gap-4 flex-wrap">
        <div className="flex-1 min-w-[250px] relative">
          <Search className="w-5 h-5 text-gray-400 absolute left-3 top-1/2 -translate-y-1/2" />
          <input
            type="text"
            placeholder="Поиск по имени ученика"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full pl-10 pr-4 py-2 border rounded-lg"
          />
        </div>

        <select
          value={selectedExam}
          onChange={(e) =>
            setSelectedExam(
              e.target.value === 'all' ? 'all' : Number(e.target.value)
            )
          }
          className="px-4 py-2 border rounded-lg"
        >
          <option value="all">Все предметы</option>
          {exams.map((id) => (
            <option key={id} value={id}>
              {examNameById(id)}
            </option>
          ))}
        </select>

        {selectedExam !== 'all' && (
          <button
            onClick={() => exportGradebook(selectedExam)}
            className="flex items-center gap-2 px-4 py-2 bg-green-600 text-white rounded-lg"
          >
            <Download className="w-4 h-4" />
            Экспорт CSV
          </button>
        )}
      </div>

      {/* Table */}
      <div className="bg-white rounded-lg border border-gray-200 overflow-hidden">
        <table className="w-full">
          <thead className="bg-gray-50 border-b">
            <tr>
              <th className="px-6 py-3 text-left">Ученик</th>
              <th className="px-6 py-3 text-left">Предмет</th>
              <th className="px-6 py-3 text-center">Оценка</th>
              <th className="px-6 py-3 text-left">Дата</th>
              <th className="px-6 py-3 text-left">Детали</th>
            </tr>
          </thead>
          <tbody className="divide-y">
            {filteredGrades.length === 0 ? (
              <tr>
                <td colSpan={5} className="px-6 py-12 text-center text-gray-500">
                  Нет данных
                </td>
              </tr>
            ) : (
              filteredGrades.map((g) => (
                <tr key={g.id} className="hover:bg-gray-50">
                  <td className="px-6 py-4">
                    {g.student_name ?? `ID ${g.student_id}`}
                  </td>
                  <td className="px-6 py-4">
                    {examNameById(g.exam_id)}
                  </td>
                  <td className="px-6 py-4 text-center">
                    <span className="inline-flex w-10 h-10 items-center justify-center rounded-full bg-blue-100 text-blue-700">
                      {g.grade}
                    </span>
                  </td>
                  <td className="px-6 py-4">
                    {new Date(g.created_at).toLocaleDateString()}
                  </td>
                  <td className="px-6 py-4">
                    {g.processed_data && (
                      <button
                        onClick={() => setSelectedGrade(g)}
                        className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg"
                      >
                        <Eye className="w-4 h-4" />
                        Просмотреть
                      </button>
                    )}
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>

      {/* Result modal */}
      {selectedGrade?.processed_data && (
        <ResultModal
          isOpen={true}
          onClose={() => setSelectedGrade(null)}
          studentName={
            selectedGrade.student_name ??
            `ID ${selectedGrade.student_id}`
          }
          subject={examNameById(selectedGrade.exam_id)}
          fileName={`submission_${selectedGrade.submission_id}`}
          answers={selectedGrade.processed_data.answers}
          totalScore={selectedGrade.processed_data.correct_answers}
          maxScore={selectedGrade.processed_data.total_questions}
          grade={selectedGrade.grade}
        />
      )}
    </div>
  );
}

function StatCard({
  icon,
  label,
  value,
}: {
  icon: React.ReactNode;
  label: string;
  value: number | string;
}) {
  return (
    <div className="bg-white rounded-lg border p-6">
      <div className="flex items-center gap-3 mb-2 text-blue-600">
        {icon}
      </div>
      <p className="text-gray-600">{label}</p>
      <p className="text-gray-900">{value}</p>
    </div>
  );
}
