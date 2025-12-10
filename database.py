import os
import asyncpg
import asyncio
import json
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

class Database:
    def __init__(self):
        self.pool = None

    async def connect(self):
        if not self.pool:
            if not DATABASE_URL:
                raise ValueError("DATABASE_URL not found in environment variables")
            try:
                self.pool = await asyncpg.create_pool(DATABASE_URL)
                print("--- Database Connected ---")
            except Exception as e:
                print(f"--- Database Connection Failed: {e} ---")
                raise e

    async def close(self):
        if self.pool:
            await self.pool.close()

    async def init_db(self):
        """Initialize database schema"""
        await self.connect()
        async with self.pool.acquire() as conn:
            # Table: Sessions
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS sessions (
                    session_id TEXT PRIMARY KEY,
                    user_id TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_active TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    metadata JSONB DEFAULT '{}'::jsonb
                );
            """)

            # Table: Messages (History)
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS messages (
                    id SERIAL PRIMARY KEY,
                    session_id TEXT REFERENCES sessions(session_id),
                    role TEXT NOT NULL,
                    content TEXT NOT NULL,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    metadata JSONB DEFAULT '{}'::jsonb
                );
            """)

            # Table: Corrections (Global or User-specific)
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS corrections (
                    id SERIAL PRIMARY KEY,
                    query_hash TEXT UNIQUE, 
                    correction TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)

            print("--- Database Schema Initialized (Sessions & Corrections) ---")

    async def get_session_history(self, session_id: str):
        async with self.pool.acquire() as conn:
            # Check if session exists
            session = await conn.fetchrow("SELECT * FROM sessions WHERE session_id = $1", session_id)
            if not session:
                return []
            
            rows = await conn.fetch("""
                SELECT role, content FROM messages 
                WHERE session_id = $1 
                ORDER BY id ASC
            """, session_id)
            return [{"role": r["role"], "content": r["content"]} for r in rows]

    async def create_session_if_not_exists(self, session_id: str, user_id: str = "guest"):
        async with self.pool.acquire() as conn:
            await conn.execute("""
                INSERT INTO sessions (session_id, user_id) 
                VALUES ($1, $2) 
                ON CONFLICT (session_id) DO NOTHING
            """, session_id, user_id)

    async def save_message(self, session_id: str, role: str, content: str):
        async with self.pool.acquire() as conn:
            await conn.execute("""
                INSERT INTO messages (session_id, role, content) 
                VALUES ($1, $2, $3)
            """, session_id, role, content)
            
            await conn.execute("""
                UPDATE sessions SET last_active = CURRENT_TIMESTAMP WHERE session_id = $1
            """, session_id)

    async def add_correction(self, query_key: str, correction: str):
        async with self.pool.acquire() as conn:
            await conn.execute("""
                INSERT INTO corrections (query_hash, correction) 
                VALUES ($1, $2)
                ON CONFLICT (query_hash) 
                DO UPDATE SET correction = EXCLUDED.correction
            """, query_key, correction)

    async def get_all_corrections(self):
        async with self.pool.acquire() as conn:
            rows = await conn.fetch("SELECT query_hash, correction FROM corrections")
            return {r["query_hash"]: r["correction"] for r in rows}

# Singleton instance
db = Database()
