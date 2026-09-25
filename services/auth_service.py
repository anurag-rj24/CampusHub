from database.connection import create_connection
from models.user import User
from utils.password import verify_password


class AuthService:

    def login(self, email, password):

        connection = create_connection()
        cursor = connection.cursor(dictionary=True)

        query = """
            SELECT
                user_id,
                first_name,
                middle_name,
                last_name,
                email,
                phone,
                password_hash,
                role,
                status,
                created_at,
                last_login
            FROM users
            WHERE email = %s
              AND status = 'ACTIVE'
        """

        cursor.execute(query, (email,))

        user_data = cursor.fetchone()

        if user_data is None:
            cursor.close()
            connection.close()
            return None

        if not verify_password(
            password,
            user_data["password_hash"]
        ):
            cursor.close()
            connection.close()
            return None

        update_query = """
            UPDATE users
            SET last_login = CURRENT_TIMESTAMP
            WHERE user_id = %s
        """

        cursor.execute(update_query, (user_data["user_id"],))
        connection.commit()

        cursor.close()
        connection.close()

        return User(
            user_id=user_data["user_id"],
            first_name=user_data["first_name"],
            middle_name=user_data["middle_name"],
            last_name=user_data["last_name"],
            email=user_data["email"],
            phone=user_data["phone"],
            password_hash=user_data["password_hash"],
            role=user_data["role"],
            status=user_data["status"],
            created_at=user_data["created_at"],
            last_login=user_data["last_login"]
        )