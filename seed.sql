-- ==========================================
-- Példadatok feltöltése (BG Party Pointer)
-- ==========================================

INSERT INTO users (username, password) VALUES
('tarsas_guru', '$2y$10$abcdefghijklmnopqrstuv'),
('jatek_mester', '$2y$10$vwxyzabcdefghijklmnopqr'),
('kocka_király', '$2y$10$1234567890abcdefghij'),
('solo_strategist', '$2y$10$9876543210zyxwvutsrqp');

-- Partik feltöltése (closed_date: lezárt partiknak van értéke, nyitottaknak NULL)
INSERT INTO parties (user_id, party_name, is_closed, description, closed_date) VALUES
(1, 'Pénteki Társas',       1, 'A keménymagos péntek esti játékok helyszíne.',       '2024-03-15 23:30:00'),
(1, 'Családi Hétvége',      0, 'Könnyedebb, családi társasjátékok és nevetés.',       NULL),
(2, 'Kocka Klub',           0, NULL,                                                  NULL),
(1, 'Gamer Éjszaka',        0, 'Egész éjszakás, hardcore stratégiai csaták.',         NULL),
(1, 'Sör & Boardgame',      1, 'Laza iszogatós, partijátékos esték.',                 '2024-04-20 02:15:00'),
(2, 'Kedd Esti Stratégia',  0, 'Csak nehéz euró játékok, agyégetés felsőfokon.',      NULL),
(2, 'Bajnokok Ligája',      1, 'Hivatalos házi bajnokság komoly tétekkel.',           '2024-05-01 22:00:00'),
(3, 'Gépház Kupa',          0, NULL,                                                  NULL),
(3, 'Hétvégi Lazulás',      0, 'Bármi jöhet, ami kikapcsol.',                        NULL),
(4, 'Szóló Kalandok',       0, 'Egyedül a világ ellen, kampány alapú játékok.',       NULL);

-- Játékosok feltöltése
INSERT INTO players (party_id, player_name, multiplier) VALUES
(1, 'Gábor',  0), (1, 'Anna',  0), (1, 'Péter',  2), (1, 'Eszter', 0),
(2, 'Anya',   0), (2, 'Apa',   0), (2, 'Laci',   5),
(3, 'Zoli',   0), (3, 'Kati',  0), (3, 'Tamás',  0),
(4, 'Balázs', 0), (4, 'Csilla',0), (4, 'Dávid',  0), (4, 'Evelin', 0),
(5, 'Misi',   0), (5, 'Bence', 0), (5, 'Dániel', 0),
(6, 'Viktor', 0), (6, 'Nóra',  2), (6, 'Krisztián', 0),
(7, 'Szandra',0), (7, 'Alex',  0), (7, 'Olivér', 0), (7, 'Lili',   0),
(8, 'Roland', 0), (8, 'Kinga', 0),
(9, 'Márk',   0), (9, 'Fanni', 0), (9, 'Milán',  0), (9, 'Janka',  0),
(10, 'Attila',0);

-- Meccsek feltöltése (date: manuálisan megadott időpontok, weighting: súlyozás)
INSERT INTO matches (party_id, game_name, date, weighting) VALUES
(1, 'Catan telepesei',              '2024-03-01 19:00:00', 100),  -- ID: 1
(1, 'Ticket to Ride: Europe',       '2024-03-01 21:30:00', 100),  -- ID: 2
(2, 'Dixit',                        '2024-03-02 15:00:00', 100),  -- ID: 3
(3, 'Terraforming Mars',            '2024-03-05 18:00:00', 150),  -- ID: 4
(1, 'Carcassonne',                  '2024-03-08 19:00:00', 100),  -- ID: 5
(1, '7 Csoda',                      '2024-03-08 21:00:00', 100),  -- ID: 6
(2, 'Azul',                         '2024-03-09 16:00:00',  80),  -- ID: 7
(3, 'Scythe',                       '2024-03-12 18:00:00', 200),  -- ID: 8
(3, 'Nemesis',                      '2024-03-12 22:00:00', 150),  -- ID: 9
(4, 'Ark Nova',                     '2024-03-15 17:00:00', 200),  -- ID: 10
(4, 'Brass: Birmingham',            '2024-03-15 21:30:00', 150),  -- ID: 11
(5, 'Fedőnevek',                    '2024-04-05 20:00:00',  50),  -- ID: 12
(5, 'Fröccs',                       '2024-04-05 21:00:00',  50),  -- ID: 13
(6, 'Dűne: Imperium',               '2024-04-09 18:30:00', 200),  -- ID: 14
(7, 'A Nyugati Királyság Építői',   '2024-04-20 17:00:00', 100),  -- ID: 15
(7, 'Anachrony',                    '2024-04-20 20:30:00', 200),  -- ID: 16
(8, 'Splendor',                     '2024-04-22 19:00:00',  80),  -- ID: 17
(9, 'Kuruzslók Quedlinburgban',     '2024-04-27 16:00:00', 100),  -- ID: 18
(9, 'Cascadia',                     '2024-04-27 19:00:00',  80),  -- ID: 19
(10, 'Mage Knight',                 '2024-04-28 14:00:00', 300);  -- ID: 20

-- Match Results
-- party_points = alap érték × 10 (infláció) × (weighting / 100) × (1 + multiplier / 10)
-- Multiplierek: Péter (id:3) ×1.2 | Laci (id:7) ×1.5 | Nóra (id:19) ×1.2 | mindenki más ×1.0
INSERT INTO match_results (match_id, player_id, `rank`, match_points, party_points) VALUES
-- 1. Meccs: Catan (weighting: 100 → ×1.0)
-- Gábor(1)×1.0, Anna(2)×1.0, Péter(3)×1.2, Eszter(4)×1.0
(1, 1, 1, 10,  400),
(1, 2, 2,  9,  300),
(1, 3, 3,  8,  240),  -- 200 × 1.2
(1, 4, 4,  6,  100),

-- 2. Meccs: Ticket to Ride (weighting: 100 → ×1.0)
-- Anna(2)×1.0, Péter(3)×1.2, Gábor(1)×1.0
(2, 2, 1, 125,  300),
(2, 3, 2, 110,  240),  -- 200 × 1.2
(2, 1, 3,  98,  100),

-- 3. Meccs: Dixit (weighting: 100 → ×1.0)
-- Laci(7)×1.5, Anya(5)×1.0, Apa(6)×1.0
(3, 7, 1,  30,  450),  -- 300 × 1.5
(3, 5, 2,  28,  200),
(3, 6, 3,  24,  100),

-- 4. Meccs: Terraforming Mars (weighting: 150 → ×1.5)
-- Kati(9)×1.0, Zoli(8)×1.0, Tamás(10)×1.0
(4, 9, 1,  85,  450),  -- 300 × 1.5
(4, 8, 2,  78,  300),  -- 200 × 1.5
(4,10, 3,  71,  150),  -- 100 × 1.5

-- 5. Meccs: Carcassonne (weighting: 100 → ×1.0)
-- Gábor(1)×1.0, Anna(2)×1.0, Eszter(4)×1.0
(5, 1, 1, 104,  300),
(5, 2, 2,  96,  200),
(5, 4, 3,  82,  100),

-- 6. Meccs: 7 Csoda (weighting: 100 → ×1.0)
-- Eszter(4)×1.0, Péter(3)×1.2, Anna(2)×1.0, Gábor(1)×1.0
(6, 4, 1,  65,  400),
(6, 3, 2,  58,  360),  -- 300 × 1.2
(6, 2, 3,  50,  200),
(6, 1, 4,  42,  100),

-- 7. Meccs: Azul (weighting: 80 → ×0.8)
-- Anya(5)×1.0, Apa(6)×1.0, Laci(7)×1.5
(7, 5, 1,  52,  240),  -- 300 × 0.8
(7, 6, 2,  45,  160),  -- 200 × 0.8
(7, 7, 3,  38,  120),  -- 100 × 0.8 × 1.5

-- 8. Meccs: Scythe (weighting: 200 → ×2.0)
-- Zoli(8)×1.0, Tamás(10)×1.0, Kati(9)×1.0
(8, 8, 1, 110,  600),  -- 300 × 2.0
(8,10, 2,  95,  400),  -- 200 × 2.0
(8, 9, 3,  92,  200),  -- 100 × 2.0

-- 9. Meccs: Nemesis (weighting: 150 → ×1.5)
-- Kati(9)×1.0, Zoli(8)×1.0
(9, 9, 1,   1,  300),  -- 200 × 1.5
(9, 8, 2,   0,  150),  -- 100 × 1.5

-- 10. Meccs: Ark Nova (weighting: 200 → ×2.0)
-- Balázs(11)×1.0, Csilla(12)×1.0, Dávid(13)×1.0, Evelin(14)×1.0
(10,11, 1,  22,  800),  -- 400 × 2.0
(10,12, 2,  14,  600),  -- 300 × 2.0
(10,13, 3,   5,  400),  -- 200 × 2.0
(10,14, 4,  -8,  200),  -- 100 × 2.0

-- 11. Meccs: Brass: Birmingham (weighting: 150 → ×1.5)
-- Dávid(13)×1.0, Balázs(11)×1.0
(11,13, 1, 154,  300),  -- 200 × 1.5
(11,11, 2, 142,  150),  -- 100 × 1.5

-- 12. Meccs: Fedőnevek (weighting: 50 → ×0.5)
-- Misi(15)×1.0, Bence(16)×1.0, Dániel(17)×1.0
(12,15, 1,   9,  150),  -- 300 × 0.5
(12,16, 2,   7,  100),  -- 200 × 0.5
(12,17, 3,   6,   50),  -- 100 × 0.5

-- 13. Meccs: Fröccs (weighting: 50 → ×0.5)
-- Bence(16)×1.0, Dániel(17)×1.0, Misi(15)×1.0
(13,16, 1,  25,  150),  -- 300 × 0.5
(13,17, 2,  21,  100),  -- 200 × 0.5
(13,15, 3,  14,   50),  -- 100 × 0.5

-- 14. Meccs: Dűne: Imperium (weighting: 200 → ×2.0)
-- Viktor(18)×1.0, Nóra(19)×1.2, Krisztián(20)×1.0
(14,18, 1,  11,  600),  -- 300 × 2.0
(14,19, 2,   9,  480),  -- 200 × 2.0 × 1.2
(14,20, 3,   8,  200),  -- 100 × 2.0

-- 15. Meccs: A Nyugati Királyság Építői (weighting: 100 → ×1.0)
-- Szandra(21)×1.0, Alex(22)×1.0, Olivér(23)×1.0, Lili(24)×1.0
(15,21, 1,  44,  400),
(15,22, 2,  38,  300),
(15,23, 3,  35,  200),
(15,24, 4,  29,  100),

-- 16. Meccs: Anachrony (weighting: 200 → ×2.0)
-- Olivér(23)×1.0, Alex(22)×1.0
(16,23, 1,  76,  400),  -- 200 × 2.0
(16,22, 2,  62,  200),  -- 100 × 2.0

-- 17. Meccs: Splendor (weighting: 80 → ×0.8)
-- Roland(25)×1.0, Kinga(26)×1.0
(17,25, 1,  16,  160),  -- 200 × 0.8
(17,26, 2,  13,   80),  -- 100 × 0.8

-- 18. Meccs: Kuruzslók Quedlinburgban (weighting: 100 → ×1.0)
-- Márk(27)×1.0, Fanni(28)×1.0, Milán(29)×1.0, Janka(30)×1.0
(18,27, 1,  82,  400),
(18,28, 2,  79,  300),
(18,29, 3,  75,  200),
(18,30, 4,  61,  100),

-- 19. Meccs: Cascadia (weighting: 80 → ×0.8)
-- Janka(30)×1.0, Fanni(28)×1.0
(19,30, 1,  94,  160),  -- 200 × 0.8
(19,28, 2,  91,   80),  -- 100 × 0.8

-- 20. Meccs: Mage Knight (weighting: 300 → ×3.0)
-- Attila(31)×1.0
(20,31, 1, 164,  300);  -- 100 × 3.0