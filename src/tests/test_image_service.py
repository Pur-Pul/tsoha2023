import unittest
import psycopg2
import psycopg2.extras
import testing.postgresql
import json
from unittest.mock import Mock
from src.services import ImageService, EditorService

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
        self.image_service = ImageService(self.mock_db)
        self.editor_service = EditorService(self.mock_db)

    def tearDown(self):
        self.cur.close()
        self.db.close()
        self.postgresql.stop()
    
    def test_clear_image(self):
        sql = """
            INSERT INTO images (
                user_id,
                data
            ) VALUES (
                %(user_id)s,
                %(data)s
            )
        """
        self.cur.execute(
            sql, {
                "user_id": 1,
                "data": json.dumps({"test_data" : "data"}, indent=2)
            }
        )
        self.cur.execute(
            sql, {
                "user_id": 2,
                "data": json.dumps({"test_data" : "data"}, indent=2)
            }
        )
        self.image_service.clear_image(1)
        self.cur.execute(
            """
                SELECT *
                FROM images
                WHERE user_id=1 
            """
        )
        result = self.cur.fetchone()
        self.assertIsNone(result)
        self.cur.execute(
            """
                SELECT *
                FROM images
                WHERE user_id=2
            """
        )
        result = self.cur.fetchone()
        self.assertIsNotNone(result)
    
    def test_save_as_image_saves_editor_data_as_a_stringified_list_of_dicts(self):
        pixels=[(1,2),(3,4),(5,6),(7,8)]
        self.editor_service.color_pixels(pixels, "white", 1)
        self.image_service.save_as_image(1)

        self.cur.execute(
            """
                SELECT data
                FROM images
                WHERE user_id=1
            """
        )
        result = self.cur.fetchone()
        self.assertEqual(type(result.data[0]), dict)
        self.assertEqual(len(result.data[0]), 4)
        self.assertEqual(len(result.data), 4)
    
    def test_get_image_returns_image_as_a_dict(self):
        data = [{"testdata":"data"}]
        json_data=json.dumps(data, indent=2)
        self.cur.execute(
            """
                INSERT INTO images (
                    user_id,
                    data
                ) VALUES (
                    %(user_id)s,
                    %(data)s
                )
            """, {
                "user_id": 1,
                "data": json_data
            }
        )
        res = self.image_service.get_image(1)
        self.assertEqual(res["image_id"], 1)
        self.assertEqual(res["data"], data)
    
    def test_get_image_ids(self):
        data = [{"testdata":"data"}]
        images = [json.dumps(data, indent=2), json.dumps(data, indent=2), json.dumps(data, indent=2)]
        sql = """
            INSERT INTO images (
                user_id,
                data
            ) VALUES (
                %(user_id)s,
                %(data)s
            )
        """
        self.cur.execute(
            sql, {
                "user_id": 2,
                "data": images[0]
            }
        )
        for image in images:
            self.cur.execute(
                sql, {
                    "user_id": 1,
                    "data": image
                }
            )
        res = self.image_service.get_image_ids(1)
        self.assertEqual(len(res), len(images))
        self.assertEqual(res, [2,3,4])
    
    def test_get_image_owner_id(self):
        self.assertEqual(self.image_service.get_image_owner_id(1), None)
        data = [{"testdata":"data"}]
        images = [json.dumps(data, indent=2), json.dumps(data, indent=2)]
        sql = """
            INSERT INTO images (
                user_id,
                data
            ) VALUES (
                %(user_id)s,
                %(data)s
            )
        """
        for i, image in enumerate(images):
            self.cur.execute(
                sql, {
                    "user_id": i,
                    "data": image
                }
            )
        
        self.assertEqual(self.image_service.get_image_owner_id(1), 0)
        self.assertEqual(self.image_service.get_image_owner_id(2), 1)
    
    def test_get_user_images(self):
        data = [{"testdata":"data"}]
        images = [json.dumps(data, indent=2), json.dumps(data, indent=2), json.dumps(data, indent=2)]
        sql = """
            INSERT INTO images (
                user_id,
                data
            ) VALUES (
                %(user_id)s,
                %(data)s
            )
        """
        self.cur.execute(
            sql, {
                "user_id": 2,
                "data": images[0]
            }
        )
        for image in images:
            self.cur.execute(
                sql, {
                    "user_id": 1,
                    "data": image
                }
            )

        res = self.image_service.get_user_images(1)
        self.assertEqual(type(res), dict)
        for id in res:
            self.assertEqual(res[id], data)