import asyncio
import sys
from pathlib import Path

# Automatically append project root to Python search path
ROOT_DIR = Path(__file__).resolve().parent.parent.parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import AsyncSessionMaker
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

CATEGORIES_SEED = [
    {
        "slug": "hardware",
        "name_en": "Hardware & building",
        "name_ne": "हार्डवेयर र निर्माण",
        "subcategories": [
            ("cement", "Cement", "सिमेन्ट"),
            ("steel", "Steel & Rods", "छड तथा स्टिल"),
            ("sanitary", "Pipes & Sanitary", "पाइप तथा स्यानिटरी"),
            ("paints", "Paints & Color", "पेन्ट र रङ्ग"),
        ],
    },
    {
        "slug": "electronics",
        "name_en": "Mobile & electronics",
        "name_ne": "मोबाइल र इलेक्ट्रोनिक्स",
        "subcategories": [
            ("mobiles", "Smartphones & Mobiles", "स्मार्टफोन र मोबाइल"),
            ("laptops", "Laptops & Computers", "ल्यापटप र कम्प्युटर"),
            ("accessories", "Mobile Accessories", "मोबाइल एसेसरीज"),
        ],
    },
    {
        "slug": "pharmacy",
        "name_en": "Pharmacies",
        "name_ne": "औषधि पसल",
        "subcategories": [
            ("medicines", "General Medicines", "सामान्य औषधि"),
            ("wellness", "Health & Wellness", "स्वास्थ्य सामान"),
        ],
    },
    {
        "slug": "grocery",
        "name_en": "Grocery & wholesale",
        "name_ne": "किराना र होलसेल",
        "subcategories": [
            ("rice", "Rice & Grains", "चामल तथा अन्न"),
            ("oil", "Cooking Oil", "खाने तेल"),
            ("beverages", "Beverages & Drinks", "पेय पदार्थ"),
        ],
    },
    {
        "slug": "auto-parts",
        "name_en": "Auto parts",
        "name_ne": "अटो पार्ट्स",
        "subcategories": [
            ("bike-parts", "Bike Parts & Service", "बाइक पार्ट्स र सर्भिसिङ"),
            ("car-parts", "Car Accessories", "कार सामान"),
        ],
    },
    {
        "slug": "furniture",
        "name_en": "Furniture & Home",
        "name_ne": "फर्निचर र घर",
        "subcategories": [
            ("wooden-furniture", "Wooden Furniture", "काठको फर्निचर"),
            ("home-decor", "Home Decor", "घर सजावट"),
        ],
    },
    {
        "slug": "restaurants",
        "name_en": "Restaurants & Food",
        "name_ne": "रेस्टुरेन्ट र खाना",
        "subcategories": [
            ("fast-food", "Fast Food & Khaja", "फास्ट फुड र खाजा"),
            ("cafes", "Cafes & Coffee", "कैफे र कफी"),
        ],
    },
    {
        "slug": "hotels",
        "name_en": "Hotels & Lodging",
        "name_ne": "होटल र आवास",
        "subcategories": [
            ("lodging", "Lodging & Rooms", "बसौटी र कोठा"),
            ("resorts", "Resorts", "रिसोर्ट"),
        ],
    },
    {
        "slug": "clothing",
        "name_en": "Clothing & Fashion",
        "name_ne": "कपडा र फेसन",
        "subcategories": [
            ("mens-wear", "Men's Wear", "पुरुषको कपडा"),
            ("womens-wear", "Women's Wear", "महिलाको कपडा"),
        ],
    },
    {
        "slug": "electrical",
        "name_en": "Electrical & Solar",
        "name_ne": "विद्युत र सौर्य",
        "subcategories": [
            ("wiring", "Wiring & Switches", "वायरिङ र स्विच"),
            ("solar-panels", "Solar Systems", "सौर्य प्रणाली"),
        ],
    },
    {
        "slug": "agriculture",
        "name_en": "Agriculture & Farming",
        "name_ne": "कृषि र खेती",
        "subcategories": [
            ("seeds", "Seeds & Fertilizer", "बीउ तथा मल"),
            ("agri-tools", "Farming Equipment", "कृषि औजार"),
        ],
    },
    {
        "slug": "jewelry",
        "name_en": "Jewelry & Gold",
        "name_ne": "गहना र सुन",
        "subcategories": [
            ("gold", "Gold Jewelry", "सुनको गहना"),
            ("silver", "Silver Jewelry", "चाँदीको गहना"),
        ],
    },
    {
        "slug": "education",
        "name_en": "Education",
        "name_ne": "शिक्षा",
        "subcategories": [
            ("institutes", "Tuition & Coaching", "ट्युसन र कोचिङ"),
            ("consultancy", "Educational Consultancy", "शैक्षिक परामर्श"),
        ],
    },
    {
        "slug": "beauty",
        "name_en": "Beauty & Spa",
        "name_ne": "सौन्दर्य र स्पा",
        "subcategories": [
            ("parlor", "Beauty Parlor & Saloon", "ब्युटी पार्लर र सैलुन"),
            ("cosmetics", "Cosmetics", "सौन्दर्य सामग्री"),
        ],
    },
    {
        "slug": "property",
        "name_en": "Property & Real Estate",
        "name_ne": "घरजग्गा",
        "subcategories": [
            ("land", "Land & Plots", "जग्गा"),
            ("rentals", "House & Room Rent", "घर तथा कोठा भाडा"),
        ],
    },
    {
        "slug": "repairs",
        "name_en": "Repair & Services",
        "name_ne": "मर्मत र सेवा",
        "subcategories": [
            ("appliance-repair", "Home Appliance Repair", "घरयासी सामान मर्मत"),
            ("plumbing", "Plumbing & Wiring", "प्लम्बिङ र वायरिङ"),
        ],
    },
    {
        "slug": "wedding",
        "name_en": "Wedding Planning",
        "name_ne": "विवाह योजना",
        "subcategories": [
            ("catering", "Catering & Party Venue", "क्याटरिङ र पार्टी प्यालेस"),
            ("photography", "Wedding Photography", "विवाह फोटोग्राफी"),
        ],
    },
    {
        "slug": "pets",
        "name_en": "Pet Supplies",
        "name_ne": "पाल्तु जनावरका सामान",
        "subcategories": [
            ("pet-food", "Pet Food & Care", "जनावरको खाना र हेरचाह"),
        ],
    },
    {
        "slug": "stationery",
        "name_en": "Stationery & Printing",
        "name_ne": "स्टेसनरी र छपाइ",
        "subcategories": [
            ("printing", "Flex & Offset Printing", "फ्लेक्स र छापाखाना"),
            ("books", "Books & Booksellers", "किताब र स्टेसनरी"),
        ],
    },
    {
        "slug": "other",
        "name_en": "Other Categories",
        "name_ne": "अन्य वर्ग",
        "subcategories": [],
    },
]

async def seed_categories():
    print("🏷️ Seeding categories and subcategories...")
    async with AsyncSessionMaker() as session:
        async with session.begin():
            for cat in CATEGORIES_SEED:
                parent_cat, created = await get_or_create(
                    session, CategoryModel,
                    {"slug": cat["slug"]},
                    {
                        "name_en": cat["name_en"],
                        "name_ne": cat["name_ne"],
                        "description": f"{cat['name_en']} category",
                        "parent_id": 0,  # Top-level root category
                        "is_active": True
                    }
                )

                for sub_slug, sub_en, sub_ne in cat["subcategories"]:
                    await get_or_create(
                        session, CategoryModel,
                        {"slug": sub_slug},
                        {
                            "name_en": sub_en,
                            "name_ne": sub_ne,
                            "description": f"{sub_en} subcategory",
                            "parent_id": parent_cat.id,
                            "is_active": True
                        }
                    )

        print("✨ Categories seeded successfully!")

if __name__ == "__main__":
    asyncio.run(seed_categories())