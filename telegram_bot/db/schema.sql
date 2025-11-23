CREATE TABLE IF NOT EXISTS mood (
    date TEXT PRIMARY KEY,
    value INTEGER CHECK(value IN (0, 1))
);

CREATE TABLE IF NOT EXISTS mileage (
    date TEXT PRIMARY KEY,
    value REAL CHECK(value >= 0)
);

CREATE TABLE IF NOT EXISTS expenses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date TEXT NOT NULL,
    category TEXT NOT NULL,
    amount REAL CHECK(amount >= 0)
);

CREATE TABLE IF NOT EXISTS salary (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date TEXT NOT NULL,
    amount REAL CHECK(amount >= 0)
);
