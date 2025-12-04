import uuid
from datetime import datetime

users = {}
admins = {"admin": {"password": "123"}}
products = {}
vouchers = {}
orders = {}
payment_methods = {"shopeepay": True, "cod": True, "transfer": True}  # opsional, dipakai di admin
kurir = {
    "JNE"     : 9000,
    "JNT"     : 8000,
    "SICEPAT" : 7000,
    "EXSPRESS": 5000
}

logged_user = None

def register_user():
    print("=== REGISTER USER ===")
    username = input("Username: ")
    pw = input("Password: ")

    if username in users:
        print("Username sudah dipakai!")
        return

    users[username] = {
        "password": pw,
        "saldo": 0,
        "koin": 0,
        "alamat": "",
        "cart": [],
        "orders": []
    }
    print("[REGISTER] Akun berhasil dibuat!")

def login_user():
    print("=== LOGIN ===")
    username = input("Username: ")
    pw = input("Password: ")

    if username not in users:
        print("Login gagal! Username salah!, ulangi")
        return None

    if users[username]["password"] != pw:
        print("Login gagal! Password salah!, ulangi")
        return None

    print(f"[LOGIN] Selamat datang, {username}!")
    return username

def login_admin():
    print("=== LOGIN ADMIN ===")
    username = input("Username admin: ")
    pw = input("Password: ")

    if username in admins and admins[username]["password"] == pw:
        print(f"[LOGIN ADMIN] Selamat datang, {username}!")
        return username
    else:
        print("Login admin gagal!")
        return None

def isi_saldo(user):
    while True:
        try:
            nominal = int(input("Masukkan saldo: "))
            if nominal <= 0:
                print("Nominal harus lebih dari 0!")
                continue
            break
        except:
            print("Input harus berupa angka!")
    users[user]["saldo"] += nominal
    print("Saldo berhasil ditambahkan!")

def tampilkan_saldo(user):
    print(f"Saldo saat ini: Rp{users[user]['saldo']}")

def set_alamat(user):
    alamat = input("Masukkan alamat lengkap: ")
    users[user]["alamat"] = alamat
    print("Alamat tersimpan.")

def add_product():
    print("=== TAMBAH PRODUK ===")
    name = input("Nama produk: ").strip()
    if not name:
        print("Nama produk tidak boleh kosong!")
        return
    
    while True:
        try:
            price = int(input("Harga: "))
            if price <= 0:
                print("Harga harus lebih dari 0!")
                continue
            break
        except:
            print("Input harga harus berupa angka!")

    while True:
        try:
            stock = int(input("Stok: "))
            if stock < 0:
                print("Stok tidak boleh negatif!")
                continue
            break
        except:
            print("Input stok harus berupa angka!")

    while True:
        try:
            berat = int(input("Berat produk (gram): "))
            if berat <= 0:
                print("Berat harus lebih dari 0!")
                continue
            break
        except :
            print("Input berat harus berupa angka!")

    while True:
        mall_input = input("Produk Mall? (y/n): ").lower()
        if mall_input in ["y", "n"]:
            mall = mall_input == "y"
            break
        else:
            print("Input hanya boleh 'y' atau 'n'!")

    pid = str(uuid.uuid4())[:6]
    products[pid] = {
        "name": name,
        "price": price,
        "stock": stock,
        "berat": berat,
        "mall": mall,
        "rating": []
    }
    print(f"[PRODUCT] {name} ditambahkan dengan ID {pid}")

def show_products(only_mall=False):
    print("=== LIST PRODUK ===")
    for pid, p in products.items():
        if only_mall and not p["mall"]:
            continue
        print(f"{pid} | {p['name']} | Rp{p['price']} | Stock:{p['stock']} | Berat:{p['berat']}g | Mall:{p['mall']}")

def add_voucher():
    code = input("Kode voucher: ").strip().upper()
    value = float(input("Nilai diskon (10 = 10%, 5000 = nominal): "))

    if value <= 100:
        value = value / 100  

    min_belanja = float(input("Minimal belanja (0 jika tidak ada): "))

    expiry = input("Tanggal kadaluarsa (YYYY-MM-DD, kosong = tidak kadaluarsa): ")
    expiry = expiry if expiry.strip() != "" else None

    vouchers[code] = {
        "value": value,
        "min_belanja": min_belanja,
        "expiry": expiry
    }

    print(f"Voucher {code} berhasil ditambahkan!")

def apply_voucher(code, barang_total):
    if not code:
        return barang_total, 0.0

    code = code.strip().upper()
    if code not in vouchers:
        print("Voucher tidak valid.")
        return barang_total, 0.0

    v = vouchers[code]
    value = v["value"]
    min_belanja = v["min_belanja"]
    expiry = v["expiry"]

    if expiry:
        try:
            exp_date = datetime.strptime(expiry, "%Y-%m-%d").date()
            if datetime.now().date() > exp_date:
                print("Voucher sudah kadaluarsa.")
                return barang_total, 0.0
        except:
            pass

    if barang_total < min_belanja:
        print(f"Total belanja belum mencapai minimal Rp{min_belanja}.")
        return barang_total, 0.0

    if value > 1:
        value = value / 100.0

    if value < 1:
        diskon = barang_total * value
        barang_total_after = barang_total - diskon
        print(f"Voucher {code} berhasil! Diskon {value*100:.0f}% (-Rp{int(diskon)})")
    else:
        diskon = value
        barang_total_after = max(0, barang_total - diskon)
        print(f"Voucher {code} berhasil! Potongan Rp{int(diskon)}")

    return barang_total_after, diskon

# ===== KERANJANG =====
def add_to_cart(user):
    if not products:
        print("Belum ada produk tersedia.")
        return

    while True:
        pid = input("Masukkan ID produk yang ingin ditambahkan ke keranjang: ").strip()
        if pid not in products:
            print("Produk tidak ditemukan!")
            print("\n=== LIST PRODUK TERSEDIA ===")
            for pid_show, p in products.items():
                print(f"{pid_show} | {p['name']} | Rp{p['price']} | Stock:{p['stock']} | Berat:{p['berat']}g | Mall:{p['mall']}")
            continue  

        while True:
            try:
                qty = int(input("Jumlah: "))
                if qty <= 0:
                    print("Jumlah harus lebih dari 0!")
                    continue
            except:
                print("Input jumlah harus berupa angka!")
                continue

            if products[pid]["stock"] < qty:
                print(f"Stok {products[pid]['name']} hanya {products[pid]['stock']}.")
                continue

            users[user]["cart"].append({"pid": pid, "qty": qty})
            products[pid]["stock"] -= qty
            print(f"{products[pid]['name']} x{qty} dimasukkan ke keranjang.")
            return 

def show_cart(user):
    print("=== KERANJANG ===")
    cart = users[user]["cart"]

    if not cart:
        print("Keranjang kosong.")
        return

    for item in cart:
        pid = item["pid"]
        qty = item["qty"]
        p = products[pid]
        print(f"[{pid}] {p['name']} x{qty} = Rp{p['price'] * qty}")

def calc_cart_total(user):
    total = 0
    for item in users[user]["cart"]:
        pid = item["pid"]
        qty = item["qty"]
        total += products[pid]["price"] * qty
    return total

def calc_cart_berat(user):
    total = 0
    for item in users[user]["cart"]:
        pid = item["pid"]
        qty = item["qty"]
        total += products[pid]["berat"] * qty
    return total

def update_cart_qty(user):
    show_cart(user)
    pid = input("Masukkan ID produk di keranjang: ")
    for item in users[user]["cart"]:
        if item["pid"] == pid:
            aksi = input("Tambah (t) atau Kurang (k) atau Set Qty (s): ").lower()
            
            if aksi == "t":
                while True:
                    try:
                        jumlah = int(input("Tambah berapa qty: "))
                        if jumlah <= 0:
                            print("Jumlah harus lebih dari 0!")
                            continue
                        break
                    except ValueError:
                        print("Input harus berupa angka!")
                if products[pid]["stock"] >= jumlah:
                    item["qty"] += jumlah
                    products[pid]["stock"] -= jumlah
                    print(f"Qty bertambah {jumlah}.")
                else:
                    print("Stok tidak cukup.")
            
            elif aksi == "k":
                while True:
                    try:
                        jumlah = int(input("Kurangi berapa qty: "))
                        if jumlah <= 0:
                            print("Jumlah harus lebih dari 0!")
                            continue
                        break
                    except ValueError:
                        print("Input harus berupa angka!")
                item["qty"] -= jumlah
                products[pid]["stock"] += jumlah
                if item["qty"] <= 0:
                    users[user]["cart"].remove(item)
                    print("Item dihapus dari keranjang.")
                else:
                    print(f"Qty berkurang {jumlah}.")
            
            elif aksi == "s":
                while True:
                    try:
                        jumlah = int(input("Set qty baru: "))
                        if jumlah < 0:
                            print("Jumlah tidak boleh negatif!")
                            continue
                        break
                    except ValueError:
                        print("Input harus berupa angka!")
                
                products[pid]["stock"] += item["qty"]  # kembalikan stok lama
                if jumlah == 0:
                    users[user]["cart"].remove(item)
                    print("Item dihapus dari keranjang.")
                elif products[pid]["stock"] >= jumlah:
                    item["qty"] = jumlah
                    products[pid]["stock"] -= jumlah
                    print(f"Qty di-set ke {jumlah}.")
                else:
                    print("Stok tidak cukup.")
            
            return
    print("Produk tidak ada di keranjang.")

def hitung_ongkir(berat):
    print("\n=== PILIH KURIR ===")
    for nama, harga in kurir.items():
        print(f"- {nama:<10} Rp{harga:,}/kg")

    while True:
        jasa = input("Kurir: ").upper().strip()
        if jasa not in kurir:
            print("Kurir tidak valid, coba lagi.")
            continue
        break

    kg = berat / 1000
    harga = round(kg * kurir[jasa])
    return harga

def checkout(user):
    if not users[user]["cart"]:
        print("Keranjang kosong.")
        return

    show_cart(user)
    barang_total = calc_cart_total(user)
    berat = calc_cart_berat(user)
    ongkir = hitung_ongkir(berat)

    kode_voucher = input("Voucher? (enter jika tidak ada): ").strip()
    if kode_voucher:
        barang_total_after, total_diskon = apply_voucher(kode_voucher, barang_total)
    else:
        barang_total_after = barang_total
        total_diskon = 0.0

    total_bayar = barang_total_after + ongkir

    print("=== METODE PEMBAYARAN TERSEDIA ===")
    for m in payment_methods:
        print("-", m.capitalize())

    method = input("Pilih metode pembayaran: ").strip().lower()
    if method not in payment_methods or not payment_methods[method]:
        print("Metode pembayaran tidak tersedia.")
        return

    print("\n" + "="*40)
    print("          RINGKASAN PESANAN          ")
    print("="*40)
    print(f"Pembeli          : {user}") 
    print(f"Alamat Pengiriman: {users[user]['alamat'] if users[user]['alamat'] else '(belum diisi)'}")
    print(f"Metode Pembayaran: {method.capitalize()}")
    print("-"*40)
    print(f"Subtotal Barang  : Rp{barang_total:,}")
    print(f"Diskon           : Rp{int(total_diskon):,}")
    print(f"Subtotal Diskon  : Rp{int(barang_total_after):,}")
    print(f"Ongkir           : Rp{ongkir:,}")
    print("-"*40)
    print(f"TOTAL BAYAR      : Rp{int(total_bayar):,}")
    print("="*40)

    if method == "shopeepay":
        if users[user]["saldo"] < total_bayar:
            print("Saldo kurang.")
            return
        users[user]["saldo"] -= total_bayar
        print("[PAY] Pembayaran ShopeePay sukses!")
        print(f"Sisa saldo kamu: Rp{users[user]['saldo']:,}")

    elif method == "cod":
        print("[PAY] Bayar di tempat, pesanan diproses!")

    elif method == "transfer":
        print("=== TRANSFER ===")
        print(f"Total yang harus ditransfer: Rp{int(total_bayar)}")
        while True:
            try:
                tf = float(input("Masukkan nominal transfer: "))
                if tf <= 0:
                    print("Nominal harus lebih dari 0!")
                    continue
                break
            except ValueError:
                print("Input harus berupa angka!")

        if tf < total_bayar:
            print("Pembayaran gagal! Uang yang ditransfer kurang.")
            return
        else:
            print("Pembayaran berhasil melalui transfer!")

    oid = str(uuid.uuid4())[:6]
    orders[oid] = {
        "user": user,
        "items": [item.copy() for item in users[user]["cart"]],
        "total": total_bayar,
        "status": "dibayar",
        "escrow": total_bayar,
        "created_at": datetime.now().isoformat(),
        "payment_method": method
    }
    users[user]["orders"].append(oid)
    users[user]["cart"].clear()

    print("[INFO] Paket akan segera dikirim ke alamat tujuan.")
    print(f"[ORDER] Order {oid} berhasil dibuat.")
    print(f"[ESCROW] Dana Rp{total_bayar} ditahan.")
    
def beri_ulasan(oid):
    print("=== BERIKAN ULASAN ===")
    seller_rate = input("Ulasan untuk seller (baik/buruk/cukup)  : ")
    kurir_rate = input("Penilaian kurir (ramah/cepat/biasa saja) : ")
    while True:
        try:
            kepuasan = int(input("Tingkat kepuasan belanja (1-5)  : "))
            if kepuasan < 1 or kepuasan > 5:
                print("Nilai kepuasan harus antara 1 sampai 5!")
                continue
            break
        except:
            print("Input kepuasan harus berupa angka 1-5!")

    orders[oid]["review"] = {
        "seller": seller_rate,
        "kurir": kurir_rate,
        "kepuasan": kepuasan
    }

    for item in orders[oid]["items"]:
        pid = item["pid"]
        products[pid]["rating"].append(kepuasan)

    print("\n[REVIEW] Terima kasih atas ulasanmu!")
    print("======= DETAIL ULASAN =======")
    print(f"Seller   : {seller_rate}")
    print(f"Kurir    : {kurir_rate}")
    print(f"Kepuasan : {kepuasan}")
    print("="*30)

    opsi_refund = input("Apakah ingin ajukan refund? (y/n): ").lower()
    if opsi_refund == "y":
        orders[oid]["status"] = "refund"
        amount = orders[oid]["escrow"]
        user = orders[oid]["user"]
        users[user]["saldo"] += amount
        orders[oid]["escrow"] = 0
        alasan = input("Alasan refund: ")

        print("\n========= REFUND ORDER =========")
        print(f"Order ID          : {oid}")
        print(f"Pembeli           : {user}")
        print(f"Alasan            : {alasan}")
        print(f"Dana Dikembalikan : Rp{amount}")
        print("="*30)
        tampilkan_status(oid) 

def tampilkan_status(oid):
    status = orders[oid]["status"]
    print("\n======== STATUS PAKET =========")
    print(f"Order ID   : {oid}")
    print(f"Pembeli    : {orders[oid]['user']}")
    print(f"Alamat     : {users[orders[oid]['user']]['alamat']}")
    print(f"Status     : {status.upper()}")
    print("="*30)

def status_paket(oid):
    if oid not in orders:
        print("Order tidak ditemukan.")
        return

    user = orders[oid]["user"]
    alamat = users[user]["alamat"]

    print(f"\n[PENGANTARAN] Paket sedang diantar ke: {alamat}")

    orders[oid]["status"] = "dikirim"
    tampilkan_status(oid)

    input("Tekan enter saat paket sudah tiba di wilayah tujuan")
    orders[oid]["status"] = "tiba"
    tampilkan_status(oid)

    konfirmasi = input("Apakah paket sudah diterima pembeli? (y/n): ").lower()

    if konfirmasi == "y":
        orders[oid]["status"] = "selesai"
        tampilkan_status(oid)
        print("[ORDER SELESAI] Paket diterima pembeli!")
        beri_ulasan(oid)
    else:
        tampilkan_status(oid)
        print("Paket belum diterima. Status tetap: tiba.")


def cancel_order(user):
    oid = input("Masukkan ID order yang ingin dibatalkan: ")
    if oid not in orders:
        print("Order tidak ditemukan.")
        return
    if orders[oid]["user"] != user:
        print("Kamu tidak berhak membatalkan order ini.")
        return
    if orders[oid]["status"] in ["selesai", "refund", "cancelled"]:
        print("Order sudah selesai/refund/cancelled, tidak bisa dibatalkan.")
        return

    alasan = input("Alasan pembatalan: ")
    amount = orders[oid]["escrow"]
    payment = orders[oid]["payment_method"]

    if payment in ["shopeepay", "transfer"]:
        users[user]["saldo"] += amount
        print(f"Dana Rp{amount:,} dikembalikan ke saldo.")
    else:
        print("COD - belum ada pembayaran, jadi tidak ada dana dikembalikan.")

    orders[oid]["escrow"] = 0
    orders[oid]["status"] = "cancelled"

    print("\n========= CANCEL ORDER =========")
    print(f"Order ID          : {oid}")
    print(f"Pembeli           : {user}")
    print(f"Alasan            : {alasan}")
    if payment in ["shopeepay", "transfer"]:
        print(f"Dana Dikembalikan : Rp{amount:,}")
    else:
        print("Dana Dikembalikan : - (COD, belum bayar)")
    print("="*30)

    tampilkan_status(oid)

def menu_admin(admin):
    while True:
        print(f"""
====== ADMIN MENU ({admin}) ======
1. Tambah Produk
2. Tambah Voucher
3. Tambah Kurir
4. Tambah Metode Pembayaran
0. Logout
""")
        pilih = input("Pilih: ")
        if pilih == "1":
            add_product()

        elif pilih == "2":
            add_voucher()

        elif pilih == "3":
            nama = input("Nama kurir: ").upper()
            while True:
                try:
                    harga = int(input("Harga per kg: "))
                    if harga <= 0:
                        print("Harga harus lebih dari 0!")
                        continue
                    break
                except:
                    print("Input harga harus berupa angka!")
            kurir[nama] = harga
            print(f"Kurir {nama} ditambahkan.")

        elif pilih == "4":
            nama = input("Nama metode pembayaran: ").lower()
            payment_methods[nama] = True
            print(f"Metode {nama} ditambahkan & diaktifkan.")

        elif pilih == "0":
            print("Logout admin...")
            break

        else:
            print("Pilihan salah!")


# ===== MENU USER =====
def menu_user(user):
    while True:
        print(f"""

====== SHOPEE MENU ({user}) ======
1. Lihat Produk
2. Tambah Alamat
3. Isi Saldo
4. Lihat Total Saldo
5. Tambah ke Keranjang
6. Lihat Keranjang
7. Ubah Qty Keranjang 
8. Checkout
9. Cancel Order
10. Status Paket
0. Logout
""")

        pilih = input("Pilih: ")

        if pilih == "1":
            show_products()

        elif pilih == "2":
            set_alamat(user)

        elif pilih == "3":
            isi_saldo(user)

        elif pilih == "4":
            tampilkan_saldo(user)

        elif pilih == "5":
            show_products()
            add_to_cart(user)

        elif pilih == "6":
            show_cart(user)

        elif pilih == "7":
            update_cart_qty(user)

        elif pilih == "8":
            checkout(user)

        elif pilih == "9":
            cancel_order(user)

        elif pilih == "10":
            oid = input("Masukkan ID order untuk pengantaran: ")
            status_paket(oid)

        elif pilih == "0":
            print("Logout...")
            break

        else:
            print("Pilihan salah!")

# ===== MENU UTAMA =====
while True:
    print("""
==== SHOPEE SYSTEM ====
1. Register User
2. Login User
3. Login Admin
0. Keluar
""")
    pilih = input("Pilih: ")

    if pilih == "1":
        register_user()

    elif pilih == "2":
        u = login_user()
        if u: menu_user(u)

    elif pilih == "3":
        a = login_admin()
        if a:menu_admin(a)

    elif pilih == "0":
        break
    
    else:
        print("Pilihan salah!")