import click
import pandas as pd
from .extensions import db
# UserDepartment をインポート対象に追加
from .models import Positions, User, EmployeeNumberHistory, DNumbers, Cards, Departments, UserDepartment
import os
import datetime
import uuid
import logging

# 'app' (Flaskアプリケーションインスタンス) を受け取るようにします
def register_commands(app):

    @app.cli.command("import-positions")
    @click.argument('csv_file')
    def import_positions(csv_file):
        """
        position_id_list.csv から Position (職位) マスターデータをインポートします。
        CSVはヘッダーなし、1列目=ID, 2列目=名前 と想定します。
    
        """
        if not os.path.exists(csv_file):
            print(f"エラー: ファイルが見つかりません: {csv_file}")
            return

        print(f"{csv_file} から職位データを読み込んでいます...")
        
        try:
            # CSVにヘッダーがないため、カラム名を指定
            df = pd.read_csv(
                csv_file, 
                header=None, 
                names=['position_id', 'position_name'],
                # position_id を integer として読み込む
                dtype={'position_id': int, 'position_name': str} 
            )

            count = 0
            for index, row in df.iterrows():
                pos_id = row['position_id']
                pos_name = row['position_name']

                # 変更: Position -> Positions
                existing_pos = Positions.query.get(pos_id)
                
                if existing_pos:
                    print(f"スキップ: Position ID {pos_id} ({pos_name}) は既に存在します。")
                    continue
                
                # 変更: Position -> Positions
                new_pos = Positions(
                    position_id=pos_id,
                    position_name=pos_name
                )
                db.session.add(new_pos)
                print(f"追加: Position ID {pos_id} ({pos_name})")
                count += 1

            # ループが正常に完了したらコミット
            db.session.commit()
            print(f"---")
            print(f"職位データのインポートが完了しました。{count}件の新しいレコードが追加されました。")

        except Exception as e:
            db.session.rollback() # エラーが発生したらロールバック
            print(f"エラーが発生したためロールバックしました: {e}")

    @app.cli.command("import-departments")
    @click.argument('csv_file')
    def import_departments(csv_file):
        """
        dept_master.csv から Department (部署) マスターデータをインポートします。
        CSVはヘッダーなし、1列目=ID, 2列目=名前 と想定します。
        """
        if not os.path.exists(csv_file):
            print(f"エラー: ファイルが見つかりません: {csv_file}")
            return

        print(f"{csv_file} から部署データを読み込んでいます...")

        try:
            df = pd.read_csv(
                csv_file,
                header=None,
                names=['department_id', 'department_name'],
                dtype={'department_id': int, 'department_name': str}
            )

            count = 0
            for index, row in df.iterrows():
                dept_id = row['department_id']
                dept_name = row['department_name']

                existing_dept = Departments.query.get(dept_id)

                if existing_dept:
                    print(f"スキップ: Department ID {dept_id} ({dept_name}) は既に存在します。")
                    continue

                new_dept = Departments(
                    department_id=dept_id,
                    department_name=dept_name,
                    start_date=datetime.date.today() # start_date を今日の日付に設定
                )
                db.session.add(new_dept)
                print(f"追加: Department ID {dept_id} ({dept_name})")
                count += 1

            db.session.commit()
            print(f"---")
            print(f"部署データのインポートが完了しました。{count}件の新しいレコードが追加されました。")

        except Exception as e:
            db.session.rollback()
            print(f"エラーが発生したためロールバックしました: {e}")

    @app.cli.command("import-data")
    @click.argument('csv_file')
    def import_data(csv_file):
        """
        指定されたCSVファイルから初期データをDBにインポートします。
        (例: flask import-data nurse_newcomer_modified.csv)
        ★ user_id は UUID を自動生成します ★
        """
        
        if not os.path.exists(csv_file):
            print(f"エラー: ファイルが見つかりません: {csv_file}")
            return

        print(f"{csv_file} からデータを読み込んでいます...")
        try:
            # nurse_newcomer_modified.csv はヘッダー付き、UTF-8 と想定
            # 1列目の名前なしカラムはインデックスとして読み込む
            df = pd.read_csv(csv_file, encoding='utf-8', index_col=0) 
        except Exception as e:
            print(f"CSV読み込みエラー: {e}")
            return
            
        print(f"{len(df)}件のデータを処理します...")

        # 'nurse_newcomer_modified.csv' のカラム名と
        # 'backend/models.py' のモデルを対応付けます
        
        for index, row in df.iterrows():
            try:
                # --- 重複チェック ---
                # employee_number をキーに EmployeeNumberHistory を検索
                emp_num_str = str(row['employee_number'])
                existing_history = EmployeeNumberHistory.query.filter_by(employee_number=emp_num_str).first()
                
                if existing_history:
                    print(f"スキップ: Employee Number {emp_num_str} ({row['name']}) は既に存在します。")
                    continue

                # --- 新規登録 ---
                # 1. user_id として UUID を生成
                user_id = str(uuid.uuid4())

                # 2. Usersテーブルへの登録
                new_user = User(
                    user_id=user_id, # 生成したUUIDを使用
                    name=row['name'],
                    birthday=pd.to_datetime(row['Birthday']).date() if pd.notna(row['Birthday']) else None,
                    hire_date=pd.to_datetime(row['hire_date']).date() if pd.notna(row['hire_date']) else None
                )
                db.session.add(new_user)
                
                # 3. EmployeeNumberHistory への登録 (職員番号の履歴)
                emp_history = EmployeeNumberHistory(
                    user_id=user_id, # 生成したUUIDを使用
                    employee_number=emp_num_str, # CSVの職員番号
                    # CSVから 'position_id' を使用
                    position_id=int(row['position_id']), 
                    start_date=pd.to_datetime(row['hire_date']).date() if pd.notna(row['hire_date']) else None
                )
                db.session.add(emp_history)

                # 4. DNumbers への登録
                if pd.notna(row['d_number']): 
                    d_num = DNumbers(
                        user_id=user_id, # 生成したUUIDを使用
                        d_number=str(row['d_number']),
                        is_active=True 
                    )
                    db.session.add(d_num)
                
                # 5. Cards への登録 (CSVにないためスキップ)
                # ...

                # 6. UserDepartment への登録 (部署との関連付け)
                if pd.notna(row['department_id']):
                    user_dept = UserDepartment(
                        user_id=user_id, # 生成したUUIDを使用
                        department_id=int(row['department_id'])
                    )
                    db.session.add(user_dept)
                
                db.session.commit()
                print(f"成功: User {user_id} (Name: {row['name']}, Emp#: {emp_num_str}) を登録しました。")

            except Exception as e:
                db.session.rollback()
                # エラー出力に 'employee_number' を使用
                print(f"エラー: User (Name: {row.get('name', 'N/A')}, Emp#: {row.get('employee_number', 'N/A')}) の登録に失敗しました。 {e}")
        
        print("データインポートが完了しました。")

    @app.cli.command("show-users")
    @click.option('--limit', '-n', default=None, type=int, help='表示する最大レコード数を指定します。')
    def show_users(limit):
        """
        データベースに登録されている全ユーザーの概要情報を表示します。
        """

        # SQLAlchemyのログをWARNING以上のみ表示に設定
        # INFOレベルのSQLクエリログが出力されない
        logging.getLogger('sqlalchemy.engine').setLevel(logging.WARNING)

        print("データベースからユーザー情報を読み込んでいます...")

        try:
            # 1. User クエリを作成 (まだ実行しない)
            #    入職日でソートしておくと limit が意味を持つ
            query = User.query.order_by(User.hire_date)

            if limit:
                # 2. limit オプションが指定されていたら件数を制限
                print(f"データベースから最大{limit}件のユーザー情報を読み込んでいます...")
                query = query.limit(limit)
            else:
                print("データベースから全ユーザー情報を読み込んでいます...")

            # 3. クエリを実行
            users = query.all()

            if not users:
                print("データベースにユーザーが見つかりません。")
                return

            if limit:
                print(f"--- {len(users)}件のユーザー情報を表示 (最大{limit}件) ---")
            else:
                print(f"--- {len(users)}件のユーザー情報 ---")

            dct = {}
            i = 0
            for user in users:
                dct[i] = {}
                dct[i]['user_id'] = user.user_id
                dct[i]['name'] = user.name
                dct[i]['hire_date'] = user.hire_date

                # 職員番号と職位 (EmployeeNumberHistory から取得)
                if user.employee_number_history:
                    history = user.employee_number_history[0]
                    dct[i]['employee_number'] = history.employee_number
                    dct[i]['position_id'] = history.position_id
                    # Position表示 (position リレーションシップが必要)
                    if history.position:
                        # PositionテーブルにIDがある場合
                        dct[i]['position_name'] = history.position.position_name
                    else:
                        # PositionテーブルにIDが見つからない場合
                        dct[i]['position_name'] = None
                else:
                    # EmployeeNumberHistory が存在しない場合
                    dct[i]['employee_number'] = None
                    dct[i]['position_id'] = None
                    dct[i]['position_name'] = None

                # D番号 (DNumbers から取得)
                if user.d_numbers:
                    # DNumbersテーブルにD番号がある場合
                    d_num = user.d_numbers[0]
                    dct[i]['d_number'] = d_num.d_number
                else:
                    # D番号がNanの場合
                    dct[i]['d_number'] = None

                # 所属部署 (UserDepartment 経由で Departments から取得)
                if user.departments:
                    dept_assoc = user.departments[0] 
                    if dept_assoc.department:
                        # DepartmentテーブルにIDがある場合
                        dct[i]['department_id'] = dept_assoc.department_id
                        dct[i]['department_name'] = dept_assoc.department.department_name
                    else:
                        # DepartmentテーブルにIDが見つからない場合
                        dct[i]['department_id'] = dept_assoc.department_id
                        dct[i]['department_name'] = None
                else:
                    # department_idがNanの場合
                    dct[i]['department_id'] = None
                    dct[i]['department_name'] = None

                i += 1
            df = pd.DataFrame.from_dict(dct, orient='index')
            print(df.head(limit))
            print("\n--- 表示完了 ---")

        except Exception as e:
            print(f"データの表示中にエラーが発生しました: {e}")