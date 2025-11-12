import click
import pandas as pd
from .extensions import db
from .models import Positions, User, EmployeeNumberHistory, DNumbers, Cards, Departments
import os
import datetime

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
        (例: flask import-data cws_exchange/results/nurse_newcomer_20250401.csv)
        """
        
        # cws_exchange/for_cws.ipynb の最終出力CSVのカラム名を確認
        # このCSVはプロジェクトルートからの相対パスで指定することを想定
        if not os.path.exists(csv_file):
            print(f"エラー: ファイルが見つかりません: {csv_file}")
            return

        print(f"{csv_file} からデータを読み込んでいます...")
        try:
            # for_cws.ipynbの最終出力（Shift_JISかもしれません）に合わせてエンコーディングを指定
            df = pd.read_csv(csv_file, encoding='utf-8') # もし 'cp932' なら変更
        except Exception as e:
            print(f"CSV読み込みエラー: {e}")
            return
            
        print(f"{len(df)}件のデータを処理します...")

        # 'cws_exchange/for_cws.ipynb' で定義されているカラム名と
        # 'backend/models.py' のモデルを対応付けます
        
        # (例: df のカラム名が '職員番号', '氏名(漢字)姓', '氏名(漢字)名', 'Felicaカード番号', 'D番号' の場合)
        
        for index, row in df.iterrows():
            try:
                # 1. Usersテーブルへの登録
                # user_id は '職員番号' を使うか、D番号を使うか、設計に合わせて決定
                # ここでは例として '給与番号' を user_id とします
                user_id = row['給与番号'] # cws_exchange/for_cws.ipynb の '給与番号' を使用
                
                # 既に存在するかチェック (職員番号はユニークなはず)
                existing_user = User.query.get(user_id)
                if existing_user:
                    print(f"スキップ: User {user_id} は既に存在します。")
                    continue

                new_user = User(
                    user_id=user_id,
                    name=f"{row['氏名(漢字)姓']} {row['氏名(漢字)名']}",
                    # '生年月日', '入職日' もCSVにあるなら追加
                    birthday=pd.to_datetime(row['生年月日']).date() if pd.notna(row['生年月日']) else None,
                    hire_date=pd.to_datetime(row['採用日']).date() if pd.notna(row['採用日']) else None
                )
                db.session.add(new_user)
                
                # 2. EmployeeNumberHistory への登録 (職員番号の履歴)
                emp_history = EmployeeNumberHistory(
                    user_id=user_id,
                    employee_number=row['給与番号'],
                    # '職位ID' は '職位' ('一般' など) から 'Positions' テーブルを引くか、
                    # 'position_code' ('0006') を直接使う
                    # 変更：コメントを Positions に修正
                    position_id=1, # 仮: 事前に 'Positions' テーブルに '一般' (ID:1) を登録しておく
                    start_date=pd.to_datetime(row['採用日']).date() if pd.notna(row['採用日']) else None
                )
                db.session.add(emp_history)

                # 3. DNumbers への登録 (変更)
                if pd.notna(row['職員番号']): # D番号のカラム名が '職員番号' だった場合
                    # 変更: DNumberHistory -> DNumbers, start_date -> is_active
                    d_num = DNumbers(
                        user_id=user_id,
                        d_number=row['職員番号'],
                        is_active=True 
                    )
                    db.session.add(d_num)
                
                # 4. Cards への登録 (変更)
                if pd.notna(row['Felicaカード番号']):
                    # 変更: Card -> Cards
                    card = Cards(
                        card_uid=row['Felicaカード番号'],
                        user_id=user_id,
                        is_active=True
                    )
                    db.session.add(card)
                
                # 他のテーブル (User_Statuses, User_Departments など) も
                # CSVデータ に基づいて登録...
                
                db.session.commit()
                print(f"成功: User {user_id} を登録しました。")

            except Exception as e:
                db.session.rollback()
                print(f"エラー: User {row.get('給与番号', 'N/A')} の登録に失敗しました。 {e}")
        
        print("データインポートが完了しました。")