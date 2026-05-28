import tkinter as tk
from tkinter import messagebox
import mysql.connector
from mysql.connector import Error

# Adatbázis kapcsolódási adatok
DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "mysql",
    "database": "boardgames_db"
}

# Globális változók
dashboard_frame = None
create_party_frame = None
current_user_id = None
current_username_global = None

# Új parti képernyő globális widgetek
player_rows = []               # Lista: [(name_var, mult_var), ...]
players_inner_frame = None     # A dinamikus játékos sorok szülő frame-je
add_player_button_widget = None
party_name_entry_widget = None
party_desc_text_widget = None


def get_db_connection():
    return mysql.connector.connect(**DB_CONFIG)


# ==========================================
# BEJELENTKEZÉS / REGISZTRÁCIÓ
# ==========================================

def handle_login():
    global current_user_id, current_username_global

    username = username_entry.get().strip()
    password = password_entry.get()

    if not username or not password:
        messagebox.showwarning("Hiba", "Adjon meg egy felhasználónevet, és jelszót.")
        return

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # id-t is lekérjük, nem csak a létezést ellenőrizzük
        query = "SELECT id FROM users WHERE username = %s AND BINARY password = %s"
        cursor.execute(query, (username, password))
        user = cursor.fetchone()

        if user:
            current_user_id = user[0]
            current_username_global = username
            messagebox.showinfo("Siker", "Sikeres bejelentkezés!")
            show_dashboard(username)
        else:
            messagebox.showerror("Hiba", "Helytelen felhasználónév / jelszó")

    except Error as e:
        messagebox.showerror("Adatbázis hiba", f"Hiba történt: {e}")
    finally:
        if 'conn' in locals() and conn.is_connected():
            cursor.close()
            conn.close()


def handle_register():
    username = username_entry.get().strip()
    password = password_entry.get()

    if not username or not password:
        messagebox.showwarning("Hiba", "Adjon meg egy felhasználónevet, és jelszót.")
        return

    if len(password) < 8:
        messagebox.showwarning("Hiba", "A jelszó min. 8 karakter hosszúságú legyen.")
        return

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        check_query = "SELECT id FROM users WHERE username = %s"
        cursor.execute(check_query, (username,))
        if cursor.fetchone():
            messagebox.showwarning("Hiba", "A megadott felhasználónév már létezik.")
            return

        insert_query = "INSERT INTO users (username, password) VALUES (%s, %s)"
        cursor.execute(insert_query, (username, password))
        conn.commit()

        messagebox.showinfo("Siker", "Sikeres regisztráció!")
        username_entry.delete(0, tk.END)
        password_entry.delete(0, tk.END)

    except Error as e:
        messagebox.showerror("Adatbázis hiba", f"Hiba történt: {e}")
    finally:
        if 'conn' in locals() and conn.is_connected():
            cursor.close()
            conn.close()


# ==========================================
# FŐOLDAL (DASHBOARD)
# ==========================================

def show_dashboard(username):
    global dashboard_frame

    login_frame.pack_forget()
    root.title("BG Party Pointer - Főoldal")

    dashboard_frame = tk.Frame(root, padx=40, pady=40)
    dashboard_frame.pack(fill=tk.BOTH, expand=True)

    # Felső sáv
    top_bar = tk.Frame(dashboard_frame)
    top_bar.pack(fill=tk.X, side=tk.TOP, pady=(0, 20))

    tk.Label(top_bar, text=f"Felhasználó: {username}",
             font=("Arial", 16, "bold"), fg="#333333").pack(side=tk.LEFT)
    tk.Button(top_bar, text="Kijelentkezés", command=handle_logout,
              font=("Arial", 12, "bold"), bg="#f44336", fg="white", padx=10).pack(side=tk.RIGHT)

    # Partik cím + plusz gomb (show_create_party-ra kötve)
    tk.Label(dashboard_frame, text="Partik",
             font=("Arial", 22, "bold"), fg="#333333").pack(pady=(10, 5))
    tk.Button(dashboard_frame, text=" + ", font=("Arial", 16, "bold"),
              bg="#4CAF50", fg="white", width=4,
              command=show_create_party).pack(pady=(0, 16))

    # --- Parti lista (görgethető, 3 oszlopos gombráccsal) ---
    _build_party_list(dashboard_frame)


def _build_party_list(parent):
    """Lekéri a felhasználó partijait és 3 oszlopos rácsban megjeleníti őket."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, party_name, is_closed FROM parties "
            "WHERE user_id = %s ORDER BY is_closed ASC, id DESC",
            (current_user_id,)
        )
        parties = cursor.fetchall()  # [(id, party_name, is_closed), ...]
    except Error as e:
        messagebox.showerror("Adatbázis hiba", f"Partik betöltése sikertelen: {e}")
        parties = []
    finally:
        if 'conn' in locals() and conn.is_connected():
            cursor.close()
            conn.close()

    if not parties:
        tk.Label(parent, text="Még nincs egy partid sem. Hozz létre egyet a + gombbal!",
                 font=("Arial", 12, "italic"), fg="#888888").pack(pady=20)
        return

    # Görgethető keret
    container = tk.Frame(parent)
    container.pack(fill=tk.BOTH, expand=True)

    canvas = tk.Canvas(container, highlightthickness=0, bg=root.cget("bg"))
    scrollbar = tk.Scrollbar(container, orient="vertical", command=canvas.yview)
    canvas.configure(yscrollcommand=scrollbar.set)

    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    grid_frame = tk.Frame(canvas, bg=root.cget("bg"))
    win_id = canvas.create_window((0, 0), window=grid_frame, anchor="nw")

    grid_frame.bind("<Configure>",
        lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
    canvas.bind("<Configure>",
        lambda e: canvas.itemconfig(win_id, width=e.width))

    # Egér görgő támogatás
    canvas.bind("<Enter>", lambda e: canvas.bind_all("<MouseWheel>",
        lambda ev: canvas.yview_scroll(int(-1 * (ev.delta / 120)), "units")))
    canvas.bind("<Leave>", lambda e: canvas.unbind_all("<MouseWheel>"))

    # Gombok 3 oszlopos rácsban
    COLS = 3
    for idx, (party_id, party_name, is_closed) in enumerate(parties):
        row_i = idx // COLS
        col_i = idx % COLS

        bg_color  = "#90CAF9" if not is_closed else "#BDBDBD"   # kék / szürke
        hover_color = "#64B5F6" if not is_closed else "#9E9E9E"
        fg_color  = "#1A237E" if not is_closed else "#424242"

        btn = tk.Button(
            grid_frame,
            text=party_name,
            font=("Arial", 12, "bold"),
            bg=bg_color, fg=fg_color,
            activebackground=hover_color,
            relief="raised", bd=2,
            width=18, height=2,
            wraplength=160,
            # command itt kerül majd bekötésre a következő lépésben
            command=lambda pid=party_id: on_party_click(pid)
        )
        btn.grid(row=row_i, column=col_i, padx=10, pady=8, sticky="nsew")

    for c in range(COLS):
        grid_frame.columnconfigure(c, weight=1)


def on_party_click(party_id):
    """Placeholder – a következő lépésben kerül kitöltésre."""
    pass


def handle_logout():
    global dashboard_frame

    if dashboard_frame:
        dashboard_frame.destroy()

    root.title("BG Party Pointer - Bejelentkezés")
    password_entry.delete(0, tk.END)
    login_frame.pack(fill=tk.BOTH, expand=True)


# ==========================================
# ÚJ PARTI KÉSZÍTÉSE KÉPERNYŐ
# ==========================================

def show_create_party():
    global create_party_frame, player_rows, players_inner_frame
    global add_player_button_widget, party_name_entry_widget, party_desc_text_widget

    # Állapot reset
    player_rows = []

    dashboard_frame.pack_forget()
    root.title("BG Party Pointer - Új Parti")

    create_party_frame = tk.Frame(root, padx=20, pady=15)
    create_party_frame.pack(fill=tk.BOTH, expand=True)

    # --- Fejléc sáv: cím + vissza gomb ---
    header = tk.Frame(create_party_frame)
    header.pack(fill=tk.X, pady=(0, 14))

    tk.Label(header, text="Új Parti készítése",
             font=("Arial", 20, "bold"), fg="#333333").pack(side=tk.LEFT)
    tk.Button(header, text="Vissza", command=hide_create_party,
              font=("Arial", 12, "bold"), bg="#f44336", fg="white", padx=14).pack(side=tk.RIGHT)

    # --- Fő tartalom: bal és jobb hasáb ---
    content = tk.Frame(create_party_frame)
    content.pack(fill=tk.BOTH, expand=True)

    # ==== BAL OLDAL: Játékosok ====
    left = tk.Frame(content, padx=8)
    left.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    tk.Label(left, text="Játékosok:", font=("Arial", 13, "bold")).pack(anchor="w", pady=(0, 6))

    # Canvas a görgethető játékos listához
    canvas = tk.Canvas(left, highlightthickness=0, bg=root.cget("bg"))
    canvas.pack(fill=tk.BOTH, expand=True)

    players_inner_frame = tk.Frame(canvas, bg=root.cget("bg"))
    win_id = canvas.create_window((0, 0), window=players_inner_frame, anchor="nw")

    # Canvas méretezés frissítések
    players_inner_frame.bind("<Configure>",
        lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
    canvas.bind("<Configure>",
        lambda e: canvas.itemconfig(win_id, width=e.width))

    # Első játékos sor hozzáadása
    _build_player_row()

    # Plusz gomb (játékos hozzáadáshoz)
    add_player_button_widget = tk.Button(
        players_inner_frame, text="  +  ",
        font=("Arial", 14, "bold"), bg="#FF8C00", fg="white",
        command=add_player_row
    )
    add_player_button_widget.pack(pady=(10, 2), anchor="w")

    # Elválasztó vonal
    tk.Frame(content, width=2, bg="#cccccc").pack(side=tk.LEFT, fill=tk.Y, padx=14)

    # ==== JOBB OLDAL: Parti adatok ====
    right = tk.Frame(content, padx=8)
    right.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    tk.Label(right, text="Parti neve:", font=("Arial", 13, "bold")).pack(anchor="w", pady=(0, 4))
    party_name_entry_widget = tk.Entry(right, font=("Arial", 13), width=28,
                                       bg="#FFFACD", relief="solid", bd=1)
    party_name_entry_widget.pack(fill=tk.X, pady=(0, 16))

    tk.Label(right, text="Parti leírása (opcionális):",
             font=("Arial", 13, "bold")).pack(anchor="w", pady=(0, 4))
    party_desc_text_widget = tk.Text(right, font=("Arial", 12), height=7, width=28,
                                      bg="#FFFACD", relief="solid", bd=1)
    party_desc_text_widget.pack(fill=tk.X, pady=(0, 20))

    tk.Button(right, text="Véglegesítés", command=handle_finalize_party,
              font=("Arial", 14, "bold"), bg="#4CAF50", fg="white",
              padx=20, pady=6).pack(pady=(4, 0))


def _build_player_row():
    """
    Egy új játékos sort épít be a players_inner_frame-be.
    Belső segédfüggvény – csak show_create_party és add_player_row hívja.
    """
    row = tk.Frame(players_inner_frame, bg=root.cget("bg"))
    row.pack(fill=tk.X, pady=3, anchor="w")

    name_var = tk.StringVar()
    tk.Entry(row, textvariable=name_var,
             font=("Arial", 12), width=18,
             bg="#FFA040", fg="white", insertbackground="white",
             relief="solid", bd=1).pack(side=tk.LEFT, padx=(0, 6))

    tk.Label(row, text="Szorzó: x1.",
             font=("Arial", 12), bg=root.cget("bg")).pack(side=tk.LEFT)

    mult_var = tk.StringVar(value="0")
    tk.Spinbox(row, from_=0, to=9, textvariable=mult_var,
               font=("Arial", 12), width=3,
               relief="solid", bd=1).pack(side=tk.LEFT)

    player_rows.append((name_var, mult_var))


def add_player_row():
    """
    Plusz gomb callbackja: eltávolítja a gombot, hozzáad egy sort, visszateszi a gombot.
    """
    add_player_button_widget.pack_forget()
    _build_player_row()
    add_player_button_widget.pack(pady=(10, 2), anchor="w")


def handle_finalize_party():
    """Validál, majd elmenti a partít és a játékosokat az adatbázisba."""
    party_name = party_name_entry_widget.get().strip()
    description = party_desc_text_widget.get("1.0", tk.END).strip()

    # Érvényes (nem üres nevű) játékosok összegyűjtése
    valid_players = []
    for name_var, mult_var in player_rows:
        name = name_var.get().strip()
        if name:
            try:
                mult = max(0, min(9, int(mult_var.get())))
            except ValueError:
                mult = 0
            valid_players.append((name, mult))

    # --- Validációk ---
    if not party_name:
        messagebox.showwarning("Hiba", "A parti nevét kötelező megadni!")
        return

    if not valid_players:
        messagebox.showwarning("Hiba", "Legalább egy játékos nevét meg kell adni!")
        return

    # Duplikált nevek ellenőrzése (kis-/nagybetű független)
    lower_names = [p[0].lower() for p in valid_players]
    if len(lower_names) != len(set(lower_names)):
        messagebox.showerror("Hiba", "Nem lehet 2 játékosnak ugyanaz a neve!")
        return

    # --- Mentés az adatbázisba ---
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        desc_value = description if description else None
        cursor.execute(
            "INSERT INTO parties (user_id, party_name, is_closed, description) VALUES (%s, %s, 0, %s)",
            (current_user_id, party_name, desc_value)
        )
        party_id = cursor.lastrowid

        for player_name, multiplier in valid_players:
            cursor.execute(
                "INSERT INTO players (party_id, player_name, multiplier) VALUES (%s, %s, %s)",
                (party_id, player_name, multiplier)
            )

        conn.commit()
        messagebox.showinfo("Siker", f"'{party_name}' parti sikeresen létrehozva!")
        hide_create_party()

    except Error as e:
        messagebox.showerror("Adatbázis hiba", f"Hiba történt: {e}")
    finally:
        if 'conn' in locals() and conn.is_connected():
            cursor.close()
            conn.close()


def hide_create_party():
    """Bezárja az új parti képernyőt és visszatér a főoldalra (lista frissítésével)."""
    global create_party_frame, dashboard_frame

    if create_party_frame:
        create_party_frame.destroy()
        create_party_frame = None

    # Dashboard újraépítése, hogy az újonnan létrehozott parti is megjelenjen
    if dashboard_frame:
        dashboard_frame.destroy()

    root.title("BG Party Pointer - Főoldal")
    show_dashboard(current_username_global)


# ==========================================
# ALAP ABLAK ÉS BEJELENTKEZŐ FELÜLET
# ==========================================

root = tk.Tk()
root.title("BG Party Pointer - Bejelentkezés")
root.geometry("700x520")
root.resizable(False, False)
root.eval('tk::PlaceWindow . center')

# A bejelentkezési felület kerete
login_frame = tk.Frame(root, padx=40, pady=40)
login_frame.pack(fill=tk.BOTH, expand=True)

# Cím
title_label = tk.Label(login_frame, text="Bejelentkezés / Regisztráció", font=("Arial", 24, "bold"))
title_label.pack(pady=(0, 30))

# Felhasználónév szöveg
username_label = tk.Label(login_frame, text="Felhasználónév:", font=("Arial", 16))
username_label.pack(pady=(0, 5))

# Felhasználónév beviteli mező
username_entry = tk.Entry(login_frame, font=("Arial", 16), width=35)
username_entry.pack(pady=(0, 20))

# Jelszó szöveg
password_label = tk.Label(login_frame, text="Jelszó:", font=("Arial", 16))
password_label.pack(pady=(0, 5))

# Jelszó beviteli mező
password_entry = tk.Entry(login_frame, font=("Arial", 16), width=35, show="*")
password_entry.pack(pady=(0, 35))

# Gombok konténere
button_frame = tk.Frame(login_frame)
button_frame.pack(fill=tk.X)

# Bejelentkezés gomb
login_button = tk.Button(button_frame, text="Bejelentkezés", command=handle_login,
                         font=("Arial", 14, "bold"), width=15, bg="#4CAF50", fg="white")
login_button.pack(side=tk.LEFT, padx=(10, 20), ipady=5)

# Regisztráció gomb
register_button = tk.Button(button_frame, text="Regisztráció", command=handle_register,
                            font=("Arial", 14, "bold"), width=15, bg="#2196F3", fg="white")
register_button.pack(side=tk.RIGHT, padx=(20, 10), ipady=5)

root.mainloop()