import mysql.connector
from mysql.connector import Error

def list_party_results_with_leaderboard(cursor, party_id):
    # 1. LEKÉRDEZÉS: Összesített pontok és a parti neve
    # A COALESCE biztosítja, hogy ha valaki még nem játszott meccset, 0 pontot kapjon None helyett
    summary_query = """
        SELECT p.party_name, pl.player_name, COALESCE(SUM(mr.party_points), 0) AS total_party_points
        FROM parties p
        JOIN players pl ON p.id = pl.party_id
        LEFT JOIN match_results mr ON pl.id = mr.player_id
        WHERE p.id = %s
        GROUP BY p.party_name, pl.id, pl.player_name
        ORDER BY total_party_points DESC;
    """
    
    cursor.execute(summary_query, (party_id,))
    summary_results = cursor.fetchall()
    
    if not summary_results:
        print(f"Nincsenek adatok a(z) {party_id}. azonosítójú partihoz.")
        return

    # A parti nevét kiszedjük az első sorból
    party_name = summary_results[0][0]
    
    # Fejléc és az Összesített pontok kiíratása egyből a név után
    print(f"\n--- Eredmények a(z) '{party_name}' csoportban ---")
    print("ÖSSZESÍTETT BAJNOKI PONTOK:")
    for row in summary_results:
        _, player_name, total_points = row
        print(f"  • {player_name:<12} : {total_points} pont")
    print("=" * 65)

    # 2. LEKÉRDEZÉS: Részletes meccstörténet
    details_query = """
        SELECT m.game_name, pl.player_name, mr.`rank`, mr.match_points, mr.party_points
        FROM matches m
        JOIN match_results mr ON m.id = mr.match_id
        JOIN players pl ON mr.player_id = pl.id
        WHERE m.party_id = %s
        ORDER BY m.id ASC, mr.`rank` ASC;
    """
    
    cursor.execute(details_query, (party_id,))
    details_results = cursor.fetchall()
    
    if not details_results:
        print("\nMég nem játszottak meccseket ebben a csoportban.")
        return
    
    last_game = None
    
    for row in details_results:
        game_name, player_name, rank, match_points, party_points = row
        
        # Sorköz és új játék fejléc kezelése
        if last_game != game_name:
            if last_game is not None:
                print()  
            print(f"\n[{game_name.upper()}]")
            print("-" * 65)
            last_game = game_name
            
        print(f"  {rank}. hely: {player_name:<12} | Elért pont: {match_points:<4} | Bajnoki pont: +{party_points}")


# Kapcsolódás és futtatás hibakezeléssel és automatikus lezárással
try:
    with mysql.connector.connect(
        host="localhost",
        user="root",
        password="mysql",
        database="boardgames_db"
    ) as adatbazis:
        
        with adatbazis.cursor() as cursor:
            list_party_results_with_leaderboard(cursor, 1)

except Error as e:
    print(f"Adatbázis hiba történt: {e}")