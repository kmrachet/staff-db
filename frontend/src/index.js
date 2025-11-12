import React, { useState, useEffect } from 'react';
import ReactDOM from 'react-dom/client';

// ▼ 1. カラム定義 (キーと表示名)
const COLUMNS = {
  user_id: "UUID",
  name: "氏名",
  d_id: "D番号",
  employee_number: "職員番号",
  position_id: "職種ID",
  position_name: "職種名称",
  department_id: "部署ID",
  department_name: "部署名称"
};

// CSVエスケープ関数
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

  // ▼ 2. 選択されたカラムを管理するState (初期値は全てのカラムキー)
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

  // ▼ 3. チェックボックス変更ハンドラ
  const handleColumnToggle = (columnKey) => {
    setSelectedColumns(prev =>
      prev.includes(columnKey)
        ? prev.filter(key => key !== columnKey) // チェックを外す
        : [...prev, columnKey] // チェックする
    );
  };

  // ▼ 4. CSVダウンロードハンドラ
  const handleDownloadCSV = () => {
    if (selectedColumns.length === 0) {
      alert("少なくとも1つのカラムを選択してください。");
      return;
    }

    // ヘッダー行 (選択されたカラムの表示名)
    const headers = selectedColumns.map(key => COLUMNS[key]);
    let csvContent = headers.join(",") + "\n";

    // データ行
    users.forEach(user => {
      const row = selectedColumns.map(key => escapeCSV(user[key]));
      csvContent += row.join(",") + "\n";
    });

    // BOM を追加してExcelでの文字化けを防ぐ
    const bom = new Uint8Array([0xEF, 0xBB, 0xBF]);
    const blob = new Blob([bom, csvContent], { type: 'text/csv;charset=utf-8;' });
    
    // ダウンロードリンクを作成して実行
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

      {/* ▼ 5. カラム選択チェックボックス ▼ */}
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

      {/* ▼ 6. ダウンロードボタン ▼ */}
      <button onClick={handleDownloadCSV} style={{ marginTop: '10px' }}>
        選択した項目をCSVダウンロード
      </button>

      {/* ▼ テーブル表示 (選択状態に関わらず全カラム表示) ▼ */}
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