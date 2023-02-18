import unittest
import psycopg2
import psycopg2.extras
import testing.postgresql
from unittest.mock import Mock
from src.services import UserService, InvalidUserNameException, InvalidPasswordException

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
        self.user_service.register(username, password)
        self.assertTrue(self.user_service.validate_credentials(username, password))
        self.assertFalse(self.user_service.validate_credentials(username, "wrong"))
    
    def test_register_valid_user(self):
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
        self.assertNotEqual(result.password, password)
    
    def test_register_too_short_username_throws_exception(self):
        username="t"
        password="testpassword"
        self.assertRaises(InvalidUserNameException, self.user_service.register, username, password)
        self.cur.execute(
        """
        SELECT username, password
        FROM users
        """
        )
        result = self.cur.fetchone()
        self.assertIsNone(result)
    
    def test_register_too_long_username_throws_exception(self):
        username="testusername"
        password="testpassword"
        self.assertRaises(InvalidUserNameException, self.user_service.register, username, password)
        self.cur.execute(
        """
        SELECT username, password
        FROM users
        """
        )
        result = self.cur.fetchone()
        self.assertIsNone(result)
    
    def test_register_too_short_password_throws_exception(self):
        username="testname"
        password="test"
        self.assertRaises(InvalidPasswordException, self.user_service.register, username, password)
        self.cur.execute(
        """
        SELECT username, password
        FROM users
        """
        )
        result = self.cur.fetchone()
        self.assertIsNone(result)
    
    def test_register_too_short_password_throws_exception(self):
        username="testname"
        password="testpasswordtestpassword"
        self.assertRaises(InvalidPasswordException, self.user_service.register, username, password)
        self.cur.execute(
        """
        SELECT username, password
        FROM users
        """
        )
        result = self.cur.fetchone()
        self.assertIsNone(result)
    
    def test_register_taken_username_throws_exception(self):
        username="testname"
        password="testpassword"
        self.user_service.register(username,password)
        self.assertRaises(InvalidUserNameException, self.user_service.register, username, password)
        self.cur.execute(
        """
        SELECT username, password
        FROM users
        """
        )
        result = self.cur.fetchall()
        self.assertEqual(len(result), 1)

    def test_get_id(self):
        username="testname"
        password="testpassword"
        self.assertIsNone(self.user_service.get_id(username))
        self.create_test_user(username, password)
        self.cur.execute(
        """
        SELECT id
        FROM users
        """
        )
        res = self.cur.fetchone()
        self.assertEqual(res.id, self.user_service.get_id(username))
