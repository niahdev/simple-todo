import React, { useEffect, useState } from 'react';
import { createRoot } from 'react-dom/client';
import './style.css';

function App() {
  const [todos, setTodos] = useState([]);
  const [title, setTitle] = useState('');
  const [error, setError] = useState('');
  async function request(path, options) {
    const response = await fetch(`/api${path}`, { ...options, headers: { 'Content-Type': 'application/json', ...options?.headers } });
    if (!response.ok) throw new Error(`요청 실패 (${response.status})`);
    return response.status === 204 ? null : response.json();
  }
  async function refresh() {
    try { setTodos(await request('/todos')); setError(''); }
    catch (e) { setError(e.message); }
  }
  useEffect(() => { refresh(); }, []);
  async function add(e) {
    e.preventDefault();
    if (!title.trim()) return;
    try { await request('/todos', { method: 'POST', body: JSON.stringify({ title: title.trim() }) }); setTitle(''); await refresh(); }
    catch (e) { setError(e.message); }
  }
  async function toggle(todo) {
    try { await request(`/todos/${todo.id}`, { method: 'PATCH', body: JSON.stringify({ completed: !todo.completed }) }); await refresh(); }
    catch (e) { setError(e.message); }
  }
  async function edit(todo) {
    const updated = window.prompt('할 일 수정', todo.title);
    if (updated === null || !updated.trim()) return;
    try { await request(`/todos/${todo.id}`, { method: 'PATCH', body: JSON.stringify({ title: updated.trim() }) }); await refresh(); }
    catch (e) { setError(e.message); }
  }
  async function remove(todo) {
    try { await request(`/todos/${todo.id}`, { method: 'DELETE' }); await refresh(); }
    catch (e) { setError(e.message); }
  }
  return <main><h1>Simple TODO</h1><p>오늘 할 일을 기록해 보세요.</p><form onSubmit={add}><input aria-label="새 할 일" value={title} onChange={e => setTitle(e.target.value)} maxLength={200} placeholder="할 일을 입력하세요"/><button>추가</button></form>{error && <p role="alert" className="error">{error}</p>}<ul>{todos.map(todo => <li key={todo.id}><label><input type="checkbox" checked={todo.completed} onChange={() => toggle(todo)}/><span className={todo.completed ? 'done' : ''}>{todo.title}</span></label><div><button className="secondary" onClick={() => edit(todo)}>수정</button><button className="danger" onClick={() => remove(todo)}>삭제</button></div></li>)}</ul>{todos.length === 0 && <p>아직 등록된 할 일이 없습니다.</p>}</main>;
}

createRoot(document.getElementById('root')).render(<App />);
