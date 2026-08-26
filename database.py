import sqlite3

DB_NAME = "game.db"

def get_connection():
    return sqlite3.connect(DB_NAME)

def init_db():
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS players (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            telegram_id INTEGER UNIQUE NOT NULL,
            name TEXT,
            gender TEXT,
            level INTEGER DEFAULT 1,
            xp INTEGER DEFAULT 0,
            coins INTEGER DEFAULT 100,
            day INTEGER DEFAULT 1,
            health INTEGER DEFAULT 100,
            energy INTEGER DEFAULT 100,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    connection.commit()
    connection.close()

def get_player(telegram_id):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        "SELECT * FROM players WHERE telegram_id = ?",
        (telegram_id,)
    )

    player = cursor.fetchone()

    connection.close()

    return player

def create_player(telegram_id):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        INSERT INTO players (telegram_id)
        VALUES (?)
        """,
        (telegram_id,)
    )

    connection.commit()
    connection.close()
def update_player_name(telegram_id, name):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        UPDATE players
        SET name = ?
        WHERE telegram_id = ?
        """,
        (name, telegram_id)
    )

    connection.commit()
    connection.close()
def update_player_gender(telegram_id, gender):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        UPDATE players
        SET gender = ?
        WHERE telegram_id = ?
        """,
        (gender, telegram_id)
    )

    connection.commit()
    connection.close()