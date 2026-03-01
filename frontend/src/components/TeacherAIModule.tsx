import { useEffect, useState } from 'react';
import { Play, FileText, Loader2, CheckCircle, XCircle, Clock, Eye } from 'lucide-react';
import { ResultModal } from './ResultModal';
import { fetchAllSubmissions } from '../api/submissions';
import { startAI, getAIResult } from '../api/ai';
import { examNameById } from '../constants/exams';

interface Answer {
  questionNumber: number;
  recognizedText: string;
  correctAnswer: string;
  isCorrect: boolean;
  confidence: number;
}

interface WorkItem {
  id: number;
  student_id: number;
  exam_id: number;
  file_path: string;
  submission_date: string;
  status: 'submitted' | 'processing' | 'processed' | 'error';
  ai_processed: boolean;
  processed_data?: {
    answers: Answer[];
    correct_answers: number;
    total_questions: number;
    grade: number;
  };
}

export function TeacherAIModule() {
  const [queue, setQueue] = useState<WorkItem[]>([]);
  const [processingIds, setProcessingIds] = useState<number[]>([]);
  const [selectedWork, setSelectedWork] = useState<WorkItem | null>(null);
  const [error, setError] = useState<string | null>(null);

  // 🔄 загрузка очереди
  useEffect(() => {
    loadQueue();
  }, []);

  const loadQueue = async () => {
    try {
      const data = await fetchAllSubmissions();
      setQueue(data);
    } catch (err: any) {
      setError(err.message || 'Ошибка загрузки очереди');
    }
  };

// В handleProcessWork замените логику на простой опрос с таймаутом
const handleProcessWork = async (id: number) => {
  try {
    setProcessingIds((prev) => [...prev, id]);
    
    // Запускаем обработку
    await startAI(id);
    
    // Опрашиваем статус каждые 2 секунды, но не более 10 раз
    let attempts = 0;
    const maxAttempts = 10;
    
    const checkStatus = async () => {
      const result = await getAIResult(id);

      if (result.status === 'processed' || result.status === 'error') {
        setProcessingIds(prev => prev.filter(pid => pid !== id));
        await loadQueue();
      } else {
        attempts++;
        setTimeout(checkStatus, 2000);
      }
    };

    
    checkStatus();
  } catch (err: any) {
    setError(err.message || 'Ошибка запуска обработки');
    setProcessingIds((prev) => prev.filter((pid) => pid !== id));
  }
};

  // ▶️ обработать все
  const handleProcessAll = () => {
    queue
      .filter((item) => item.status === 'submitted')
      .forEach((item, index) => {
        setTimeout(() => handleProcessWork(item.id), index * 500);
      });
  };

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'submitted':
        return <Badge icon={<Clock />} text="Ожидает" color="gray" />;
      case 'processing':
        return <Badge icon={<Loader2 className="animate-spin" />} text="Обработка" color="blue" />;
      case 'processed':
        return <Badge icon={<CheckCircle />} text="Готово" color="green" />;
      case 'error':
        return <Badge icon={<XCircle />} text="Ошибка" color="red" />;
      default:
        return null;
    }
  };

  const pendingCount = queue.filter((i) => i.status === 'submitted').length;

  return (
    <div className="space-y-6">
      {error && (
        <div className="p-4 bg-red-50 border border-red-200 rounded-lg text-red-700">
          {error}
        </div>
      )}

      <div className="flex items-center justify-between">
        <div>
          <p className="text-gray-900 mb-1">Очередь обработки</p>
          <p className="text-gray-500">Работ в очереди: {pendingCount}</p>
        </div>

        {pendingCount > 0 && (
          <button
            onClick={handleProcessAll}
            className="flex items-center gap-2 px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
          >
            <Play className="w-5 h-5" />
            Обработать все
          </button>
        )}
      </div>

      <div className="bg-white rounded-lg border border-gray-200 divide-y">
        {queue.length === 0 ? (
          <div className="px-6 py-12 text-center text-gray-500">
            Очередь пуста
          </div>
        ) : (
          queue.map((item) => (
            <div key={item.id} className="px-6 py-5 flex justify-between">
              <div>
                <p>{examNameById(item.exam_id)}</p>
                <p className="text-gray-500">{item.file_path}</p>
                <p className="text-gray-400">
                  {new Date(item.submission_date).toLocaleDateString()}
                </p>
              </div>

              <div className="flex items-center gap-4">
                {getStatusBadge(item.status)}

                {item.status === 'submitted' && (
                  <button
                    onClick={() => handleProcessWork(item.id)}
                    className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
                  >
                    Обработать
                  </button>
                )}

                {item.status === 'processed' && item.processed_data && (
                  <button
                    onClick={() => setSelectedWork(item)}
                    className="flex items-center gap-2 px-4 py-2 bg-green-600 text-white rounded-lg"
                  >
                    <Eye className="w-4 h-4" />
                    Детали
                  </button>
                )}
              </div>
            </div>
          ))
        )}
      </div>

      {selectedWork?.processed_data && (
        <ResultModal
          isOpen={true}
          onClose={() => setSelectedWork(null)}
          studentName={`ID ${selectedWork.student_id}`}
          subject={`Экзамен ${selectedWork.exam_id}`}
          fileName={selectedWork.file_path}
          answers={selectedWork.processed_data.answers}
          totalScore={selectedWork.processed_data.correct_answers}
          maxScore={selectedWork.processed_data.total_questions}
          grade={selectedWork.processed_data.grade}
        />
      )}
    </div>
  );
}

function Badge({
  icon,
  text,
  color,
}: {
  icon: React.ReactNode;
  text: string;
  color: 'gray' | 'blue' | 'green' | 'red';
}) {
  const colors = {
    gray: 'bg-gray-100 text-gray-700',
    blue: 'bg-blue-100 text-blue-700',
    green: 'bg-green-100 text-green-700',
    red: 'bg-red-100 text-red-700',
  };

  return (
    <span
      className={`inline-flex items-center gap-1 px-3 py-1 rounded-full ${colors[color]}`}
    >
      {icon}
      {text}
    </span>
  );
}
