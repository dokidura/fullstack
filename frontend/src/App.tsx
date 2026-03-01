import { useState, useEffect } from 'react';
import { UserCircle, BookOpen, Brain, ClipboardList, LogOut } from 'lucide-react';
import { Auth } from './components/Auth';
import { StudentSubmissions } from './components/StudentSubmissions';
import { TeacherAIModule } from './components/TeacherAIModule';
import { TeacherGradeSheet } from './components/TeacherGradeSheet';
import { getMe } from './api/auth';
import { getToken } from './auth/token';

type Role = 'student' | 'teacher';
type Page = 'submissions' | 'ai-module' | 'grades';

interface User {
  id: number;
  email: string;
  role: Role;
  full_name: string;
}

export default function App() {
  const [user, setUser] = useState<User | null>(null);
  const [currentPage, setCurrentPage] = useState<Page>('submissions');

  // 🔄 Восстановление сессии (через /auth/me, а не через localStorage user)
  useEffect(() => {
    const token = getToken();
    if (!token) return;

    (async () => {
      try {
        const me: User = await getMe();
        setUser(me);
        setCurrentPage(me.role === 'teacher' ? 'ai-module' : 'submissions');
      } catch {
        // токен протух/невалиден → чистим
        localStorage.removeItem('token');
        localStorage.removeItem('currentUser'); // на всякий случай, если остался старый
        setUser(null);
        setCurrentPage('submissions');
      }
    })();
  }, []);

  // ✅ логин: Auth.tsx отдаёт userData уже после /me
  const handleLogin = (userData: User) => {
    setUser(userData);
    // оставим currentUser как кеш для UI (не источник прав!)
    localStorage.setItem('currentUser', JSON.stringify(userData));
    setCurrentPage(userData.role === 'teacher' ? 'ai-module' : 'submissions');
  };

  const handleLogout = () => {
    setUser(null);
    localStorage.removeItem('token');
    localStorage.removeItem('currentUser');
    setCurrentPage('submissions');
  };

  if (!user) {
    return <Auth onLogin={handleLogin} />;
  }

  // 🔒 Простая защита "роутов" (у тебя вкладки вместо react-router)
  const safePage: Page =
    user.role === 'teacher'
      ? currentPage
      : 'submissions'; // студент не может попасть на teacher-страницы

  const renderPage = () => {
    if (safePage === 'submissions') {
      return <StudentSubmissions user={user} />;
    }
    if (safePage === 'ai-module' && user.role === 'teacher') {
      return <TeacherAIModule />;
    }
    if (safePage === 'grades' && user.role === 'teacher') {
      return <TeacherGradeSheet />;
    }
    return <StudentSubmissions user={user} />;
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <BookOpen className="w-8 h-8 text-blue-600" />
              <h1 className="text-gray-900">Электронные экзаменационные бланки</h1>
            </div>

            {/* User Info & Logout */}
            <div className="flex items-center gap-4">
              <div className="flex items-center gap-3 bg-gray-100 rounded-lg px-4 py-2">
                <UserCircle className="w-5 h-5 text-gray-600" />
                <div className="text-right">
                  <p className="text-gray-900">{user.full_name}</p>
                  <p className="text-gray-500">
                    {user.role === 'teacher' ? 'Учитель' : 'Ученик'}
                  </p>
                </div>
              </div>
              <button
                onClick={handleLogout}
                className="flex items-center gap-2 px-4 py-2 text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded-lg transition-colors"
              >
                <LogOut className="w-4 h-4" />
                Выход
              </button>
            </div>
          </div>
        </div>
      </header>

      {/* Navigation */}
      <nav className="bg-white border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex gap-1">
            <button
              onClick={() => setCurrentPage('submissions')}
              className={`flex items-center gap-2 px-4 py-3 border-b-2 transition-colors ${
                safePage === 'submissions'
                  ? 'border-blue-600 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700'
              }`}
            >
              <BookOpen className="w-4 h-4" />
              {user.role === 'student' ? 'Мои работы' : 'Работы учеников'}
            </button>

            {user.role === 'teacher' && (
              <>
                <button
                  onClick={() => setCurrentPage('ai-module')}
                  className={`flex items-center gap-2 px-4 py-3 border-b-2 transition-colors ${
                    safePage === 'ai-module'
                      ? 'border-blue-600 text-blue-600'
                      : 'border-transparent text-gray-500 hover:text-gray-700'
                  }`}
                >
                  <Brain className="w-4 h-4" />
                  Модуль ИИ
                </button>
                <button
                  onClick={() => setCurrentPage('grades')}
                  className={`flex items-center gap-2 px-4 py-3 border-b-2 transition-colors ${
                    safePage === 'grades'
                      ? 'border-blue-600 text-blue-600'
                      : 'border-transparent text-gray-500 hover:text-gray-700'
                  }`}
                >
                  <ClipboardList className="w-4 h-4" />
                  Ведомости
                </button>
              </>
            )}
          </div>
        </div>
      </nav>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {renderPage()}
      </main>
    </div>
  );
}
