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
    personal_extension_number = Column(VARCHAR(50), comment="個人の内線")

    # リレーションシップ
    status_history = relationship('UserStatusHistory', back_populates='user')
    employee_number_history = relationship('EmployeeNumberHistory', back_populates='user')
    d_number_history = relationship('DNumberHistory', back_populates='user')
    system_ids = relationship('SystemID', back_populates='user')
    cards = relationship('Card', back_populates='user')
    departments = relationship('UserDepartment', back_populates='user')

class UserStatus(TimestampMixin, db.Model):
    __tablename__ = 'User_Statuses'
    status_id = Column(Integer, primary_key=True, comment="ステータスID (PK)")
    status_name = Column(VARCHAR(100), comment="ステータス名")

    # リレーションシップ
    user_history = relationship('UserStatusHistory', back_populates='status')

class UserStatusHistory(TimestampMixin, db.Model):
    __tablename__ = 'User_Status_History'
    status_history_id = Column(Integer, primary_key=True, comment="履歴ID (PK)")
    user_id = Column(VARCHAR(255), ForeignKey('Users.user_id'), comment="管理ID (FK)")
    status_id = Column(Integer, ForeignKey('User_Statuses.status_id'), comment="ステータスID (FK)")
    start_date = Column(DATE, comment="開始日")
    end_date = Column(DATE, nullable=True, comment="終了日")

    # リレーションシップ
    user = relationship('User', back_populates='status_history')
    status = relationship('UserStatus', back_populates='user_history')

# --------------------
# 2. 各種ID管理
# --------------------

class Position(TimestampMixin, db.Model):
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
    position = relationship('Position', back_populates='employee_number_history')

class DNumberHistory(TimestampMixin, db.Model):
    __tablename__ = 'D_Number_History'
    d_number_history_id = Column(Integer, primary_key=True, comment="履歴ID (PK)")
    user_id = Column(VARCHAR(255), ForeignKey('Users.user_id'), comment="管理ID (FK)")
    d_number = Column(VARCHAR(100), comment="D番号")
    start_date = Column(DATE, comment="開始日")
    end_date = Column(DATE, nullable=True, comment="終了日")
    
    # リレーションシップ
    user = relationship('User', back_populates='d_number_history')

class SystemID(TimestampMixin, db.Model):
    __tablename__ = 'System_IDs'
    system_id_record_id = Column(Integer, primary_key=True, comment="レコードID (PK)")
    user_id = Column(VARCHAR(255), ForeignKey('Users.user_id'), comment="管理ID (FK)")
    system_id = Column(VARCHAR(255), comment="情報システムID")
    is_active = Column(BOOLEAN, default=True, comment="有効フラグ")
    
    # リレーションシップ
    user = relationship('User', back_populates='system_ids')

class Card(TimestampMixin, db.Model):
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

class Department(TimestampMixin, db.Model):
    __tablename__ = 'Departments'
    department_id = Column(Integer, primary_key=True, comment="部署ID (PK)")
    department_extension_number = Column(VARCHAR(50), comment="部署の内線")
    create_date = Column(DATE, comment="設立日")
    
    # リレーションシップ
    name_history = relationship('DepartmentNameHistory', back_populates='department')
    users = relationship('UserDepartment', back_populates='department')

class DepartmentNameHistory(TimestampMixin, db.Model):
    __tablename__ = 'Department_Name_History'
    dept_name_history_id = Column(Integer, primary_key=True, comment="履歴ID (PK)")
    department_id = Column(Integer, ForeignKey('Departments.department_id'), comment="部署ID (FK)")
    department_name = Column(VARCHAR(255), comment="部署名")
    start_date = Column(DATE, comment="開始日")
    end_date = Column(DATE, nullable=True, comment="終了日")
    
    # リレーションシップ
    department = relationship('Department', back_populates='name_history')

# 中間テーブル (Users と Departments)
class UserDepartment(TimestampMixin, db.Model):
    __tablename__ = 'User_Departments'
    user_id = Column(VARCHAR(255), ForeignKey('Users.user_id'), primary_key=True, comment="管理ID (PK, FK)")
    department_id = Column(Integer, ForeignKey('Departments.department_id'), primary_key=True, comment="部署ID (PK, FK)")
    
    # リレーショングループ
    user = relationship('User', back_populates='departments')
    department = relationship('Department', back_populates='users')

# --------------------
# 4. システム連携
# --------------------

class ExternalSystem(TimestampMixin, db.Model):
    __tablename__ = 'External_Systems'
    system_id = Column(Integer, primary_key=True, comment="システムID (PK)")
    system_name = Column(VARCHAR(255), comment="外部システム名")
    start_date = Column(DATE, comment="開始日")
    end_date = Column(DATE, nullable=True, comment="終了日")
    
    # リレーションシップ
    export_settings = relationship('ExternalSystemExport', back_populates='system')

class ExternalSystemExport(TimestampMixin, db.Model):
    __tablename__ = 'External_System_Exports'
    export_setting_id = Column(Integer, primary_key=True, comment="設定ID (PK)")
    system_id = Column(Integer, ForeignKey('External_Systems.system_id'), comment="システムID (FK)")
    table_name = Column(VARCHAR(255), comment="対象テーブル名")
    column_name = Column(VARCHAR(255), comment="対象カラム名")
    
    # リレーションシップ
    system = relationship('ExternalSystem', back_populates='export_settings')