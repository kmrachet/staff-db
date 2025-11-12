import React, { useState, useEffect } from 'react';
import ReactDOM from 'react-dom/client';

function App() {
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    // APIを呼び出す
    fetch('/api/users/') // このパスでバックエンドにリクエストされます
      .then(response => {
        if (!response.ok) {
          throw new Error('Network response was not ok');
        }
        return response.json();
      })
      .then(data => {
        setUsers(data);
        setLoading(false);
      })
      .catch(error => {
        setError(error.message);
        setLoading(false);
      });
  }, []);

  if (loading) {
    return <div>Loading...</div>;
  }

  if (error) {
    return <div>Error: {error}</div>;
  }

  return (
    <div>
      <h1>職員リスト</h1>
      <table>
        {/* ▼ カラム名を指定のものに変更 ▼ */}
        <thead>
          <tr>
            <th>UUID</th>
            <th>氏名</th>
            <th>D番号</th>
            <th>職員番号</th>
            <th>職種ID</th>
            <th>職種名称</th>
            <th>部署ID</th>
            <th>部署名称</th>
          </tr>
        </thead>
        {/* ▲ カラム名を指定のものに変更 ▲ */}

        {/* ▼ 表示するデータを指定のものに変更 ▼ */}
        <tbody>
          {users.map(user => (
            <tr key={user.user_id}>
              <td>{user.user_id}</td>
              <td>{user.name}</td>
              <td>{user.d_id}</td>
              <td>{user.employee_number}</td>
              <td>{user.position_id}</td>
              <td>{user.position_name}</td>
              <td>{user.department_id}</td>
              <td>{user.department_name}</td>
            </tr>
          ))}
        </tbody>
        {/* ▲ 表示するデータを指定のものに変更 ▲ */}
      </table>
    </div>
  );
}

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);