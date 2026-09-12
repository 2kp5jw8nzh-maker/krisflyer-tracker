import json
import os

# ---------------------------------------------------------------------------
# This script rebuilds data.json from the hand-maintained tables below. Run it
# whenever you (or Claude) manually refresh the award chart, destination
# lists, or promotions -- e.g. after checking singaporeair.com/flyscoot.com
# yourself. It preserves the lastChecked/lastChangeDetected fields that the
# automated check_promos.py script maintains, so a manual rebuild doesn't
# erase the auto-checker's monitoring state.
# ---------------------------------------------------------------------------

# ---------------------------------------------------------------------------
# SIA KrisFlyer one-way award chart, effective 1 Nov 2025
# Figures in thousands of KrisFlyer miles. Source: singaporeair.com official
# award chart PDF (KrisFlyer programme updates 2025).
# "-" = not offered in that cabin on that zone (e.g. no First on regional hops)
# ---------------------------------------------------------------------------
sia_rates = [
    dict(zone="Z2", zoneName="Malaysia, Indonesia & Brunei", region="Southeast Asia",
         econSaver=8.0, premSaver=None, busSaver=22.0, firstSaver=32.0,
         econAdv=16.5, premAdv=40.5, busAdv=60.5, firstAdv=None),
    dict(zone="Z3", zoneName="Philippines, Thailand, Vietnam, Myanmar & Cambodia", region="Southeast Asia",
         econSaver=13.0, premSaver=None, busSaver=25.0, firstSaver=38.0,
         econAdv=27.5, premAdv=46.0, busAdv=72.0, firstAdv=None),
    dict(zone="Z4", zoneName="South China, Hong Kong SAR & Taiwan", region="North Asia",
         econSaver=15.5, premSaver=28.0, busSaver=35.5, firstSaver=47.5,
         econAdv=33.0, premAdv=57.5, busAdv=84.0, firstAdv=None),
    dict(zone="Z5", zoneName="North China (Beijing & Shanghai)", region="North Asia",
         econSaver=20.5, premSaver=36.0, busSaver=45.0, firstSaver=61.5,
         econAdv=44.0, premAdv=75.0, busAdv=112.5, firstAdv=None),
    dict(zone="Z6", zoneName="South Asia (India, Sri Lanka, Maldives, Nepal & Bangladesh)", region="South Asia",
         econSaver=19.0, premSaver=36.0, busSaver=45.0, firstSaver=61.5,
         econAdv=40.5, premAdv=75.0, busAdv=112.5, firstAdv=None),
    dict(zone="Z7", zoneName="Japan & South Korea", region="North Asia",
         econSaver=25.5, premSaver=39.5, busSaver=54.5, firstSaver=81.0,
         econAdv=49.5, premAdv=80.5, busAdv=138.0, firstAdv=None),
    dict(zone="Z8", zoneName="Australia — Perth & Darwin", region="Southwest Pacific",
         econSaver=20.5, premSaver=None, busSaver=42.5, firstSaver=60.5,
         econAdv=40.5, premAdv=75.0, busAdv=114.5, firstAdv=None),
    dict(zone="Z9", zoneName="Australia (excl. Perth/Darwin) & New Zealand", region="Southwest Pacific",
         econSaver=29.0, premSaver=53.5, busSaver=72.0, firstSaver=98.0,
         econAdv=60.5, premAdv=103.5, busAdv=178.5, firstAdv=None),
    dict(zone="Z10", zoneName="Africa, Middle East & Turkey", region="Africa / Middle East",
         econSaver=32.0, premSaver=51.5, busSaver=68.0, firstSaver=95.0,
         econAdv=66.5, premAdv=122.0, busAdv=171.0, firstAdv=None),
    dict(zone="Z11", zoneName="Europe", region="Europe",
         econSaver=44.0, premSaver=74.5, busSaver=108.5, firstSaver=148.0,
         econAdv=79.0, premAdv=141.5, busAdv=259.5, firstAdv=None),
    dict(zone="Z12", zoneName="USA — West Coast", region="Americas",
         econSaver=44.0, premSaver=79.0, busSaver=112.5, firstSaver=154.0,
         econAdv=79.0, premAdv=148.0, busAdv=262.0, firstAdv=None),
    dict(zone="Z13", zoneName="USA — East Coast", region="Americas",
         econSaver=46.0, premSaver=84.5, busSaver=117.0, firstSaver=156.0,
         econAdv=84.5, premAdv=165.0, busAdv=279.5, firstAdv=None),
]

# ---------------------------------------------------------------------------
# Scoot KrisFlyer award chart (launched 13 Aug 2025). Economy only.
# Figures in thousands of KrisFlyer miles, one-way, ex-Singapore (Zone 1).
# Source: flyscoot.com official Scoot award chart PDF.
# ---------------------------------------------------------------------------
scoot_rates = [
    dict(zone="SZ2", zoneName="Malaysia (Kuching, Miri, Kota Kinabalu, Sibu)", region="Southeast Asia", saver=1.5, advantage=3.5),
    dict(zone="SZ3", zoneName="Malaysia (Peninsular — KL, Penang, Langkawi, etc.)", region="Southeast Asia", saver=2.0, advantage=4.5),
    dict(zone="SZ4", zoneName="Indonesia (Jakarta, Pekanbaru, Padang, Belitung)", region="Southeast Asia", saver=2.5, advantage=5.5),
    dict(zone="SZ5", zoneName="Indonesia (Bali, Surabaya, Medan & other cities)", region="Southeast Asia", saver=4.5, advantage=9.0),
    dict(zone="SZ6", zoneName="N. Thailand (Chiang Mai/Rai, Koh Samui) & Labuan Bajo", region="Southeast Asia", saver=6.0, advantage=12.0),
    dict(zone="SZ7", zoneName="Thailand (Bangkok, Phuket, Krabi, Hat Yai)", region="Southeast Asia", saver=6.5, advantage=12.5),
    dict(zone="SZ8", zoneName="Laos & Vietnam (excl. Nha Trang)", region="Southeast Asia", saver=12.0, advantage=24.0),
    dict(zone="SZ9", zoneName="Philippines & Nha Trang (Vietnam)", region="Southeast Asia", saver=8.0, advantage=13.5),
    dict(zone="SZ10", zoneName="Hong Kong, Macau, Taiwan & S. China (Haikou, Nanning, Guangzhou)", region="North Asia", saver=12.5, advantage=24.0),
    dict(zone="SZ11", zoneName="China — other cities", region="North Asia", saver=24.0, advantage=37.5),
    dict(zone="SZ12", zoneName="India", region="South Asia", saver=4.5, advantage=9.0),
    dict(zone="SZ13", zoneName="Japan & South Korea", region="North Asia", saver=6.0, advantage=12.5),
    dict(zone="SZ14", zoneName="Australia — Perth", region="Southwest Pacific", saver=7.5, advantage=15.5),
    dict(zone="SZ15", zoneName="Australia (excl. Perth)", region="Southwest Pacific", saver=8.0, advantage=16.0),
    dict(zone="SZ16", zoneName="Greece & Austria", region="Europe", saver=13.5, advantage=22.5),
]
# Note: India (SZ12) and Japan/Korea (SZ13) mileage figures were extracted from a
# complex PDF matrix and are flagged as needing manual confirmation against the
# official chart before booking (see sources).
scoot_flagged_zones = ["SZ12", "SZ13"]

# ---------------------------------------------------------------------------
# SIA destinations ex-Singapore mapped to zones (based on official destination
# list + zone definitions above). Not a full traffic-rights list -- a
# representative mapping of cities SIA currently serves from Singapore.
# ---------------------------------------------------------------------------
sia_destinations = [
    ("Kuala Lumpur", "Malaysia", "Z2"), ("Penang", "Malaysia", "Z2"),
    ("Jakarta", "Indonesia", "Z2"), ("Denpasar (Bali)", "Indonesia", "Z2"),
    ("Medan", "Indonesia", "Z2"), ("Bandung", "Indonesia", "Z2"),
    ("Manila", "Philippines", "Z3"), ("Cebu", "Philippines", "Z3"),
    ("Bangkok", "Thailand", "Z3"), ("Phuket", "Thailand", "Z3"),
    ("Hanoi", "Vietnam", "Z3"), ("Ho Chi Minh City", "Vietnam", "Z3"),
    ("Da Nang", "Vietnam", "Z3"), ("Yangon", "Myanmar", "Z3"),
    ("Hong Kong", "Hong Kong SAR", "Z4"), ("Taipei", "Taiwan", "Z4"),
    ("Xiamen", "China", "Z4"), ("Shenzhen", "China", "Z4"),
    ("Shanghai", "China", "Z5"),
    ("Mumbai", "India", "Z6"), ("Chennai", "India", "Z6"),
    ("Bengaluru", "India", "Z6"), ("Kochi", "India", "Z6"),
    ("Kolkata", "India", "Z6"), ("Colombo", "Sri Lanka", "Z6"),
    ("Malé", "Maldives", "Z6"), ("Dhaka", "Bangladesh", "Z6"),
    ("Kathmandu", "Nepal", "Z6"),
    ("Tokyo (Haneda)", "Japan", "Z7"), ("Tokyo (Narita)", "Japan", "Z7"),
    ("Osaka", "Japan", "Z7"), ("Nagoya", "Japan", "Z7"), ("Seoul", "South Korea", "Z7"),
    ("Perth", "Australia", "Z8"), ("Darwin", "Australia", "Z8"),
    ("Adelaide", "Australia", "Z9"), ("Brisbane", "Australia", "Z9"),
    ("Melbourne", "Australia", "Z9"), ("Sydney", "Australia", "Z9"),
    ("Dubai", "UAE", "Z10"), ("Riyadh", "Saudi Arabia", "Z10"),
    ("Istanbul", "Türkiye", "Z10"), ("Cape Town", "South Africa", "Z10"),
    ("Johannesburg", "South Africa", "Z10"),
    ("Amsterdam", "Netherlands", "Z11"), ("Barcelona", "Spain", "Z11"),
    ("Brussels", "Belgium", "Z11"), ("Copenhagen", "Denmark", "Z11"),
    ("Frankfurt", "Germany", "Z11"), ("Munich", "Germany", "Z11"),
    ("London (Heathrow)", "United Kingdom", "Z11"), ("London (Gatwick)", "United Kingdom", "Z11"),
    ("Manchester", "United Kingdom", "Z11"), ("Milan", "Italy", "Z11"),
    ("Rome", "Italy", "Z11"), ("Paris", "France", "Z11"), ("Zurich", "Switzerland", "Z11"),
    ("Los Angeles", "USA", "Z12"), ("San Francisco", "USA", "Z12"),
    ("Newark", "USA", "Z13"), ("New York (JFK)", "USA", "Z13"),
]

# ---------------------------------------------------------------------------
# Scoot destinations ex-Singapore mapped to zones (per Scoot's own award-chart
# zone list crossed with Scoot's current network / Wikipedia route list).
# ---------------------------------------------------------------------------
scoot_destinations = [
    ("Kuching", "Malaysia", "SZ2"), ("Miri", "Malaysia", "SZ2"),
    ("Kota Kinabalu", "Malaysia", "SZ2"), ("Sibu", "Malaysia", "SZ2"),
    ("Kuala Lumpur", "Malaysia", "SZ3"), ("Penang", "Malaysia", "SZ3"),
    ("Langkawi", "Malaysia", "SZ3"), ("Ipoh", "Malaysia", "SZ3"),
    ("Kota Bharu", "Malaysia", "SZ3"), ("Kuantan", "Malaysia", "SZ3"),
    ("Malacca", "Malaysia", "SZ3"),
    ("Jakarta", "Indonesia", "SZ4"), ("Pekanbaru", "Indonesia", "SZ4"),
    ("Palembang", "Indonesia", "SZ4"), ("Tanjung Pandan (Belitung)", "Indonesia", "SZ4"),
    ("Denpasar (Bali)", "Indonesia", "SZ5"), ("Surabaya", "Indonesia", "SZ5"),
    ("Medan", "Indonesia", "SZ5"), ("Yogyakarta", "Indonesia", "SZ5"),
    ("Semarang", "Indonesia", "SZ5"), ("Balikpapan", "Indonesia", "SZ5"),
    ("Makassar", "Indonesia", "SZ5"), ("Manado", "Indonesia", "SZ5"),
    ("Lombok", "Indonesia", "SZ5"), ("Bandung", "Indonesia", "SZ5"),
    ("Chiang Mai", "Thailand", "SZ6"), ("Chiang Rai", "Thailand", "SZ6"),
    ("Koh Samui", "Thailand", "SZ6"), ("Labuan Bajo", "Indonesia", "SZ6"),
    ("Bangkok", "Thailand", "SZ7"), ("Phuket", "Thailand", "SZ7"),
    ("Krabi", "Thailand", "SZ7"), ("Hat Yai", "Thailand", "SZ7"),
    ("Vientiane", "Laos", "SZ8"), ("Hanoi", "Vietnam", "SZ8"),
    ("Ho Chi Minh City", "Vietnam", "SZ8"), ("Da Nang", "Vietnam", "SZ8"),
    ("Phu Quoc", "Vietnam", "SZ8"),
    ("Manila", "Philippines", "SZ9"), ("Cebu", "Philippines", "SZ9"),
    ("Clark", "Philippines", "SZ9"), ("Davao", "Philippines", "SZ9"),
    ("Iloilo", "Philippines", "SZ9"), ("Nha Trang", "Vietnam", "SZ9"),
    ("Hong Kong", "Hong Kong SAR", "SZ10"), ("Macau", "Macau SAR", "SZ10"),
    ("Taipei", "Taiwan", "SZ10"), ("Haikou", "China", "SZ10"),
    ("Nanning", "China", "SZ10"), ("Guangzhou", "China", "SZ10"),
    ("Changsha", "China", "SZ11"), ("Fuzhou", "China", "SZ11"),
    ("Hangzhou", "China", "SZ11"), ("Jieyang", "China", "SZ11"),
    ("Kunming", "China", "SZ11"), ("Nanjing", "China", "SZ11"),
    ("Qingdao", "China", "SZ11"), ("Shenyang", "China", "SZ11"),
    ("Tianjin", "China", "SZ11"), ("Wuhan", "China", "SZ11"),
    ("Xi'an", "China", "SZ11"), ("Zhengzhou", "China", "SZ11"),
    ("Amritsar", "India", "SZ12"), ("Chennai", "India", "SZ12"),
    ("Coimbatore", "India", "SZ12"), ("Thiruvananthapuram", "India", "SZ12"),
    ("Tiruchirapalli", "India", "SZ12"), ("Visakhapatnam", "India", "SZ12"),
    ("Naha (Okinawa)", "Japan", "SZ13"), ("Osaka", "Japan", "SZ13"),
    ("Sapporo", "Japan", "SZ13"), ("Tokyo (Haneda)", "Japan", "SZ13"),
    ("Tokyo (Narita)", "Japan", "SZ13"), ("Jeju", "South Korea", "SZ13"),
    ("Seoul (Incheon)", "South Korea", "SZ13"),
    ("Perth", "Australia", "SZ14"),
    ("Melbourne", "Australia", "SZ15"), ("Sydney", "Australia", "SZ15"),
    ("Athens", "Greece", "SZ16"), ("Vienna", "Austria", "SZ16"),
]

# ---------------------------------------------------------------------------
# Promotions active/known as of research date (12 Sep 2026)
# ---------------------------------------------------------------------------
promotions = [
    dict(
        id="sia-grs-sep2026",
        airline="SIA",
        title="KrisFlyer Global Redemption Sale",
        status="active",
        discount="15% off Economy Saver awards (most regions); 15% off Premium Economy on select US non-stops; 10% off Scoot Economy Saver awards",
        bookWindow="8 Sep 2026 09:00 SGT – 20 Sep 2026 23:59 SGT",
        travelWindow="1 Nov 2026 – 31 May 2027",
        notes="Excludes Johannesburg & Auckland. No refund/cancellation on promo fares. No stopovers. Blackout dates apply by route.",
        url="https://www.singaporeair.com/en_UK/sg/ppsclub-krisflyer/kf-flight-redemption/",
        # Machine-readable rules the board uses to bake this discount straight
        # into the mileage table. Only evaluated while status is "active" or
        # "closing" -- a booking_closed promo never adjusts table prices.
        rules=[
            dict(airline="SIA", field="econSaver", discountPct=15, excludeCities=["Johannesburg", "Auckland"]),
            dict(airline="SIA", field="premSaver", discountPct=15, includeZones=["Z12", "Z13"]),
            dict(airline="Scoot", field="saver", discountPct=10),
        ],
    ),
    dict(
        id="sia-spontaneous-sep2026",
        airline="SIA",
        title="KrisFlyer Spontaneous Escapes (September round)",
        status="booking_closed",
        discount="~30% off selected Economy/Premium Economy/Business awards",
        bookWindow="Closed 31 Aug 2026",
        travelWindow="1–30 Sep 2026",
        notes="Latest confirmed round; booking window has closed. Next round not yet announced as of 12 Sep 2026 — the weekly refresh will pick it up when SIA publishes it.",
        url="https://www.singaporeair.com/en_UK/sg/plan-travel/promotions/global/kf/kf-promo/kfescapes/",
        rules=[],
    ),
    dict(
        id="scoot-spontaneous-sep2026",
        airline="Scoot",
        title="Scoot KrisFlyer Spontaneous Escapes (September round)",
        status="booking_closed",
        discount="15% off selected Scoot Economy Saver awards",
        bookWindow="Closed 31 Aug 2026",
        travelWindow="1–30 Sep 2026",
        notes="Latest confirmed round; booking window has closed. Next round not yet announced as of 12 Sep 2026.",
        url="https://www.flyscoot.com/en/krisflyer/spontaneous-escapes",
        rules=[],
    ),
]

meta = dict(
    lastUpdated="2026-09-12T00:00:00+08:00",
    sources=[
        dict(label="SIA one-way Saver/Advantage award chart (PDF, eff. 1 Nov 2025)",
             url="https://www.singaporeair.com/content/dam/sia/web-assets/pdfs/ppsclub-krisflyer/krisflyer/progupdates/awardcharts/SingaporeAirlinesOne-WayAdvantageSaverAwardChartupdated1Nov25.pdf"),
        dict(label="Scoot KrisFlyer award chart (PDF)",
             url="https://cdn.flyscoot.com/prod/docs/default-source/scoot-award-chart/scoot-award-chart-pdf.pdf"),
        dict(label="KrisFlyer programme updates 2025",
             url="https://www.singaporeair.com/en_UK/us/ppsclub-krisflyer/KFupdates2025/"),
        dict(label="KrisFlyer Global Redemption Sale (official)",
             url="https://www.singaporeair.com/en_UK/sg/ppsclub-krisflyer/kf-flight-redemption/"),
        dict(label="KrisFlyer Spontaneous Escapes (official)",
             url="https://www.singaporeair.com/en_UK/sg/plan-travel/promotions/global/kf/kf-promo/kfescapes/"),
        dict(label="Scoot Spontaneous Escapes (official)",
             url="https://www.flyscoot.com/en/krisflyer/spontaneous-escapes"),
        dict(label="List of Singapore Airlines destinations (Wikipedia)",
             url="https://en.wikipedia.org/wiki/List_of_Singapore_Airlines_destinations"),
        dict(label="List of Scoot destinations (Wikipedia)",
             url="https://en.wikipedia.org/wiki/List_of_Scoot_destinations"),
    ],
)

def dest_list(rows):
    return [dict(city=c, country=k, zone=z) for c, k, z in rows]

# Preserve the auto-checker's monitoring state if data.json already exists.
if os.path.exists("data.json"):
    try:
        with open("data.json", "r", encoding="utf-8") as f:
            existing = json.load(f)
        meta["lastChecked"] = existing.get("meta", {}).get("lastChecked")
        meta["lastChangeDetected"] = existing.get("meta", {}).get("lastChangeDetected")
    except Exception:
        pass
else:
    meta["lastChecked"] = None
    meta["lastChangeDetected"] = None

data = dict(
    meta=meta,
    siaRates=sia_rates,
    scootRates=scoot_rates,
    scootFlaggedZones=scoot_flagged_zones,
    siaDestinations=dest_list(sia_destinations),
    scootDestinations=dest_list(scoot_destinations),
    promotions=promotions,
)

with open("data.json", "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print("SIA zones:", len(sia_rates), "| Scoot zones:", len(scoot_rates))
print("SIA destinations:", len(sia_destinations), "| Scoot destinations:", len(scoot_destinations))
print("Promotions:", len(promotions))
