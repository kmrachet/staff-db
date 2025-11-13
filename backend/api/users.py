from flask import Blueprint, jsonify
from ..models import User, EmployeeNumberHistory, Departments, UserDepartment, Positions, DNumbers, Cards
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
                "d_id": None,
                "employee_number": None,
                "position_id": None,
                "position_name": None,
                "department_id": None,
                "department_name": None,
                # ▼ 追加
                "card_uid": None,
                "card_management_id": None
            }

            # D番号
            if user.d_numbers:
                user_data["d_id"] = user.d_numbers[0].d_number 

            # 職員番号・職位
            if user.employee_number_history:
                latest_history = user.employee_number_history[0] 
                user_data["employee_number"] = latest_history.employee_number
                user_data["position_id"] = latest_history.position_id
                if latest_history.position:
                     user_data["position_name"] = latest_history.position.position_name

            # 部署
            if user.departments:
                dept_assoc = user.departments[0]
                user_data["department_id"] = dept_assoc.department_id
                if dept_assoc.department:
                    user_data["department_name"] = dept_assoc.department.department_name

            # ▼ カード情報 (Cards relationship)
            if user.cards:
                # 1人のユーザーが複数のカードを持つ可能性もありますが、ここでは最初の1枚を表示します
                card = user.cards[0]
                user_data["card_uid"] = card.card_uid
                user_data["card_management_id"] = card.card_management_id

            results.append(user_data)

        return jsonify(results), 200

    except Exception as e:
        print(f"Error in /api/users/: {e}")
        return jsonify(error=str(e)), 500