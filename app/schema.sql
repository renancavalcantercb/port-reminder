CREATE TABLE timers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                channel_id TEXT NOT NULL,
                ship_name TEXT NOT NULL,
                timer_end TIMESTAMP NOT NULL,
                notified BOOLEAN DEFAULT FALSE
            );
CREATE TABLE sqlite_sequence(name,seq);
