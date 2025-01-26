import aiosqlite
import os

DATABASE_PATH = "timers.db"


async def init_db():
    schema_path = os.path.join(os.path.dirname(__file__), "schema.sql")
    async with aiosqlite.connect(DATABASE_PATH) as db:
        with open(schema_path, "r") as schema_file:
            schema = schema_file.read()
        await db.executescript(schema)
        await db.commit()


async def add_timer(user_id, channel_id, ship_name, timer_end):
    async with aiosqlite.connect(DATABASE_PATH) as db:
        await db.execute(
            """
            INSERT INTO timers (user_id, channel_id, ship_name, timer_end, notified)
            VALUES (?, ?, ?, ?, ?)
        """,
            (user_id, channel_id, ship_name, timer_end, False),
        )
        await db.commit()


async def get_active_timers(user_id):
    async with aiosqlite.connect(DATABASE_PATH) as db:
        rows = await db.execute_fetchall(
            """
            SELECT ship_name, timer_end
            FROM timers
            WHERE user_id = ? AND timer_end > datetime('now')
        """,
            (user_id,),
        )
        return rows


async def get_expired_timers(current_time):
    async with aiosqlite.connect(DATABASE_PATH) as db:
        rows = await db.execute_fetchall(
            """
            SELECT id, user_id, channel_id, ship_name
            FROM timers
            WHERE timer_end <= ? AND notified = FALSE
        """,
            (current_time,),
        )
        return rows


async def mark_timer_notified(timer_id):
    async with aiosqlite.connect(DATABASE_PATH) as db:
        await db.execute("UPDATE timers SET notified = TRUE WHERE id = ?", (timer_id,))
        await db.commit()


async def register_user(user_id, username):
    async with aiosqlite.connect(DATABASE_PATH) as db:
        existing = await db.execute_fetchall(
            """
            SELECT id FROM star_notifications WHERE user_id = ?
            """,
            (user_id,),
        )
        if existing:
            return f"{username} is already registered for star notifications!"

        await db.execute(
            """
            INSERT INTO star_notifications (user_id, username)
            VALUES (?, ?)
            """,
            (user_id, username),
        )
        await db.commit()
        return f"{username} has been registered for star notifications!"


async def get_registered_users():
    async with aiosqlite.connect(DATABASE_PATH) as db:
        rows = await db.execute_fetchall(
            """
            SELECT user_id, username
            FROM star_notifications
            """
        )
        return rows


async def delete_user(user_id):
    async with aiosqlite.connect(DATABASE_PATH) as db:
        cursor = await db.execute(
            "SELECT user_id FROM star_notifications WHERE user_id = ?", (user_id,)
        )
        user = await cursor.fetchone()

        if not user:
            return f"No user found with ID {user_id}."

        await db.execute("DELETE FROM star_notifications WHERE user_id = ?", (user_id,))
        await db.commit()

        return f"User with ID {user_id} has been deleted from notifications."


async def add_or_update_curse_counter(emoji, name):
    """
    Add a new emoji or update the curse word counter for an existing one.
    """
    async with aiosqlite.connect(DATABASE_PATH) as db:
        await db.execute(
            """
            INSERT INTO curse_word_counters (emoji, name, count)
            VALUES (?, ?, 1)
            ON CONFLICT(emoji) DO UPDATE SET count = count + 1
            """,
            (emoji, name),
        )
        await db.commit()

async def undo_last_curse_counter():
    """
    Undo the last curse word counter based on the most recent created_at timestamp.
    """
    async with aiosqlite.connect(DATABASE_PATH) as db:
        cursor = await db.execute(
            """
            SELECT emoji, name, count
            FROM curse_word_counters
            WHERE count > 0
            ORDER BY created_at DESC
            LIMIT 1
            """
        )
        last_entry = await cursor.fetchone()

        if last_entry:
            emoji, name, count = last_entry
            if count > 0:
                await db.execute(
                    """
                    UPDATE curse_word_counters
                    SET count = count - 1
                    WHERE emoji = ?
                    """,
                    (emoji,),
                )
                await db.commit()
                return emoji, name

        return None


async def get_curse_counters():
    """
    Retrieve all curse word counters from the database, sorted by count.
    """
    async with aiosqlite.connect(DATABASE_PATH) as db:
        rows = await db.execute_fetchall(
            """
            SELECT emoji, name, count
            FROM curse_word_counters
            ORDER BY count DESC
            """
        )
        return rows
