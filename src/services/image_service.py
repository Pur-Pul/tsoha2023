from flask_sqlalchemy import SQLAlchemy


class ImageService:
    def __init__(self, database = None):
        if database is None:
            from src.db import db
            self._db = db
        else:
            self._db = database

    def clear_image(self, image_id):
        self._db.session.execute(
            """
            DELETE FROM images
            WHERE image_id=:image_id
            """, {
                "image_id": image_id
            }
        )
        self._db.session.commit()

    def _convert_to_image(self, user_id):
        distinct_actions = self._db.session.execute(
            """
            SELECT order_number, row_number, col_number, color
            FROM editors
            WHERE (order_number, row_number, col_number) in (
                SELECT MAX(order_number), row_number, col_number
                FROM editors
                WHERE user_id=:user_id
                GROUP BY row_number, col_number
            )
            ORDER BY order_number
            """,{
                "user_id":user_id,
            }
        ).fetchall()
        return distinct_actions

    def save_as_image(self, user_id):
        image = self._convert_to_image(user_id)
        image_id = self._db.session.execute(
            """
            SELECT max(image_id)
            FROM images
            """
        ).fetchone()
        if image_id[0] is not None:
            image_id = image_id[0]+1
        else:
            image_id = 0

        last_order_number = 0
        new_order_number = 0
        for pixel in image:
            if last_order_number < pixel.order_number:
                new_order_number+=1
                last_order_number+=1
            self._db.session.execute(
                """
                INSERT INTO images (
                    image_id,
                    user_id,
                    row_number,
                    col_number,
                    color,
                    order_number
                ) VALUES (
                    :image_id,
                    :user_id,
                    :row_number,
                    :col_number,
                    :color,
                    :order_number
                )
                """, {
                    "image_id":image_id,
                    "user_id":user_id,
                    "row_number":pixel.row_number,
                    "col_number":pixel.col_number,
                    "color":pixel.color,
                    "order_number":new_order_number
                }
            )
        self._db.session.commit()

    def get_image(self, image_id):
        image = self._db.session.execute(
            """
            SELECT order_number, row_number, col_number, color
            FROM images
            WHERE image_id=:image_id
            ORDER BY order_number
            """, {
                "image_id": image_id
            }
        ).fetchall()
        image_dict = {"id" : image_id}
        for i, row in enumerate(image):
            image_dict[i] = tuple(row)
        return image_dict

    def get_image_ids(self, user_id):
        image_ids = self._db.session.execute(
            """
            SELECT DISTINCT image_id
            FROM images
            WHERE user_id=:user_id
            ORDER BY image_id
            """, {
                "user_id": user_id
            }
        ).fetchall()
        image_ids = [row[0] for row in image_ids]
        return list(image_ids)

    def get_image_owner_id(self, image_id):
        user_id = self._db.session.execute(
            """
            SELECT DISTINCT user_id
            FROM images
            WHERE image_id=:image_id
            """, {
                "image_id": image_id
            }
        ).fetchone()
        if user_id:
            return user_id[0]
        return None
