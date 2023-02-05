import unittest
import psycopg2
import psycopg2.extras
import testing.postgresql
from unittest.mock import Mock
from werkzeug.security import generate_password_hash
from src.services import UserService

class TestUserService(unittest.TestCase):
    def setUp(self) -> None:
        self.postgresql = testing.postgresql.Postgresql()
        self.db = psycopg2.connect(**self.postgresql.dsn())
        self.cur = self.db.cursor(cursor_factory = psycopg2.extras.NamedTupleCursor)

        file = open("schema.sql")
        self.cur.execute(file.read())
        self.db.commit()

        self.mock_db = Mock()

        def execute(sql : str, values = None):
            if values is not None:
                for key in values:
                    sql = sql.replace(":"+key+"\n", "'"+str(values[key])+"'"+"\n")
                    sql = sql.replace(":"+key+",", "'"+str(values[key])+"'"+",")
                    sql = sql.replace(":"+key+")", "'"+str(values[key])+"'"+")")
                    sql = sql.replace(":"+key+";", "'"+str(values[key])+"'"+";")
            self.cur.execute(sql)
            return self.cur
        self.mock_db.session.execute.side_effect = execute
        def commit():
            self.db.commit()
        self.mock_db.session.commit.side_effect = commit
        self.user_service = UserService(self.mock_db)

    def tearDown(self):
        self.cur.close()
        self.db.close()
        self.postgresql.stop()
    
    def create_test_user(self, username, password):
        self.cur.execute(
        """
        INSERT INTO users (username, password) VALUES (%(username)s, %(password)s)
        """, {"username" : username, "password":password}
        )
        self.db.commit()

    def test_clear_user(self):
        self.create_test_user("testname", "testpassword")
        self.user_service.clear_user(1)
        self.cur.execute(
        """
        SELECT *
        FROM users
        """
        )
        empty = self.cur.fetchall()
        self.assertFalse(empty)
    
    def test_validate_credentials(self):
        username="testname"
        password="testpassword"
        hashed_password = generate_password_hash(password)
        self.create_test_user(username, hashed_password)
        self.assertTrue(self.user_service.validate_credentials(username, password))
    
    def test_register(self):
        username="testname"
        password="testpassword"
        self.user_service.register(username,password)
        self.cur.execute(
        """
        SELECT username, password
        FROM users
        """
        )
        result = self.cur.fetchone()
        self.assertEqual(result.username, username)
        self.assertEqual(result.password, password)
    
    def test_get_id(self):
        username="testname"
        password="testpassword"
        self.create_test_user(username, password)
        self.cur.execute(
        """
        SELECT id
        FROM users
        """
        )
        res = self.cur.fetchone()
        self.assertEqual(res.id, 1)
