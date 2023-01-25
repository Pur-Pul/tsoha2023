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
                :username,
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

    def color_pixels(self, pixels : list, color : str, user_id : int):
        for pixel in pixels:
            self._add_pixel(*pixel, color, user_id)
        self._action_counter += 1
    
    def get_actions(self, user_id) -> list:
        actions = self._db.session.execute(
            """
            SELECT row_number, col_number, color
            FROM editors 
            WHERE user_id=:user_id
            ORDER BY order_number
            """,{
                "user_id":user_id,
            }
        ).fetchall()
        return list(actions)
