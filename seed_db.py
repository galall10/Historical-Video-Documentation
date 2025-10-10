import sys
from tqdm import tqdm
from utils.database import landmarks_collection, connect_to_db

def get_landmarks():
    """Returns a list of 100 Egyptian landmarks."""
    return [
        # Cairo & Giza (20)
        {"name": "Pyramids of Giza", "governorate": "Giza", "category": "Historical", "latitude": 29.9792, "longitude": 31.1342},
        {"name": "Great Sphinx of Giza", "governorate": "Giza", "category": "Historical", "latitude": 29.9753, "longitude": 31.1376},
        {"name": "The Egyptian Museum", "governorate": "Cairo", "category": "Museum", "latitude": 30.0475, "longitude": 31.2337},
        {"name": "Khan el-Khalili", "governorate": "Cairo", "category": "Market", "latitude": 30.0478, "longitude": 31.2622},
        {"name": "Old Cairo (Coptic Cairo)", "governorate": "Cairo", "category": "Religious", "latitude": 30.0054, "longitude": 31.2302},
        {"name": "Al-Azhar Mosque", "governorate": "Cairo", "category": "Religious", "latitude": 30.0456, "longitude": 31.2626},
        {"name": "Cairo Citadel (Citadel of Saladin)", "governorate": "Cairo", "category": "Historical", "latitude": 30.0296, "longitude": 31.2610},
        {"name": "Mosque of Muhammad Ali", "governorate": "Cairo", "category": "Religious", "latitude": 30.0287, "longitude": 31.2599},
        {"name": "Cairo Tower", "governorate": "Cairo", "category": "Modern", "latitude": 30.0459, "longitude": 31.2243},
        {"name": "Zamalek", "governorate": "Cairo", "category": "District", "latitude": 30.0609, "longitude": 31.2197},
        {"name": "Sakkara Pyramids (Step Pyramid of Djoser)", "governorate": "Giza", "category": "Historical", "latitude": 29.8712, "longitude": 31.2165},
        {"name": "Red Pyramid", "governorate": "Giza", "category": "Historical", "latitude": 29.8091, "longitude": 31.2062},
        {"name": "Bent Pyramid", "governorate": "Giza", "category": "Historical", "latitude": 29.7905, "longitude": 31.2098},
        {"name": "Mosque of Ibn Tulun", "governorate": "Cairo", "category": "Religious", "latitude": 30.0287, "longitude": 31.2496},
        {"name": "Hanging Church", "governorate": "Cairo", "category": "Religious", "latitude": 30.0053, "longitude": 31.2301},
        {"name": "Bab Zuweila", "governorate": "Cairo", "category": "Historical", "latitude": 30.0420, "longitude": 31.2590},
        {"name": "Pharaonic Village", "governorate": "Giza", "category": "Entertainment", "latitude": 29.9884, "longitude": 31.2107},
        {"name": "Cairo Opera House", "governorate": "Cairo", "category": "Culture", "latitude": 30.0425, "longitude": 31.2225},
        {"name": "Sultan Hassan Mosque", "governorate": "Cairo", "category": "Religious", "latitude": 30.0327, "longitude": 31.2588},
        {"name": "Gayer-Anderson Museum", "governorate": "Cairo", "category": "Museum", "latitude": 30.0285, "longitude": 31.2505},

        # Luxor (10)
        {"name": "Valley of the Kings", "governorate": "Luxor", "category": "Historical", "latitude": 25.7402, "longitude": 32.6014},
        {"name": "Karnak Temple", "governorate": "Luxor", "category": "Historical", "latitude": 25.7188, "longitude": 32.6573},
        {"name": "Luxor Temple", "governorate": "Luxor", "category": "Historical", "latitude": 25.7006, "longitude": 32.6393},
        {"name": "Mortuary Temple of Hatshepsut", "governorate": "Luxor", "category": "Historical", "latitude": 25.7382, "longitude": 32.6066},
        {"name": "Colossi of Memnon", "governorate": "Luxor", "category": "Historical", "latitude": 25.7205, "longitude": 32.6105},
        {"name": "Luxor Museum", "governorate": "Luxor", "category": "Museum", "latitude": 25.7095, "longitude": 32.6454},
        {"name": "Valley of the Queens", "governorate": "Luxor", "category": "Historical", "latitude": 25.7289, "longitude": 32.5923},
        {"name": "Medinet Habu", "governorate": "Luxor", "category": "Historical", "latitude": 25.7189, "longitude": 32.5998},
        {"name": "Ramesseum", "governorate": "Luxor", "category": "Historical", "latitude": 25.7277, "longitude": 32.6108},
        {"name": "Tombs of the Nobles", "governorate": "Luxor", "category": "Historical", "latitude": 25.7323, "longitude": 32.6094},

        # Aswan (10)
        {"name": "Abu Simbel Temples", "governorate": "Aswan", "category": "Historical", "latitude": 22.3371, "longitude": 31.6257},
        {"name": "Philae Temple", "governorate": "Aswan", "category": "Historical", "latitude": 24.0253, "longitude": 32.8906},
        {"name": "Aswan High Dam", "governorate": "Aswan", "category": "Modern", "latitude": 23.9723, "longitude": 32.8795},
        {"name": "Unfinished Obelisk", "governorate": "Aswan", "category": "Historical", "latitude": 24.0780, "longitude": 32.9029},
        {"name": "Nubian Museum", "governorate": "Aswan", "category": "Museum", "latitude": 24.0811, "longitude": 32.8943},
        {"name": "Elephantine Island", "governorate": "Aswan", "category": "Historical", "latitude": 24.0875, "longitude": 32.8917},
        {"name": "Aga Khan Mausoleum", "governorate": "Aswan", "category": "Historical", "latitude": 24.0903, "longitude": 32.8791},
        {"name": "Temple of Kom Ombo", "governorate": "Aswan", "category": "Historical", "latitude": 24.4522, "longitude": 32.9286},
        {"name": "Temple of Horus at Edfu", "governorate": "Aswan", "category": "Historical", "latitude": 24.9784, "longitude": 32.8732},
        {"name": "Kalabsha Temple", "governorate": "Aswan", "category": "Historical", "latitude": 23.9631, "longitude": 32.8661},

        # Alexandria (10)
        {"name": "Bibliotheca Alexandrina", "governorate": "Alexandria", "category": "Culture", "latitude": 31.2089, "longitude": 29.9092},
        {"name": "Catacombs of Kom El Shoqafa", "governorate": "Alexandria", "category": "Historical", "latitude": 31.1783, "longitude": 29.8923},
        {"name": "Citadel of Qaitbay", "governorate": "Alexandria", "category": "Historical", "latitude": 31.2140, "longitude": 29.8852},
        {"name": "Montaza Palace", "governorate": "Alexandria", "category": "Historical", "latitude": 31.2882, "longitude": 29.9839},
        {"name": "Pompey's Pillar", "governorate": "Alexandria", "category": "Historical", "latitude": 31.1822, "longitude": 29.8966},
        {"name": "Alexandria National Museum", "governorate": "Alexandria", "category": "Museum", "latitude": 31.1994, "longitude": 29.9056},
        {"name": "Roman Amphitheatre", "governorate": "Alexandria", "category": "Historical", "latitude": 31.1925, "longitude": 29.9025},
        {"name": "Royal Jewelry Museum", "governorate": "Alexandria", "category": "Museum", "latitude": 31.2411, "longitude": 29.9517},
        {"name": "El-Mursi Abul Abbas Mosque", "governorate": "Alexandria", "category": "Religious", "latitude": 31.2075, "longitude": 29.8844},
        {"name": "Stanley Bridge", "governorate": "Alexandria", "category": "Modern", "latitude": 31.2464, "longitude": 29.9589},

        # Sinai & Red Sea (10)
        {"name": "Saint Catherine's Monastery", "governorate": "South Sinai", "category": "Religious", "latitude": 28.5560, "longitude": 33.9761},
        {"name": "Mount Sinai", "governorate": "South Sinai", "category": "Religious", "latitude": 28.5391, "longitude": 33.9746},
        {"name": "Ras Muhammad National Park", "governorate": "South Sinai", "category": "Nature", "latitude": 27.7303, "longitude": 34.2547},
        {"name": "Naama Bay", "governorate": "South Sinai", "category": "Entertainment", "latitude": 27.9133, "longitude": 34.3278},
        {"name": "Blue Hole", "governorate": "South Sinai", "category": "Nature", "latitude": 28.5728, "longitude": 34.5369},
        {"name": "Colored Canyon", "governorate": "South Sinai", "category": "Nature", "latitude": 29.2833, "longitude": 34.7333},
        {"name": "Hurghada Marina", "governorate": "Red Sea", "category": "Entertainment", "latitude": 27.2281, "longitude": 33.8433},
        {"name": "Giftun Islands", "governorate": "Red Sea", "category": "Nature", "latitude": 27.2333, "longitude": 33.9333},
        {"name": "Marsa Alam", "governorate": "Red Sea", "category": "Nature", "latitude": 25.0667, "longitude": 34.9000},
        {"name": "El Gouna", "governorate": "Red Sea", "category": "Entertainment", "latitude": 27.3942, "longitude": 33.6782},

        # Western Desert & Oases (10)
        {"name": "Siwa Oasis", "governorate": "Matrouh", "category": "Nature", "latitude": 29.2033, "longitude": 25.5192},
        {"name": "White Desert National Park", "governorate": "New Valley", "category": "Nature", "latitude": 27.0600, "longitude": 27.9700},
        {"name": "Bahariya Oasis", "governorate": "Giza", "category": "Nature", "latitude": 28.3500, "longitude": 28.8667},
        {"name": "Farafra Oasis", "governorate": "New Valley", "category": "Nature", "latitude": 27.0606, "longitude": 27.9714},
        {"name": "Dakhla Oasis", "governorate": "New Valley", "category": "Nature", "latitude": 25.6917, "longitude": 29.0000},
        {"name": "Kharga Oasis", "governorate": "New Valley", "category": "Nature", "latitude": 25.4419, "longitude": 30.5458},
        {"name": "Temple of the Oracle", "governorate": "Matrouh", "category": "Historical", "latitude": 29.2000, "longitude": 25.5167},
        {"name": "Fortress of Shali", "governorate": "Matrouh", "category": "Historical", "latitude": 29.2031, "longitude": 25.5194},
        {"name": "Gebel el-Mawta (Mountain of the Dead)", "governorate": "Matrouh", "category": "Historical", "latitude": 29.2000, "longitude": 25.5333},
        {"name": "Crystal Mountain", "governorate": "New Valley", "category": "Nature", "latitude": 27.6000, "longitude": 28.5000},

        # Middle Egypt & Fayoum (10)
        {"name": "Abydos Temple (Temple of Seti I)", "governorate": "Sohag", "category": "Historical", "latitude": 26.1846, "longitude": 31.9190},
        {"name": "Dendera Temple Complex", "governorate": "Qena", "category": "Historical", "latitude": 26.1417, "longitude": 32.6708},
        {"name": "Beni Hasan", "governorate": "Minya", "category": "Historical", "latitude": 27.9333, "longitude": 30.8500},
        {"name": "Tell el-Amarna", "governorate": "Minya", "category": "Historical", "latitude": 27.6469, "longitude": 30.8958},
        {"name": "Wadi El Hitan (Valley of the Whales)", "governorate": "Faiyum", "category": "Nature", "latitude": 29.2667, "longitude": 30.0333},
        {"name": "Lake Qarun", "governorate": "Faiyum", "category": "Nature", "latitude": 29.4833, "longitude": 30.5833},
        {"name": "Tunis Village", "governorate": "Faiyum", "category": "Culture", "latitude": 29.3833, "longitude": 30.4833},
        {"name": "Pyramid of Meidum", "governorate": "Beni Suef", "category": "Historical", "latitude": 29.3739, "longitude": 31.1561},
        {"name": "Hawara Pyramid", "governorate": "Faiyum", "category": "Historical", "latitude": 29.2736, "longitude": 30.8986},
        {"name": "Monastery of Saint Anthony", "governorate": "Red Sea", "category": "Religious", "latitude": 28.8500, "longitude": 32.3500},

        # Nile Delta & Canal Cities (10)
        {"name": "Tanis", "governorate": "Sharqia", "category": "Historical", "latitude": 30.9728, "longitude": 31.8747},
        {"name": "Rosetta (Rashid)", "governorate": "Beheira", "category": "Historical", "latitude": 31.3995, "longitude": 30.4200},
        {"name": "Suez Canal", "governorate": "Suez", "category": "Modern", "latitude": 30.5852, "longitude": 32.2616},
        {"name": "Ismailia Museum", "governorate": "Ismailia", "category": "Museum", "latitude": 30.5961, "longitude": 32.2714},
        {"name": "Port Said Military Museum", "governorate": "Port Said", "category": "Museum", "latitude": 31.2622, "longitude": 32.3050},
        {"name": "Bubastis", "governorate": "Sharqia", "category": "Historical", "latitude": 30.5703, "longitude": 31.5060},
        {"name": "Damietta", "governorate": "Damietta", "category": "City", "latitude": 31.4167, "longitude": 31.8167},
        {"name": "Wadi El Natrun", "governorate": "Beheira", "category": "Religious", "latitude": 30.4167, "longitude": 30.3333},
        {"name": "St. Macarius Monastery", "governorate": "Beheira", "category": "Religious", "latitude": 30.2833, "longitude": 30.3167},
        {"name": "Mit Ghamr Dovecotes", "governorate": "Dakahlia", "category": "Culture", "latitude": 30.7167, "longitude": 31.2500},

        # Upper Egypt (South) (5)
        {"name": "Temple of Khnum at Esna", "governorate": "Qena", "category": "Historical", "latitude": 25.2929, "longitude": 32.5529},
        {"name": "Gebel el-Silsila", "governorate": "Aswan", "category": "Historical", "latitude": 24.6333, "longitude": 32.9333},
        {"name": "Red Monastery", "governorate": "Sohag", "category": "Religious", "latitude": 26.5547, "longitude": 31.6199},
        {"name": "White Monastery", "governorate": "Sohag", "category": "Religious", "latitude": 26.5500, "longitude": 31.6000},
        {"name": "Nag Hammadi", "governorate": "Qena", "category": "Historical", "latitude": 26.0500, "longitude": 32.1500},

        # Additional Cairo & Giza Landmarks (20)
        {"name": "Grand Egyptian Museum", "governorate": "Giza", "category": "Museum", "latitude": 29.9895, "longitude": 31.1179},
        {"name": "Ibn Tulun Mosque", "governorate": "Cairo", "category": "Religious", "latitude": 30.0286, "longitude": 31.2497},
        {"name": "Al-Azhar Mosque", "governorate": "Cairo", "category": "Religious", "latitude": 30.0456, "longitude": 31.2625},
        {"name": "Muhammad Ali Mosque", "governorate": "Cairo", "category": "Religious", "latitude": 30.0283, "longitude": 31.2594},
        {"name": "Sultan Hassan Mosque", "governorate": "Cairo", "category": "Religious", "latitude": 30.0311, "longitude": 31.2564},
        {"name": "Al-Rifa'i Mosque", "governorate": "Cairo", "category": "Religious", "latitude": 30.0317, "longitude": 31.2583},
        {"name": "Amr Ibn Al-As Mosque", "governorate": "Cairo", "category": "Religious", "latitude": 30.0100, "longitude": 31.2333},
        {"name": "Mosque of Al-Hakim", "governorate": "Cairo", "category": "Religious", "latitude": 30.0564, "longitude": 31.2611},
        {"name": "Bayt Al-Suhaymi", "governorate": "Cairo", "category": "Historical", "latitude": 30.0503, "longitude": 31.2622},
        {"name": "Gayer-Anderson Museum", "governorate": "Cairo", "category": "Museum", "latitude": 30.0297, "longitude": 31.2500},
        {"name": "Manial Palace", "governorate": "Cairo", "category": "Historical", "latitude": 30.0244, "longitude": 31.2267},
        {"name": "Abdeen Palace", "governorate": "Cairo", "category": "Historical", "latitude": 30.0417, "longitude": 31.2481},
        {"name": "Tahrir Square", "governorate": "Cairo", "category": "Modern", "latitude": 30.0444, "longitude": 31.2358},
        {"name": "Cairo Tower", "governorate": "Cairo", "category": "Modern", "latitude": 30.0456, "longitude": 31.2247},
        {"name": "Al-Azhar Park", "governorate": "Cairo", "category": "Nature", "latitude": 30.0419, "longitude": 31.2611},
        {"name": "City of the Dead", "governorate": "Cairo", "category": "Historical", "latitude": 30.0500, "longitude": 31.2800},
        {"name": "Fustat City", "governorate": "Cairo", "category": "Historical", "latitude": 30.0056, "longitude": 31.2333},
        {"name": "Rhoda Island", "governorate": "Cairo", "category": "Nature", "latitude": 30.0278, "longitude": 31.2267},
        {"name": "Manyal Palace", "governorate": "Cairo", "category": "Historical", "latitude": 30.0269, "longitude": 31.2275},
        {"name": "Baron Empain Palace", "governorate": "Cairo", "category": "Historical", "latitude": 30.0867, "longitude": 31.3267},

        # Luxor & Upper Egypt Landmarks (25)
        {"name": "Karnak Temple Complex", "governorate": "Luxor", "category": "Historical", "latitude": 25.7188, "longitude": 32.6575},
        {"name": "Luxor Temple", "governorate": "Luxor", "category": "Historical", "latitude": 25.6997, "longitude": 32.6392},
        {"name": "Valley of the Kings", "governorate": "Luxor", "category": "Historical", "latitude": 25.7400, "longitude": 32.6017},
        {"name": "Temple of Hatshepsut", "governorate": "Luxor", "category": "Historical", "latitude": 25.7383, "longitude": 32.6067},
        {"name": "Colossi of Memnon", "governorate": "Luxor", "category": "Historical", "latitude": 25.7200, "longitude": 32.6100},
        {"name": "Medinet Habu", "governorate": "Luxor", "category": "Historical", "latitude": 25.7197, "longitude": 32.6008},
        {"name": "Ramesseum", "governorate": "Luxor", "category": "Historical", "latitude": 25.7281, "longitude": 32.6100},
        {"name": "Temple of Seti I", "governorate": "Qena", "category": "Historical", "latitude": 26.1850, "longitude": 31.9167},
        {"name": "Dendera Temple Complex", "governorate": "Qena", "category": "Historical", "latitude": 26.1417, "longitude": 32.6697},
        {"name": "Abydos Temple", "governorate": "Sohag", "category": "Historical", "latitude": 26.1850, "longitude": 31.9167},
        {"name": "Temple of Khonsu", "governorate": "Luxor", "category": "Historical", "latitude": 25.7186, "longitude": 32.6578},
        {"name": "Luxor Museum", "governorate": "Luxor", "category": "Museum", "latitude": 25.7017, "longitude": 32.6400},
        {"name": "Mummification Museum", "governorate": "Luxor", "category": "Museum", "latitude": 25.6972, "longitude": 32.6397},
        {"name": "Howard Carter House", "governorate": "Luxor", "category": "Historical", "latitude": 25.6967, "longitude": 32.6400},
        {"name": "Winter Palace Hotel", "governorate": "Luxor", "category": "Historical", "latitude": 25.6983, "longitude": 32.6392},
        {"name": "Luxor International Airport", "governorate": "Luxor", "category": "Modern", "latitude": 25.6711, "longitude": 32.7067},
        {"name": "Esna Lock", "governorate": "Luxor", "category": "Modern", "latitude": 25.2931, "longitude": 32.5533},
        {"name": "Temple of Montu", "governorate": "Luxor", "category": "Historical", "latitude": 25.7181, "longitude": 32.6583},
        {"name": "Deir el-Medina", "governorate": "Luxor", "category": "Historical", "latitude": 25.7289, "longitude": 32.6014},
        {"name": "Temple of Amenhotep III", "governorate": "Luxor", "category": "Historical", "latitude": 25.7200, "longitude": 32.6100},
        {"name": "Luxor Bazaar", "governorate": "Luxor", "category": "Market", "latitude": 25.6989, "longitude": 32.6394},
        {"name": "Nile Corniche Luxor", "governorate": "Luxor", "category": "Nature", "latitude": 25.6981, "longitude": 32.6389},
        {"name": "Banana Island", "governorate": "Luxor", "category": "Nature", "latitude": 25.6833, "longitude": 32.6500},
        {"name": "Luxor Sound and Light Show", "governorate": "Luxor", "category": "Entertainment", "latitude": 25.7000, "longitude": 32.6400},
        {"name": "Felucca Ride Luxor", "governorate": "Luxor", "category": "Entertainment", "latitude": 25.6983, "longitude": 32.6392},

        # Aswan & Nubia Landmarks (20)
        {"name": "Aswan High Dam", "governorate": "Aswan", "category": "Modern", "latitude": 23.9700, "longitude": 32.8800},
        {"name": "Abu Simbel Temples", "governorate": "Aswan", "category": "Historical", "latitude": 22.3372, "longitude": 31.6258},
        {"name": "Philae Temple", "governorate": "Aswan", "category": "Historical", "latitude": 24.0250, "longitude": 32.8833},
        {"name": "Edfu Temple", "governorate": "Aswan", "category": "Historical", "latitude": 24.9775, "longitude": 32.8733},
        {"name": "Kom Ombo Temple", "governorate": "Aswan", "category": "Historical", "latitude": 24.4517, "longitude": 32.9283},
        {"name": "Temple of Kalabsha", "governorate": "Aswan", "category": "Historical", "latitude": 23.9500, "longitude": 32.8667},
        {"name": "Nubian Museum", "governorate": "Aswan", "category": "Museum", "latitude": 24.0833, "longitude": 32.9000},
        {"name": "Aswan Museum", "governorate": "Aswan", "category": "Museum", "latitude": 24.0917, "longitude": 32.8983},
        {"name": "Unfinished Obelisk", "governorate": "Aswan", "category": "Historical", "latitude": 24.0750, "longitude": 32.8983},
        {"name": "Elephantine Island", "governorate": "Aswan", "category": "Nature", "latitude": 24.0833, "longitude": 32.8833},
        {"name": "Aswan Botanical Gardens", "governorate": "Aswan", "category": "Nature", "latitude": 24.0917, "longitude": 32.8833},
        {"name": "Nubian Village", "governorate": "Aswan", "category": "Culture", "latitude": 24.1000, "longitude": 32.9000},
        {"name": "Temple of Beit el-Wali", "governorate": "Aswan", "category": "Historical", "latitude": 23.9500, "longitude": 32.8667},
        {"name": "Temple of Dakka", "governorate": "Aswan", "category": "Historical", "latitude": 23.9500, "longitude": 32.8667},
        {"name": "Temple of Maharraqa", "governorate": "Aswan", "category": "Historical", "latitude": 23.9500, "longitude": 32.8667},
        {"name": "Aswan Souk", "governorate": "Aswan", "category": "Market", "latitude": 24.0917, "longitude": 32.8983},
        {"name": "Nasser Lake", "governorate": "Aswan", "category": "Nature", "latitude": 23.5000, "longitude": 32.5000},
        {"name": "Sehel Island", "governorate": "Aswan", "category": "Nature", "latitude": 24.0500, "longitude": 32.8833},
        {"name": "Aswan Corniche", "governorate": "Aswan", "category": "Nature", "latitude": 24.0917, "longitude": 32.8983},
        {"name": "Fatimid Cemetery", "governorate": "Aswan", "category": "Historical", "latitude": 24.1000, "longitude": 32.9000},

        # Alexandria & Mediterranean Coast Landmarks (20)
        {"name": "Bibliotheca Alexandrina", "governorate": "Alexandria", "category": "Museum", "latitude": 31.2089, "longitude": 29.9086},
        {"name": "Pompey's Pillar", "governorate": "Alexandria", "category": "Historical", "latitude": 31.1825, "longitude": 29.8967},
        {"name": "Qaitbay Citadel", "governorate": "Alexandria", "category": "Historical", "latitude": 31.2136, "longitude": 29.8858},
        {"name": "Catacombs of Kom el-Shoqafa", "governorate": "Alexandria", "category": "Historical", "latitude": 31.1789, "longitude": 29.8925},
        {"name": "Montaza Palace", "governorate": "Alexandria", "category": "Historical", "latitude": 31.2889, "longitude": 30.0158},
        {"name": "Alexandria National Museum", "governorate": "Alexandria", "category": "Museum", "latitude": 31.2000, "longitude": 29.9000},
        {"name": "Ras el-Tin Palace", "governorate": "Alexandria", "category": "Historical", "latitude": 31.2000, "longitude": 29.8833},
        {"name": "Abu al-Abbas al-Mursi Mosque", "governorate": "Alexandria", "category": "Religious", "latitude": 31.2000, "longitude": 29.8833},
        {"name": "Kom el-Dikka", "governorate": "Alexandria", "category": "Historical", "latitude": 31.2000, "longitude": 29.9000},
        {"name": "Roman Theater", "governorate": "Alexandria", "category": "Historical", "latitude": 31.2000, "longitude": 29.9000},
        {"name": "Stanley Bridge", "governorate": "Alexandria", "category": "Modern", "latitude": 31.2000, "longitude": 29.8833},
        {"name": "Alexandria Opera House", "governorate": "Alexandria", "category": "Culture", "latitude": 31.2000, "longitude": 29.9000},
        {"name": "Alexandria Aquarium", "governorate": "Alexandria", "category": "Entertainment", "latitude": 31.2000, "longitude": 29.9000},
        {"name": "Shallalat Gardens", "governorate": "Alexandria", "category": "Nature", "latitude": 31.2000, "longitude": 29.9000},
        {"name": "Mamoura Beach", "governorate": "Alexandria", "category": "Nature", "latitude": 31.2000, "longitude": 29.8833},
        {"name": "Agami Beach", "governorate": "Alexandria", "category": "Nature", "latitude": 31.1000, "longitude": 29.7667},
        {"name": "Sidi Abdel Rahman", "governorate": "Matruh", "category": "Nature", "latitude": 30.8500, "longitude": 28.8500},
        {"name": "Marsa Matruh", "governorate": "Matruh", "category": "City", "latitude": 31.3500, "longitude": 27.2333},
        {"name": "Cleopatra Beach", "governorate": "Matruh", "category": "Nature", "latitude": 31.3500, "longitude": 27.2333},
        {"name": "Almaza Bay", "governorate": "Matruh", "category": "Nature", "latitude": 31.3500, "longitude": 27.2333},

        # Sinai & Red Sea Landmarks (20)
        {"name": "Mount Sinai", "governorate": "South Sinai", "category": "Religious", "latitude": 28.5397, "longitude": 33.9756},
        {"name": "St. Catherine's Monastery", "governorate": "South Sinai", "category": "Religious", "latitude": 28.5561, "longitude": 33.9761},
        {"name": "Sharm El Sheikh", "governorate": "South Sinai", "category": "City", "latitude": 27.9667, "longitude": 34.3333},
        {"name": "Ras Muhammad National Park", "governorate": "South Sinai", "category": "Nature", "latitude": 27.7333, "longitude": 34.2500},
        {"name": "Dahab", "governorate": "South Sinai", "category": "City", "latitude": 28.4833, "longitude": 34.5000},
        {"name": "Blue Hole Dahab", "governorate": "South Sinai", "category": "Nature", "latitude": 28.5722, "longitude": 34.5367},
        {"name": "Nuweiba", "governorate": "South Sinai", "category": "City", "latitude": 29.0333, "longitude": 34.6667},
        {"name": "Taba", "governorate": "South Sinai", "category": "City", "latitude": 29.5000, "longitude": 34.8833},
        {"name": "Taba Heights", "governorate": "South Sinai", "category": "Modern", "latitude": 29.5000, "longitude": 34.8833},
        {"name": "Hurghada", "governorate": "Red Sea", "category": "City", "latitude": 27.2500, "longitude": 33.8333},
        {"name": "Giftun Island", "governorate": "Red Sea", "category": "Nature", "latitude": 27.1833, "longitude": 33.9333},
        {"name": "El Gouna", "governorate": "Red Sea", "category": "Modern", "latitude": 27.4000, "longitude": 33.6833},
        {"name": "Soma Bay", "governorate": "Red Sea", "category": "Modern", "latitude": 26.8500, "longitude": 33.9833},
        {"name": "Safaga", "governorate": "Red Sea", "category": "City", "latitude": 26.7333, "longitude": 33.9333},
        {"name": "Quseir", "governorate": "Red Sea", "category": "City", "latitude": 26.1000, "longitude": 34.2833},
        {"name": "Marsa Alam", "governorate": "Red Sea", "category": "City", "latitude": 25.0667, "longitude": 34.9000},
        {"name": "Wadi el-Gemal National Park", "governorate": "Red Sea", "category": "Nature", "latitude": 24.5000, "longitude": 35.0000},
        {"name": "Shalateen", "governorate": "Red Sea", "category": "City", "latitude": 23.1333, "longitude": 35.5833},
        {"name": "Halayeb Triangle", "governorate": "Red Sea", "category": "Nature", "latitude": 22.5000, "longitude": 35.5000},
        {"name": "Zafarana", "governorate": "Red Sea", "category": "Nature", "latitude": 28.4167, "longitude": 32.6667},

        # Western Desert & Oases Landmarks (20)
        {"name": "Siwa Oasis", "governorate": "Matruh", "category": "Nature", "latitude": 29.2000, "longitude": 25.5167},
        {"name": "Temple of the Oracle", "governorate": "Matruh", "category": "Historical", "latitude": 29.2000, "longitude": 25.5167},
        {"name": "Cleopatra's Pool", "governorate": "Matruh", "category": "Nature", "latitude": 29.2000, "longitude": 25.5167},
        {"name": "Shali Fortress", "governorate": "Matruh", "category": "Historical", "latitude": 29.2000, "longitude": 25.5167},
        {"name": "Bahariya Oasis", "governorate": "Giza", "category": "Nature", "latitude": 28.3500, "longitude": 28.8500},
        {"name": "White Desert", "governorate": "New Valley", "category": "Nature", "latitude": 27.5000, "longitude": 28.0000},
        {"name": "Black Desert", "governorate": "New Valley", "category": "Nature", "latitude": 27.5000, "longitude": 28.0000},
        {"name": "Crystal Mountain", "governorate": "New Valley", "category": "Nature", "latitude": 27.5000, "longitude": 28.0000},
        {"name": "Farafra Oasis", "governorate": "New Valley", "category": "Nature", "latitude": 27.0667, "longitude": 27.9667},
        {"name": "Dakhla Oasis", "governorate": "New Valley", "category": "Nature", "latitude": 25.5000, "longitude": 29.0000},
        {"name": "Kharga Oasis", "governorate": "New Valley", "category": "Nature", "latitude": 25.4500, "longitude": 30.5500},
        {"name": "Temple of Hibis", "governorate": "New Valley", "category": "Historical", "latitude": 25.4500, "longitude": 30.5500},
        {"name": "Al-Qasr Village", "governorate": "New Valley", "category": "Historical", "latitude": 25.4500, "longitude": 30.5500},
        {"name": "Mut Village", "governorate": "New Valley", "category": "Historical", "latitude": 25.4500, "longitude": 30.5500},
        {"name": "Bagawat Necropolis", "governorate": "New Valley", "category": "Historical", "latitude": 25.4500, "longitude": 30.5500},
        {"name": "Temple of Nadura", "governorate": "New Valley", "category": "Historical", "latitude": 25.4500, "longitude": 30.5500},
        {"name": "Qasr al-Labakha", "governorate": "New Valley", "category": "Historical", "latitude": 25.4500, "longitude": 30.5500},
        {"name": "Deir al-Hagar", "governorate": "New Valley", "category": "Historical", "latitude": 25.4500, "longitude": 30.5500},
        {"name": "Temple of Qasr Dush", "governorate": "New Valley", "category": "Historical", "latitude": 25.4500, "longitude": 30.5500},
        {"name": "Roman Necropolis", "governorate": "New Valley", "category": "Historical", "latitude": 25.4500, "longitude": 30.5500},

        # Delta & Canal Zone Landmarks (15)
        {"name": "Port Said Lighthouse", "governorate": "Port Said", "category": "Historical", "latitude": 31.2667, "longitude": 32.3000},
        {"name": "Suez Canal", "governorate": "Suez", "category": "Modern", "latitude": 30.5852, "longitude": 32.2616},
        {"name": "Ismailia Museum", "governorate": "Ismailia", "category": "Museum", "latitude": 30.5961, "longitude": 32.2714},
        {"name": "Port Said Military Museum", "governorate": "Port Said", "category": "Museum", "latitude": 31.2622, "longitude": 32.3050},
        {"name": "Bubastis", "governorate": "Sharqia", "category": "Historical", "latitude": 30.5703, "longitude": 31.5060},
        {"name": "Damietta", "governorate": "Damietta", "category": "City", "latitude": 31.4167, "longitude": 31.8167},
        {"name": "Wadi El Natrun", "governorate": "Beheira", "category": "Religious", "latitude": 30.4167, "longitude": 30.3333},
        {"name": "St. Macarius Monastery", "governorate": "Beheira", "category": "Religious", "latitude": 30.2833, "longitude": 30.3167},
        {"name": "Mit Ghamr Dovecotes", "governorate": "Dakahlia", "category": "Culture", "latitude": 30.7167, "longitude": 31.2500},
        {"name": "Tanta", "governorate": "Gharbia", "category": "City", "latitude": 30.7833, "longitude": 31.0000},
        {"name": "Mansoura", "governorate": "Dakahlia", "category": "City", "latitude": 31.0500, "longitude": 31.3833},
        {"name": "Zagazig", "governorate": "Sharqia", "category": "City", "latitude": 30.5833, "longitude": 31.5000},
        {"name": "Banha", "governorate": "Qalyubia", "category": "City", "latitude": 30.4667, "longitude": 31.1833},
        {"name": "Qalyub", "governorate": "Qalyubia", "category": "City", "latitude": 30.1833, "longitude": 31.2000},
        {"name": "Shibin El Kom", "governorate": "Menoufia", "category": "City", "latitude": 30.5500, "longitude": 31.0167},

        # Additional Upper Egypt Landmarks (20)
        {"name": "Temple of Khnum at Esna", "governorate": "Qena", "category": "Historical", "latitude": 25.2929, "longitude": 32.5529},
        {"name": "Gebel el-Silsila", "governorate": "Aswan", "category": "Historical", "latitude": 24.6333, "longitude": 32.9333},
        {"name": "Red Monastery", "governorate": "Sohag", "category": "Religious", "latitude": 26.5547, "longitude": 31.6199},
        {"name": "White Monastery", "governorate": "Sohag", "category": "Religious", "latitude": 26.5500, "longitude": 31.6000},
        {"name": "Nag Hammadi", "governorate": "Qena", "category": "Historical", "latitude": 26.0500, "longitude": 32.1500},
        {"name": "Qena Temple", "governorate": "Qena", "category": "Historical", "latitude": 26.1667, "longitude": 32.7167},
        {"name": "Dendera Zodiac", "governorate": "Qena", "category": "Historical", "latitude": 26.1417, "longitude": 32.6697},
        {"name": "Temple of Hathor", "governorate": "Qena", "category": "Historical", "latitude": 26.1417, "longitude": 32.6697},
        {"name": "Abydos", "governorate": "Sohag", "category": "Historical", "latitude": 26.1850, "longitude": 31.9167},
        {"name": "Sohag Museum", "governorate": "Sohag", "category": "Museum", "latitude": 26.5500, "longitude": 31.7000},
        {"name": "Akhmim", "governorate": "Sohag", "category": "Historical", "latitude": 26.5667, "longitude": 31.7500},
        {"name": "Temple of Min", "governorate": "Sohag", "category": "Historical", "latitude": 26.5667, "longitude": 31.7500},
        {"name": "El-Minya", "governorate": "Minya", "category": "City", "latitude": 28.0833, "longitude": 30.7500},
        {"name": "Beni Hasan Tombs", "governorate": "Minya", "category": "Historical", "latitude": 27.9333, "longitude": 30.8833},
        {"name": "Tell el-Amarna", "governorate": "Minya", "category": "Historical", "latitude": 27.6667, "longitude": 30.9000},
        {"name": "Mallawi Museum", "governorate": "Minya", "category": "Museum", "latitude": 27.7333, "longitude": 30.8333},
        {"name": "Assiut", "governorate": "Assiut", "category": "City", "latitude": 27.1833, "longitude": 31.1833},
        {"name": "Assiut Barrage", "governorate": "Assiut", "category": "Modern", "latitude": 27.1833, "longitude": 31.1833},
        {"name": "Qena", "governorate": "Qena", "category": "City", "latitude": 26.1667, "longitude": 32.7167},
        {"name": "Luxor West Bank", "governorate": "Luxor", "category": "Historical", "latitude": 25.7200, "longitude": 32.6100},

        # Additional Miscellaneous Landmarks (20)
        {"name": "St. Paul's Monastery", "governorate": "Red Sea", "category": "Religious", "latitude": 28.8442, "longitude": 32.5442},
        {"name": "Coloured Canyon", "governorate": "South Sinai", "category": "Nature", "latitude": 29.2833, "longitude": 34.7333},
        {"name": "Fjord Bay", "governorate": "South Sinai", "category": "Nature", "latitude": 29.4200, "longitude": 34.8800},
        {"name": "Mahmya Island", "governorate": "Red Sea", "category": "Nature", "latitude": 27.2333, "longitude": 33.9333},
        {"name": "Al-Gawhara Palace Museum", "governorate": "Cairo", "category": "Museum", "latitude": 30.0289, "longitude": 31.2600},
        {"name": "Ras El Bar", "governorate": "Damietta", "category": "Nature", "latitude": 31.5000, "longitude": 31.8333},
        {"name": "Lake Manzala", "governorate": "Dakahlia", "category": "Nature", "latitude": 31.2500, "longitude": 32.1667},
        {"name": "Wadi Degla", "governorate": "Cairo", "category": "Nature", "latitude": 29.9833, "longitude": 31.3667},
        {"name": "Wadi Rayan", "governorate": "Faiyum", "category": "Nature", "latitude": 29.1667, "longitude": 30.4167},
        {"name": "Faiyum Oasis", "governorate": "Faiyum", "category": "Nature", "latitude": 29.3000, "longitude": 30.8333},
        {"name": "Hawara Pyramid", "governorate": "Faiyum", "category": "Historical", "latitude": 29.2667, "longitude": 30.9000},
        {"name": "Lahun Pyramid", "governorate": "Faiyum", "category": "Historical", "latitude": 29.2333, "longitude": 30.9667},
        {"name": "Karanis", "governorate": "Faiyum", "category": "Historical", "latitude": 29.5167, "longitude": 30.9000},
        {"name": "Medinet Madi", "governorate": "Faiyum", "category": "Historical", "latitude": 29.2000, "longitude": 30.6500},
        {"name": "Qasr Qarun", "governorate": "Faiyum", "category": "Historical", "latitude": 29.3667, "longitude": 30.4167},
        {"name": "Dimai", "governorate": "Faiyum", "category": "Historical", "latitude": 29.4833, "longitude": 30.6167},
        {"name": "Soknopaiou Nesos", "governorate": "Faiyum", "category": "Historical", "latitude": 29.5333, "longitude": 30.6667},
        {"name": "Tebtunis", "governorate": "Faiyum", "category": "Historical", "latitude": 29.1000, "longitude": 30.7500},
        {"name": "Berenice", "governorate": "Red Sea", "category": "Historical", "latitude": 23.9500, "longitude": 35.4833},
        {"name": "Myos Hormos", "governorate": "Red Sea", "category": "Historical", "latitude": 26.1167, "longitude": 34.2500},
    ]

def seed_database():
    """Seed the database with a comprehensive list of 300 Egyptian landmarks."""
    # Ensure DB connection is active
    connect_to_db()
    if landmarks_collection is None:
        print("Database connection not established. Aborting seed.")
        return

    try:
        print("Clearing existing landmark data...")
        landmarks_collection.delete_many({})  # Clear existing data
        print("Existing data cleared.")

        egyptian_landmarks = get_landmarks()
        total_landmarks = len(egyptian_landmarks)
        print(f"Found {total_landmarks} landmarks to insert.")

        # Insert with a progress bar
        with tqdm(total=total_landmarks, desc="Seeding Database", unit="landmark") as pbar:
            for landmark in egyptian_landmarks:
                landmarks_collection.insert_one(landmark)
                pbar.update(1)

        print("\nDatabase seeding completed successfully!")
        print(f"Total landmarks inserted: {landmarks_collection.count_documents({})}")

    except Exception as e:
        print(f"\nAn error occurred during database seeding: {e}")

if __name__ == "__main__":
    seed_database()
