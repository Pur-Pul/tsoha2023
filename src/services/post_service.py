from datetime import datetime, timezone
class PostService:
    def __init__(self, database = None):
        if database is None:
            from db import db
            self._db = db
        else:
            self._db = database

    def make_post(self, image_id, title):
        id = self._db.session.execute(
            """
            INSERT INTO posts (
                image_id,
                title
            )
            VALUES (
                :image_id,
                :title
            )
            RETURNING id
            """, {
                "image_id":image_id,
                "title":title
            }
        ).fetchone()[0]
        return id

    def get_posts(self, option):
        sql = """
            SELECT posts.id, posts.image_id, posts.title, posts.time, COALESCE(SUM(votes.points),0) AS votes
            FROM posts
            JOIN reply_section
            ON posts.id = reply_section.post_id
            LEFT JOIN votes
            ON reply_section.reply_id = votes.reply_id
            GROUP BY posts.id 
            """
        sort_option = {
            "new" : "ORDER BY posts.time DESC",
            "old" : "ORDER BY posts.time",
            "popular" : "ORDER BY votes DESC"
        }
        posts = self._db.session.execute(sql+sort_option[option]).fetchall()
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
    
    def get_post(self, post_id):
        val = self._db.session.execute(
            """
            SELECT posts.id, posts.image_id, posts.title, posts.time, COALESCE(SUM(votes.points),0) AS votes, users.username
            FROM posts
            JOIN reply_section
            ON posts.id = reply_section.post_id
            LEFT JOIN votes
            ON reply_section.reply_id = votes.reply_id
            JOIN images
            ON posts.image_id = images.image_id
            JOIN users
            ON images.user_id = users.id
            WHERE posts.id=:post_id
            GROUP BY posts.id, users.username
            """, {
                "post_id":post_id
            }
        ).fetchone()
        print(val.time)
        return val
