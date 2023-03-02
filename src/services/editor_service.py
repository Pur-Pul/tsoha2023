class EditorService:
    def __init__(self, database = None):
        if database is None:
            from db import db
            self._db = db
        else:
            self._db = database

    def _add_pixel(self, row : int, column : int, color : str, user_id : int, action_counter : int):
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
                "order_number":action_counter,
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
            action_counter = result[0]+1
        else:
            action_counter = 0
        for pixel in pixels:
            self._add_pixel(*pixel, color, user_id, action_counter)

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

    def undo_action(self, user_id):
        old_action = self._db.session.execute(
            """
            DELETE FROM editors
            WHERE user_id=:user_id
            AND order_number=(
                                SELECT MAX(order_number)
                                FROM editors
                                WHERE user_id=:user_id
                            )
            RETURNING *;
            """, {"user_id":user_id}
        ).fetchall()
        self._db.session.commit()
        return_val = {"old_action":[], "new_action":[]}

        for pixel in old_action:
            new = self._db.session.execute(
                """
                SELECT col_number, row_number, color FROM editors
                WHERE user_id=:user_id
                AND col_number=:col_number
                AND row_number=:row_number
                AND order_number=(
                                    SELECT MAX(order_number)
                                    FROM editors
                                    WHERE user_id=:user_id
                                    AND col_number=:col_number
                                    AND row_number=:row_number
                )
                """, {
                    "user_id":user_id,
                    "col_number":pixel.col_number,
                    "row_number":pixel.row_number
                }
            ).fetchone()
            if new is not None:
                new = new._asdict()
            else:
                new = {"color": None, "col_number":pixel.col_number, "row_number": pixel.row_number}
            return_val["new_action"].append(new)
            return_val["old_action"].append(pixel._asdict())

        return return_val
