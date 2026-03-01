export const EXAMS = [
  { id: 1, name: 'Русский язык' },
  { id: 2, name: 'Математика' },
  { id: 3, name: 'Физика' },
  { id: 4, name: 'Литература' },
  { id: 5, name: 'Химия' },
];

export function examNameById(id: number): string {
  return EXAMS.find(e => e.id === id)?.name || `Экзамен #${id}`;
}
