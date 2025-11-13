import React, { useState, useEffect } from 'react';
import ReactDOM from 'react-dom/client';

// ▼ 1. カラム定義に追加
const COLUMNS = {
  user_id: "UUID",
  name: "氏名",
  d_id: "D番号",
  employee_number: "職員番号",
  position_id: "職種ID",
  position_name: "職種名称",
  department_id: "部署ID",
  department_name: "部署名称",
  card_uid: "カードUID",             // 追加
  card_management_id: "カード管理ID" // 追加
};

const escapeCSV = (str) => {
  if (str === null || str === undefined) {
    return "";
  }
  const s = String(str);
  if (s.includes('"') || s.includes(',') || s.includes('\n')) {
    return `"${s.replace(/"/g, '""')}"`;
  }
  return s;
};

function App() {
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const [selectedColumns, setSelectedColumns] = useState(Object.keys(COLUMNS));

  useEffect(() => {
    fetch('/api/users/')
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

  const handleColumnToggle = (columnKey) => {
    setSelectedColumns(prev =>
      prev.includes(columnKey)
        ? prev.filter(key => key !== columnKey)
        : [...prev, columnKey]
    );
  };

  const handleDownloadCSV = () => {
    if (selectedColumns.length === 0) {
      alert("少なくとも1つのカラムを選択してください。");
      return;
    }

    const headers = selectedColumns.map(key => COLUMNS[key]);
    let csvContent = headers.join(",") + "\n";

    users.forEach(user => {
      const row = selectedColumns.map(key => escapeCSV(user[key]));
      csvContent += row.join(",") + "\n";
    });

    const bom = new Uint8Array([0xEF, 0xBB, 0xBF]);
    const blob = new Blob([bom, csvContent], { type: 'text/csv;charset=utf-8;' });
    
    const link = document.createElement("a");
    const url = URL.createObjectURL(blob);
    link.setAttribute("href", url);
    link.setAttribute("download", "staff_list.csv");
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  if (loading) {
    return <div>Loading...</div>;
  }

  if (error) {
    return <div>Error: {error}</div>;
  }

  return (
    <div>
      <h1>職員リスト</h1>

      <div>
        <h3>CSVダウンロード項目:</h3>
        {Object.entries(COLUMNS).map(([key, label]) => (
          <label key={key} style={{ marginRight: '10px' }}>
            <input
              type="checkbox"
              checked={selectedColumns.includes(key)}
              onChange={() => handleColumnToggle(key)}
            />
            {label}
          </label>
        ))}
      </div>

      <button onClick={handleDownloadCSV} style={{ marginTop: '10px' }}>
        選択した項目をCSVダウンロード
      </button>

      <table style={{ marginTop: '20px' }}>
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
            {/* ▼ ヘッダー追加 */}
            <th>カードUID</th>
            <th>カード管理ID</th>
          </tr>
        </thead>
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
              {/* ▼ データ追加 */}
              <td>{user.card_uid}</td>
              <td>{user.card_management_id}</td>
            </tr>
          ))}
        </tbody>
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