import click
import pandas as pd
from .extensions import db
from .models import Position  # Positionモデルをインポート
import os

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

                # 既に存在するかDBで確認 (getは主キー検索)
                existing_pos = Position.query.get(pos_id)
                
                if existing_pos:
                    print(f"スキップ: Position ID {pos_id} ({pos_name}) は既に存在します。")
                    continue
                
                # 新規作成
                new_pos = Position(
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
                # ここでは例として '職員番号' を user_id とします
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
                    position_id=1, # 仮: 事前に 'Positions' テーブルに '一般' (ID:1) を登録しておく
                    start_date=pd.to_datetime(row['採用日']).date() if pd.notna(row['採用日']) else None
                )
                db.session.add(emp_history)

                # 3. DNumberHistory への登録
                if pd.notna(row['職員番号']): # D番号のカラム名が '職員番号' だった場合
                    d_num_history = DNumberHistory(
                        user_id=user_id,
                        d_number=row['職員番号'],
                        start_date=pd.to_datetime(row['採用日']).date() if pd.notna(row['採用日']) else None
                    )
                    db.session.add(d_num_history)
                
                # 4. Cards への登録
                if pd.notna(row['Felicaカード番号']):
                    card = Card(
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