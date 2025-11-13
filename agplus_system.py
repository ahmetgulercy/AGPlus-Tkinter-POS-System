# agplus_system_v1.0.py  (Beyaz Tema, Stabil + İstenen Fixler)
# Development by Ahmet GULER - Turkish Hacker - Cyber Security Researcher - Malware Analyst - Software Developer
# Contact;
# www.instagram.com/benahmetguler/
# x.com/ahmetgulercyb
# tr.linkedin.com/in/ahmetgulerhacker

# This work has been done for the first time. I’m fully aware that it is not a high-level project yet, but it is still under development. 
# I thought the basic skeleton structure might be useful for you as well. The developed structure is currently being used by some businesses.
# Please feel free to contact me if you have any questions. Thx <3

import tkinter as tk
from tkinter import ttk, messagebox
import json, datetime, copy, os
from pathlib import Path
import sys
from pathlib import Path
import os

# --------------------- Sabitler / Tema ---------------------
# DATA_FILE = APP_DIR / "data.json"
# DAYEND_DIR = APP_DIR / "gunsonu_kayitlari"

# ---- YENİ KALICI DOSYA YOLLARI (Ürünler artık silinmeyecek) ----
BASE_DATA_DIR = Path(os.environ["APPDATA"]) / "AGPlusAdisyon"
BASE_DATA_DIR.mkdir(parents=True, exist_ok=True)

DATA_FILE = BASE_DATA_DIR / "data.json"
DAYEND_DIR = BASE_DATA_DIR / "gunsonu_kayitlari"
DAYEND_DIR.mkdir(exist_ok=True)

DEFAULT_PIN = "1234"

COL = {
    "bg": "#FFFFFF",          # Beyaz ana arkaplan
    "panel": "#FFFFFF",       # Paneller beyaz
    "border": "#E5E7EB",      # İnce gri sınır
    "text": "#111827",        # Koyu metin
    "muted": "#6B7280",       # Açıklama metinleri
    "primary": "#1D4ED8",     # Mavi
    "danger": "#DC2626",      # Kırmızı
    "success": "#16A34A",     # Yeşil
    "table_empty": "#FFEB3B", # Sarı (boş masa)
    "table_open": "#EF4444",  # Kırmızı (açık masa)
    "order_yellow": "#FFF4AF",# Sipariş listesi sarımsı
    "heading": "#F3F4F6",     # Tablo başlık gri
    "blue_btn": "#2563EB"     # Genel durum butonu
}

FONT_SM = ("Segoe UI", 10)
FONT_MD = ("Segoe UI", 12)
FONT_LG = ("Segoe UI Semibold", 14)
FONT_XL = ("Segoe UI Semibold", 18)

def today_str():
    return datetime.date.today().isoformat()

def now_str():
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def time_hhmm():
    return datetime.datetime.now().strftime("%H:%M")

# Varsayılan veri: Artık sadece Bahçe/Havuz/Daire masaları var
DEFAULT_TABLES = {}
for area in ("Bahçe", "Havuz", "Daire"):
    for i in range(1, 21):
        DEFAULT_TABLES[f"{area} {i}"] = {"open": False, "items": [], "total": 0.0}

DEFAULT_DATA = {
    "last_reset": today_str(),
    "categories": [
        "KAHVALTI","SALATA","ÇORBA","IZGARA","DÖNER","TATLI","İÇECEKLER","SICAK İÇECEKLER"
    ],
    "products": [],
    "tables": DEFAULT_TABLES,
    "sales": []  # {table, amount, method, ts}
}

# --------------------- Veri ---------------------
def load_data():
    # İlk çalıştırma ise varsayılan data oluştur
    if not DATA_FILE.exists():
        save_data(DEFAULT_DATA)

    with open(DATA_FILE, "r", encoding="utf-8") as f:
        d = json.load(f)

    changed = False

    # Eksik anahtarları tamamla (categories, products, tables, sales vs.)
    for k, v in DEFAULT_DATA.items():
        if k not in d:
            d[k] = copy.deepcopy(v)
            changed = True

    old_tables = d.get("tables", {})
    new_tables = {}
    if isinstance(old_tables, dict):
        for key, val in old_tables.items():
            if isinstance(key, str) and key.startswith(("Bahçe ", "Havuz ", "Daire ")):
                new_tables[key] = val
    d["tables"] = new_tables

    # Zorunlu tüm Bahçe/Havuz/Daire 1..20 masalarını oluştur (eksik olanları ekle)
    for area in ("Bahçe", "Havuz", "Daire"):
        for i in range(1, 21):
            name = f"{area} {i}"
            if name not in d["tables"]:
                d["tables"][name] = {"open": False, "items": [], "total": 0.0}
                changed = True

    # last_reset'i bugüne çek (eski mekanizma ile uyum için)
    if d.get("last_reset") != today_str():
        d["last_reset"] = today_str()
        changed = True

    if changed:
        save_data(d)

    return d

def save_data(d):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(d, f, ensure_ascii=False, indent=2)

# --------------------- Scrollable yardımcıları ---------------------
class ScrollableFrame(tk.Frame):
    """Beyaz tema korunarak dikey scroll sağlayan sarmalayıcı."""
    def __init__(self, master, bg=None, **kwargs):
        super().__init__(master, bg=bg or COL["panel"], **kwargs)
        self.canvas = tk.Canvas(self, bg=bg or COL["panel"], highlightthickness=0)
        self.vsb = tk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.inner = tk.Frame(self.canvas, bg=bg or COL["panel"])
        self.inner_id = self.canvas.create_window((0,0), window=self.inner, anchor="nw")

        self.canvas.configure(yscrollcommand=self.vsb.set)
        self.canvas.pack(side="left", fill="both", expand=True)
        self.vsb.pack(side="right", fill="y")

        self.inner.bind("<Configure>", self._on_configure)
        self.canvas.bind("<Configure>", self._on_canvas_config)
        # Fare çarkı
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)
        self.canvas.bind_all("<Button-4>", self._on_mousewheel)
        self.canvas.bind_all("<Button-5>", self._on_mousewheel)

    def _on_configure(self, _e):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def _on_canvas_config(self, e):
        self.canvas.itemconfig(self.inner_id, width=e.width)

    def _on_mousewheel(self, e):
        delta = 0
        if getattr(e, "num", None) == 4:
            delta = -1
        elif getattr(e, "num", None) == 5:
            delta = 1
        else:
            delta = -1 * int(e.delta/120)
        self.canvas.yview_scroll(delta, "units")

# --------------------- Uygulama ---------------------
class App:
    def __init__(self, root):
        self.root = root
        self.data = load_data()

        # Varsayılan kategori (BAHÇE) 
        self.current_area = "Bahçe"

        root.title("Adisyon – BAHÇE")
        root.geometry("1200x720")
        root.minsize(1024, 640)
        root.configure(bg=COL["bg"])

        self.table_buttons = {}
        # Otomatik sıfırlama ZAMANLAYICILARI KALDIRILDI (23:59 yok)
        # Footer periyodik güncelle kalsın
        self.root.after(60_000, self._tick_update_footer)

        # Login: ana pencere login'e kadar gizli
        self.root.withdraw()
        self.show_login()

    def _tick_update_footer(self):
        try:
            if hasattr(self, "footer_label") and self.footer_label.winfo_exists():
                total = sum(s.get("amount", 0.0) for s in self.data.get("sales", []))
                self.footer_label.config(text=f"Bugün toplam satış: {total:.2f}₺")
        finally:
            self.root.after(60_000, self._tick_update_footer)

    # --- pencere temizle ---
    def clear(self):
        for w in self.root.winfo_children():
            w.destroy()
        self.root.configure(bg=COL["bg"])  # beyaz

    # ---------------- Login ----------------
    def show_login(self):
        self.clear()
        LoginDialog(self, on_success=self._after_login)

    def _after_login(self):
        # Login OK → ana pencereyi göster
        self.root.deiconify()
        self.show_main()

    # ---------------- Main -----------------
    def show_main(self):
        self.clear()
        # Üst satır (tema/tasarım korunuyor)
        top = tk.Frame(self.root, bg=COL["bg"])
        top.pack(fill="x", pady=(12, 6))

        # Sol kısım: alan başlığı ve alan seçim butonları (renk/tema korunarak)
        left_head = tk.Frame(top, bg=COL["bg"])
        left_head.pack(side="left", padx=12)
        self.title_lbl = tk.Label(left_head, text=self.current_area.upper(), bg=COL["bg"], fg=COL["text"], font=FONT_XL)
        self.title_lbl.pack(side="left")

        # Kategori (Bahçe/Havuz/Daire) butonları — mevcut tema ile düz butonlar
        area_wrap = tk.Frame(left_head, bg=COL["bg"])
        area_wrap.pack(side="left", padx=12)
        for area in ("Bahçe", "Havuz", "Daire"):
            tk.Button(area_wrap, text=area, font=FONT_MD, bg=COL["panel"], bd=1, relief="solid",
                      command=lambda a=area: self.switch_area(a)).pack(side="left", padx=4)

        # Sağdan sola mevcut butonlar (tasarım korunur)
        tk.Button(top, text="ÇIKIŞ", font=FONT_LG, bg=COL["panel"], bd=1, relief="solid",
                  command=self.show_login).pack(side="right", padx=6)
        tk.Button(top, text="RAPOR GÖRÜNTÜLE", font=FONT_LG, bg=COL["panel"], bd=1, relief="solid",
                  command=self.view_report).pack(side="right", padx=6)
        tk.Button(top, text="GÜN SONU", font=FONT_LG, bg=COL["panel"], bd=1, relief="solid",
                  command=self.day_end_info).pack(side="right", padx=6)
        tk.Button(top, text="ÜRÜN YÖNETİMİ", font=FONT_LG, bg=COL["panel"], bd=1, relief="solid",
                  command=self.manage_products).pack(side="right", padx=6)
        tk.Button(top, text="GENEL DURUM", font=FONT_LG, fg="white", bg=COL["blue_btn"], bd=0,
                  command=self.general_status).pack(side="right", padx=6)

        # Masalar paneli (scroll ile)
        grid_panel = tk.Frame(self.root, bg=COL["panel"], highlightbackground=COL["border"], highlightthickness=1)
        grid_panel.pack(fill="both", expand=True, padx=12, pady=8)
        tk.Label(grid_panel, text="Masalar", bg=COL["panel"], fg=COL["text"], font=FONT_LG).pack(anchor="w", padx=12, pady=8)

        # Scrollable alan
        self.tables_scroll = ScrollableFrame(grid_panel, bg=COL["panel"])
        self.tables_scroll.pack(fill="both", expand=True, padx=0, pady=(0,8))
        self.table_buttons = {}
        self._render_tables_in_scroll()

        # Alt bilgi
        bottom = tk.Frame(self.root, bg=COL["bg"])
        bottom.pack(fill="x")
        total = sum(s.get("amount", 0.0) for s in self.data.get("sales", []))
        self.footer_label = tk.Label(bottom, text=f"Bugün toplam satış: {total:.2f}₺", bg=COL["bg"], fg=COL["muted"], font=FONT_MD)
        self.footer_label.pack(side="right", padx=12, pady=8)

    def switch_area(self, area):
        self.current_area = area
        self.title_lbl.config(text=self.current_area.upper())
        self._render_tables_in_scroll()

    def _render_tables_in_scroll(self):
        # Önce içeriği temizle
        for c in self.tables_scroll.inner.winfo_children():
            c.destroy()
        self.table_buttons = {}
        cols = 5
        # Seçili alan için 20 masa
        for i in range(1, 21):
            name = f"{self.current_area} {i}"
            t = self.data["tables"].get(name, {"open": False, "total": 0.0, "items": []})
            color = COL["table_open"] if t.get("open") else COL["table_empty"]
            text = f"{name}\n" + (f"{t.get('total',0.0):.2f}₺" if t.get("open") else "")
            b = tk.Button(
                self.tables_scroll.inner, text=text, width=14, height=5, bg=color, fg="#111",
                font=FONT_LG, bd=2, relief="ridge", activebackground=color,
                command=(lambda n=name: (self.open_table(n)))
            )
            r, c = (i-1)//cols, (i-1)%cols
            b.grid(row=r, column=c, padx=12, pady=12)
            self.table_buttons[name] = b
        # Grid genişlemeleri
        for c in range(cols):
            self.tables_scroll.inner.grid_columnconfigure(c, weight=1)

    def refresh_tables(self):
        # Yalnızca görünen alanın masalarını güncelle
        for name, btn in self.table_buttons.items():
            t = self.data["tables"][name]
            btn.configure(
                text=f"{name}\n" + (f"{t['total']:.2f}₺" if t["open"] else ""),
                bg=COL["table_open"] if t["open"] else COL["table_empty"],
                activebackground=COL["table_open"] if t["open"] else COL["table_empty"]
            )
        save_data(self.data)

    def open_table(self, name):
        try:
            TableWindow(self, name)
        except Exception as e:
            import traceback
            traceback.print_exc()
            messagebox.showerror("Hata", f"Masa açılırken sorun oluştu:\n{e}")

    def manage_products(self):
        ProductManager(self)

    def general_status(self):
        GeneralStatusWindow(self)

    def view_report(self):
        ReportWindow(self)

    # --- Gün Sonu (bilgi penceresi + tamamla butonu) ---
    def day_end_info(self):
        DayEndWindow(self)

# --------------------- Login Dialog ---------------------
class LoginDialog:
    def __init__(self, app, on_success):
        self.app = app
        self.on_success = on_success
        self.win = tk.Toplevel(app.root)
        self.win.title("Şifre")
        self.win.geometry("560x460")
        self.win.resizable(False, False)
        self.win.grab_set()
        self.win.attributes("-topmost", True)
        # Kapatılırsa uygulamadan çık
        self.win.protocol("WM_DELETE_WINDOW", app.root.destroy)

        wrap = tk.Frame(self.win, bg="#0F5DB5")
        wrap.pack(fill="both", expand=True)
        tk.Label(wrap, text="Şifre", font=FONT_XL, bg="#0F5DB5", fg="white").pack(pady=(18, 8))
        self.entry = tk.Entry(wrap, font=("Segoe UI", 22), show="*", justify="center", width=10, bd=0)
        self.entry.pack()

        pad = tk.Frame(wrap, bg="#0F5DB5"); pad.pack(pady=10)
        buttons = ["1","2","3","4","5","6","7","8","9","Sil","0","Giriş"]
        for i, t in enumerate(buttons):
            tk.Button(pad, text=t, width=10, height=2, font=FONT_LG,
                      command=lambda x=t: self.press(x)).grid(row=i//3, column=i%3, padx=6, pady=6)

        bottom = tk.Frame(wrap, bg="#0F5DB5"); bottom.pack(side="bottom", fill="x", pady=10)
        tk.Label(bottom, text="Ahmet GÜLER - 0530 704 95 58", bg="#0F5DB5", fg="white", font=FONT_LG).pack()

        # Merkezde aç
        self.win.update_idletasks()
        sw, sh = self.win.winfo_screenwidth(), self.win.winfo_screenheight()
        x = (sw//2) - (560//2); y = (sh//2) - (460//2)
        self.win.geometry(f"560x460+{x}+{y}")
        self.entry.focus_set()

    def press(self, t):
        if t == "Sil":
            cur = self.entry.get()
            self.entry.delete(0, tk.END)
            self.entry.insert(0, cur[:-1])
        elif t == "Giriş":
            if self.entry.get() == DEFAULT_PIN:
                self.win.destroy()
                self.on_success()
            else:
                messagebox.showerror("Hata", "Yanlış şifre")
                self.entry.delete(0, tk.END)
        else:
            self.entry.insert(tk.END, t)

# --------------------- Gün Sonu Penceresi ---------------------
class DayEndWindow:
    def __init__(self, app):
        self.app = app
        self.win = tk.Toplevel(app.root)
        self.win.title("Gün Sonu Bilgi")
        self.win.geometry("820x560")
        self.win.configure(bg=COL["panel"])

        # Özet
        total = sum(s.get("amount", 0.0) for s in app.data.get("sales", []))
        cash = sum(s.get("amount", 0.0) for s in app.data.get("sales", []) if s.get("method") == "Nakit")
        card = total - cash
        open_tables = sum(1 for t in app.data["tables"].values() if t.get("open"))
        head = tk.Frame(self.win, bg=COL["panel"]); head.pack(fill="x", padx=12, pady=(12, 4))
        tk.Label(head, text=f"Bugün Toplam Satış: {total:.2f}₺", font=FONT_LG, bg=COL["panel"]).pack(anchor="w")
        tk.Label(head, text=f"Nakit: {cash:.2f}₺   |   Kart: {card:.2f}₺", font=FONT_LG, bg=COL["panel"]).pack(anchor="w")
        tk.Label(head, text=f"Açık Masa Sayısı: {open_tables}", font=FONT_LG, bg=COL["panel"]).pack(anchor="w")

        # Satış listesi
        style = ttk.Style(self.win)
        style.configure("Treeview.Heading", font=("Segoe UI", 12, "bold"), background=COL['heading'])
        cols = ("Masa", "Tutar", "Yöntem", "Zaman")
        tree = ttk.Treeview(self.win, columns=cols, show="headings")
        for c in cols:
            tree.heading(c, text=c)
            tree.column(c, anchor="center", width=180)
        tree.pack(fill="both", expand=True, padx=12, pady=10)
        for s in app.data.get("sales", []):
            tree.insert("", tk.END, values=(s.get("table"), f"{s.get('amount',0):.2f}₺", s.get("method"), s.get("ts", "-")))

        # Alt butonlar
        footer = tk.Frame(self.win, bg=COL["panel"]); footer.pack(fill="x", padx=12, pady=(0,12))
        tk.Button(footer, text="Gün Sonunu Tamamla", font=FONT_LG, bg=COL["success"], fg="white",
                  command=self._complete_day_end).pack(side="right", padx=6)
        tk.Button(footer, text="Kapat", font=FONT_LG, command=self.win.destroy).pack(side="right", padx=6)

    def _complete_day_end(self):
        if not messagebox.askyesno("Onay", "Gün sonunu tamamlayıp tüm masaları sıfırlamak istiyor musunuz?"):
            return

        # Klasör oluştur
        DAYEND_DIR.mkdir(parents=True, exist_ok=True)
        stamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        out_dir = DAYEND_DIR / stamp
        out_dir.mkdir(exist_ok=True)
        out_file = out_dir / "gunsonu.json"

        # Rapor verisi
        total = sum(s.get("amount", 0.0) for s in self.app.data.get("sales", []))
        cash = sum(s.get("amount", 0.0) for s in self.app.data.get("sales", []) if s.get("method") == "Nakit")
        card = total - cash
        open_tables = sum(1 for t in self.app.data["tables"].values() if t.get("open"))
        rapor = {
            "tarih": today_str(),
            "kapanis_saati": datetime.datetime.now().strftime("%H:%M:%S"),
            "toplam_satis": round(total,2),
            "nakit": round(cash,2),
            "kart": round(card,2),
            "acik_masa_sayisi": open_tables,
            "satis_kayitlari": self.app.data.get("sales", [])
        }
        with open(out_file, "w", encoding="utf-8") as f:
            json.dump(rapor, f, ensure_ascii=False, indent=2)

        # Masaları ve satışları sıfırla (ÜRÜNLERİ SİLMEZ)
        for t in self.app.data["tables"].values():
            t["items"] = []
            t["total"] = 0.0
            t["open"] = False
        self.app.data["sales"] = []
        self.app.data["last_reset"] = today_str()
        save_data(self.app.data)
        self.app._render_tables_in_scroll()

        messagebox.showinfo("Tamamlandı", f"Gün sonu kaydedildi ve sıfırlandı.\n{out_file}")
        self.win.destroy()

# --------------------- Table Window ---------------------
class TableWindow:
    def __init__(self, app, table_name):
        self.app = app
        self.tname = table_name
        self.orig = app.data["tables"][self.tname]
        self.staged = []  # onaylanana kadar geçici

        self.win = tk.Toplevel(app.root)
        self.win.title(self.tname)
        self.win.geometry("1200x700")
        self.win.configure(bg=COL["bg"])
        self.win.protocol("WM_DELETE_WINDOW", self.back_to_main)

        # Üst büyük butonlar (tasarım korunur)
        top = tk.Frame(self.win, bg=COL["panel"], highlightbackground=COL["border"], highlightthickness=1)
        top.pack(fill="x", padx=10, pady=8)
        self.btn_back = tk.Button(top, text="GERİ", font=FONT_LG, width=12, height=2, command=self.back_to_main)
        self.btn_back.pack(side="left", padx=6)
        self.btn_confirm = tk.Button(top, text="SİPARİŞ ONAYI", font=FONT_LG, width=16, height=2, bg=COL["primary"], fg="white", command=self.confirm_order)
        self.btn_confirm.pack(side="left", padx=6)
        self.btn_pay = tk.Button(top, text="ÖDEME AL", font=FONT_LG, width=12, height=2, bg=COL["success"], fg="white", command=self.take_payment)
        self.btn_pay.pack(side="left", padx=6)
        self.btn_exit = tk.Button(top, text="ÇIKIŞ", font=FONT_LG, width=12, height=2, command=self.back_to_main)
        self.btn_exit.pack(side="right", padx=6)

        self._update_confirm_visibility()
        self._update_pay_enabled()

        # Gövde
        body = tk.Frame(self.win, bg=COL["bg"])
        body.pack(fill="both", expand=True, padx=10, pady=6)

        # Sol: Kategoriler (tasarım korunur)
        left = tk.Frame(body, bg=COL["panel"], highlightbackground=COL["border"], highlightthickness=1)
        left.pack(side="left", fill="y")
        self.lbl_cats = tk.Label(left, text="KATEGORİLER", bg=COL["panel"], fg=COL["text"], font=FONT_LG)
        self.lbl_cats.pack(padx=10, pady=(10,6))
        self.lbl_cats.bind("<Double-Button-1>", self._open_category_manager)
        self.cat_wrap = tk.Frame(left, bg=COL["panel"])
        self.cat_wrap.pack(padx=10, pady=6)
        self.selected_category = None
        self._draw_categories()

        # Orta: Ürünler (SCROLL EKLENDİ)
        center = tk.Frame(body, bg=COL["panel"], highlightbackground=COL["border"], highlightthickness=1)
        center.pack(side="left", fill="both", expand=True, padx=10)
        self.prod_title = tk.Label(center, text="Kategori seçiniz", bg=COL["panel"], fg=COL["muted"], font=FONT_MD)
        self.prod_title.pack(anchor="w", padx=10, pady=8)

        self.products_scroll = ScrollableFrame(center, bg=COL["panel"])
        self.products_scroll.pack(fill="both", expand=True, padx=8, pady=8)

        # Sağ: Sipariş listesi
        right = tk.Frame(body, bg=COL["panel"], highlightbackground=COL["border"], highlightthickness=1)
        right.pack(side="right", fill="y")
        tk.Label(right, text="Sipariş", bg=COL["panel"], fg=COL["text"], font=FONT_LG).pack(padx=10, pady=8)
        self.order_list = tk.Listbox(right, width=32, height=22, bg=COL["order_yellow"], font=FONT_MD)
        self.order_list.pack(padx=10)
        self.lbl_total = tk.Label(right, text="Toplam: 0.00₺", bg=COL["panel"], fg=COL["text"], font=FONT_LG)
        self.lbl_total.pack(padx=10, pady=6)
        ctl = tk.Frame(right, bg=COL["panel"])
        ctl.pack(padx=10, pady=(0,10))
        tk.Button(ctl, text="Seçileni Sil", font=FONT_MD, width=12, command=self._remove_selected).pack(side="left", padx=4)
        tk.Button(ctl, text="Tümünü Sil", font=FONT_MD, width=12, command=self._clear_all).pack(side="left", padx=4)

        self._refresh_order_list()

    # ---- Kategori işlemleri ----
    def _draw_categories(self):
        for w in self.cat_wrap.winfo_children():
            w.destroy()
        for c in self.app.data.get("categories", []):
            tk.Button(self.cat_wrap, text=c, bg=COL["table_empty"], bd=1, relief="solid", font=FONT_MD, width=18,
                      command=lambda k=c: self._set_category(k)).pack(pady=4)

    def _open_category_manager(self, *_):
        CategoryManager(self.app, on_change=self._on_categories_changed)

    def _on_categories_changed(self):
        save_data(self.app.data)
        self._draw_categories()
        self._set_category(None)

    def _set_category(self, cat):
        self.selected_category = cat
        for w in self.products_scroll.inner.winfo_children():
            w.destroy()
        if not cat:
            self.prod_title.config(text="Kategori seçiniz", fg=COL["muted"])
            return
        self.prod_title.config(text=cat, fg=COL["text"])
        grid = tk.Frame(self.products_scroll.inner, bg=COL["panel"])
        grid.pack(pady=8)
        prods = [p for p in self.app.data.get("products", []) if p.get("category") == cat]
        for i, p in enumerate(prods):
            b = tk.Button(grid, text=f"{p['name']}\n{p['price']:.2f}₺", bg=COL["table_empty"], width=18, height=4,
                          font=FONT_MD, command=lambda pr=p: self._add_item(pr))
            b.grid(row=i//4, column=i%4, padx=10, pady=10)

    # ---- Sipariş işlemleri ----
    def _add_item(self, product):
        found = next((x for x in self.staged if x['name'] == product['name']), None)
        if found:
            found['qty'] += 1
        else:
            self.staged.append({"name": product['name'], "price": product['price'], "qty": 1})
        self._refresh_order_list()

    def _remove_selected(self):
        sel = self.order_list.curselection()
        if not sel:
            return
        idx = sel[0]
        all_items = self.staged + self.orig["items"]
        if 0 <= idx < len(all_items):
            removed = all_items[idx]
            # öncelik staged
            for i, it in enumerate(self.staged):
                if it['name'] == removed['name'] and it['price'] == removed['price']:
                    self.staged.pop(i)
                    break
            else:
                for i, it in enumerate(self.orig['items']):
                    if it['name'] == removed['name'] and it['price'] == removed['price']:
                        self.orig['items'].pop(i)
                        self.orig['total'] = sum(x['qty']*x['price'] for x in self.orig['items'])
                        self.orig['open'] = self.orig['total'] > 0
                        save_data(self.app.data)
                        self.app.refresh_tables()
                        break
        self._refresh_order_list()

    def _clear_all(self):
        if not self.staged and not self.orig["items"]:
            return
        if not messagebox.askyesno("Onay", "Tüm ürünler silinsin mi?"):
            return
        self.staged = []
        self.orig["items"] = []
        self.orig["total"] = 0.0
        self.orig["open"] = False
        save_data(self.app.data)
        self._refresh_order_list()
        self.app.refresh_tables()

    def _refresh_order_list(self):
        self.order_list.delete(0, tk.END)
        total = 0.0
        for it in self.staged:
            line = f"{it['qty']}x {it['name']}  → {it['qty']*it['price']:.2f}₺"
            self.order_list.insert(tk.END, line)
            total += it['qty'] * it['price']
        for it in self.orig['items']:
            line = f"(Kayıtlı) {it['qty']}x {it['name']}  → {it['qty']*it['price']:.2f}₺"
            self.order_list.insert(tk.END, line)
            total += it['qty'] * it['price']
        self.lbl_total.config(text=f"Toplam: {total:.2f}₺")
        self._update_confirm_visibility()
        self._update_pay_enabled()

    def _update_confirm_visibility(self):
        if self.staged:
            if not self.btn_confirm.winfo_ismapped():
                self.btn_confirm.pack(side="left", padx=6)
        else:
            if self.btn_confirm.winfo_ismapped():
                self.btn_confirm.pack_forget()

    def _update_pay_enabled(self):
        enabled = (self.orig.get('total', 0.0) > 0.0)
        self.btn_pay.configure(state=("normal" if enabled else "disabled"))

    def confirm_order(self):
        for it in self.staged:
            found = next((x for x in self.orig['items'] if x['name'] == it['name']), None)
            if found:
                found['qty'] += it['qty']
            else:
                self.orig['items'].append(copy.deepcopy(it))
        self.staged = []
        self.orig['total'] = sum(i['qty']*i['price'] for i in self.orig['items'])
        self.orig['open'] = self.orig['total'] > 0
        save_data(self.app.data)
        self.app.refresh_tables()
        self.win.destroy()

    def take_payment(self):
        if self.orig.get('total', 0.0) <= 0:
            return
        PaymentWindow(self)

    def back_to_main(self):
        self.win.destroy()

# --------------------- Payment Window ---------------------
class PaymentWindow:
    def __init__(self, table_window):
        self.tw = table_window
        self.app = table_window.app
        self.table = table_window.orig
        self.remaining = float(self.table['total'])

        self.win = tk.Toplevel(self.app.root)
        self.win.title("Ödeme")
        self.win.geometry("1000x600")
        self.win.resizable(False, False)
        self.win.configure(bg=COL['bg'])

        top = tk.Frame(self.win, bg=COL['panel'], highlightbackground=COL['border'], highlightthickness=1)
        top.pack(fill='x', padx=12, pady=(12, 8))
        self.header_lbl = tk.Label(top, text=self._header_text(), font=FONT_XL, bg=COL['panel'], fg=COL['text'])
        self.header_lbl.pack(padx=12, pady=10)

        body = tk.Frame(self.win, bg=COL['bg']); body.pack(fill='both', expand=True, padx=12, pady=8)

        left = tk.Frame(body, bg=COL['panel'], highlightbackground=COL['border'], highlightthickness=1)
        left.pack(side='left', padx=8, pady=6)
        tk.Label(left, text="Tutar Giriniz", font=FONT_LG, bg=COL['panel']).pack(pady=(10, 6))

        amt_row = tk.Frame(left, bg=COL['panel']); amt_row.pack(pady=4)
        self.amount = tk.Entry(amt_row, font=("Segoe UI", 22), width=10, justify='right')
        self.amount.pack(side='left', padx=6)
        tk.Button(amt_row, text="Tutarın Tamamı", font=FONT_MD, bg=COL['table_empty'], command=self._fill_full_amount).pack(side='left', padx=6)

        pad = tk.Frame(left, bg=COL['panel']); pad.pack(padx=12, pady=10)
        keys = ["1","2","3","4","5","6","7","8","9","Sil","0","Temizle"]
        for i, k in enumerate(keys):
            tk.Button(pad, text=k, width=8, height=2, font=FONT_LG,
                      command=lambda t=k: self._keypress(t)).grid(row=i//3, column=i%3, padx=6, pady=6)

        right = tk.Frame(body, bg=COL['panel'], highlightbackground=COL['border'], highlightthickness=1)
        right.pack(side='left', padx=18, pady=6)
        tk.Label(right, text="Ödeme Şekli", font=FONT_LG, bg=COL['panel']).pack(pady=(10, 8))
        self.btn_cash = tk.Button(right, text="NAKİT", width=16, height=2, font=FONT_LG, bg=COL['table_empty'], command=lambda: self._pay('Nakit'))
        self.btn_cash.pack(pady=8)
        self.btn_card = tk.Button(right, text="KREDİ KARTI", width=16, height=2, font=FONT_LG, bg=COL['table_empty'], command=lambda: self._pay('Kart'))
        self.btn_card.pack(pady=8)

        tk.Button(self.win, text="Kapat", font=FONT_LG, command=self.win.destroy).pack(pady=8)

    def _header_text(self):
        return f"Masa Toplamı: {self.table['total']:.2f}₺  |  Kalan: {self.remaining:.2f}₺"

    def _fill_full_amount(self):
        self.amount.delete(0, tk.END)
        self.amount.insert(0, f"{self.remaining:.2f}")

    def _keypress(self, t):
        if t == "Sil":
            cur = self.amount.get()
            self.amount.delete(0, tk.END)
            self.amount.insert(0, cur[:-1])
        elif t == "Temizle":
            self.amount.delete(0, tk.END)
        else:
            self.amount.insert(tk.END, t)

    def _pay(self, method):
        raw = self.amount.get().strip()
        if raw:
            try:
                amt = float(raw)
            except ValueError:
                messagebox.showerror("Hata", "Geçerli bir tutar girin.")
                return
        else:
            amt = self.remaining
        if amt <= 0:
            return
        if amt > self.remaining:
            if not messagebox.askyesno("Uyarı", f"Girilen tutar ({amt:.2f}₺) kalandan ({self.remaining:.2f}₺) fazla. Devam edilsin mi?"):
                return
            amt = self.remaining

        self.app.data.setdefault('sales', []).append({
            "table": self.tw.tname,
            "amount": amt,
            "method": "Nakit" if method == 'Nakit' else 'Kart',
            "ts": now_str()
        })
        save_data(self.app.data)

        self.remaining -= amt
        self.header_lbl.config(text=self._header_text())
        self.amount.delete(0, tk.END)

        if self.remaining <= 0.0001:
            self.table['items'] = []
            self.table['total'] = 0.0
            self.table['open'] = False
            save_data(self.app.data)
            self.app.refresh_tables()
            messagebox.showinfo("Tamam", "Ödeme tamamlandı. Masa kapatıldı.")
            self.win.destroy()
            try:
                self.tw.win.destroy()
            except Exception:
                pass

# --------------------- Ürün Yönetimi ---------------------
class ProductManager:
    def __init__(self, app):
        self.app = app
        self.win = tk.Toplevel(app.root)
        self.win.title("Ürün Yönetimi")
        self.win.geometry("880x540")
        self.win.configure(bg=COL['bg'])

        header = tk.Frame(self.win, bg=COL['bg'])
        header.pack(fill='x', pady=(10, 4))
        tk.Label(header, text="Ürünler", font=FONT_XL, bg=COL['bg']).pack(side='left', padx=12)

        wrap = tk.Frame(self.win, bg=COL['panel'], highlightbackground=COL['border'], highlightthickness=1)
        wrap.pack(fill='both', expand=True, padx=12, pady=8)

        style = ttk.Style(self.win)
        style.configure("Treeview.Heading", font=("Segoe UI", 12, "bold"), background=COL['heading'])
        style.configure("Treeview", font=("Segoe UI", 11))

        columns = ("Ürün Adı", "Kategori", "Fiyat")
        self.tree = ttk.Treeview(wrap, columns=columns, show='headings')
        for c in columns:
            self.tree.heading(c, text=c)
            self.tree.column(c, anchor='w', width=260 if c != 'Fiyat' else 120)
        self.tree.pack(fill='both', expand=True, padx=10, pady=10)

        btns = tk.Frame(wrap, bg=COL['panel'])
        btns.pack(fill='x', padx=10, pady=(0,10))
        tk.Button(btns, text="Ekle", font=FONT_LG, width=12, bg="#4CAF50", fg="white", command=self._add).pack(side='left', padx=6)
        tk.Button(btns, text="Düzenle", font=FONT_LG, width=12, bg="#FFC107", fg="black", command=self._edit).pack(side='left', padx=6)
        tk.Button(btns, text="Sil", font=FONT_LG, width=12, bg="#F44336", fg="white", command=self._delete).pack(side='left', padx=6)

        self._refresh()

    def _refresh(self):
        self.tree.delete(*self.tree.get_children())
        for p in self.app.data.get('products', []):
            self.tree.insert('', tk.END, values=(p['name'], p.get('category','-'), f"{p['price']:.2f}"))

    def _add(self):
        ProductDialog(self.app, on_save=self._refresh)

    def _edit(self):
        sel = self.tree.selection()
        if not sel:
            return
        vals = self.tree.item(sel[0], 'values')
        prod = next((p for p in self.app.data['products'] if p['name'] == vals[0] and f"{p['price']:.2f}" == vals[2]), None)
        if prod:
            ProductDialog(self.app, product=prod, on_save=self._refresh)

    def _delete(self):
        sel = self.tree.selection()
        if not sel:
            return
        name = self.tree.item(sel[0], 'values')[0]
        self.app.data['products'] = [p for p in self.app.data['products'] if p['name'] != name]
        save_data(self.app.data)
        self._refresh()

class ProductDialog:
    def __init__(self, app, product=None, on_save=None):
        self.app = app
        self.product = product
        self.on_save = on_save

        self.win = tk.Toplevel(app.root)
        self.win.title("Ürün Düzenle" if product else "Ürün Ekle")
        self.win.update_idletasks()
        ww,hh = 420,320
        sw,sh = self.win.winfo_screenwidth(), self.win.winfo_screenheight()
        x=(sw//2)-(ww//2); y=(sh//2)-(hh//2)
        self.win.geometry(f"{ww}x{hh}+{x}+{y}")

        form = tk.Frame(self.win)
        form.pack(padx=12, pady=10, fill='x')

        tk.Label(form, text="Ürün Adı:", font=FONT_MD).grid(row=0, column=0, sticky='w', pady=6)
        self.ent_name = tk.Entry(form, font=FONT_MD)
        self.ent_name.grid(row=0, column=1, sticky='ew', pady=6)

        tk.Label(form, text="Kategori:", font=FONT_MD).grid(row=1, column=0, sticky='w', pady=6)
        self.cmb_cat = ttk.Combobox(form, values=self.app.data.get('categories', []), font=FONT_MD)
        self.cmb_cat.grid(row=1, column=1, sticky='ew', pady=6)

        tk.Label(form, text="Fiyat:", font=FONT_MD).grid(row=2, column=0, sticky='w', pady=6)
        self.ent_price = tk.Entry(form, font=FONT_MD)
        self.ent_price.grid(row=2, column=1, sticky='ew', pady=6)

        form.columnconfigure(1, weight=1)

        if product:
            self.ent_name.insert(0, product['name'])
            self.cmb_cat.set(product.get('category',''))
            self.ent_price.insert(0, f"{product['price']}")

        btns = tk.Frame(self.win)
        btns.pack(pady=10)
        tk.Button(btns, text="Kaydet", font=FONT_LG, width=12, command=self._save).pack(side='left', padx=6)
        tk.Button(btns, text="İptal", font=FONT_LG, width=12, command=self.win.destroy).pack(side='left', padx=6)

    def _save(self):
        name = self.ent_name.get().strip()
        cat = self.cmb_cat.get().strip()
        try:
            price = float(self.ent_price.get())
        except Exception:
            messagebox.showerror("Hata", "Geçerli bir fiyat girin.")
            return
        if not name or not cat:
            messagebox.showerror("Hata", "Ürün adı ve kategori zorunlu.")
            return
        if self.product:
            self.product.update({"name": name, "category": cat, "price": price})
        else:
            self.app.data.setdefault('products', []).append({"name": name, "category": cat, "price": price})
        save_data(self.app.data)
        if self.on_save:
            self.on_save()
        self.win.destroy()

# --------------------- Kategori Yönetimi ---------------------
class CategoryManager:
    def __init__(self, app, on_change=None):
        self.app = app
        self.on_change = on_change

        self.win = tk.Toplevel(app.root)
        self.win.title("Kategori Yönetimi")
        self.win.update_idletasks()
        ww,hh = 460,380
        sw,sh = self.win.winfo_screenwidth(), self.win.winfo_screenheight()
        x=(sw//2)-(ww//2); y=(sh//2)-(hh//2)
        self.win.geometry(f"{ww}x{hh}+{x}+{y}")

        tk.Label(self.win, text="Kategoriler", font=FONT_XL).pack(pady=8)
        self.lst = tk.Listbox(self.win, height=12, font=FONT_MD)
        self.lst.pack(fill='both', expand=True, padx=10)

        btns = tk.Frame(self.win); btns.pack(pady=8)
        tk.Button(btns, text="Ekle", width=10, command=self._add).pack(side='left', padx=4)
        tk.Button(btns, text="Düzenle", width=10, command=self._edit).pack(side='left', padx=4)
        tk.Button(btns, text="Sil", width=10, command=self._delete).pack(side='left', padx=4)

        self._refresh()

    def _refresh(self):
        self.lst.delete(0, tk.END)
        for c in self.app.data.get('categories', []):
            self.lst.insert(tk.END, c)

    def _add(self):
        self._edit(existing=None)

    def _edit(self, existing=None):
        if existing is None:
            sel = self.lst.curselection()
            if sel:
                existing = self.lst.get(sel[0])
        top = tk.Toplevel(self.win)
        top.title("Kategori Ekle / Düzenle")
        top.update_idletasks()
        ww,hh = 400,220
        sw,sh = top.winfo_screenwidth(), top.winfo_screenheight()
        x=(sw//2)-(ww//2); y=(sh//2)-(hh//2)
        top.geometry(f"{ww}x{hh}+{x}+{y}")
        top.resizable(False, False)
        frm = tk.Frame(top, padx=20, pady=20)
        frm.pack(fill="both", expand=True)
        tk.Label(frm, text="Kategori Adı:", font=("Segoe UI", 12, "bold")).pack(pady=(10, 5))
        ent = tk.Entry(frm, font=("Segoe UI", 12), width=25)
        ent.pack(pady=5)
        if existing:
            ent.insert(0, existing)
        def saveit():
            name = ent.get().strip()
            if not name:
                messagebox.showerror("Hata", "Kategori adı boş olamaz.")
                return
            cats = self.app.data.setdefault('categories', [])
            if existing and existing in cats:
                cats[cats.index(existing)] = name
                for p in self.app.data.get('products', []):
                    if p.get('category') == existing:
                        p['category'] = name
            else:
                if name not in cats:
                    cats.append(name)
            save_data(self.app.data)
            self._refresh()
            top.destroy()
            if self.on_change:
                self.on_change()
        tk.Button(frm, text="Kaydet", font=("Segoe UI", 12), width=12, command=saveit).pack(pady=15)

    def _delete(self):
        sel = self.lst.curselection()
        if not sel:
            return
        name = self.lst.get(sel[0])
        cats = self.app.data.get('categories', [])
        if name in cats:
            cats.remove(name)
            save_data(self.app.data)
            self._refresh()
            if self.on_change:
                self.on_change()

# --------------------- Rapor ---------------------
class ReportWindow:
    def __init__(self, app):
        self.app = app
        win = tk.Toplevel(app.root)
        win.title("Günlük Satış Raporu")
        win.geometry("900x560")
        style = ttk.Style(win)
        style.configure("Treeview.Heading", font=("Segoe UI", 12, "bold"), background=COL['heading'])
        cols = ("Masa", "Tutar", "Yöntem", "Zaman")
        tree = ttk.Treeview(win, columns=cols, show="headings")
        for c in cols:
            tree.heading(c, text=c)
            tree.column(c, anchor="center", width=180)
        tree.pack(fill="both", expand=True, padx=12, pady=10)

        total = sum(s.get("amount", 0) for s in app.data.get("sales", []))
        cash = sum(s.get("amount", 0) for s in app.data.get("sales", []) if s.get("method") == "Nakit")
        card = total - cash
        for s in app.data.get("sales", []):
            tree.insert("", tk.END, values=(s.get("table"), f"{s.get('amount',0):.2f}₺", s.get("method"), s.get("ts", "-")))

        info = tk.Frame(win); info.pack(pady=6)
        tk.Label(info, text=f"Toplam Satış: {total:.2f}₺", font=FONT_LG).pack(side="left", padx=10)
        tk.Label(info, text=f"Nakit: {cash:.2f}₺  |  Kart: {card:.2f}₺", font=FONT_LG).pack(side="left", padx=10)
        tk.Button(win, text="Kapat", font=FONT_LG, command=win.destroy).pack(pady=8)

# --------------------- Genel Durum ---------------------
class GeneralStatusWindow:
    def __init__(self, app):
        self.app = app
        self.win = tk.Toplevel(app.root)
        self.win.title("Aktif Masalar ve Sipariş Durumu")
        self.win.geometry("900x540")
        style = ttk.Style(self.win)
        style.configure("Treeview.Heading", font=("Segoe UI", 12, "bold"), background=COL['heading'])
        cols = ("Masa", "Toplam (₺)", "Sipariş Sayısı", "Durum")
        self.tree = ttk.Treeview(self.win, columns=cols, show="headings")
        for c in cols:
            self.tree.heading(c, text=c)
            self.tree.column(c, anchor="center", width=200 if c != "Sipariş Sayısı" else 140)
        self.tree.pack(fill="both", expand=True, padx=12, pady=10)
        ctrl = tk.Frame(self.win); ctrl.pack(fill="x", pady=(0,8))
        tk.Button(ctrl, text="GÜNCELLE", font=FONT_LG, bg=COL["blue_btn"], fg="white", command=self.refresh).pack(side="left", padx=8)
        self.lbl_sum = tk.Label(ctrl, text="", font=FONT_LG)
        self.lbl_sum.pack(side="right", padx=8)
        self.refresh()

    def refresh(self):
        self.tree.delete(*self.tree.get_children())
        total_open = 0
        total_amount = 0.0
        for name, t in self.app.data["tables"].items():
            qty = sum(i.get("qty",0) for i in t.get("items", []))
            status = "Açık" if t.get("open") else "Kapalı"
            self.tree.insert("", tk.END, values=(name, f"{t.get("total",0.0):.2f}", qty, status))
            if t.get("open"):
                total_open += 1
                total_amount += t.get("total", 0.0)
        self.lbl_sum.config(text=f"Açık Masa: {total_open} | Açık Masalar Toplamı: {total_amount:.2f}₺")

# --------------------- main ---------------------
if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()
