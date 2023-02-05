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

    def get_posts(self):
        posts = self._db.session.execute(
            """
            SELECT id, image_id, title
            FROM posts
            """
        ).fetchall()
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
