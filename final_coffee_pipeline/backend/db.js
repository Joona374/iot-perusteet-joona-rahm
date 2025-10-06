import sqlite3 from "sqlite3";
import { open } from "sqlite";

// open() returns a promise
export async function initDb() {
  const db = await open({
    filename: "./coffee_data.db",
    driver: sqlite3.Database,
  });

  await db.exec(`
    CREATE TABLE IF NOT EXISTS temperatures (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
      value REAL
    );
  `);

  console.log("📦 SQLite ready (coffee_data.db)");
  return db;
}
