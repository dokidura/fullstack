import { X, CheckCircle, XCircle, FileText, Eye } from 'lucide-react';

interface Answer {
  questionNumber: number;
  recognizedText: string;
  correctAnswer: string;
  isCorrect: boolean;
  confidence: number;
}

interface ResultModalProps {
  isOpen: boolean;
  onClose: () => void;
  studentName: string;
  subject: string;
  fileName: string;
  answers: Answer[];
  totalScore: number;
  maxScore: number;
  grade: number;
}

export function ResultModal({
  isOpen,
  onClose,
  studentName,
  subject,
  fileName,
  answers,
  totalScore,
  maxScore,
  grade
}: ResultModalProps) {
  if (!isOpen) return null;

  const percentage = Math.round((totalScore / maxScore) * 100);

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
      <div className="bg-white rounded-lg shadow-xl max-w-4xl w-full max-h-[90vh] overflow-hidden flex flex-col">
        {/* Header */}
        <div className="px-6 py-4 border-b border-gray-200 flex items-center justify-between">
          <div>
            <h2 className="text-gray-900 mb-1">Результаты обработки бланка</h2>
            <p className="text-gray-600">{studentName} • {subject}</p>
          </div>
          <button
            onClick={onClose}
            className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
          >
            <X className="w-5 h-5 text-gray-500" />
          </button>
        </div>

        {/* Stats */}
        <div className="px-6 py-4 bg-gray-50 border-b border-gray-200">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <FileText className="w-5 h-5 text-gray-400" />
              <span className="text-gray-600">{fileName}</span>
            </div>
            <div className="flex items-center gap-6">
              <div className="text-right">
                <p className="text-gray-500">Результат</p>
                <p className="text-gray-900">{totalScore} / {maxScore}</p>
              </div>
              <div className="text-right">
                <p className="text-gray-500">Процент</p>
                <p className="text-gray-900">{percentage}%</p>
              </div>
              <div className="text-center">
                <p className="text-gray-500 mb-1">Оценка</p>
                <div className={`inline-flex items-center justify-center w-10 h-10 rounded-full ${
                  grade === 5 ? 'bg-green-100 text-green-700' :
                  grade === 4 ? 'bg-blue-100 text-blue-700' :
                  grade === 3 ? 'bg-yellow-100 text-yellow-700' : 'bg-red-100 text-red-700'
                }`}>
                  <span>{grade}</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Answers List */}
        <div className="flex-1 overflow-y-auto px-6 py-4">
          <div className="space-y-3">
            {answers.map((answer) => (
              <div
                key={answer.questionNumber}
                className={`p-4 rounded-lg border-2 ${
                  answer.isCorrect
                    ? 'bg-green-50 border-green-200'
                    : 'bg-red-50 border-red-200'
                }`}
              >
                <div className="flex items-start gap-3">
                  <div className="mt-1">
                    {answer.isCorrect ? (
                      <CheckCircle className="w-5 h-5 text-green-600" />
                    ) : (
                      <XCircle className="w-5 h-5 text-red-600" />
                    )}
                  </div>
                  
                  <div className="flex-1">
                    <div className="flex items-center justify-between mb-2">
                      <p className={`font-medium ${
                        answer.isCorrect ? 'text-green-900' : 'text-red-900'
                      }`}>
                        Вопрос {answer.questionNumber}
                      </p>
                      <div className="flex items-center gap-2">
                        <Eye className="w-4 h-4 text-gray-400" />
                        <span className="text-gray-500">
                          Уверенность: {answer.confidence}%
                        </span>
                      </div>
                    </div>

                    <div className="grid grid-cols-2 gap-4">
                      <div>
                        <p className="text-gray-600 mb-1">Распознанный ответ:</p>
                        <div className="bg-white px-3 py-2 rounded border border-gray-200">
                          <p className={answer.isCorrect ? 'text-green-700' : 'text-red-700'}>
                            {answer.recognizedText || '(не распознано)'}
                          </p>
                        </div>
                      </div>
                      <div>
                        <p className="text-gray-600 mb-1">Правильный ответ:</p>
                        <div className="bg-white px-3 py-2 rounded border border-gray-200">
                          <p className="text-gray-900">{answer.correctAnswer}</p>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Footer */}
        <div className="px-6 py-4 border-t border-gray-200 bg-gray-50">
          <div className="flex items-center justify-between">
            <p className="text-gray-600">
              Обработано через Tesseract OCR
            </p>
            <button
              onClick={onClose}
              className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
            >
              Закрыть
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
