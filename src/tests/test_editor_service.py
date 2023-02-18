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
        pixels = [[(1,2),(3,4),(5,6),(7,8)],[(9,10),(11,12),(13,14),(15,16)]]
        color = "white"
        self.editor_service.color_pixels(pixels[0], color, 1)
        self.editor_service.color_pixels([(17,18),(19,20)], color, 2)
        self.editor_service.color_pixels(pixels[1], color, 1)
        self.cur.execute(
        """
        SELECT *
        FROM editors
        WHERE user_id=1 AND order_number=0
        """
        )
        result = self.cur.fetchall()
        for i, row in enumerate(result):
            self.assertEqual(row.row_number, pixels[0][i][0])
            self.assertEqual(row.col_number, pixels[0][i][1])
            self.assertEqual(row.color, color)
        self.cur.execute(
        """
        SELECT *
        FROM editors
        WHERE user_id=1 AND order_number=1
        """
        )
        result = self.cur.fetchall()
        for i, row in enumerate(result):
            self.assertEqual(row.row_number, pixels[1][i][0])
            self.assertEqual(row.col_number, pixels[1][i][1])
            self.assertEqual(row.color, color)
    
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
            self.assertEqual(row, actions[i])
    
    def test_clear_actions(self):
        pixels = [[(1,2),(3,4),(5,6),(7,8)],[(9,10),(11,12),(13,14),(15,16)]]
        color = "white"
        self.editor_service.color_pixels(pixels[0], color, 1)
        self.editor_service.color_pixels(pixels[1], color, 2)
        self.editor_service.clear_actions(1)
        self.cur.execute(
        """
        SELECT *
        FROM editors
        WHERE user_id=1
        """
        )
        result = self.cur.fetchall()
        self.assertEqual(len(result),0)
        self.cur.execute(
        """
        SELECT *
        FROM editors
        WHERE user_id=2
        """
        )
        result = self.cur.fetchall()
        self.assertEqual(len(result),4)
    
    def test_undo_action_returns_no_actions_if_canvas_is_empty(self):
        pixels = [[(1,2),(3,4),(5,6),(7,8)],[(9,10),(11,12),(13,14),(15,16)]]
        color = "red"
        self.editor_service.color_pixels(pixels[1], color, 2)
        val = self.editor_service.undo_action(1)
        self.assertEqual(val["new_action"], [])
        self.assertEqual(val["old_action"], [])
    
    def test_undo_action_returns_old_action_and_clear_new_action_if_canvas_contains_one_stroke(self):
        pixels = [[(1,2),(3,4),(5,6),(7,8)],[(9,10),(11,12),(13,14),(15,16)]]
        color = "red"
        self.editor_service.color_pixels(pixels[0], color, 1)
        self.editor_service.color_pixels(pixels[1], color, 2)
        val = self.editor_service.undo_action(1)
        
        self.assertNotEqual(val["new_action"], [])
        for pixel in val["new_action"]:
            self.assertEqual(pixel["color"], None)
            self.assertTrue((pixel["row_number"],pixel["col_number"]) in pixels[0])
        
        self.assertTrue(len(val["old_action"]), len(pixels[0]))
        for pixel in val["old_action"]:
            self.assertEqual(pixel["color"], color)
            self.assertTrue((pixel["row_number"],pixel["col_number"]) in pixels[0])

    def test_undo_action_returns_old_action_and_new_action_if_canvas_contains_overlapping_strokes(self):
        pixels = [[(1,2),(3,4),(5,6),(7,8)],[(9,10),(11,12),(13,14),(15,16)]]
        color = "red"
        self.editor_service.color_pixels(pixels[0], color, 1)
        self.editor_service.color_pixels(pixels[0], "blue", 1)
        self.editor_service.color_pixels(pixels[1], color, 2)
        val = self.editor_service.undo_action(1)
        
        self.assertTrue(len(val["new_action"]), len(pixels[0]))
        for pixel in val["new_action"]:
            self.assertEqual(pixel["color"], color)
            self.assertTrue((pixel["row_number"],pixel["col_number"]) in pixels[0])
        
        self.assertTrue(len(val["old_action"]), len(pixels[0]))
        for pixel in val["old_action"]:
            self.assertEqual(pixel["color"], "blue")
            self.assertTrue((pixel["row_number"],pixel["col_number"]) in pixels[0])