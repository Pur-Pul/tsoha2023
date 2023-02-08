class ReplyService:
    def __init__(self, db):
        self._db = db

    def _create_main_reply(self) -> int:
        id = self._db.session.execute(
            """
            INSERT INTO replies (
                reply_id,
                user_id,
                content
            ) VALUES (
                :reply_id,
                :user_id,
                :content
            )
            RETURNING id
            """, {
                "reply_id": -1,
                "user_id": -1,
                "content": ""
            }
            
        ).fetchone()[0]
        return id

    def create_reply_section(self, post_id):
        main_reply_id = self._create_main_reply
        self._db.session.execute(
            """
            INSERT INTO reply_section (
                post_id,
                reply_id
                ) VALUES (
                    :post_id,
                    :reply_id
                )
            """, {
                "post_id": post_id,
                "reply_id": main_reply_id
            }
        )
        self._db.session.commit()
    
    def create_reply(self, reply_id, user_id, content):
        pass

    def create_vote(self, reply_id, user_id):
        pass

    def create_post_reply(self, post_id, user_id, content):
        self._db(
            """
            INSERT INTO replies (
                reply_id,
                user_id,
                content
            )
            SELECT reply_id, :user_id, :content 
            FROM reply_section
            WHERE post_id=:post_id
            """, {
                "user_id":user_id,
                "content":content
            }
        )
        self._db.session.commit()

    def get_post_replies(self, post_id):
        pass