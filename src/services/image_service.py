import json
class ImageService:
    def __init__(self, database = None):
        if database is None:
            from db import db
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
            ) AND user_id=:user_id
            ORDER BY order_number
            """,{
                "user_id":user_id,
            }
        ).fetchall()
        actions = []
        last_order_number = 0
        new_order_number = 0
        for action in distinct_actions:
            actions.append(
                action._asdict()
            )
            if last_order_number < action.order_number:
                new_order_number+=1
                last_order_number = action.order_number
            actions[-1]["order_number"] = new_order_number
        return json.dumps(actions, indent=2)

    def save_as_image(self, user_id):
        image = self._convert_to_image(user_id)

        self._db.session.execute(
            """
            INSERT INTO images (
                user_id,
                data
            ) VALUES (
                :user_id,
                :data
            )
            """, {
                "user_id":user_id,
                "data":image
            }
        )
        self._db.session.commit()

    def get_image(self, image_id):
        image_dict = self._db.session.execute(
            """
            SELECT image_id, data
            FROM images
            WHERE image_id=:image_id
            """, {
                "image_id": image_id
            }
        ).fetchone()
        return image_dict._asdict()

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

    def get_user_images(self, user_id):
        result = self._db.session.execute(
            """
            SELECT image_id, data
            FROM images
            WHERE user_id=:user_id
            ORDER BY image_id
            """, {
                "user_id": user_id
            }
        ).fetchall()
        images = {}
        for image in result:
            images[image.image_id] = image.data
        return images
