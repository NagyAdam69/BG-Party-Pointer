DROP DATABASE IF EXISTS boardgames_db;

CREATE DATABASE IF NOT EXISTS boardgames_db
DEFAULT CHARACTER SET utf8mb4
COLLATE utf8mb4_hungarian_ci;

USE boardgames_db;

-- 1. Felhasználók táblája (A bejelentkezéshez és regisztrációhoz)
CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL
);

-- 2. Partik / Csoportok táblája (Javítva: user_id és is_closed hozzáadva)
CREATE TABLE parties (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,                          -- Összekötés a users táblával
    party_name VARCHAR(100) NOT NULL,
    is_closed TINYINT(1) NOT NULL DEFAULT 0,       -- 0: nyitott, 1: lezárt
    description TEXT NULL,                         -- Opcionális leírás
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- 3. Játékosok táblája (Szorzóval ellátva)
CREATE TABLE players (
    id INT AUTO_INCREMENT PRIMARY KEY,
    party_id INT NOT NULL,
    player_name VARCHAR(100) NOT NULL,
    multiplier TINYINT NOT NULL DEFAULT 0,
    FOREIGN KEY (party_id) REFERENCES parties(id) ON DELETE CASCADE,
    CONSTRAINT chk_multiplier CHECK (multiplier BETWEEN 0 AND 9) -- Garantálja a 0-9 tartományt
);

-- 4. Meccsek táblája
CREATE TABLE matches (
    id INT AUTO_INCREMENT PRIMARY KEY,
    party_id INT NOT NULL,
    game_name VARCHAR(100) NOT NULL,
    FOREIGN KEY (party_id) REFERENCES parties(id) ON DELETE CASCADE
);

-- 5. Meccsek eredményei tábla
CREATE TABLE match_results (
    match_id INT NOT NULL,
    player_id INT NOT NULL,
    `rank` INT NOT NULL,
    match_points INT NOT NULL,
    party_points INT NOT NULL,
    PRIMARY KEY (match_id, player_id),
    FOREIGN KEY (match_id) REFERENCES matches(id) ON DELETE CASCADE,
    FOREIGN KEY (player_id) REFERENCES players(id) ON DELETE CASCADE
);