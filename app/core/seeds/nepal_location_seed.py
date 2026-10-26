import asyncio
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

# Change this:

# To this:
from app.core.database import AsyncSessionMaker

from app.hajaro.models.locations import Locations, Locationtype
from app.hajaro.models.categories import CategoryModel

async def get_or_create(session: AsyncSession, model, unique_filters, defaults=None):
    stmt = select(model).filter_by(**unique_filters)
    result = await session.execute(stmt)
    instance = result.scalar_one_or_none()
    
    if instance:
        return instance, False
    
    params = dict(unique_filters)
    if defaults:
        params.update(defaults)
    
    instance = model(**params)
    session.add(instance)
    await session.flush()
    return instance, True

# Official reference mapping: Province -> Districts -> Key Municipalities
NEPAL_GEOGRAPHY = {
    "koshi": {
        "name_en": "Koshi Province", "name_ne": "कोशी प्रदेश",
        "districts": {
            "bhojpur": ("Bhojpur District", "भोजपुर जिल्ला", ["Bhojpur", "Shadananda"]),
            "dhankuta": ("Dhankuta District", "धनकुटा जिल्ला", ["Dhankuta", "Mahalaxmi", "Pakhribas"]),
            "ilam": ("Ilam District", "इलाम जिल्ला", ["Ilam", "Deumai", "Ilam Municipality", "Suryodaya"]),
            "jhapa": ("Jhapa District", "झापा जिल्ला", ["Damak", "Birtamod", "Mechinagar", "Bhadrapur", "Kankai", "Gauradaha", "Shivasatakshi", "Urlabari"]),
            "khotang": ("Khotang District", "खोटाङ जिल्ला", ["Diktel Rupakot Majhuwagadhi", "Halesi Tuwachung"]),
            "morang": ("Morang District", "मोरङ जिल्ला", ["Biratnagar", "Letang", "Rangeli", "Urlabari", "Belbari", "Pathari Shanishchare"]),
            "okhaldunga": ("Okhaldhunga District", "ओखलढुङ्गा जिल्ला", ["Siddhicharan"]),
            "panchthar": ("Panchthar District", "पाँचथर जिल्ला", ["Phidim"]),
            "sankhuwasabha": ("Sankhuwasabha District", "सङ्खुवासभा जिल्ला", ["Khandbari", "Chainpur", "Dharmadevi", "Panchkhapan"]),
            "solukhumbu": ("Solukhumbu District", "सोलुखुम्बु जिल्ला", ["Solududhkunda"]),
            "sunsari": ("Sunsari District", "सुनसरी जिल्ला", ["Itahari", "Dharan", "Inaruwa", "Barahachhetra", "Duhabi"]),
            "taplejung": ("Taplejung District", "ताप्लेजुङ जिल्ला", ["Phungling"]),
            "tehrathum": ("Tehrathum District", "तेह्रथुम जिल्ला", ["Myanglung", "Laligurans"]),
            "udayapur": ("Udayapur District", "उदयपुर जिल्ला", ["Triyuga", "Katari", "Chaudandigadhi", "Beltar Basaha"])
        }
    },
    "madhesh": {
        "name_en": "Madhesh Province", "name_ne": "मधेश प्रदेश",
        "districts": {
            "bara": ("Bara District", "बारा जिल्ला", ["Kalaiya", "Jeetpursimara", "Nijgadh", "Mahagadhimai"]),
            "dhanusha": ("Dhanusha District", "धनुषा जिल्ला", ["Janakpurdham", "Dhanushadham", "Ganeshman Charnath", "Hansapur"]),
            "mahottari": ("Mahottari District", "महोत्तरी जिल्ला", ["Jaleshwar", "Bardibas", "Gaushala", "Lalbandi"]),
            "parsa": ("Parsa District", "पर्सा जिल्ला", ["Birgunj", "Bahudarmai", "Pokhariya"]),
            "saptari": ("Saptari District", "सप्तरी जिल्ला", ["Rajbiraj", "Kanchanrup", "Dakneshwori", "Hanumannagar"]),
            "sarlahi": ("Sarlahi District", "सर्लाही जिल्ला", ["Malangawa", "Ishworpur", "Lalbandi", "Hariwan"]),
            "siraha": ("Siraha District", "सिराहा जिल्ला", ["Siraha", "Lahan", "Dhangadhimai", "Golbazar", "Mirchaiya"]),
            "rautahat": ("Rautahat District", "रौतहट जिल्ला", ["Gaur", "Chandrapur", "Garuda", "Gujara"])
        }
    },
    "bagmati": {
        "name_en": "Bagmati Province", "name_ne": "बागमती प्रदेश",
        "districts": {
            "bhaktapur": ("Bhaktapur District", "भक्तपुर जिल्ला", ["Bhaktapur", "Madhyapur Thimi", "Suryabinayak", "Changunarayan"]),
            "chitwan": ("Chitwan District", "चितवन जिल्ला", ["Bharatpur", "Ratnanagar", "Rapti", "Khairahani", "Kalika"]),
            "dhading": ("Dhading District", "धादिङ जिल्ला", ["Nilkantha", "Dhunibeshi"]),
            "dolakha": ("Dolakha District", "दोलखा जिल्ला", ["Bhimeshwor", "Jiri"]),
            "kathmandu-dist": ("Kathmandu District", "काठमाडौं जिल्ला", ["Kathmandu", "Kirtipur", "Budhanilkantha", "Chandragiri", "Tokha", "Tarakeshwar", "Nagarjun", "Gokarneshwor", "Kageshwari Manohara", "Shankharapur", "Dakshinkali"]),
            "kavrepalanchok": ("Kavrepalanchok District", "काभ्रेपलाञ्चोक जिल्ला", ["Dhulikhel", "Banepa", "Panauti", "Panchkhal", "Namobuddha"]),
            "lalitpur": ("Lalitpur District", "ललितपुर जिल्ला", ["Lalitpur", "Godawari", "Mahalaxmi"]),
            "makwanpur": ("Makwanpur District", "मकवानपुर जिल्ला", ["Hetauda", "Thaha"]),
            "nuwakot": ("Nuwakot District", "नुवाकोट जिल्ला", ["Bidur"]),
            "ramechhap": ("Ramechhap District", "रामेछाप जिल्ला", ["Manthali", "Ramechhap"]),
            "rasuwa": ("Rasuwa District", "रसुवा जिल्ला", []),
            "sindhuli": ("Sindhuli District", "सिन्धुली जिल्ला", ["Kamalamai", "Dudhauli"]),
            "sindhupalchok": ("Sindhupalchok District", "सिन्धुपाल्चोक जिल्ला", ["Chautara Sangachokgadhi", "Melamchi", "Barhabise"])
        }
    },
    "gandaki": {
        "name_en": "Gandaki Province", "name_ne": "गण्डकी प्रदेश",
        "districts": {
            "baglung": ("Baglung District", "बाग्लुङ जिल्ला", ["Baglung", "Dhorpatan", "Galkot", "Jaimuni"]),
            "gorkha": ("Gorkha District", "गोरखा जिल्ला", ["Gorkha", "Palungtar"]),
            "kaski": ("Kaski District", "कास्की जिल्ला", ["Pokhara", "Annapurna", "Machhapuchhre", "Rupa"]),
            "lamjung": ("Lamjung District", "लमजुङ जिल्ला", ["Besisahar", "Sundarbazar", "Rainas", "MadhyaNepal"]),
            "manang": ("Manang District", "मनाङ जिल्ला", []),
            "mustang": ("Mustang District", "मुस्ताङ जिल्ला", []),
            "myagdi": ("Myagdi District", "म्याग्दी जिल्ला", ["Beni"]),
            "parbat": ("Parbat District", "पर्वत जिल्ला", ["Kushma", "Phalebas"]),
            "syangja": ("Syangja District", "स्याङ्जा जिल्ला", ["Putalibazar", "Waling", "Chapakot", "Galyang"]),
            "tanahun": ("Tanahun District", "तनहुँ जिल्ला", ["Vyas", "Bhanu", "Shuklagandaki", "Bhimad"])
        }
    },
    "lumbini": {
        "name_en": "Lumbini Province", "name_ne": "लुम्बिनी प्रदेश",
        "districts": {
            "arghakhanchi": ("Arghakhanchi District", "अर्घाखाँची जिल्ला", ["Sandhikharka", "Bhumikasthan", "Shitganga"]),
            "banke": ("Banke District", "बाँके जिल्ला", ["Nepalgunj", "Kohalpur"]),
            "bardiya": ("Bardiya District", "बर्दिया जिल्ला", ["Gulariya", "Madhuwan", "Rajapur", "Thakur Baba", "Barbardiya"]),
            "dang": ("Dang District", "दाङ जिल्ला", ["Ghorahi", "Tulsipur", "Lamahi"]),
            "eastern-nawalparasi": ("Nawalparasi East District", "नवलपरासी पूर्व", ["Gaidakot", "Devachuli", "Kawasoti", "Madhyabindu"]),
            "gulmi": ("Gulmi District", "गुल्मी जिल्ला", ["Resunga", "Musikot"]),
            "kapilvastu": ("Kapilvastu District", "कपिलवस्तु जिल्ला", ["Kapilvastu", "Taulihawa", "Shivaraj", "Krishnanagar", "Buddhabhumi"]),
            "palpa": ("Palpa District", "पाल्पा जिल्ला", ["Tansen", "Rampur"]),
            "pyuthan": ("Pyuthan District", "प्यूठान जिल्ला", ["Pyuthan", "Swargadwari"]),
            "rolpa": ("Rolpa District", "रोल्पा जिल्ला", ["Rolpa"]),
            "rukum-east": ("East Rukum District", "पूर्वी रुकुम जिल्ला", []),
            "rupandehi": ("Rupandehi District", "रूपन्देही जिल्ला", ["Butwal", "Siddharthanagar", "Tilottama", "Lumbini Sanskritik"])
        }
    },
    "karnali": {
        "name_en": "Karnali Province", "name_ne": "कर्णाली प्रदेश",
        "districts": {
            "dailekh": ("Dailekh District", "दैलेख जिल्ला", ["Narayan", "Dullu", "Aathabis"]),
            "dolpa": ("Dolpa District", "डोल्पा जिल्ला", ["Tripurasundari", "Thuli Bheri"]),
            "humla": ("Humla District", "हुम्ला जिल्ला", ["Simkot"]),
            "jajarkot": ("Jajarkot District", "जाजरकोट जिल्ला", ["Bheri", "Nalgad", "Chhedagad"]),
            "jumla": ("Jumla District", "जुम्ला जिल्ला", ["Chandannath"]),
            "kalikot": ("Kalikot District", "कालिकोट जिल्ला", ["Khandachakra", "Raskot", "Tilagufa"]),
            "mugu": ("Mugu District", "मुगु जिल्ला", ["Chhayanath Rara"]),
            "salyan": ("Salyan District", "सल्यान जिल्ला", ["Sharada", "Bagchaur", "Bangad Kupinde"]),
            "surkhet": ("Surkhet District", "सुर्खेत जिल्ला", ["Birendranagar", "Bheriganga", "Gurbhakot", "Panchpuri"]),
            "western-rukum": ("West Rukum District", "पश्चिम रुकुम जिल्ला", ["Musikot", "Aathbiskot", "Chaurjahari"])
        }
    },
    "sudurpashchim": {
        "name_en": "Sudurpashchim Province", "name_ne": "सुदूरपश्चिम प्रदेश",
        "districts": {
            "achham": ("Achham District", "अछाम जिल्ला", ["Mangalsen", "Sanphebagar", "Kamalbazar", "Panchadewal Binayak"]),
            "baitadi": ("Baitadi District", "बैतडी जिल्ला", ["Dasharathchanda", "Patan", "Melauli", "Purchaudi"]),
            "bajhang": ("Bajhang District", "बझाङ जिल्ला", ["JayaPrithivi", "Bungal"]),
            "bajura": ("Bajura District", "बाजुरा जिल्ला", ["Badimalika", "Triveni", "Budhiganga", "Budhinanda"]),
            "dadeldhura": ("Dadeldhura District", "डडेलधुरा जिल्ला", ["Amargadhi", "Parasuram"]),
            "darchula": ("Darchula District", "दार्चुला जिल्ला", ["Mahakali", "Shailyashikhar"]),
            "doti": ("Doti District", "डोटी जिल्ला", ["Dipayal Silgadhi", "Shikhar"]),
            "kailali": ("Kailali District", "कैलाली जिल्ला", ["Dhangadhi", "Tikapur", "Lamki Chuha", "Ghorighodi", "Gauriganga", "Godawari"]),
            "kanchanpur": ("Kanchanpur District", "कञ्चनपुर जिल्ला", ["Bhimdatta", "Punarbas", "Shuklaphanta", "Belauri", "Bedkot"])
        }
    }
}

async def seed_nepal_geography():
    print("🌍 Seeding complete Nepal geography (Provinces, 77 Districts, Municipalities)...")
    async with AsyncSessionMaker() as session:
        async with session.begin():
            
            # Root Country Node
            nepal, _ = await get_or_create(
                session, Locations,
                {"slug": "nepal"},
                {
                    "name_en": "Nepal", "name_ne": "नेपाल",
                    "location_type": Locationtype.PROVINCE, # Or country root representation
                    "is_active": True, "parent_id": None
                }
            )

            for prov_slug, prov_info in NEPAL_GEOGRAPHY.items():
                prov_node, _ = await get_or_create(
                    session, Locations,
                    {"slug": prov_slug},
                    {
                        "name_en": prov_info["name_en"], "name_ne": prov_info["name_ne"],
                        "location_type": Locationtype.PROVINCE, "parent_id": nepal.id, "is_active": True
                    }
                )

                for dist_slug, dist_data in prov_info["districts"].items():
                    dist_name_en, dist_name_ne, municipalities = dist_data
                    dist_node, _ = await get_or_create(
                        session, Locations,
                        {"slug": dist_slug},
                        {
                            "name_en": dist_name_en, "name_ne": dist_name_ne,
                            "location_type": Locationtype.DISTRICT, "parent_id": prov_node.id, "is_active": True
                        }
                    )

                    for muni_name in municipalities:
                        muni_slug = muni_name.lower().replace(" ", "-").replace("(", "").replace(")", "")
                        await get_or_create(
                            session, Locations,
                            {"slug": muni_slug},
                            {
                                "name_en": muni_name, "name_ne": muni_name,
                                "location_type": Locationtype.MUNICIPALITY, "parent_id": dist_node.id, "is_active": True
                            }
                        )

            # Seed Core Categories
            categories_data = [
                ("hardware", "Hardware & Construction", "हार्डवेयर र निर्माण", [
                    ("cement", "Cement", "सिमेन्ट"),
                    ("steel", "Steel & Rods", "छड तथा स्टिल"),
                ]),
                ("grocery", "Grocery & Wholesale", "किराणा तथा थोक", [
                    ("rice", "Rice & Grains", "चामल तथा अन्न"),
                    ("oil", "Cooking Oil", "खाने तेल"),
                ]),
                ("pharmacy", "Pharmacy & Health", "औषधि तथा स्वास्थ्य", []),
                ("electronics", "Mobile & Electronics", "मोबाइल तथा इलेक्ट्रोनिक्स", []),
                ("auto", "Auto & Bike", "अटो तथा बाइक", []),
            ]

            for cat_slug, cat_en, cat_ne, subcategories in categories_data:
                parent_cat, _ = await get_or_create(
                    session, CategoryModel,
                    {"slug": cat_slug},
                    {
                        "name_en": cat_en, "name_ne": cat_ne,
                        "description": f"{cat_en} category", "parent_id": 0, "is_active": True
                    }
                )

                for sub_slug, sub_en, sub_ne in subcategories:
                    await get_or_create(
                        session, CategoryModel,
                        {"slug": sub_slug},
                        {
                            "name_en": sub_en, "name_ne": sub_ne,
                            "description": f"{sub_en} subcategory", "parent_id": parent_cat.id, "is_active": True
                        }
                    )

        print("✨ Full Nepal location hierarchy & categories seeded successfully!")

if __name__ == "__main__":
    asyncio.run(seed_nepal_geography())