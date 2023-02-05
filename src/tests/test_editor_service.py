import unittest
import psycopg2
import psycopg2.extras
import testing.postgresql
from unittest.mock import Mock
from src.services import EditorService

class TestEditorService(unittest.TestCase):
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
        self.editor_service = EditorService(self.mock_db)

    def tearDown(self):
        self.cur.close()
        self.db.close()
        self.postgresql.stop()

    def test_color_pixels(self):
        pixels = [(1,2),(3,4),(5,6),(7,8)]
        color = "white"
        self.editor_service.color_pixels(pixels, color, 1)
        self.cur.execute(
        """
        SELECT *
        FROM editors
        """
        )
        result = self.cur.fetchall()
        print(result)
        for i, row in enumerate(result):
            self.assertEqual(row.row_number, pixels[i][0])
            self.assertEqual(row.col_number, pixels[i][1])
            self.assertEqual(row.color, color)
            self.assertEqual(row.user_id, 1)
            self.assertEqual(row.order_number, 0)
    
    def test_get_actions(self):
        sql = """
            INSERT INTO editors (
                user_id,
                order_number,
                row_number,
                col_number,
                color
            ) VALUES (
                %(user_id)s,
                %(order_number)s,
                %(row_number)s,
                %(col_number)s,
                %(color)s
            )
        """
        actions = [
            {
                "user_id": 1,
                "order_number":0,
                "row_number":1,
                "col_number":2,
                "color":"white"
            }, {
                "user_id": 1,
                "order_number":1,
                "row_number":3,
                "col_number":4,
                "color":"black"
            }, {
                "user_id": 2,
                "order_number":1,
                "row_number":5,
                "col_number":6,
                "color":"black" 
            }
        ]
        for action in actions:
            self.cur.execute(sql, action)
            action.pop("user_id")
        result = self.editor_service.get_actions(1)
        self.assertEqual(len(result), 2)
        
        for i, row in enumerate(result):
            self.assertEqual(row, tuple(actions[i].values()))
