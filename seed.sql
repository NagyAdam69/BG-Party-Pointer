-- ==========================================
-- Példadatok feltöltése (BG Party Pointer)
-- ==========================================

INSERT INTO users (username, password) VALUES
('tarsas_guru', '$2y$10$abcdefghijklmnopqrstuv'), 
('jatek_mester', '$2y$10$vwxyzabcdefghijklmnopqr'),
('kocka_király', '$2y$10$1234567890abcdefghij'),
('solo_strategist', '$2y$10$9876543210zyxwvutsrqp');

-- Partik feltöltése az új 'description' mezővel kiegészítve
INSERT INTO parties (user_id, party_name, is_closed, description) VALUES
(1, 'Pénteki Társas', 1, 'A keménymagos péntek esti játékok helyszíne.'),
(1, 'Családi Hétvége', 0, 'Könnyedebb, családi társasjátékok és nevetés.'),
(2, 'Kocka Klub', 0, NULL), -- Opcionális, így lehet NULL is
(1, 'Gamer Éjszaka', 0, 'Egész éjszakás, hardcore stratégiai csaták.'),
(1, 'Sör & Boardgame', 1, 'Laza iszogatós, partijátékos esték.'),
(2, 'Kedd Esti Stratégia', 0, 'Csak nehéz euró játékok, agyégetés felsőfokon.'),
(2, 'Bajnokok Ligája', 1, 'Hivatalos házi bajnokság komoly tétekkel.'),
(3, 'Gépház Kupa', 0, NULL),
(3, 'Hétvégi Lazulás', 0, 'Bármi jöhet, ami kikapcsol.'),
(4, 'Szóló Kalandok', 0, 'Egyedül a világ ellen, kampány alapú játékok.');

-- Játékosok feltöltése az új 'multiplier' mezővel kiegészítve
INSERT INTO players (party_id, player_name, multiplier) VALUES
(1, 'Gábor', 0), (1, 'Anna', 0), (1, 'Péter', 2), (1, 'Eszter', 0), -- Péter: 2 (jelentése: 1.2)
(2, 'Anya', 0), (2, 'Apa', 0), (2, 'Laci', 5),                        -- Laci: 5 (jelentése: 1.5)
(3, 'Zoli', 0), (3, 'Kati', 0), (3, 'Tamás', 0),
(4, 'Balázs', 0), (4, 'Csilla', 0), (4, 'Dávid', 0), (4, 'Evelin', 0),
(5, 'Misi', 0), (5, 'Bence', 0), (5, 'Dániel', 0),
(6, 'Viktor', 0), (6, 'Nóra', 2), (6, 'Krisztián', 0),                -- Nóra: 2 (jelentése: 1.2)
(7, 'Szandra', 0), (7, 'Alex', 0), (7, 'Olivér', 0), (7, 'Lili', 0),
(8, 'Roland', 0), (8, 'Kinga', 0),
(9, 'Márk', 0), (9, 'Fanni', 0), (9, 'Milán', 0), (9, 'Janka', 0),
(10, 'Attila', 0);

INSERT INTO matches (party_id, game_name) VALUES
(1, 'Catan telepesei'),           -- ID: 1
(1, 'Ticket to Ride: Europe'),    -- ID: 2
(2, 'Dixit'),                     -- ID: 3
(3, 'Terraforming Mars'),         -- ID: 4
(1, 'Carcassonne'),               -- ID: 5
(1, '7 Csoda'),                   -- ID: 6
(2, 'Azul'),                      -- ID: 7
(3, 'Scythe'),                    -- ID: 8
(3, 'Nemesis'),                   -- ID: 9
(4, 'Ark Nova'),                  -- ID: 10
(4, 'Brass: Birmingham'),         -- ID: 11
(5, 'Fedőnevek'),                 -- ID: 12
(5, 'Fröccs'),                    -- ID: 13
(6, 'Dűne: Imperium'),            -- ID: 14
(7, 'A Nyugati Királyság Építői'),-- ID: 15
(7, 'Anachrony'),                 -- ID: 16
(8, 'Splendor'),                  -- ID: 17
(9, 'Kuruzslók Quedlinburgban'),  -- ID: 18
(9, 'Cascadia'),                  -- ID: 19
(10, 'Mage Knight');              -- ID: 20

-- Match Results: (match_id, player_id, rank, match_points, party_points)
INSERT INTO match_results (match_id, player_id, `rank`, match_points, party_points) VALUES
-- 1. Meccs: Catan (4 játékos, győzelemhez 10 pont kell)
(1, 1, 1, 10, 40),
(1, 2, 2, 9, 30),
(1, 3, 3, 8, 20),
(1, 4, 4, 6, 10),

-- 2. Meccs: Ticket to Ride (3 játékos)
(2, 2, 1, 125, 30),
(2, 3, 2, 110, 20),
(2, 1, 3, 98, 10),

-- 3. Meccs: Dixit (3 játékos)
(3, 7, 1, 30, 30),
(3, 5, 2, 28, 20),
(3, 6, 3, 24, 10),

-- 4. Meccs: Terraforming Mars (3 játékos)
(4, 9, 1, 85, 30),
(4, 8, 2, 78, 20),
(4, 10, 3, 71, 10),

-- 5. Meccs: Carcassonne (3 játékos)
(5, 1, 1, 104, 30),
(5, 2, 2, 96, 20),
(5, 4, 3, 82, 10),

-- 6. Meccs: 7 Csoda (4 játékos)
(6, 4, 1, 65, 40),
(6, 3, 2, 58, 30),
(6, 2, 3, 50, 20),
(6, 1, 4, 42, 10),

-- 7. Meccs: Azul (3 játékos)
(7, 5, 1, 52, 30),
(7, 6, 2, 45, 20),
(7, 7, 3, 38, 10),

-- 8. Meccs: Scythe (3 játékos)
(8, 8, 1, 110, 30),
(8, 10, 2, 95, 20),
(8, 9, 3, 92, 10),

-- 9. Meccs: Nemesis (2 játékos - félig kooperatív, túlélési pontok)
(9, 9, 1, 1, 20),
(9, 8, 2, 0, 10),

-- 10. Meccs: Ark Nova (4 játékos)
(10, 11, 1, 22, 40),
(10, 12, 2, 14, 30),
(10, 13, 3, 5, 20),
(10, 14, 4, -8, 10),

-- 11. Meccs: Brass: Birmingham (2 játékos)
(11, 13, 1, 154, 20),
(11, 11, 2, 142, 10),

-- 12. Meccs: Fedőnevek (3 játékos)
(12, 15, 1, 9, 30),
(12, 16, 2, 7, 20),
(12, 17, 3, 6, 10),

-- 13. Meccs: Fröccs (3 játékos)
(13, 16, 1, 25, 30),
(13, 17, 2, 21, 20),
(13, 15, 3, 14, 10),

-- 14. Meccs: Dűne: Imperium (3 játékos)
(14, 18, 1, 11, 30),
(14, 19, 2, 9, 20),
(14, 20, 3, 8, 10),

-- 15. Meccs: A Nyugati Királyság Építői (4 játékos)
(15, 21, 1, 44, 40),
(15, 22, 2, 38, 30),
(15, 23, 3, 35, 20),
(15, 24, 4, 29, 10),

-- 16. Meccs: Anachrony (2 játékos)
(16, 23, 1, 76, 20),
(16, 22, 2, 62, 10),

-- 17. Meccs: Splendor (2 játékos)
(17, 25, 1, 16, 20),
(17, 26, 2, 13, 10),

-- 18. Meccs: Kuruzslók Quedlinburgban (4 játékos)
(18, 27, 1, 82, 40),
(18, 28, 2, 79, 30),
(18, 29, 3, 75, 20),
(18, 30, 4, 61, 10),

-- 19. Meccs: Cascadia (2 játékos)
(19, 30, 1, 94, 20),
(19, 28, 2, 91, 10),

-- 20. Meccs: Mage Knight (1 játékos / Szóló játék pontszáma)
(20, 31, 1, 164, 10);