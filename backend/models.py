from .extensions import db
from sqlalchemy.sql import func
from sqlalchemy import Column, Integer, String, DATE, TIMESTAMP, BOOLEAN, VARCHAR, ForeignKey, PrimaryKeyConstraint
from sqlalchemy.orm import relationship

# 共通のタイムスタンプカラム（ミックスイン）
class TimestampMixin:
    # デフォルトで現在日時、更新時にも自動で現在日時を設定
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())

# --------------------
# 1. 職員の基本情報
# --------------------

class User(TimestampMixin, db.Model):
    __tablename__ = 'Users'
    user_id = Column(VARCHAR(255), primary_key=True, comment="管理ID (PK)")
    name = Column(VARCHAR(255), comment="氏名")
    birthday = Column(DATE, comment="生年月日")
    hire_date = Column(DATE, comment="入職日")
    # personal_extension_number はER図から削除

    # リレーションシップ
    # status_history はER図から削除
    employee_number_history = relationship('EmployeeNumberHistory', back_populates='user')
    d_numbers = relationship('DNumbers', back_populates='user') # DNumberHistory から DNumbers に変更
    system_ids = relationship('System_IDs', back_populates='user') # SystemID から System_IDs に変更
    cards = relationship('Cards', back_populates='user') # Card から Cards に変更
    departments = relationship('UserDepartment', back_populates='user')

# UserStatus と UserStatusHistory はER図から削除

# --------------------
# 2. 各種ID管理
# --------------------

class Positions(TimestampMixin, db.Model): # Position -> Positions
    __tablename__ = 'Positions'
    position_id = Column(Integer, primary_key=True, comment="職位ID (PK)")
    position_name = Column(VARCHAR(100), comment="職位名")
    
    # リレーションシップ
    employee_number_history = relationship('EmployeeNumberHistory', back_populates='position')

class EmployeeNumberHistory(TimestampMixin, db.Model):
    __tablename__ = 'Employee_Number_History'
    employee_number_history_id = Column(Integer, primary_key=True, comment="履歴ID (PK)")
    user_id = Column(VARCHAR(255), ForeignKey('Users.user_id'), comment="管理ID (FK)")
    employee_number = Column(VARCHAR(100), comment="職員番号")
    position_id = Column(Integer, ForeignKey('Positions.position_id'), comment="職位ID (FK)")
    start_date = Column(DATE, comment="開始日")
    end_date = Column(DATE, nullable=True, comment="終了日")

    # リレーションシップ
    user = relationship('User', back_populates='employee_number_history')
    position = relationship('Positions', back_populates='employee_number_history') # Position -> Positions

class DNumbers(TimestampMixin, db.Model): # DNumberHistory -> DNumbers
    __tablename__ = 'D_Numbers'
    d_number_history_id = Column(Integer, primary_key=True, comment="履歴ID (PK)")
    user_id = Column(VARCHAR(255), ForeignKey('Users.user_id'), comment="管理ID (FK)")
    d_number = Column(VARCHAR(100), comment="D番号")
    is_active = Column(BOOLEAN, default=True, comment="有効フラグ") # start_date, end_date から変更
    
    # リレーションシップ
    user = relationship('User', back_populates='d_numbers') # d_number_history -> d_numbers

class System_IDs(TimestampMixin, db.Model): # SystemID -> System_IDs
    __tablename__ = 'System_IDs'
    system_id_record_id = Column(Integer, primary_key=True, comment="レコードID (PK)")
    user_id = Column(VARCHAR(255), ForeignKey('Users.user_id'), comment="管理ID (FK)")
    system_id = Column(VARCHAR(255), comment="情報システムID")
    is_active = Column(BOOLEAN, default=True, comment="有効フラグ")
    
    # リレーションシップ
    user = relationship('User', back_populates='system_ids')

class Cards(TimestampMixin, db.Model): # Card -> Cards
    __tablename__ = 'Cards'
    card_uid = Column(VARCHAR(255), primary_key=True, comment="カードUID (PK)")
    user_id = Column(VARCHAR(255), ForeignKey('Users.user_id'), comment="管理ID (FK)")
    card_management_id = Column(VARCHAR(255), comment="カード管理用ID")
    is_active = Column(BOOLEAN, default=True, comment="有効フラグ")
    
    # リレーションシップ
    user = relationship('User', back_populates='cards')

# --------------------
# 3. 部署・所属管理
# --------------------

class Departments(TimestampMixin, db.Model): # Department -> Departments
    __tablename__ = 'Departments'
    department_id = Column(Integer, primary_key=True, comment="部署ID (PK)")
    department_extension_number = Column(VARCHAR(50), comment="部署の内線")
    start_date = Column(DATE, comment="開始日") # create_date から変更
    end_date = Column(DATE, nullable=True, comment="終了日") # 新規追加
    
    # リレーションシップ
    # name_history はER図から削除
    users = relationship('UserDepartment', back_populates='department')

# DepartmentNameHistory はER図から削除

# 中間テーブル (Users と Departments)
class UserDepartment(TimestampMixin, db.Model):
    __tablename__ = 'User_Departments'
    user_id = Column(VARCHAR(255), ForeignKey('Users.user_id'), primary_key=True, comment="管理ID (PK, FK)")
    department_id = Column(Integer, ForeignKey('Departments.department_id'), primary_key=True, comment="部署ID (PK, FK)")
    
    # リレーショングループ
    user = relationship('User', back_populates='departments')
    department = relationship('Departments', back_populates='users') # Department -> Departments

# --------------------
# 4. システム連携
# --------------------

class External_Systems(TimestampMixin, db.Model): # ExternalSystem -> External_Systems
    __tablename__ = 'External_Systems'
    system_id = Column(Integer, primary_key=True, comment="システムID (PK)")
    system_name = Column(VARCHAR(255), comment="外部システム名")
    start_date = Column(DATE, comment="開始日")
    end_date = Column(DATE, nullable=True, comment="終了日")
    
    # リレーションシップ
    export_settings = relationship('External_System_Exports', back_populates='system') # ExternalSystemExport -> External_System_Exports

class External_System_Exports(TimestampMixin, db.Model): # ExternalSystemExport -> External_System_Exports
    __tablename__ = 'External_System_Exports'
    export_setting_id = Column(Integer, primary_key=True, comment="設定ID (PK)")
    system_id = Column(Integer, ForeignKey('External_Systems.system_id'), comment="システムID (FK)")
    table_name = Column(VARCHAR(255), comment="対象テーブル名")
    column_name = Column(VARCHAR(255), comment="対象カラム名")
    transform_id = Column(VARCHAR(255), comment="変換先ID") # 新規追加
    
    # リレーションシップ
    system = relationship('External_Systems', back_populates='export_settings') # ExternalSystem -> External_Systems