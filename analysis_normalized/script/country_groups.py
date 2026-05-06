COUNTRY_GROUPS = {
    # Sudeste Asiático (ASEAN)
    "asean": ["IDN","MYS","PHL","SGP","THA","VNM","KHM","LAO","MMR","BRN", "TWN","HKG"],
    
    # Asia (sin Medio Oriente ni ASEAN)
    "asia": ["CHN","HKG","VNM","KHM", "MYS","PHL","SGP","THA","LAO", "TWN","IDN", "BRN","MMR",
             "BGD","PAK","JPN","KOR","SAU", "ARE", "IND"],
    
    # América del norte
    "north_america": ["CAN", "USA","MEX"],

    # América del sur y centroamérica
    "south_america": ["BRA","ARG","CHL","PER", "COL","CRI"],

    # África Subsahariana
    "africa_subsaharan": ["CMR","CIV","SEN","NGA","COD","ZAF", "STP","AGO",],
    
    "central_eastern_europe": [
        "LUX", "DEU", "AUT", "CZE", "HRV", "HUN", "SVK", "SVN", "POL",
        "CHE", "NLD", "BEL", 
        "DNK", "FIN", "NOR", "SWE",
        "ROU", "BGR", "BLR", "RUS", "UKR", "LTU", "LVA", "EST"
        ],

    # Europa + Norte de África + Medio Oriente
    "europe_extended": [
        "LUX", "DEU", "AUT",  "HRV", "SVN", "HUN", "CZE", "SVK",  "POL",
        "ROU", "BGR", "TUR", "GRC", "CYP", "KAZ", "BLR",  "RUS", "UKR", "LTU", "LVA", "EST",
        "DNK", "FIN", "NOR", "SWE", "ISL",
        "NLD", "BEL", "IRL", "GBR", "MLT", "ITA", "CHE",
        "ESP", "PRT", "MAR","FRA",  "TUN", 
        "ISR", "EGY", "JOR"
        ],
}


COUNTRY_ORDER = COUNTRY_GROUPS["europe_extended"].copy()
for _ in range(3):
    COUNTRY_ORDER.pop()
COUNTRY_ORDER += COUNTRY_GROUPS["africa_subsaharan"]
COUNTRY_ORDER += COUNTRY_GROUPS["asia"] + ["JOR","EGY", "ISR",   "AUS", "NZL"]
COUNTRY_ORDER += COUNTRY_GROUPS["north_america"]
COUNTRY_ORDER += COUNTRY_GROUPS["south_america"]