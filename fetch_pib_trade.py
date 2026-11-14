#!/usr/bin/env python3
"""
Fetches the latest monthly India Foreign Trade PIB Press Release
and updates data/trade_data.json when a new month is published.
"""
import json
import re
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime
from pathlib import Path

DATA_FILE = Path(__file__).resolve().parent.parent / "data" / "trade_data.json"
PIB_RSS_URL = "https://www.pib.gov.in/RssMain.aspx?ModId=6&Lang=1&Reg=3"

MONTH_MAP = {
    "january": "01", "february": "02", "march": "03", "april": "04",
    "may": "05", "june": "06", "july": "07", "august": "08",
    "september": "09", "october": "10", "november": "11", "december": "12"
}

def fetch_text(url: str) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=25) as resp:
        return resp.read().decode("utf-8", errors="ignore")

def parse_release(html: str, pr_url: str):
    m_month = re.search(
        r"total exports \(Merchandise and Services combined\) for ([A-Za-z]+)\s+(\d{4})",
        html, re.IGNORECASE
    )
    if not m_month:
        return None
    month_name, year = m_month.group(1), m_month.group(2)
    mm = MONTH_MAP.get(month_name.lower())
    if not mm:
        return None

    def grab(pattern):
        m = re.search(pattern, html, re.IGNORECASE | re.DOTALL)
        return round(float(m.group(1)), 2) if m else None

    merch_exp = grab(r"Merchandise exports during " + month_name + r"\s+" + year + r"\s+were\s+US\$\s*([\d.]+)\s+Billion")
    merch_imp = grab(r"Merchandise imports during " + month_name + r"\s+" + year + r"\s+were\s+US\$\s*([\d.]+)\s+Billion")
    serv_exp = grab(r"services export for " + month_name + r"\s+" + year + r"\*?\s+is\s+US\$\s*([\d.]+)\s+Billion")
    serv_imp = grab(r"services imports for " + month_name + r"\s+" + year + r"\*?\s+is\s+US\$\s*([\d.]+)\s+Billion")
    total_exp = grab(r"total exports \(Merchandise and Services combined\) for " + month_name + r"\s+" + year + r"\*?\s+(?:is|are)\s+estimated at\s+US\$\s*([\d.]+)\s+Billion")
    total_imp = grab(r"Total imports \(Merchandise and Services combined\) for " + month_name + r"\s+" + year + r"\*?\s+(?:is|are)\s+estimated at\s+US\$\s*([\d.]+)\s+Billion")
    yoy_exp = grab(r"registering a (?:positive )?growth of\s*([-\d.]+)\s*percent vis-à-vis " + month_name)

    if None in (merch_exp, merch_imp, serv_exp, serv_imp, total_exp, total_imp):
        return None

    prid_match = re.search(r"PRID=(\d+)", pr_url)
    prid_label = f"PIB PRID {prid_match.group(1)}" if prid_match else "PIB Auto-Sync"
    return {
        "id": f"{year}-{mm}",
        "label": f"{month_name[:3].title()} {year}",
        "merchExp": merch_exp,
        "merchImp": merch_imp,
        "servExp": serv_exp,
        "servImp": serv_imp,
        "totalExp": total_exp,
        "totalImp": total_imp,
        "balance": round(total_exp - total_imp, 2),
        "yoyExp": yoy_exp,
        "coreExp": None,
        "coreImp": None,
        "source": prid_label
    }

def main():
    data = json.loads(DATA_FILE.read_text())
    existing_ids = {row["id"] for row in data["monthly"]}

    try:
        rss_xml = fetch_text(PIB_RSS_URL)
        root = ET.fromstring(rss_xml)
    except Exception as exc:
        print(f"RSS fetch skipped: {exc}")
        return

    updated = False
    for item in root.findall(".//item"):
        title = (item.findtext("title") or "").lower()
        link = item.findtext("link") or ""
        if "merchandise" in title and ("exports" in title or "trade" in title):
            try:
                html = fetch_text(link)
                entry = parse_release(html, link)
                if entry and entry["id"] not in existing_ids:
                    data["monthly"].append(entry)
                    existing_ids.add(entry["id"])
                    updated = True
                    print(f"Added {entry['label']} from {entry['source']}")
            except Exception as exc:
                print(f"Failed parsing {link}: {exc}")

    if updated:
        data["monthly"].sort(key=lambda r: r["id"])
        data["last_updated"] = datetime.utcnow().strftime("%Y-%m-%d")
        DATA_FILE.write_text(json.dumps(data, indent=2) + "\n")
    else:
        print("No new monthly PIB release found.")

if __name__ == "__main__":
    main()
