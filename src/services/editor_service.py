from flask_sqlalchemy import SQLAlchemy

class EditorService:
    def __init__(self, db : SQLAlchemy):
        self._db = db
        self._action_counter = 0
    
    def _add_pixel(self, row : int, column : int, color : str, user_id : int):
        self._db.session.execute(
            """INSERT INTO editors (
                user_id,
                order_number,
                row_number,
                col_number,
                color
            ) VALUES (
                :user_id,
                :order_number,
                :row,
                :col,
                :color
            )""", {
                "user_id":user_id,
                "order_number":self._action_counter,
                "row":row,
                "col":column,
                "color":color
            }
        )
        self._db.session.commit()

    def color_pixels(self, pixels : list, color : str, user_id : int):
        result = self._db.session.execute(
            """
            SELECT order_number
            FROM editors 
            WHERE user_id=:user_id
            ORDER BY order_number DESC
            """,{
                "user_id":user_id,
            }
        ).fetchone()
        if result:
            self._action_counter = result[0]+1
        for pixel in pixels:
            self._add_pixel(*pixel, color, user_id)
    
    def get_actions(self, user_id) -> list:
        actions = self._db.session.execute(
            """
            SELECT order_number, row_number, col_number, color
            FROM editors 
            WHERE user_id=:user_id
            ORDER BY order_number
            """,{
                "user_id":user_id,
            }
        ).fetchall()
        actions = [tuple(row) for row in actions]
        return list(actions)

    def clear_actions(self, user_id):
        self._db.session.execute(
            """
            DELETE FROM editors
            WHERE user_id=:user_id
            """,{
                "user_id":user_id
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
