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
party_detail_frame = None
current_user_id = None
current_username_global = None

# Új parti képernyő globális widgetek
player_rows = []
players_inner_frame = None
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

        query = "SELECT id FROM users WHERE BINARY username = %s AND BINARY password = %s"
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

    top_bar = tk.Frame(dashboard_frame)
    top_bar.pack(fill=tk.X, side=tk.TOP, pady=(0, 20))

    tk.Label(top_bar, text=f"Felhasználó: {username}",
             font=("Arial", 16, "bold"), fg="#333333").pack(side=tk.LEFT)
    tk.Button(top_bar, text="Kijelentkezés", command=handle_logout,
              font=("Arial", 12, "bold"), bg="#f44336", fg="white", padx=10).pack(side=tk.RIGHT)

    tk.Label(dashboard_frame, text="Partik",
             font=("Arial", 22, "bold"), fg="#333333").pack(pady=(10, 5))
    tk.Button(dashboard_frame, text=" + ", font=("Arial", 16, "bold"),
              bg="#4CAF50", fg="white", width=4,
              command=show_create_party).pack(pady=(0, 16))

    _build_party_list(dashboard_frame)


def _build_party_list(parent):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, party_name, is_closed FROM parties "
            "WHERE user_id = %s ORDER BY is_closed ASC, id DESC",
            (current_user_id,)
        )
        parties = cursor.fetchall()
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

    canvas.bind("<Enter>", lambda e: canvas.bind_all("<MouseWheel>",
        lambda ev: canvas.yview_scroll(int(-1 * (ev.delta / 120)), "units")))
    canvas.bind("<Leave>", lambda e: canvas.unbind_all("<MouseWheel>"))

    COLS = 3
    for idx, (party_id, party_name, is_closed) in enumerate(parties):
        row_i = idx // COLS
        col_i = idx % COLS

        bg_color    = "#90CAF9" if not is_closed else "#BDBDBD"
        hover_color = "#64B5F6" if not is_closed else "#9E9E9E"
        fg_color    = "#1A237E" if not is_closed else "#424242"

        btn = tk.Button(
            grid_frame,
            text=party_name,
            font=("Arial", 12, "bold"),
            bg=bg_color, fg=fg_color,
            activebackground=hover_color,
            relief="raised", bd=2,
            width=18, height=2,
            wraplength=160,
            command=lambda pid=party_id: on_party_click(pid)
        )
        btn.grid(row=row_i, column=col_i, padx=10, pady=8, sticky="nsew")

    for c in range(COLS):
        grid_frame.columnconfigure(c, weight=1)


def on_party_click(party_id):
    global dashboard_frame
    dashboard_frame.pack_forget()
    show_party_detail(party_id)


def handle_logout():
    global dashboard_frame

    if dashboard_frame:
        dashboard_frame.destroy()

    root.title("BG Party Pointer - Bejelentkezés")
    password_entry.delete(0, tk.END)
    login_frame.pack(fill=tk.BOTH, expand=True)


# ==========================================
# PARTI RÉSZLETEK KÉPERNYŐ
# ==========================================

def show_party_detail(party_id):
    global party_detail_frame

    root.title("BG Party Pointer - Parti részletei")

    party_detail_frame = tk.Frame(root, padx=16, pady=12)
    party_detail_frame.pack(fill=tk.BOTH, expand=True)

    # --- Adatok lekérése ---
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Parti adatok
        cursor.execute(
            "SELECT party_name, is_closed, closed_date, description FROM parties WHERE id = %s",
            (party_id,)
        )
        party = cursor.fetchone()
        if not party:
            messagebox.showerror("Hiba", "A parti nem található.")
            party_detail_frame.destroy()
            show_dashboard(current_username_global)
            return
        party_name, is_closed, closed_date, party_description = party

        # Játékosok (id, név, multiplier)
        cursor.execute(
            "SELECT id, player_name, multiplier FROM players WHERE party_id = %s",
            (party_id,)
        )
        players = cursor.fetchall()  # [(id, name, multiplier), ...]

        # Meccsek (id, game_name, date, weighting, win_con)
        cursor.execute(
            "SELECT id, game_name, date, weighting, win_con FROM matches "
            "WHERE party_id = %s ORDER BY date DESC",
            (party_id,)
        )
        matches = cursor.fetchall()

        # Meccs eredmények: {match_id: [(player_id, rank, match_points, sec_match_points), ...]}
        match_results = {}
        if matches:
            match_ids = [m[0] for m in matches]
            fmt = ",".join(["%s"] * len(match_ids))
            cursor.execute(
                f"SELECT match_id, player_id, `rank`, match_points, sec_match_points "
                f"FROM match_results WHERE match_id IN ({fmt}) ORDER BY match_id, match_points DESC",
                match_ids
            )
            for row in cursor.fetchall():
                mid = row[0]
                match_results.setdefault(mid, []).append(row[1:])
                # (player_id, rank, match_points, sec_match_points)

    except Error as e:
        messagebox.showerror("Adatbázis hiba", f"Hiba történt: {e}")
        party_detail_frame.destroy()
        show_dashboard(current_username_global)
        return
    finally:
        if 'conn' in locals() and conn.is_connected():
            cursor.close()
            conn.close()

    # Segédszótár: player_id → (name, multiplier)
    player_map = {p[0]: (p[1], p[2]) for p in players}

    # ---- FEJLÉC SÁV ----
    header = tk.Frame(party_detail_frame)
    header.pack(fill=tk.X, pady=(0, 10))

    tk.Label(header, text=party_name,
             font=("Arial", 20, "bold"), fg="#1A237E").pack(side=tk.LEFT, padx=(0, 14))

    # Kuka gomb
    tk.Button(
        header, text="🗑", font=("Arial", 14), bg="#f44336", fg="white",
        relief="flat", padx=6, pady=2,
        command=lambda: handle_delete_party(party_id, party_name)
    ).pack(side=tk.LEFT, padx=(0, 8))

    # Parti lezárása / lezárva felirat
    if is_closed:
        date_str = closed_date.strftime("%Y.%m.%d %H:%M") if closed_date else "–"
        tk.Label(header, text=f"Lezárva: {date_str}",
                 font=("Arial", 11, "italic"), fg="#555555",
                 bg="#E0E0E0", padx=10, pady=4, relief="flat").pack(side=tk.LEFT, padx=(0, 8))
    else:
        tk.Button(
            header, text="Parti lezárása",
            font=("Arial", 11, "bold"), bg="#607D8B", fg="white",
            padx=10, pady=4,
            command=lambda: handle_close_party(party_id, party_name)
        ).pack(side=tk.LEFT, padx=(0, 8))

    # Vissza gomb
    tk.Button(
        header, text="Vissza",
        font=("Arial", 11, "bold"), bg="#f44336", fg="white",
        padx=10, pady=4,
        command=lambda: hide_party_detail()
    ).pack(side=tk.RIGHT)

    # ---- FŐ TARTALOM: bal ranglista + jobb meccsek ----
    content = tk.Frame(party_detail_frame)
    content.pack(fill=tk.BOTH, expand=True)

    # == BAL: RANGLISTA ==
    left = tk.Frame(content, width=220, padx=6)
    left.pack(side=tk.LEFT, fill=tk.Y)
    left.pack_propagate(False)

    tk.Label(left, text="Ranglista:", font=("Arial", 13, "bold"), fg="#333333").pack(anchor="w", pady=(0, 6))

    # Segédfüggvény: bajnoki pontok kiszámítása
    def calc_party_points(n_players, rank, weighting, multiplier):
        base = (n_players - rank + 1) * 100
        return round(base * (weighting / 100) * (1 + multiplier / 10))

    # Ranglista konténer – törölhető és újraépíthető
    ranglista_container = tk.Frame(left)
    ranglista_container.pack(fill=tk.X)

    def refresh_ranglista():
        for w in ranglista_container.winfo_children():
            w.destroy()

        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT id, weighting FROM matches WHERE party_id = %s", (party_id,))
            fresh_matches = cursor.fetchall()
            if fresh_matches:
                mids = [m[0] for m in fresh_matches]
                fmt = ",".join(["%s"] * len(mids))
                cursor.execute(
                    f"SELECT match_id, player_id, `rank`, match_points "
                    f"FROM match_results WHERE match_id IN ({fmt})", mids
                )
                rows = cursor.fetchall()
            else:
                rows = []
        except Error as e:
            tk.Label(ranglista_container, text=f"Hiba: {e}",
                     font=("Arial", 9), fg="red").pack()
            return
        finally:
            if 'conn' in locals() and conn.is_connected():
                cursor.close()
                conn.close()

        fresh_results = {}
        for mid, pid, rank, mp in rows:
            fresh_results.setdefault(mid, []).append((pid, rank, mp))

        totals = {}
        w_map = {m[0]: m[1] for m in fresh_matches}
        for mid, wt in w_map.items():
            res = fresh_results.get(mid, [])
            n = len(res)
            for (pid, rank, mp) in res:
                _, pmult = player_map.get(pid, ("?", 0))
                pp = calc_party_points(n, rank, wt, pmult)
                totals[pid] = totals.get(pid, 0) + pp

        sorted_pl = sorted(players, key=lambda p: totals.get(p[0], 0), reverse=True)

        hdr = tk.Frame(ranglista_container, bg="#388E3C")
        hdr.pack(fill=tk.X)
        for txt, w in [("név", 9), ("pont", 7), ("rank", 5)]:
            tk.Label(hdr, text=txt, font=("Arial", 10, "bold"),
                     fg="white", bg="#388E3C", width=w, anchor="w").pack(side=tk.LEFT, padx=2, pady=3)

        for rank_i, (pid, pname, pmult) in enumerate(sorted_pl, start=1):
            pts = totals.get(pid, 0)
            row_bg = "#F1F8E9" if rank_i % 2 == 0 else "#DCEDC8"
            row = tk.Frame(ranglista_container, bg=row_bg)
            row.pack(fill=tk.X)
            tk.Label(row, text=pname, font=("Arial", 10),
                     bg=row_bg, width=9, anchor="w").pack(side=tk.LEFT, padx=2, pady=2)
            tk.Label(row, text=str(pts), font=("Arial", 10, "bold"),
                     bg=row_bg, anchor="w", width=7).pack(side=tk.LEFT)
            tk.Label(row, text=str(rank_i), font=("Arial", 10, "bold"),
                     fg="#1B5E20", bg=row_bg, width=4, anchor="w").pack(side=tk.LEFT, padx=2)
            if pmult != 0:
                tk.Label(row, text=f"(x1.{pmult})", font=("Arial", 7),
                         fg="#555555", bg=row_bg).pack(side=tk.LEFT)

    refresh_ranglista()

    # Leírás doboz (ha van)
    if party_description:
        tk.Label(left, text="Leírás:", font=("Arial", 10, "bold"),
                 fg="#555555").pack(anchor="w", pady=(12, 2))
        desc_box = tk.Frame(left, bg="#E8F5E9", relief="solid", bd=1)
        desc_box.pack(fill=tk.X, pady=(0, 6))
        tk.Label(desc_box, text=party_description, font=("Arial", 10),
                 bg="#E8F5E9", fg="#2E2E2E", wraplength=180,
                 justify="left", anchor="nw", padx=8, pady=6).pack(fill=tk.X)

    # Elválasztó
    tk.Frame(content, width=2, bg="#CCCCCC").pack(side=tk.LEFT, fill=tk.Y, padx=10)

    # == JOBB: MECCSEK ==
    right_outer = tk.Frame(content)
    right_outer.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    # Felső sáv: "Meccsek:" cím + Új meccs gomb
    matches_header = tk.Frame(right_outer)
    matches_header.pack(fill=tk.X, pady=(0, 8))

    tk.Label(matches_header, text="Meccsek:", font=("Arial", 13, "bold"), fg="#333333").pack(side=tk.LEFT)

    new_match_btn_ref = [None]
    new_match_form_ref = [None]

    def show_new_match_form():
        if new_match_btn_ref[0]:
            new_match_btn_ref[0].pack_forget()
        _build_new_match_form(mc_inner, mc_canvas, players, party_id, is_closed,
                              new_match_btn_ref, new_match_form_ref,
                              player_map, calc_party_points, refresh_ranglista)

    if not is_closed:
        btn = tk.Button(
            matches_header, text="Új meccs",
            font=("Arial", 11, "bold"), bg="#FF8C00", fg="white",
            padx=12, pady=3,
            command=show_new_match_form
        )
        btn.pack(side=tk.LEFT, padx=(12, 0))
        new_match_btn_ref[0] = btn

    # Görgethető meccs lista
    mc_container = tk.Frame(right_outer)
    mc_container.pack(fill=tk.BOTH, expand=True)

    mc_canvas = tk.Canvas(mc_container, highlightthickness=0, bg=root.cget("bg"))
    mc_scroll = tk.Scrollbar(mc_container, orient="vertical", command=mc_canvas.yview)
    mc_canvas.configure(yscrollcommand=mc_scroll.set)

    mc_scroll.pack(side=tk.RIGHT, fill=tk.Y)
    mc_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    mc_inner = tk.Frame(mc_canvas, bg=root.cget("bg"))
    mc_win = mc_canvas.create_window((0, 0), window=mc_inner, anchor="nw")

    mc_inner.bind("<Configure>", lambda e: mc_canvas.configure(scrollregion=mc_canvas.bbox("all")))
    mc_canvas.bind("<Configure>", lambda e: mc_canvas.itemconfig(mc_win, width=e.width))
    mc_canvas.bind("<Enter>", lambda e: mc_canvas.bind_all("<MouseWheel>",
        lambda ev: mc_canvas.yview_scroll(int(-1 * (ev.delta / 120)), "units")))
    mc_canvas.bind("<Leave>", lambda e: mc_canvas.unbind_all("<MouseWheel>"))

    if not matches:
        tk.Label(mc_inner, text="Még nincs egyetlen meccs sem ebben a partiban.",
                 font=("Arial", 11, "italic"), fg="#888888").pack(pady=20)
    else:
        for (mid, game_name, mdate, weighting, win_con) in matches:
            _build_match_card(mc_inner, mid, game_name, mdate, weighting, win_con,
                              match_results.get(mid, []), player_map, calc_party_points,
                              party_id, is_closed)


def _build_match_card(parent, mid, game_name, mdate, weighting, win_con, results,
                      player_map, calc_party_points, party_id, is_closed,
                      before_widget=None):
    """Egy meccs kártyát épít fel a meccs listában."""
    GOLD      = "#FFC107"
    GOLD_HDR  = "#FF8F00"
    ROW_A     = "#FFF8E1"
    ROW_B     = "#FFECB3"

    n_players = len(results)

    # Rendezés helyezés szerint növekvő (1. hely elöl)
    sorted_results = sorted(results, key=lambda r: r[1])

    # Ha before_widget meg van adva, az új kártya a lista elejére kerül
    pack_kwargs = dict(fill=tk.X, padx=4, pady=6)
    if before_widget is not None:
        pack_kwargs["before"] = before_widget

    card = tk.Frame(parent, relief="ridge", bd=2, bg=GOLD, padx=4, pady=4)
    card.pack(**pack_kwargs)

    # --- Felső sor: dátum | játék neve | súlyozás | X törlés ---
    top_row = tk.Frame(card, bg=GOLD)
    top_row.pack(fill=tk.X)

    # X gomb – csak nyitott partinál
    if not is_closed:
        tk.Button(
            top_row, text="✕", font=("Arial", 10, "bold"),
            bg="#e53935", fg="white", relief="flat",
            padx=4, pady=0, cursor="hand2",
            command=lambda m=mid, g=game_name: _confirm_delete_match(m, g, parent, party_id)
        ).pack(side=tk.RIGHT, padx=(4, 2), pady=2)

    date_str = mdate.strftime("%Y-%m-%d  %H:%M") if mdate else "–"
    tk.Label(top_row, text=date_str, font=("Arial", 9),
             bg=GOLD, fg="#4E342E", anchor="w").pack(side=tk.LEFT, padx=4)

    tk.Label(top_row, text=game_name, font=("Arial", 13, "bold"),
             bg=GOLD, fg="#1A237E", anchor="center").pack(side=tk.LEFT, expand=True)

    weight_label = f"súlyozás: {weighting}%"
    if win_con == "min":
        weight_label += "  |  ↓ kevesebb pont nyer"
    tk.Label(top_row, text=weight_label,
             font=("Arial", 9), bg=GOLD, fg="#4E342E", anchor="e").pack(side=tk.RIGHT, padx=4)

    # --- Táblázat ---
    # col0=név, col1=győzelmi pontok (+ másodlagos), col2=helyezés, col3=bajnoki pontok
    table_frame = tk.Frame(card, bg=card.cget("bg"))
    table_frame.pack(fill=tk.X, pady=(4, 0))
    table_frame.columnconfigure(0, weight=3)
    table_frame.columnconfigure(1, weight=0, minsize=130)  # győzelmi pontok – kicsit szélesebb a sec miatt
    table_frame.columnconfigure(2, weight=0, minsize=90)
    table_frame.columnconfigure(3, weight=2)

    # Fejléc sor
    hdr_cols = [("név", "w"), ("győzelmi pontok", "w"), ("helyezés", "center"), ("bajnoki pontok", "e")]
    for col_i, (txt, anch) in enumerate(hdr_cols):
        tk.Label(table_frame, text=txt, font=("Arial", 9, "bold"),
                 bg=GOLD_HDR, fg="white", anchor=anch, padx=6).grid(
                 row=0, column=col_i, sticky="ew", pady=3)

    # Játékos sorok
    for i, (pid, rank, match_points, sec_points) in enumerate(sorted_results):
        pname, pmult = player_map.get(pid, ("?", 0))
        party_points = calc_party_points(n_players, rank, weighting, pmult)
        row_bg = ROW_A if i % 2 == 0 else ROW_B
        grid_row = i + 1

        # Név + szorzó
        name_cell = tk.Frame(table_frame, bg=row_bg)
        name_cell.grid(row=grid_row, column=0, sticky="ew", pady=1)
        tk.Label(name_cell, text=pname, font=("Arial", 10),
                 bg=row_bg, anchor="w", padx=6).pack(side=tk.LEFT)
        if pmult != 0:
            tk.Label(name_cell, text=f"(x1.{pmult})", font=("Arial", 7),
                     fg="#555555", bg=row_bg).pack(side=tk.LEFT)

        # Győzelmi pontok + opcionális másodlagos pont
        pts_cell = tk.Frame(table_frame, bg=row_bg)
        pts_cell.grid(row=grid_row, column=1, sticky="ew", pady=1)
        tk.Label(pts_cell, text=str(match_points), font=("Arial", 10),
                 bg=row_bg, anchor="e").pack(side=tk.LEFT, padx=(6, 1))
        if sec_points is not None:
            tk.Label(pts_cell, text=f"({sec_points})", font=("Arial", 7),
                     fg="#777777", bg=row_bg).pack(side=tk.LEFT, padx=(0, 4))

        # Helyezés
        rank_colors = {1: "#B8860B", 2: "#808080", 3: "#8B4513"}
        rank_fg = rank_colors.get(rank, "#333333")
        tk.Label(table_frame, text=str(rank), font=("Arial", 10, "bold"),
                 fg=rank_fg, bg=row_bg, anchor="center").grid(row=grid_row, column=2, sticky="ew")

        # Bajnoki pontok
        tk.Label(table_frame, text=f"+{party_points}", font=("Arial", 10, "bold"),
                 fg="#1B5E20", bg=row_bg, anchor="e", padx=6).grid(row=grid_row, column=3, sticky="ew")

    return card


def _build_new_match_form(mc_inner, mc_canvas, players, party_id, is_closed,
                          new_match_btn_ref, new_match_form_ref,
                          player_map, calc_party_points, refresh_ranglista):
    """Új meccs rögzítő form, a meccs lista tetején jelenik meg."""

    GREEN   = "#4CAF50"
    RED_BTN = "#f44336"
    GOLD    = "#FFC107"
    GOLD_HDR = "#FF8F00"
    ROW_A   = "#FFF8E1"
    ROW_B   = "#FFECB3"

    # Meglévő kártyák elmentése a forma létrehozása előtt
    existing = mc_inner.winfo_children()[:]

    form = tk.Frame(mc_inner, relief="ridge", bd=2, bg=GOLD, padx=4, pady=4)
    form.pack(fill=tk.X, padx=4, pady=6)
    # Form mozgatása a lista elejére: form elöl, utána a többi
    for child in existing:
        child.pack_forget()
        child.pack(fill=tk.X, padx=4, pady=6)

    new_match_form_ref[0] = form

    def destroy_form():
        form.destroy()
        new_match_form_ref[0] = None
        if new_match_btn_ref[0]:
            new_match_btn_ref[0].pack(side=tk.LEFT, padx=(12, 0))

    # Fejléc
    tk.Label(form, text="Új meccs:", font=("Arial", 11, "bold"),
             bg=GOLD, fg="#1A237E").pack(anchor="w", padx=4, pady=(2, 4))

    # 1. sor: Cím + Súlyozás
    row1 = tk.Frame(form, bg=GOLD)
    row1.pack(fill=tk.X, padx=2, pady=(0, 4))

    tk.Label(row1, text="Cím:", font=("Arial", 10, "bold"), bg=GOLD).pack(side=tk.LEFT, padx=(4, 2))
    title_var = tk.StringVar()
    tk.Entry(row1, textvariable=title_var, font=("Arial", 10),
             bg="#FFFDE7", relief="solid", bd=1, width=22).pack(side=tk.LEFT, padx=(0, 12))

    tk.Label(row1, text="súlyozás:", font=("Arial", 10, "bold"), bg=GOLD).pack(side=tk.LEFT, padx=(0, 2))
    weight_var = tk.StringVar(value="100")
    tk.Spinbox(row1, from_=0, to=1000, increment=10,
               textvariable=weight_var, font=("Arial", 10),
               width=5, relief="solid", bd=1).pack(side=tk.LEFT, padx=(0, 2))
    tk.Label(row1, text="%", font=("Arial", 10, "bold"), bg=GOLD).pack(side=tk.LEFT)

    # Táblázat fejléc
    tbl = tk.Frame(form, bg=GOLD_HDR)
    tbl.pack(fill=tk.X, pady=(4, 0))
    tbl.columnconfigure(0, weight=3)
    tbl.columnconfigure(1, weight=2)
    tbl.columnconfigure(2, weight=3)

    for col_i, (txt, anch) in enumerate([("név", "w"), ("játszott?", "center"), ("győzelmi pontok", "center")]):
        tk.Label(tbl, text=txt, font=("Arial", 9, "bold"),
                 bg=GOLD_HDR, fg="white", anchor=anch, padx=6).grid(
                 row=0, column=col_i, sticky="ew", pady=3)

    # Játékos sorok
    played_vars = {}
    points_vars = {}

    for i, (pid, pname, pmult) in enumerate(players):
        row_bg = ROW_A if i % 2 == 0 else ROW_B
        played_var = tk.BooleanVar(value=True)
        points_var = tk.StringVar()
        played_vars[pid] = played_var
        points_vars[pid] = points_var

        tk.Label(tbl, text=pname, font=("Arial", 10),
                 bg=row_bg, anchor="w", padx=6).grid(row=i+1, column=0, sticky="ew", pady=1)

        cb = tk.Checkbutton(tbl, variable=played_var,
                            bg=row_bg, activebackground=row_bg,
                            relief="flat", cursor="hand2")
        cb.grid(row=i+1, column=1, sticky="ew")

        tk.Entry(tbl, textvariable=points_var, font=("Arial", 10),
                 bg="#FFFDE7", relief="solid", bd=1,
                 justify="center").grid(row=i+1, column=2, sticky="ew", padx=4, pady=1)

    # Győztes sor
    win_row = tk.Frame(form, bg="#FFA000")
    win_row.pack(fill=tk.X, pady=(6, 0))

    tk.Label(win_row, text="Győztes:", font=("Arial", 10, "bold"),
             bg="#FFA000", fg="white").pack(side=tk.LEFT, padx=(8, 6))
    win_con_var = tk.StringVar(value="legtöbb")
    win_con_menu = tk.OptionMenu(win_row, win_con_var, "legtöbb", "legkevesebb")
    win_con_menu.config(font=("Arial", 10), bg="#FFFDE7", relief="solid")
    win_con_menu.pack(side=tk.LEFT)

    # Gombok
    btn_row = tk.Frame(form, bg=GOLD)
    btn_row.pack(fill=tk.X, pady=(8, 4))

    tk.Button(btn_row, text="Kész", font=("Arial", 11, "bold"),
              bg=GREEN, fg="white", padx=20, pady=4,
              command=lambda: _handle_save_match(
                  title_var, weight_var, played_vars, points_vars, win_con_var,
                  players, party_id, player_map, calc_party_points,
                  form, new_match_btn_ref, new_match_form_ref, mc_inner, mc_canvas,
                  refresh_ranglista
              )).pack(side=tk.LEFT, padx=(8, 6))

    tk.Button(btn_row, text="Mégse", font=("Arial", 11, "bold"),
              bg=RED_BTN, fg="white", padx=20, pady=4,
              command=destroy_form).pack(side=tk.LEFT)

    form.update_idletasks()
    mc_canvas.configure(scrollregion=mc_canvas.bbox("all"))


def _handle_save_match(title_var, weight_var, played_vars, points_vars, win_con_var,
                       players, party_id, player_map, calc_party_points,
                       form, new_match_btn_ref, new_match_form_ref, mc_inner, mc_canvas,
                       refresh_ranglista):
    """Validálja és menti az új meccset."""

    # Validáció: Cím
    title = title_var.get().strip()
    if not title:
        messagebox.showwarning("Hiányzó adat", "Kérlek add meg a meccs címét!")
        return

    # Validáció: Súlyozás
    weight_str = weight_var.get().strip()
    try:
        weight = int(weight_str)
        if weight % 10 != 0:
            raise ValueError
        if not (0 <= weight <= 1000):
            raise ValueError
    except ValueError:
        messagebox.showwarning("Hibás súlyozás",
            "A súlyozás csak 10-zel osztható egész szám lehet (0–1000).\n"
            "Az egyszerűség kedvéért kérlek kerekítsd a legközelebbi tízes értékre!")
        return

    # Aktív játékosok összegyűjtése
    active = []
    for pid, pname, pmult in players:
        if played_vars[pid].get():
            active.append((pid, pname, pmult, points_vars[pid].get().strip()))

    if len(active) < 1:
        messagebox.showwarning("Hiányzó adat", "Legalább egy játékosnak játszania kell!")
        return

    # Validáció: Pontok
    for pid, pname, pmult, pts_str in active:
        if pts_str == "":
            messagebox.showwarning("Hiányzó pont",
                f"'{pname}' játékos részt vett, de nem adtál meg győzelmi pontot!")
            return
        try:
            int(pts_str)
        except ValueError:
            messagebox.showwarning("Hibás pont",
                f"'{pname}' győzelmi pontja csak egész szám lehet!")
            return

    active_pts = [(pid, pname, pmult, int(pts_str)) for pid, pname, pmult, pts_str in active]

    win_con_raw = win_con_var.get()
    win_con_db = "max" if win_con_raw == "legtöbb" else "min"
    reverse_sort = (win_con_db == "max")

    active_pts.sort(key=lambda x: x[3], reverse=reverse_sort)

    # Döntetlen ellenőrzés
    tied_result = _check_and_resolve_ties(active_pts, reverse_sort)
    if tied_result is None:
        return
    active_pts = tied_result

    # Helyezések kiosztása
    ranked = _assign_ranks(active_pts, reverse=reverse_sort)

    unique_ranks = sorted(set(r[5] for r in ranked))
    n_effective = len(unique_ranks)

    # Mentés adatbázisba
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute(
            "INSERT INTO matches (party_id, game_name, weighting, win_con) VALUES (%s, %s, %s, %s)",
            (party_id, title, weight, win_con_db)
        )
        match_id = cursor.lastrowid

        for pid, pname, pmult, match_pts, sec_pts, rank in ranked:
            party_pts = calc_party_points(n_effective, rank, weight, pmult)
            cursor.execute(
                "INSERT INTO match_results (match_id, player_id, `rank`, match_points, sec_match_points, party_points) "
                "VALUES (%s, %s, %s, %s, %s, %s)",
                (match_id, pid, rank, match_pts, sec_pts, party_pts)
            )

        conn.commit()
    except Error as e:
        messagebox.showerror("Adatbázis hiba", f"Hiba történt: {e}")
        return
    finally:
        if 'conn' in locals() and conn.is_connected():
            cursor.close()
            conn.close()

    # Form eltüntetése, gomb visszahozása
    form.destroy()
    new_match_form_ref[0] = None
    if new_match_btn_ref[0]:
        new_match_btn_ref[0].pack(side=tk.LEFT, padx=(12, 0))

    # Új meccs kártya megjelenítése a lista TETEJÉN
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, game_name, date, weighting, win_con FROM matches WHERE id = %s",
            (match_id,)
        )
        new_match = cursor.fetchone()
        cursor.execute(
            "SELECT player_id, `rank`, match_points, sec_match_points "
            "FROM match_results WHERE match_id = %s ORDER BY match_points DESC",
            (match_id,)
        )
        new_results = cursor.fetchall()
        # → [(player_id, rank, match_points, sec_match_points), ...]
    except Error as e:
        messagebox.showerror("Adatbázis hiba", f"Meccs betöltése sikertelen: {e}")
        return
    finally:
        if 'conn' in locals() and conn.is_connected():
            cursor.close()
            conn.close()

    mid, gname, mdate, mweight, mwin_con = new_match

    # Összes meglévő kártya törlése és újraépítése az új meccsel elöl
    for child in mc_inner.winfo_children():
        child.destroy()

    # Új meccs kártya elsőnek
    _build_match_card(mc_inner, mid, gname, mdate, mweight, mwin_con,
                      new_results, player_map, calc_party_points, party_id,
                      is_closed=False)

    # Többi meccs lekérése és megjelenítése sorban
    try:
        conn2 = get_db_connection()
        cursor2 = conn2.cursor()
        cursor2.execute(
            "SELECT id, game_name, date, weighting, win_con FROM matches "
            "WHERE party_id = %s AND id != %s ORDER BY date DESC",
            (party_id, match_id)
        )
        rest_matches = cursor2.fetchall()
        rest_results = {}
        if rest_matches:
            rest_ids = [m[0] for m in rest_matches]
            fmt2 = ",".join(["%s"] * len(rest_ids))
            cursor2.execute(
                f"SELECT match_id, player_id, `rank`, match_points, sec_match_points "
                f"FROM match_results WHERE match_id IN ({fmt2})",
                rest_ids
            )
            for row in cursor2.fetchall():
                rest_results.setdefault(row[0], []).append(row[1:])
    except Error as e:
        messagebox.showerror("Adatbázis hiba", f"Meccsek betöltése sikertelen: {e}")
        rest_matches = []
    finally:
        if 'conn2' in locals() and conn2.is_connected():
            cursor2.close()
            conn2.close()

    for (rmid, rgname, rmdate, rmweight, rmwin_con) in rest_matches:
        _build_match_card(mc_inner, rmid, rgname, rmdate, rmweight, rmwin_con,
                          rest_results.get(rmid, []), player_map, calc_party_points,
                          party_id, is_closed=False)

    refresh_ranglista()
    mc_canvas.configure(scrollregion=mc_canvas.bbox("all"))


def _check_and_resolve_ties(active_pts, reverse_sort):
    """
    Ellenőrzi van-e döntetlen a fő pontokban.
    Ha igen, felugró ablakban kéri a másodlagos pontokat.
    Visszatér a (pid, pname, pmult, match_pts, sec_pts) listával, vagy None ha megszakítva.
    """
    from collections import defaultdict

    groups = defaultdict(list)
    for pid, pname, pmult, pts in active_pts:
        groups[pts].append((pid, pname, pmult, pts))

    tied_groups = {pts: members for pts, members in groups.items() if len(members) > 1}

    if not tied_groups:
        return [(pid, pname, pmult, pts, None) for pid, pname, pmult, pts in active_pts]

    dialog = tk.Toplevel(root)
    dialog.title("Döntetlen törés")
    dialog.grab_set()
    dialog.resizable(False, False)

    tk.Label(dialog, text="Döntetlen pontállás!",
             font=("Arial", 13, "bold"), fg="#B71C1C").pack(padx=20, pady=(14, 4))
    tk.Label(dialog,
             text="Az alábbi játékosoknak egyenlő a pontjuk.\n"
                  "Adj meg másodlagos pontokat a döntetlen töréshez.\n"
                  "Ha üresen hagyod, abszolút döntetlen lesz (azonos helyezés).\n"
                  "A döntetlen törésben mindig a TÖBB másodlagos pont nyer.",
             font=("Arial", 9), fg="#555555", justify="left").pack(padx=20, pady=(0, 10))

    sec_vars = {}

    for pts_val, members in sorted(tied_groups.items(), reverse=reverse_sort):
        grp_frame = tk.LabelFrame(dialog, text=f"Döntetlen: {pts_val} pont",
                                  font=("Arial", 9, "bold"), fg="#E65100",
                                  padx=8, pady=6)
        grp_frame.pack(fill=tk.X, padx=16, pady=4)

        for pid, pname, pmult, _ in members:
            row = tk.Frame(grp_frame)
            row.pack(fill=tk.X, pady=2)
            tk.Label(row, text=f"{pname}  ({pts_val} pont)",
                     font=("Arial", 10), width=24, anchor="w").pack(side=tk.LEFT)
            sec_var = tk.StringVar()
            sec_vars[pid] = sec_var
            tk.Entry(row, textvariable=sec_var, font=("Arial", 10),
                     width=8, relief="solid", bd=1,
                     justify="center").pack(side=tk.LEFT, padx=(6, 0))
            tk.Label(row, text="mp.", font=("Arial", 9),
                     fg="#777777").pack(side=tk.LEFT, padx=2)

    result_holder = [None]

    def on_ok():
        sec_values = {}
        for pid, sv in sec_vars.items():
            val = sv.get().strip()
            if val == "":
                sec_values[pid] = None
            else:
                try:
                    sec_values[pid] = int(val)
                except ValueError:
                    messagebox.showwarning("Hibás adat",
                        "A másodlagos pontok csak egész számok lehetnek!",
                        parent=dialog)
                    return
        result_holder[0] = sec_values
        dialog.destroy()

    def on_cancel():
        dialog.destroy()

    btn_row = tk.Frame(dialog)
    btn_row.pack(pady=12)
    tk.Button(btn_row, text="OK", font=("Arial", 11, "bold"),
              bg="#4CAF50", fg="white", padx=18,
              command=on_ok).pack(side=tk.LEFT, padx=6)
    tk.Button(btn_row, text="Mégse", font=("Arial", 11, "bold"),
              bg="#f44336", fg="white", padx=14,
              command=on_cancel).pack(side=tk.LEFT, padx=6)

    dialog.wait_window()

    if result_holder[0] is None:
        return None

    sec_values = result_holder[0]

    result = []
    for pid, pname, pmult, pts in active_pts:
        sec = sec_values.get(pid, None)
        result.append((pid, pname, pmult, pts, sec))
    return result


def _assign_ranks(active_with_sec, reverse=True):
    """
    Helyezések kiosztása holtversennyel.
    Input:  [(pid, pname, pmult, match_pts, sec_pts), ...]
    Output: [(pid, pname, pmult, match_pts, sec_pts, rank), ...]
    reverse=True  → több pont = jobb helyezés (max win_con)
    reverse=False → kevesebb pont = jobb helyezés (min win_con)
    A másodlagos pont törésben mindig több = jobb.
    """
    # Sec pont: ha reverse=True, nagyobb sec jobb (float('-inf') a None helyett)
    #           ha reverse=False, kisebb fő jobb, de sec-nél még mindig nagyobb = jobb
    # Megoldás: sec-t mindig ugyanolyan irányban kezeljük mint a fő pontot,
    # kivéve hogy a sec törés iránya mindig "több = jobb" marad.
    # Ezért sec-et külön kezeljük: fő pontot rendezzük reverse szerint,
    # sec-et pedig mindig csökkenően (nagyobb sec = jobb).
    def sort_key(x):
        mp = x[3]
        sec = x[4] if x[4] is not None else float('-inf')
        # Ha reverse=False (min), a kisebb fő pont legyen elöl → negáljuk
        return (-mp if not reverse else mp, sec)

    sorted_list = sorted(active_with_sec, key=sort_key, reverse=True)

    ranked = []
    rank = 1
    i = 0
    while i < len(sorted_list):
        pid, pname, pmult, mp, sec = sorted_list[i]
        j = i + 1
        while j < len(sorted_list):
            _, _, _, mp2, sec2 = sorted_list[j]
            if mp2 == mp and (sec2 == sec or (sec is None and sec2 is None)):
                j += 1
            else:
                break
        for k in range(i, j):
            p = sorted_list[k]
            ranked.append((p[0], p[1], p[2], p[3], p[4], rank))
        rank += (j - i)
        i = j

    return ranked


def _confirm_delete_match(match_id, game_name, mc_inner_parent, party_id):
    """Megerősítés után törli a meccset és frissíti a parti képernyőt."""
    confirm = messagebox.askyesno(
        "Meccs törlése",
        f"Biztosan törölni szeretnéd a(z) '{game_name}' meccset?\nAz összes eredménye is törlődik!"
    )
    if not confirm:
        return

    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM matches WHERE id = %s", (match_id,))
        conn.commit()
        messagebox.showinfo("Siker", f"'{game_name}' meccs törölve.")
    except Error as e:
        messagebox.showerror("Adatbázis hiba", f"Hiba történt: {e}")
        return
    finally:
        if 'conn' in locals() and conn.is_connected():
            cursor.close()
            conn.close()

    global party_detail_frame
    if party_detail_frame:
        party_detail_frame.destroy()
        party_detail_frame = None
    show_party_detail(party_id)


def hide_party_detail():
    global party_detail_frame, dashboard_frame

    if party_detail_frame:
        party_detail_frame.destroy()
        party_detail_frame = None

    if dashboard_frame:
        dashboard_frame.destroy()
    root.title("BG Party Pointer - Főoldal")
    show_dashboard(current_username_global)


def handle_delete_party(party_id, party_name):
    confirm = messagebox.askyesno(
        "Parti törlése",
        f"Biztosan törölni szeretnéd a(z) '{party_name}' partít?\n"
        "Ez az összes meccset és eredményt is törli!"
    )
    if not confirm:
        return

    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM parties WHERE id = %s AND user_id = %s",
                       (party_id, current_user_id))
        conn.commit()
        messagebox.showinfo("Siker", f"'{party_name}' parti törölve.")
        hide_party_detail()
    except Error as e:
        messagebox.showerror("Adatbázis hiba", f"Hiba történt: {e}")
    finally:
        if 'conn' in locals() and conn.is_connected():
            cursor.close()
            conn.close()


def handle_close_party(party_id, party_name):
    confirm = messagebox.askyesno(
        "Parti lezárása",
        f"Biztosan le szeretnéd zárni a(z) '{party_name}' partít?\n"
        "Lezárás után nem lehet több meccset hozzáadni!"
    )
    if not confirm:
        return

    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE parties SET is_closed = 1, closed_date = NOW() "
            "WHERE id = %s AND user_id = %s",
            (party_id, current_user_id)
        )
        conn.commit()
        messagebox.showinfo("Siker", f"'{party_name}' parti lezárva.")
        global party_detail_frame
        if party_detail_frame:
            party_detail_frame.destroy()
            party_detail_frame = None
        show_party_detail(party_id)
    except Error as e:
        messagebox.showerror("Adatbázis hiba", f"Hiba történt: {e}")
    finally:
        if 'conn' in locals() and conn.is_connected():
            cursor.close()
            conn.close()


# ==========================================
# ÚJ PARTI KÉSZÍTÉSE KÉPERNYŐ
# ==========================================

def show_create_party():
    global create_party_frame, player_rows, players_inner_frame
    global add_player_button_widget, party_name_entry_widget, party_desc_text_widget

    player_rows = []

    dashboard_frame.pack_forget()
    root.title("BG Party Pointer - Új Parti")

    create_party_frame = tk.Frame(root, padx=20, pady=15)
    create_party_frame.pack(fill=tk.BOTH, expand=True)

    header = tk.Frame(create_party_frame)
    header.pack(fill=tk.X, pady=(0, 14))

    tk.Label(header, text="Új Parti készítése",
             font=("Arial", 20, "bold"), fg="#333333").pack(side=tk.LEFT)
    tk.Button(header, text="Vissza", command=hide_create_party,
              font=("Arial", 12, "bold"), bg="#f44336", fg="white", padx=14).pack(side=tk.RIGHT)

    content = tk.Frame(create_party_frame)
    content.pack(fill=tk.BOTH, expand=True)

    left = tk.Frame(content, padx=8)
    left.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    tk.Label(left, text="Játékosok:", font=("Arial", 13, "bold")).pack(anchor="w", pady=(0, 6))

    canvas = tk.Canvas(left, highlightthickness=0, bg=root.cget("bg"))
    canvas.pack(fill=tk.BOTH, expand=True)

    players_inner_frame = tk.Frame(canvas, bg=root.cget("bg"))
    win_id = canvas.create_window((0, 0), window=players_inner_frame, anchor="nw")

    players_inner_frame.bind("<Configure>",
        lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
    canvas.bind("<Configure>",
        lambda e: canvas.itemconfig(win_id, width=e.width))

    _build_player_row()

    add_player_button_widget = tk.Button(
        players_inner_frame, text="  +  ",
        font=("Arial", 14, "bold"), bg="#FF8C00", fg="white",
        command=add_player_row
    )
    add_player_button_widget.pack(pady=(10, 2), anchor="w")

    tk.Frame(content, width=2, bg="#cccccc").pack(side=tk.LEFT, fill=tk.Y, padx=14)

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
    add_player_button_widget.pack_forget()
    _build_player_row()
    add_player_button_widget.pack(pady=(10, 2), anchor="w")


def handle_finalize_party():
    party_name = party_name_entry_widget.get().strip()
    description = party_desc_text_widget.get("1.0", tk.END).strip()

    valid_players = []
    for name_var, mult_var in player_rows:
        name = name_var.get().strip()
        if name:
            try:
                mult = max(0, min(9, int(mult_var.get())))
            except ValueError:
                mult = 0
            valid_players.append((name, mult))

    if not party_name:
        messagebox.showwarning("Hiba", "A parti nevét kötelező megadni!")
        return

    if not valid_players:
        messagebox.showwarning("Hiba", "Legalább egy játékos nevét meg kell adni!")
        return

    lower_names = [p[0].lower() for p in valid_players]
    if len(lower_names) != len(set(lower_names)):
        messagebox.showerror("Hiba", "Nem lehet 2 játékosnak ugyanaz a neve!")
        return

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
    global create_party_frame, dashboard_frame

    if create_party_frame:
        create_party_frame.destroy()
        create_party_frame = None

    if dashboard_frame:
        dashboard_frame.destroy()

    root.title("BG Party Pointer - Főoldal")
    show_dashboard(current_username_global)


# ==========================================
# ALAP ABLAK ÉS BEJELENTKEZŐ FELÜLET
# ==========================================

root = tk.Tk()
root.title("BG Party Pointer - Bejelentkezés")
root.geometry("900x600")
root.resizable(True, True)
root.eval('tk::PlaceWindow . center')

login_frame = tk.Frame(root, padx=40, pady=40)
login_frame.pack(fill=tk.BOTH, expand=True)

title_label = tk.Label(login_frame, text="Bejelentkezés / Regisztráció", font=("Arial", 24, "bold"))
title_label.pack(pady=(0, 30))

username_label = tk.Label(login_frame, text="Felhasználónév:", font=("Arial", 16))
username_label.pack(pady=(0, 5))

username_entry = tk.Entry(login_frame, font=("Arial", 16), width=35)
username_entry.pack(pady=(0, 20))

password_label = tk.Label(login_frame, text="Jelszó:", font=("Arial", 16))
password_label.pack(pady=(0, 5))

password_entry = tk.Entry(login_frame, font=("Arial", 16), width=35, show="*")
password_entry.pack(pady=(0, 35))

button_frame = tk.Frame(login_frame)
button_frame.pack(fill=tk.X)

login_button = tk.Button(button_frame, text="Bejelentkezés", command=handle_login,
                         font=("Arial", 14, "bold"), width=15, bg="#4CAF50", fg="white")
login_button.pack(side=tk.LEFT, padx=(10, 20), ipady=5)

register_button = tk.Button(button_frame, text="Regisztráció", command=handle_register,
                            font=("Arial", 14, "bold"), width=15, bg="#2196F3", fg="white")
register_button.pack(side=tk.RIGHT, padx=(20, 10), ipady=5)

root.mainloop()