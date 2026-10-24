"""Build and decode a ZATCA Phase 1 simplified-invoice QR, no hardware needed.

Usage:
    python3 tools/zatca_qr_demo.py
    python3 tools/zatca_qr_demo.py --seller "My Shop" --vat 300000000000003 --total 115.00 --tax 15.00
Optional PNG output:  pip install qrcode[pil]
"""
import argparse
import base64
from datetime import datetime, timezone

TAGS = ["Seller name", "VAT number", "Timestamp", "Total (with VAT)", "VAT amount"]


def encode(fields):
    out = bytearray()
    for tag, value in enumerate(fields, start=1):
        data = str(value).encode("utf-8")
        assert len(data) < 256, "field too long for a 1-byte length"
        out += bytes([tag, len(data)]) + data
    return base64.b64encode(bytes(out)).decode()


def decode(b64):
    raw, i, res = base64.b64decode(b64), 0, []
    while i < len(raw):
        tag, length = raw[i], raw[i + 1]
        res.append((tag, raw[i + 2 : i + 2 + length].decode("utf-8")))
        i += 2 + length
    return res


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--seller", default="Test Trading Est.")
    p.add_argument("--vat", default="300000000000003")
    p.add_argument("--total", default="115.00")
    p.add_argument("--tax", default="15.00")
    a = p.parse_args()

    ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    payload = encode([a.seller, a.vat, ts, a.total, a.tax])
    print("QR payload (base64):\n" + payload + "\n")
    for tag, val in decode(payload):
        print(f"tag {tag} - {TAGS[tag - 1]}: {val}")

    try:
        import qrcode
        qrcode.make(payload).save("zatca_qr_demo.png")
        print("\nSaved zatca_qr_demo.png - scan it with your phone camera.")
    except ImportError:
        print("\n(pip install qrcode[pil] to also save a PNG you can scan)")
