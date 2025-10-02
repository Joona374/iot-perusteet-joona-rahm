const express = require("express");
const sqlite3 = require("sqlite3");
const app = express();
app.use(express.json());
const port = 3000;

const db = new sqlite3.Database("./database.db", (err) => {
  if (err) {
    console.error("Could not connect to database", err);
  } else console.log("Connected to database");
});

db.run(`CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE)
    `);

// GET endpoint
app.get("/api/sensor", (req, res) => {
  res.json({
    temperature: 22.5,
    humidity: 55,
    status: "OK",
  });
});

app.get("/api/users", (req, res) => {
  db.all(`SELECT * FROM users`, [], (err, rows) => {
    if (err) return res.status(500).json({ error: err.message });
    res.json(rows);
  });
});

app.post("/api/users", (req, res) => {
  const { name, email } = req.body;
  db.run(
    `INSERT INTO users (name, email) VALUES (?, ?)`,
    [name, email],
    function (err) {
      if (err) return res.status(400).json({ error: err.message });
      res.status(201).json({ id: this.lastID, name, email });
    }
  );
});

app.listen(port, () => {
  console.log(`Server running at http://localhost:${port}`);
});
