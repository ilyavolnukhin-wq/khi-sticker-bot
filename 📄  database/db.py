import asyncpg
from config import DATABASE_URL

class Database:
    def __init__(self):
        self.pool = None
    
    async def create_pool(self):
        try:
            self.pool = await asyncpg.create_pool(
                dsn=DATABASE_URL,
                ssl={'require': True},
                min_size=2,
                max_size=10
            )
            print("✅ База данных подключена (Neon)")
        except Exception as e:
            print(f"❌ Ошибка подключения к БД: {e}")
            raise
    
    async def init_tables(self):
        async with self.pool.acquire() as conn:
            tables = [
                '''CREATE TABLE IF NOT EXISTS albums (
                    id SERIAL PRIMARY KEY,
                    name VARCHAR(100) NOT NULL,
                    total_numeric INTEGER,
                    total_letter INTEGER,
                    is_active BOOLEAN DEFAULT true,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )''',
                '''CREATE TABLE IF NOT EXISTS stickers (
                    id SERIAL PRIMARY KEY,
                    album_id INTEGER REFERENCES albums(id),
                    number VARCHAR(10),
                    name VARCHAR(200),
                    team VARCHAR(100),
                    category VARCHAR(50),
                    section VARCHAR(50),
                    UNIQUE(album_id, number)
                )''',
                '''CREATE TABLE IF NOT EXISTS users (
                    id SERIAL PRIMARY KEY,
                    telegram_id BIGINT UNIQUE NOT NULL,
                    username VARCHAR(100),
                    album_id INTEGER REFERENCES albums(id),
                    joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )''',
                '''CREATE TABLE IF NOT EXISTS user_stickers (
                    id SERIAL PRIMARY KEY,
                    user_id INTEGER REFERENCES users(id),
                    sticker_id INTEGER REFERENCES stickers(id),
                    status VARCHAR(20) DEFAULT 'have',
                    is_tradeable BOOLEAN DEFAULT false,
                    added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(user_id, sticker_id)
                )''',
                '''CREATE TABLE IF NOT EXISTS trades (
                    id SERIAL PRIMARY KEY,
                    from_user_id INTEGER REFERENCES users(id),
                    to_user_id INTEGER REFERENCES users(id),
                    offered_sticker_ids INTEGER[],
                    wanted_sticker_ids INTEGER[],
                    status VARCHAR(20) DEFAULT 'pending',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )'''
            ]
            for query in tables:
                await conn.execute(query)
            print("✅ Таблицы созданы")
    
    async def close(self):
        if self.pool:
            await self.pool.close()

db = Database()

