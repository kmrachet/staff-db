from flask import Blueprint, jsonify
# Models.py から必要なモデルをインポートします
from ..models import User, EmployeeNumberHistory, Departments, UserDepartment, Positions, DNumbers
from ..extensions import db

api_bp = Blueprint('api', __name__, url_prefix='/api')

@api_bp.route('/users/', methods=['GET'])
def get_users():
    """
    全職員の情報を取得するAPI
    """
    try:
        users = User.query.all()
        results = []
        
        for user in users:
            user_data = {
                "user_id": user.user_id,
                "name": user.name,
                
                # ▼ 各モデルから関連データを取得 (存在しない場合は None をセット)
                "d_id": None,
                "employee_number": None,
                "position_id": None,
                "position_name": None,
                "department_id": None,
                "department_name": None
            }

            # D番号 (DNumbers relationship)
            if user.d_numbers:
                # 最初の (またはアクティブな) D番号を取得
                user_data["d_id"] = user.d_numbers[0].d_number 

            # 職員番号・職位 (EmployeeNumberHistory relationship)
            if user.employee_number_history:
                latest_history = user.employee_number_history[0] 
                user_data["employee_number"] = latest_history.employee_number
                user_data["position_id"] = latest_history.position_id
                # 関連する Position モデルから職位名を取得
                if latest_history.position:
                     user_data["position_name"] = latest_history.position.position_name

            # 部署 (UserDepartment relationship)
            if user.departments:
                dept_assoc = user.departments[0]
                user_data["department_id"] = dept_assoc.department_id
                # 関連する Department モデルから部署名を取得
                if dept_assoc.department:
                    user_data["department_name"] = dept_assoc.department.department_name

            results.append(user_data)

        return jsonify(results), 200

    except Exception as e:
        print(f"Error in /api/users/: {e}") # サーバーログにエラーを出力
        return jsonify(error=str(e)), 500