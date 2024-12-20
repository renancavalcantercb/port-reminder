import aiosqlite

DATABASE_PATH = "timers.db"


async def init_db():
    async with aiosqlite.connect(DATABASE_PATH) as db:
        await db.execute(
            """
            CREATE TABLE IF NOT EXISTS timers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                channel_id TEXT NOT NULL,
                ship_name TEXT NOT NULL,
                timer_end TIMESTAMP NOT NULL,
                notified BOOLEAN DEFAULT FALSE
            )
        """
        )
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
