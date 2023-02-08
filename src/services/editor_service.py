class EditorService:
    def __init__(self, database = None):
        if database is None:
            from src.db import db
            self._db = db
        else:
            self._db = database
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
        actions = [action._asdict() for action in actions]
        return actions

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
