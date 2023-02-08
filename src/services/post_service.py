from datetime import datetime, timezone
class PostService:
    def __init__(self, database = None):
        if database is None:
            from src.db import db
            self._db = db
        else:
            self._db = database

    def make_post(self, image_id, title):
        self._db.session.execute(
            """
            INSERT INTO posts (
                image_id,
                title
            )
            VALUES (
                :image_id,
                :title
            )
            """, {
                "image_id":image_id,
                "title":title
            }
        )
        self._db.session.commit()

    def get_posts(self, option):
        sql = {
            "new" : """
            SELECT id, image_id, title, time
            FROM posts
            ORDER BY time DESC
            """,
            "old" : """
            SELECT id, image_id, title, time
            FROM posts
            ORDER BY time
            """,
            "popular" : """
            
            """
        }
        posts = self._db.session.execute(sql[option]).fetchall()
        return posts

    def clear_post(self, post_id):
        self._db.session.execute(
            """
            DELETE FROM posts
            WHERE id=:id
            """, {
                "id":post_id
            }
        )
        self._db.session.commit()
