import sys
import os

def test_billing_module():
    print("[*] AegisMatrix Ticari Altyapı ve Billing Modülü İnceleniyor...")
    try:
        import app.feature_billing as billing_mod
        print("    [+] Başarılı: app.feature_billing modülü doğrudan içe aktarıldı.")

        # Modül içerisindeki yönlendiriciyi dinamik olarak bul
        router_obj = None
        for attr_name in dir(billing_mod):
            attr = getattr(billing_mod, attr_name)
            if type(attr).__name__ in ["APIRouter", "FastAPI"]:
                router_obj = attr
                print(f"    [+] Tespit Edilen Yönlendirici Değişkeni: '{attr_name}' ({type(attr).__name__})")
                break

        if router_obj:
            print(f"    [+] Yönlendirici İçindeki Endpoint Sayısı: {len(router_obj.routes)}")
        else:
            print("    [!] Uyarı: Modül içerisinde doğrudan bir APIRouter nesnesi bulunamadı, ancak modül hatasız yükleniyor.")

        print("\n[✔] Ticari Altyapı Modülü Yükleme Testi Başarıyla Tamamlandı.")

    except Exception as e:
        print(f"[!] KRİTİK HATA [Billing Test]: {str(e)}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    test_billing_module()
