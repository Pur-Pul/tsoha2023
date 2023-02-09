from werkzeug.security import check_password_hash
class InvalidUserNameException(Exception):
    def __init__(self, username, message="Username is not valid"):
        self.username = username
        self.message = message
        super().__init__(self.message)
        

class UserService:
    def __init__(self, database = None):
        if database is None:
            from src.db import db
            self._db = db
        else:
            self._db = database

    def clear_user(self, user_id):
        self._db.session.execute(
            """
            DELETE FROM users
            WHERE id=:id
            """, {
                "id": user_id
            }
        )
        self._db.session.commit()

    def _fetch_user(self, username):
        user = self._db.session.execute(
            """
            SELECT id, password
            FROM users 
            WHERE username=:username;
            """, {
                "username":username
            }
        ).fetchone()
        return user

    def validate_credentials(self, username, password):
        user = self._fetch_user(username)
        return user and check_password_hash(user.password, password)

    def register(self, username, hash_value):
        id = self._db.session.execute(
            """
            INSERT INTO users (
                username,
                password
            ) SELECT :username, :password
            WHERE NOT EXISTS (SELECT username FROM users WHERE username=:username)
            RETURNING id;
            """, {
                "username":username,
                "password":hash_value
            }
        ).fetchone()
        if id is None:
            raise InvalidUserNameException(username, "Username is already taken")
        else:
            return id

    def get_id(self, username):
        user_id = self._db.session.execute(
            "SELECT id FROM users WHERE username=:username;",
            {"username":username}
        ).fetchone()
        if user_id:
            return user_id[0]
        return None
