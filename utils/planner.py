import os
import json
import logging
import random
import requests
import google.generativeai as genai

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Predefined coordinates and data for top travel destinations to serve as a robust local fallback
MOCK_DESTINATIONS = {
    "paris": {
        "coords": [48.8566, 2.3522],
        "currency": "EUR",
        "language": "French",
        "emergency": "112",
        "customs": "Always greet shopkeepers with 'Bonjour' or 'Bonsoir' when entering.",
        "safety": "Watch out for pickpockets in crowded tourist spots like Eiffel Tower and Montmartre.",
        "best_foods": "Croissants, Steak Frites, Escargot, Macarons, and Crêpes.",
        "avoid": "Avoid dining in restaurants directly adjacent to major tourist spots; they are often overpriced.",
        "weather_summary": "Mild temperatures with occasional light showers, typical for the season.",
        "temperature": "12°C - 22°C (54°F - 72°F)",
        "clothing": ["Light layers", "Water-resistant jacket", "Comfortable walking shoes"],
        "attractions": [
            {"name": "Eiffel Tower", "lat": 48.8584, "lng": 2.2945, "description": "The iconic wrought-iron lattice tower on the Champ de Mars.", "time": "09:00 AM - 12:00 PM"},
            {"name": "Louvre Museum", "lat": 48.8606, "lng": 2.3376, "description": "The world's largest art museum and home to the Mona Lisa.", "time": "01:30 PM - 05:00 PM"},
            {"name": "Sacré-Cœur & Montmartre", "lat": 48.8867, "lng": 2.3431, "description": "A beautiful basilica on a hill overlooking the entire city.", "time": "06:00 PM - 09:00 PM"},
            {"name": "Musée d'Orsay", "lat": 48.8599, "lng": 2.3265, "description": "Famous museum housing French art from 1848 to 1914, located in a grand railway station.", "time": "09:30 AM - 12:30 PM"},
            {"name": "Arc de Triomphe & Champs-Élysées", "lat": 48.8738, "lng": 2.2950, "description": "The monumental arch at the center of Place Charles de Gaulle.", "time": "02:00 PM - 05:00 PM"},
            {"name": "Sainte-Chapelle & Notre-Dame", "lat": 48.8554, "lng": 2.3450, "description": "Stunning 13th-century Gothic chapel famous for its stained glass.", "time": "09:00 AM - 12:00 PM"},
            {"name": "Jardin du Luxembourg", "lat": 48.8462, "lng": 2.3371, "description": "Tranquil royal palace garden with lawns, statues, and fountains.", "time": "02:00 PM - 04:30 PM"}
        ],
        "restaurants": [
            {"name": "Le Comptoir du Relais", "description": "Famous, bustling bistro serving high-end French classics.", "type": "Lunch"},
            {"name": "Bouillon Chartier", "description": "Historic restaurant offering traditional cuisine at incredibly low prices.", "type": "Dinner"},
            {"name": "Angelina Paris", "description": "Chic tearoom known for its rich, decadent hot chocolate.", "type": "Cafe"},
            {"name": "L'As du Fallafel", "description": "Celebrated spot in the Marais district serving legendary falafel wraps.", "type": "Lunch"},
            {"name": "Le Jules Verne", "description": "Fine-dining restaurant located inside the Eiffel Tower itself.", "type": "Dinner"}
        ],
        "nearby": [
            {"name": "Palace of Versailles", "distance": "20 km", "description": "The stunning primary residence of the French kings under Louis XIV."},
            {"name": "Disneyland Paris", "distance": "32 km", "description": "A world-class magical theme park destination perfect for family fun."}
        ],
        "checklist": [
            "Purchase Paris Museum Pass in advance",
            "Book Louvre museum tickets online",
            "Reserve Eiffel Tower summit tickets 1-2 months early",
            "Get a Paris Metro card (Navigo Decouverte)"
        ]
    },
    "tokyo": {
        "coords": [35.6762, 139.6503],
        "currency": "JPY (Japanese Yen)",
        "language": "Japanese",
        "emergency": "119 (Fire/Ambulance), 110 (Police)",
        "customs": "Never tip. Bow when greeting. Do not walk and eat at the same time.",
        "safety": "Extremely safe, but watch for scams in nightlife districts like Roppongi.",
        "best_foods": "Sushi, Ramen, Tempura, Yakitori, Okonomiyaki, and Tonkatsu.",
        "avoid": "Avoid talking loudly on trains and throwing trash on the street (take it home).",
        "weather_summary": "Generally temperate. Cherry blossoms in spring, warm in summer, pleasant autumn.",
        "temperature": "8°C - 26°C (46°F - 79°F)",
        "clothing": ["Comfortable, easily removable walking shoes", "Smart casual wear", "Light jacket"],
        "attractions": [
            {"name": "Senso-ji Temple (Asakusa)", "lat": 35.7148, "lng": 139.7967, "description": "Tokyo's oldest and one of its most significant Buddhist temples.", "time": "09:00 AM - 11:30 AM"},
            {"name": "Shibuya Crossing & Hachiko", "lat": 35.6595, "lng": 139.7005, "description": "The world's busiest pedestrian intersection, lit by vibrant screens.", "time": "06:00 PM - 08:30 PM"},
            {"name": "Meiji Jingu Shrine & Harajuku", "lat": 35.6764, "lng": 139.6993, "description": "A serene Shinto shrine set within a dense, tranquil forest.", "time": "01:30 PM - 04:30 PM"},
            {"name": "Tokyo Skytree", "lat": 35.7101, "lng": 139.8107, "description": "The tallest structure in Japan, offering panoramic city-wide views.", "time": "09:00 AM - 11:30 AM"},
            {"name": "TeamLab Planets", "lat": 35.6491, "lng": 139.7927, "description": "An immersive digital art museum where you walk through water.", "time": "01:30 PM - 04:30 PM"},
            {"name": "Shinjuku Gyoen National Garden", "lat": 35.6852, "lng": 139.7101, "description": "A large park with gorgeous Japanese traditional, English, and French gardens.", "time": "10:00 AM - 01:00 PM"},
            {"name": "Akihabara Electric Town", "lat": 35.6997, "lng": 139.7715, "description": "The epicenter of anime, gaming, electronics, and otaku culture.", "time": "03:00 PM - 07:00 PM"}
        ],
        "restaurants": [
            {"name": "Ichiran Ramen", "description": "Famous tonkotsu ramen served in individual eating booths.", "type": "Lunch"},
            {"name": "Sukiyabashi Jiro Roppongi", "description": "High-end Michelin starred sushi experience.", "type": "Dinner"},
            {"name": "Harajuku Gyoza Lou", "description": "Casual, beloved local joint specializing in pan-fried and steamed gyoza.", "type": "Lunch"},
            {"name": "Robot Restaurant (Nightlife)", "description": "High-energy neon show with music, robots, and dancers.", "type": "Entertainment"},
            {"name": "Kagurazaka Ishikawa", "description": "Refined multi-course Kaiseki cuisine showcasing seasonal ingredients.", "type": "Dinner"}
        ],
        "nearby": [
            {"name": "Mount Fuji & Hakone", "distance": "100 km", "description": "Scenic hot spring resort area with stunning views of Mt. Fuji."},
            {"name": "Kamakura", "distance": "50 km", "description": "Coastal town filled with historic Buddhist temples and a giant bronze Buddha."}
        ],
        "checklist": [
            "Rent a pocket Wi-Fi or buy an eSIM",
            "Get a welcome Suica or Pasmo IC card",
            "Book Tokyo Skytree and teamLab tickets in advance",
            "Prepare cash (many smaller shops still prefer cash)"
        ]
    },
    "new york": {
        "coords": [40.7128, -74.0060],
        "currency": "USD (US Dollar)",
        "language": "English",
        "emergency": "911",
        "customs": "Tipping is expected: 18-22% in sit-down restaurants, $1-$2 per drink at bars.",
        "safety": "Generally safe, but be alert in transit hubs and avoid unlit park areas late at night.",
        "best_foods": "New York Pizza, Bagels with Schmear, Pastrami Sandwiches, Cheesecake, and Hot Dogs.",
        "avoid": "Avoid buying tickets from costumed characters in Times Square; they will demand tips.",
        "weather_summary": "Four distinct seasons. Hot summers, snowy winters, and beautiful springs/autumns.",
        "temperature": "1°C - 29°C (34°F - 84°F)",
        "clothing": ["Comfortable layers", "Walking shoes", "Warm coat (for winter)", "Light clothes (for summer)"],
        "attractions": [
            {"name": "Central Park", "lat": 40.7851, "lng": -73.9683, "description": "Huge, scenic urban park in the middle of Manhattan.", "time": "09:00 AM - 12:00 PM"},
            {"name": "Empire State Building", "lat": 40.7484, "lng": -73.9857, "description": "Famous Art Deco skyscraper offering breathtaking high-altitude views.", "time": "01:30 PM - 04:00 PM"},
            {"name": "Times Square & Broadway", "lat": 40.7580, "lng": -73.9855, "description": "The neon-lit heart of NYC's theater district.", "time": "07:00 PM - 10:00 PM"},
            {"name": "Statue of Liberty & Ellis Island", "lat": 40.6892, "lng": -74.0445, "description": "The iconic monument of freedom in New York Harbor.", "time": "09:00 AM - 01:00 PM"},
            {"name": "The High Line & Chelsea Market", "lat": 40.7480, "lng": -74.0048, "description": "A public park built on a historic elevated freight rail line.", "time": "02:30 PM - 05:30 PM"},
            {"name": "Metropolitan Museum of Art", "lat": 40.7794, "lng": -73.9632, "description": "One of the world's greatest art museums, spanning 5,000 years of culture.", "time": "10:00 AM - 02:00 PM"},
            {"name": "Brooklyn Bridge walk", "lat": 40.7061, "lng": -73.9969, "description": "Walk across the historic suspension bridge for iconic skyline photos.", "time": "04:30 PM - 06:30 PM"}
        ],
        "restaurants": [
            {"name": "Katz's Delicatessen", "description": "Legendary Jewish deli serving towering hot pastrami sandwiches.", "type": "Lunch"},
            {"name": "Joe's Pizza", "description": "The quintessential Greenwich Village spot for a classic NY slice.", "type": "Snack"},
            {"name": "Balthazar", "description": "Lively French brasserie serving exceptional seafood and steak frites.", "type": "Dinner"},
            {"name": "Peter Luger Steak House", "description": "Famous Brooklyn establishment renowned for dry-aged porterhouse steaks.", "type": "Dinner"},
            {"name": "Russ & Daughters", "description": "Historic shop serving smoked fish, bagels, and traditional Jewish specialties.", "type": "Breakfast"}
        ],
        "nearby": [
            {"name": "Coney Island", "distance": "25 km", "description": "Historic seaside resort and amusement park in southern Brooklyn."},
            {"name": "Hudson Valley", "distance": "80 km", "description": "Scenic towns, hiking trails, and wineries along the Hudson River."}
        ],
        "checklist": [
            "Buy Broadway show tickets via TKTS booth or online",
            "Book Statue of Liberty pedestal/crown access months ahead",
            "Get a MetroCard or use contactless OMNY for transit",
            "Download a subway map app"
        ]
    },
    "london": {
        "coords": [51.5074, -0.1278],
        "currency": "GBP (British Pound)",
        "language": "English",
        "emergency": "999 or 112",
        "customs": "Queueing is sacred. Stand on the right on Tube escalators. Tipping is 10-12.5% if service is not included.",
        "safety": "Generally safe, pickpocketing is common on the Tube and around major sights.",
        "best_foods": "Fish and Chips, Full English Breakfast, Sunday Roast, Chicken Tikka Masala, and Afternoon Tea.",
        "avoid": "Avoid paying cash for transit; use contactless or Oyster card instead.",
        "weather_summary": "Unpredictable. Light rain can happen anytime, summers are mild, winters are cool.",
        "temperature": "5°C - 23°C (41°F - 73°F)",
        "clothing": ["Travel umbrella", "Light raincoat", "Comfortable walking shoes", "Warm layers"],
        "attractions": [
            {"name": "Tower of London & Tower Bridge", "lat": 51.5081, "lng": -0.0759, "description": "Historic castle housing the Crown Jewels, next to the iconic bridge.", "time": "09:00 AM - 12:30 PM"},
            {"name": "British Museum", "lat": 51.5194, "lng": -0.1270, "description": "World-famous museum dedicated to human history, art, and culture.", "time": "01:30 PM - 04:30 PM"},
            {"name": "Westminster Abbey & Big Ben", "lat": 51.4994, "lng": -0.1273, "description": "Royal coronation church next to the Houses of Parliament.", "time": "09:30 AM - 12:00 PM"},
            {"name": "London Eye", "lat": 51.5033, "lng": -0.1195, "description": "Giant observation wheel offering spectacular views across the River Thames.", "time": "01:30 PM - 03:00 PM"},
            {"name": "Covent Garden & West End", "lat": 51.5117, "lng": -0.1240, "description": "Bustling shopping, dining, and theater district.", "time": "06:00 PM - 09:30 PM"},
            {"name": "Buckingham Palace & St. James's Park", "lat": 51.5014, "lng": -0.1419, "description": "The King's official London residence. Catch Changing of the Guard.", "time": "10:00 AM - 01:00 PM"},
            {"name": "Tate Modern & Borough Market", "lat": 51.5076, "lng": -0.0994, "description": "Modern art gallery and London's oldest, most famous food market.", "time": "01:30 PM - 05:00 PM"}
        ],
        "restaurants": [
            {"name": "Dishoom", "description": "Highly popular restaurant serving delicious Bombay street food in vintage decor.", "type": "Dinner"},
            {"name": "Rules", "description": "London's oldest restaurant, serving traditional British game and classic pies.", "type": "Dinner"},
            {"name": "The Golden Hind", "description": "Historic Marylebone spot serving excellent, fresh, traditional fish and chips.", "type": "Lunch"},
            {"name": "Fortnum & Mason", "description": "The ultimate destination for a high-end, traditional English Afternoon Tea.", "type": "Afternoon Tea"},
            {"name": "Padella", "description": "Acclaimed counter-style pasta bar serving freshly rolled pasta dishes.", "type": "Lunch"}
        ],
        "nearby": [
            {"name": "Windsor Castle", "distance": "35 km", "description": "The oldest and largest inhabited castle in the world, a royal residence."},
            {"name": "Stonehenge & Bath", "distance": "150 km", "description": "Prehistoric stone monument and beautiful Roman-built Georgian city."}
        ],
        "checklist": [
            "Use a contactless card or phone for all Tube and Bus travel",
            "Book free tickets online for the Sky Garden or major museums",
            "Book West End show tickets in advance",
            "Pack an umbrella and dress in layers"
        ]
    }
}

# General fallback generator for cities not in the pre-defined list
def generate_procedural_itinerary(destination, days, budget, travelers, style, interests, transportation, hotel_pref, starting_city):
    """
    Generates a realistic travel plan procedurally based on user inputs.
    Uses standard geolocation lookups or defaults to place markers reasonably.
    """
    # Seed random with destination name to keep it semi-stable
    random.seed(destination.lower() + str(days) + budget + style)
    
    # Try to search open coordinates for the destination, or use placeholder
    lat, lng = 30.0, 31.0 # Default Cairo/Middle East
    try:
        # Use OpenStreetMap Nominatim API (public, no key needed) to resolve real coords!
        headers = {'User-Agent': 'TravelGPT_AI_Planner/1.0'}
        url = f"https://nominatim.openstreetmap.org/search?q={requests.utils.quote(destination)}&format=json&limit=1"
        res = requests.get(url, headers=headers, timeout=3)
        if res.status_code == 200:
            data = res.json()
            if data:
                lat = float(data[0]['lat'])
                lng = float(data[0]['lon'])
                logger.info(f"Resolved coordinates for {destination}: {lat}, {lng}")
    except Exception as e:
        logger.warning(f"Error fetching coordinates for {destination}: {e}")
        # Generate random coordinate deviation around a general area
        lat = 30.0 + random.uniform(-10, 10)
        lng = 15.0 + random.uniform(-20, 20)

    # Let's derive custom currency/language based on destination
    currency = "USD ($)"
    language = "English"
    dest_lower = destination.lower()
    
    # Simple heuristics
    if any(c in dest_lower for c in ["italy", "rome", "florence", "venice", "milan", "spain", "madrid", "barcelona", "germany", "berlin", "munich", "france", "paris", "nice", "greece", "athens"]):
        currency = "EUR (Euro)"
        language = "Local language"
    elif any(c in dest_lower for c in ["japan", "tokyo", "kyoto", "osaka"]):
        currency = "JPY (Japanese Yen)"
        language = "Japanese"
    elif any(c in dest_lower for c in ["india", "delhi", "mumbai", "goa", "jaipur"]):
        currency = "INR (Indian Rupee)"
        language = "Hindi / English"
    elif any(c in dest_lower for c in ["uk", "london", "manchester", "scotland", "edinburgh"]):
        currency = "GBP (British Pound)"
        language = "English"
    elif any(c in dest_lower for c in ["thailand", "bangkok", "phuket", "chiang mai"]):
        currency = "THB (Thai Baht)"
        language = "Thai"
    elif any(c in dest_lower for c in ["australia", "sydney", "melbourne"]):
        currency = "AUD (Australian Dollar)"
        language = "English"

    # Define standard activity generators based on travel style and interests
    activities_pool = {
        "History": [
            {"activity": "Visit the Old Quarter & Museum", "description": "Explore the historic artifacts, local monument structures, and heritage museums.", "attraction": "Heritage Museum"},
            {"activity": "Historic Guided Walking Tour", "description": "Discover local stories and architectural marvels with an expert guide.", "attraction": "Old Town Center"},
            {"activity": "Ancient Ruins Exploration", "description": "Walk among the historic ruins and learn about the ancient civilization that lived here.", "attraction": "Ancient Ruins"},
            {"activity": "Castle or Palace Tour", "description": "Marvel at the lavish architecture and royal history of the area's main palace.", "attraction": "Royal Palace"}
        ],
        "Food": [
            {"activity": "Local Street Food Hunt", "description": "Explore bustling night markets and food stalls to sample authentic local dishes.", "attraction": "Central Food Market"},
            {"activity": "Gourmet Tasting Tour", "description": "Sample artisanal cheese, wine, pastries, and signature culinary creations.", "attraction": "Gourmet Avenue"},
            {"activity": "Traditional Cooking Class", "description": "Learn to make classic local dishes under the guidance of a professional chef.", "attraction": "Culinary Academy"},
            {"activity": "Fine Dining Experience", "description": "Indulge in a premium multi-course meal highlighting local, seasonal ingredients.", "attraction": "Michelin Row"}
        ],
        "Nature": [
            {"activity": "Botanical Gardens Walk", "description": "Stroll through beautifully landscaped gardens and glasshouses with exotic flora.", "attraction": "National Botanical Gardens"},
            {"activity": "Scenic Hike / Nature Trail", "description": "Take a scenic path through lush forests or hills for stunning panoramic views.", "attraction": "Nature Park Trail"},
            {"activity": "Waterfall or Lake Visit", "description": "Relax near scenic waters, take photos, and enjoy the soothing sound of nature.", "attraction": "Scenic Falls"},
            {"activity": "Sunset Viewpoint Hike", "description": "Hike up to the highest point in the area to witness a spectacular sunset.", "attraction": "Panoramic Viewpoint"}
        ],
        "Shopping": [
            {"activity": "Bazaar & Souvenir Shopping", "description": "Haggle for local handicrafts, textiles, spices, and unique souvenirs.", "attraction": "Grand Bazaar"},
            {"activity": "High-Street Fashion Shopping", "description": "Explore local boutiques, high-end designer stores, and trendy avenues.", "attraction": "Fashion Street"},
            {"activity": "Flea Market Exploration", "description": "Browse vintage clothing, antiques, and interesting collectibles.", "attraction": "Local Flea Market"}
        ],
        "Beaches": [
            {"activity": "Beach Relaxation & Swimming", "description": "Lounge on soft white sand, swim in crystal-clear waters, and enjoy a fresh coconut.", "attraction": "Sandy Bay Beach"},
            {"activity": "Snorkeling / Coastal Tour", "description": "Explore vibrant coral reefs and marine life just off the shoreline.", "attraction": "Marine Reef Cove"},
            {"activity": "Sunset Beach Walk & Drinks", "description": "Take a peaceful stroll along the shore as the sun dips below the horizon, followed by beachside cocktails.", "attraction": "Sunset Coastline"}
        ],
        "Trekking": [
            {"activity": "Mountain Ridge Trekking", "description": "A challenging but rewarding trek along mountain ridges with sheer drops and epic views.", "attraction": "Alpine Ridge"},
            {"activity": "Forest Wilderness Trail", "description": "Trek deep into local national forest, keeping an eye out for local wildlife.", "attraction": "Wild Forest Reserve"},
            {"activity": "Valley View Trek", "description": "Hike through lush green valleys, crossing small streams and rustic rope bridges.", "attraction": "River Valley Trail"}
        ],
        "Nightlife": [
            {"activity": "Rooftop Lounge Experience", "description": "Sip cocktails while taking in the dazzling illuminated skyline of the city.", "attraction": "Skyline Rooftop Lounge"},
            {"activity": "Bar Crawl & Live Music", "description": "Visit local pubs and live music venues featuring local bands or DJs.", "attraction": "Music & Entertainment District"},
            {"activity": "Night Clubbing / Night Show", "description": "Dance the night away or watch a spectacular cabaret / cultural performance.", "attraction": "Neon Theater"}
        ],
        "Culture": [
            {"activity": "Art Gallery & Craft Center", "description": "Admire contemporary artworks and watch local craftsmen create traditional items.", "attraction": "National Art Gallery"},
            {"activity": "Temples & Spiritual Sites", "description": "Visit historic spiritual buildings and experience local religious customs.", "attraction": "Spiritual Sanctuary"},
            {"activity": "Cultural Performance Show", "description": "Watch a traditional dance, theater, or musical performance rich in local lore.", "attraction": "Cultural Heritage Theater"}
        ]
    }

    # Fallback pool in case interests don't map
    fallback_activities = [
        {"activity": "City Sightseeing Bus Tour", "description": "Hop on and off to see all the major landmarks of the city.", "attraction": "Central Square"},
        {"activity": "Local Park Picnic", "description": "Buy fresh bread, cheese, and fruits and relax in the city's green lung.", "attraction": "City Park"},
        {"activity": "Panoramic Observation Deck", "description": "Head up to the city's highest tower to get a 360-degree orientation.", "attraction": "Observation Deck"}
    ]

    # Map requested interests or use all if empty
    selected_interests = [i for i in interests if i in activities_pool]
    if not selected_interests:
        selected_interests = list(activities_pool.keys())

    # Build Itinerary Days
    itinerary = []
    # Shuffle interests pool to get variety
    for d in range(1, int(days) + 1):
        day_interests = list(selected_interests)
        random.shuffle(day_interests)
        
        # Pick 3 activities based on interests
        act_list = []
        for i in range(3):
            interest = day_interests[i % len(day_interests)]
            options = activities_pool[interest]
            act = random.choice(options)
            # Avoid direct duplicate names in the same day
            if act not in act_list:
                act_list.append(act)
            else:
                act_list.append(random.choice(fallback_activities))

        # Designate morning, afternoon, evening
        morning = {
            "activity": act_list[0]["activity"],
            "description": act_list[0]["description"],
            "attraction": f"{destination} {act_list[0]['attraction']}",
            "time": "09:00 AM - 12:00 PM"
        }
        afternoon = {
            "activity": act_list[1]["activity"],
            "description": act_list[1]["description"],
            "attraction": f"{destination} {act_list[1]['attraction']}",
            "time": "01:30 PM - 04:30 PM"
        }
        evening = {
            "activity": act_list[2]["activity"],
            "description": act_list[2]["description"],
            "attraction": f"{destination} {act_list[2]['attraction']}",
            "time": "06:30 PM - 09:30 PM"
        }

        # Restaurants
        restaurants = [
            {"name": f"Le {destination} Bistro", "description": "Charming local eatery serving fresh house specialties.", "type": "Lunch"},
            {"name": f"The {destination} Grill & Tavern", "description": "Atmospheric venue serving traditional dinner menu.", "type": "Dinner"}
        ]

        itinerary.append({
            "day": d,
            "morning": morning,
            "afternoon": afternoon,
            "evening": evening,
            "restaurants": restaurants,
            "travel_time": f"{random.randint(1, 3)} hours total transit time via {transportation.lower()}"
        })

    # Calculations for Budget based on Style and Days
    multiplier = {"luxury": 4.5, "family": 2.5, "solo": 1.0, "adventure": 1.5, "budget": 0.6}[style.lower()]
    base_daily_hotel = {"luxury": 350, "family": 180, "solo": 60, "adventure": 90, "budget": 35}[style.lower()]
    base_daily_food = {"luxury": 120, "family": 80, "solo": 30, "adventure": 40, "budget": 15}[style.lower()]
    
    hotel_cost = int(base_daily_hotel * days * travelers)
    food_cost = int(base_daily_food * days * travelers)
    transport_cost = int(15 * days * travelers * (1.8 if transportation.lower() == "rental car" else 1.0))
    attractions_cost = int(25 * days * travelers * (2.0 if "Luxury" in style else 1.0))
    shopping_cost = int(100 * travelers * multiplier)
    total_cost = hotel_cost + food_cost + transport_cost + attractions_cost + shopping_cost

    budget_breakdown = {
        "hotel": hotel_cost,
        "food": food_cost,
        "transport": transport_cost,
        "attractions": attractions_cost,
        "shopping": shopping_cost,
        "total": total_cost,
        "currency": currency.split()[0],
        "suggestions": [
            f"Opt for local street food stalls or small family-run diners instead of tourist hotspots.",
            f"Use public transit instead of taxis or ride-shares. Consider a multi-day transit pass.",
            f"Look for free walking tours or museum free-admission days.",
            f"Book tickets and hotel rooms online in advance to secure early bird rates."
        ]
    }

    # Packing checklist based on season and style
    clothing_list = ["Comfortable walking shoes", "Breathable socks", "Light jacket", "Underwear and sleepwear"]
    if "adventure" in style.lower() or "trekking" in selected_interests:
        clothing_list.extend(["Sturdy hiking boots", "Moisture-wicking activewear", "Rain coat"])
    if "beaches" in selected_interests:
        clothing_list.extend(["Swimwear", "Sun hat", "Sandals", "Sunglasses"])
    if budget_breakdown["currency"] == "EUR":
        clothing_list.append("Slightly formal outfit for evenings")

    packing_list = {
        "clothing": clothing_list,
        "electronics": ["Phone charger", "Universal power adapter", "Power bank", "Camera / memory cards"],
        "toiletries": ["Toothbrush and toothpaste", "Deodorant", "Sunscreen (SPF 30+)", "Personal medication", "Hand sanitizer"],
        "documents": ["Passport (valid at least 6 months)", "Visa documents", "Travel insurance printout", "Credit/Debit cards", "Hotel reservation confirmations"],
        "activities_specific": ["Reusable water bottle", "Small daypack", "Compact travel umbrella"]
    }

    # Travel tips
    travel_tips = {
        "customs": f"Be respectful of local traditions. In spiritual areas, dress modestly and ask permission before taking photos of individuals.",
        "emergency_numbers": "112 (Universal Emergency Number) or look up local equivalent upon arrival.",
        "safety": f"Keep your cash and passports in a secure inner pocket or money belt. Be aware of your surroundings, especially at night.",
        "currency": currency,
        "language": f"{language}. A greeting in the local language always opens doors and brings smiles.",
        "best_foods": "Local seasonal fruits, regional street snacks, and freshly cooked local delicacies.",
        "avoid": "Avoid walking in unlit alleys alone at night, and do not accept unsolicited help with luggage from unlicensed guides."
    }

    # Weather
    weather = {
        "summary": "Pleasant conditions expected. A mix of sunshine and passing clouds.",
        "temperature": "18°C - 25°C (64°F - 77°F)",
        "clothing_suggestions": "Comfortable light clothes during the day, with a light sweater or jacket for the cooler evening hours."
    }

    # Checklist
    checklist = [
        {"task": "Check passport validity and visa requirements", "completed": False},
        {"task": "Buy travel medical insurance", "completed": False},
        {"task": "Notify bank of upcoming travel", "completed": False},
        {"task": "Secure hotel and transportation bookings", "completed": False},
        {"task": "Pack adapters suitable for the destination plug type", "completed": False}
    ]

    # Map markers (generates markers around the base lat/lng)
    map_markers = [
        {"name": f"Hotel: {hotel_pref} Choice", "lat": lat + 0.005, "lng": lng - 0.005, "type": "hotel"},
        {"name": f"Starting Hub: {starting_city} Connection", "lat": lat - 0.012, "lng": lng + 0.010, "type": "transport"}
    ]
    for d_idx, day_plan in enumerate(itinerary):
        # Generate some slight offsets for attractions
        map_markers.append({
            "name": day_plan["morning"]["attraction"],
            "lat": lat + 0.015 * (d_idx + 1) * (-1 if d_idx % 2 == 0 else 1),
            "lng": lng + 0.012 * (d_idx + 1),
            "type": "attraction"
        })
        map_markers.append({
            "name": day_plan["afternoon"]["attraction"],
            "lat": lat - 0.008 * (d_idx + 1),
            "lng": lng - 0.018 * (d_idx + 1) * (-1 if d_idx % 2 == 0 else 1),
            "type": "attraction"
        })

    nearby_attractions = [
        {"name": f"{destination} Scenic Countryside", "distance": "15 km", "description": "A gorgeous valley with local farms and nature walks."},
        {"name": f"Historic Neighboring Town", "distance": "28 km", "description": "An authentic town famous for traditional architecture and craft workshops."}
    ]

    return {
        "destination": destination,
        "starting_city": starting_city,
        "days": days,
        "budget": budget,
        "travelers": travelers,
        "style": style,
        "interests": interests,
        "itinerary": itinerary,
        "budget_breakdown": budget_breakdown,
        "packing_list": packing_list,
        "travel_tips": travel_tips,
        "weather": weather,
        "checklist": checklist,
        "nearby_attractions": nearby_attractions,
        "map_markers": map_markers
    }

def generate_travel_plan(destination, days, budget, travelers, style, interests, transportation, hotel_pref, starting_city, api_key=None):
    """
    Generate travel plan using Gemini API (if key is set) or fall back to high-quality local generation.
    """
    api_key_to_use = api_key or os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
    
    if not api_key_to_use:
        logger.info("No Gemini API key detected. Falling back to local procedural travel generator.")
        dest_key = destination.lower().strip()
        
        # Check if we have high-quality pre-defined data for this destination
        if dest_key in MOCK_DESTINATIONS:
            # We have high quality data! Let's adapt it to user parameters
            mock_data = MOCK_DESTINATIONS[dest_key]
            
            # Geocode coords
            lat, lng = mock_data["coords"]
            
            # Map attractions to the day count
            itinerary = []
            selected_interests = [i for i in interests if i in ["History", "Food", "Nature", "Shopping", "Beaches", "Trekking", "Nightlife", "Culture"]]
            if not selected_interests:
                selected_interests = ["History", "Culture", "Food"]
                
            num_days = int(days)
            for d in range(1, num_days + 1):
                # Pick morning, afternoon, evening from our attractions pool
                # modulo indexing
                attr_idx1 = ((d - 1) * 3) % len(mock_data["attractions"])
                attr_idx2 = ((d - 1) * 3 + 1) % len(mock_data["attractions"])
                attr_idx3 = ((d - 1) * 3 + 2) % len(mock_data["attractions"])
                
                morning_attr = mock_data["attractions"][attr_idx1]
                afternoon_attr = mock_data["attractions"][attr_idx2]
                evening_attr = mock_data["attractions"][attr_idx3]
                
                rest_idx1 = ((d - 1) * 2) % len(mock_data["restaurants"])
                rest_idx2 = ((d - 1) * 2 + 1) % len(mock_data["restaurants"])
                
                restaurants = [
                    mock_data["restaurants"][rest_idx1],
                    mock_data["restaurants"][rest_idx2]
                ]
                
                itinerary.append({
                    "day": d,
                    "morning": {
                        "activity": f"Visit {morning_attr['name']}. {morning_attr['description']}",
                        "description": f"Best time to explore: {morning_attr['time']}. Soak in the local atmosphere.",
                        "attraction": morning_attr["name"],
                        "time": morning_attr["time"]
                    },
                    "afternoon": {
                        "activity": f"Explore {afternoon_attr['name']}. {afternoon_attr['description']}",
                        "description": f"Plan to spend around 2-3 hours here.",
                        "attraction": afternoon_attr["name"],
                        "time": afternoon_attr["time"]
                    },
                    "evening": {
                        "activity": f"Relax at {evening_attr['name']}. {evening_attr['description']}",
                        "description": f"Enjoy the evening sights.",
                        "attraction": evening_attr["name"],
                        "time": evening_attr["time"]
                    },
                    "restaurants": restaurants,
                    "travel_time": f"Approx 1.5 - 2 hours of travel time utilizing local {transportation.lower()} systems"
                })

            # Recalculate cost
            multiplier = {"luxury": 4.5, "family": 2.5, "solo": 1.0, "adventure": 1.5, "budget": 0.6}[style.lower()]
            base_daily_hotel = {"luxury": 300, "family": 170, "solo": 50, "adventure": 80, "budget": 30}[style.lower()]
            base_daily_food = {"luxury": 110, "family": 70, "solo": 25, "adventure": 35, "budget": 12}[style.lower()]
            
            hotel_cost = int(base_daily_hotel * num_days * travelers)
            food_cost = int(base_daily_food * num_days * travelers)
            transport_cost = int(12 * num_days * travelers)
            attractions_cost = int(20 * num_days * travelers)
            shopping_cost = int(80 * travelers * multiplier)
            total_cost = hotel_cost + food_cost + transport_cost + attractions_cost + shopping_cost
            
            budget_breakdown = {
                "hotel": hotel_cost,
                "food": food_cost,
                "transport": transport_cost,
                "attractions": attractions_cost,
                "shopping": shopping_cost,
                "total": total_cost,
                "currency": mock_data["currency"],
                "suggestions": [
                    f"Get a local reloadable transit card to save on single ride tickets.",
                    f"Book main sights online in advance to skip lines and secure discounts.",
                    f"Stay slightly outside the city center to cut hotel rates in half."
                ]
            }

            # Packing list
            clothing_list = list(mock_data.get("clothing", ["Comfortable clothes", "Walking shoes"]))
            if "Beaches" in selected_interests:
                clothing_list.extend(["Swimwear", "Sunglasses"])
            packing_list = {
                "clothing": clothing_list,
                "electronics": ["Mobile phone", "Charger", "Universal adapter", "Power bank"],
                "toiletries": ["Toothbrush", "Toothpaste", "Sunscreen", "Personal medicine"],
                "documents": ["Passport", "Tickets", "Travel insurance card", "Hotel confirmation"],
                "activities_specific": ["Comfortable backpack for daytime outings"]
            }

            travel_tips = {
                "customs": mock_data["customs"],
                "emergency_numbers": mock_data["emergency"],
                "safety": mock_data["safety"],
                "currency": mock_data["currency"] + " - local ATM withdrawals recommended.",
                "language": mock_data["language"] + ". Learning greeting words helps a lot.",
                "best_foods": mock_data["best_foods"],
                "avoid": mock_data["avoid"]
            }

            weather = {
                "summary": mock_data["weather_summary"],
                "temperature": mock_data["temperature"],
                "clothing_suggestions": ", ".join(mock_data["clothing"])
            }

            checklist = [{"task": item, "completed": False} for item in mock_data["checklist"]]
            if not checklist:
                checklist = [{"task": "Confirm tickets", "completed": False}]

            # Map markers
            map_markers = [
                {"name": f"Hotel: {hotel_pref} Choice", "lat": lat + 0.003, "lng": lng - 0.003, "type": "hotel"},
                {"name": f"Starting Station: {starting_city} Connection", "lat": lat - 0.010, "lng": lng + 0.008, "type": "transport"}
            ]
            for attr in mock_data["attractions"][:num_days * 2]:
                map_markers.append({
                    "name": attr["name"],
                    "lat": attr["lat"],
                    "lng": attr["lng"],
                    "type": "attraction"
                })

            return {
                "destination": destination.capitalize(),
                "starting_city": starting_city.capitalize(),
                "days": days,
                "budget": budget,
                "travelers": travelers,
                "style": style,
                "interests": interests,
                "itinerary": itinerary,
                "budget_breakdown": budget_breakdown,
                "packing_list": packing_list,
                "travel_tips": travel_tips,
                "weather": weather,
                "checklist": checklist,
                "nearby_attractions": mock_data["nearby"],
                "map_markers": map_markers
            }
        else:
            # Generate dynamically for any other city using the procedural engine
            return generate_procedural_itinerary(
                destination, days, budget, travelers, style, interests, transportation, hotel_pref, starting_city
            )

    # API key is present! Use Gemini API to create an awesome personalized travel plan
    try:
        logger.info(f"Gemini API key detected. Generating plan for {destination} via Gemini...")
        genai.configure(api_key=api_key_to_use)
        
        prompt = f"""
You are TravelGPT, an expert AI travel planner. Generate a highly detailed, personalized travel itinerary and complete travel plan based on these parameters:
- Destination City: {destination}
- Starting City: {starting_city}
- Duration: {days} Days
- Travel Budget Style: {budget}
- Number of Travelers: {travelers}
- Travel Style: {style}
- Interests: {', '.join(interests)}
- Preferred Local Transportation: {transportation}
- Hotel Preference: {hotel_pref}

You MUST return a JSON object with EXACTLY the following keys. Do not return any other text, markdown formatting (outside of the json code block), or additional comments. Ensure coordinates (latitude and longitude) are accurate for the specified destination's actual attractions.

JSON structure:
{{
  "destination": "Name of destination",
  "starting_city": "Name of starting city",
  "days": {days},
  "budget": "{budget}",
  "travelers": {travelers},
  "style": "{style}",
  "interests": {json.dumps(interests)},
  "itinerary": [
    {{
      "day": 1,
      "morning": {{
        "activity": "Detailed description of morning activity",
        "description": "Elaborate context of what to see, what to do",
        "attraction": "Famous Attraction Name",
        "time": "09:00 AM - 12:00 PM"
      }},
      "afternoon": {{
        "activity": "Detailed description of afternoon activity",
        "description": "More context on lunch/afternoon sightseeing",
        "attraction": "Afternoon Attraction Name",
        "time": "01:30 PM - 05:00 PM"
      }},
      "evening": {{
        "activity": "Detailed description of evening activity",
        "description": "Context of local dinner spots, walks, night views",
        "attraction": "Evening Attraction Name or Plaza",
        "time": "06:30 PM - 09:30 PM"
      }},
      "restaurants": [
        {{"name": "Recommended Restaurant Name 1", "description": "Brief note on food type/ambiance", "type": "Lunch"}},
        {{"name": "Recommended Restaurant Name 2", "description": "Brief note on food type/ambiance", "type": "Dinner"}}
      ],
      "travel_time": "Estimated local travel time between sites for the day"
    }}
  ],
  "budget_breakdown": {{
    "hotel": 150,
    "food": 80,
    "transport": 20,
    "attractions": 40,
    "shopping": 50,
    "total": 340,
    "currency": "USD",
    "suggestions": [
      "Budget saving tip 1 specific to this destination",
      "Budget saving tip 2 specific to this destination"
    ]
  }},
  "packing_list": {{
    "clothing": ["clothing item 1", "clothing item 2", "clothing item 3"],
    "electronics": ["charger", "adapter type needed here", "power bank"],
    "toiletries": ["toiletries needed"],
    "documents": ["passport", "tickets", "etc"],
    "activities_specific": ["specialized gear/items based on interests"]
  }},
  "travel_tips": {{
    "customs": "Important local customs and manners",
    "emergency_numbers": "Local police, medical, fire emergency telephone numbers",
    "safety": "Safety advice specific to the destination neighborhoods/common scams",
    "currency": "Name of currency and tips (cash vs card)",
    "language": "Primary language and common simple phrases to know",
    "best_foods": "Top 4-5 local dishes/drinks to try",
    "avoid": "What to avoid doing or buying in this city"
  }},
  "weather": {{
    "summary": "Expected climate/weather summary for the trip",
    "temperature": "Temperature range in Celsius and Fahrenheit",
    "clothing_suggestions": "What clothes are best suited to the weather"
  }},
  "checklist": [
    {{"task": "Pre-trip task 1", "completed": false}},
    {{"task": "Pre-trip task 2", "completed": false}}
  ],
  "nearby_attractions": [
    {{"name": "Attraction 1 outside city", "distance": "25 km", "description": "Short description"}},
    {{"name": "Attraction 2 outside city", "distance": "40 km", "description": "Short description"}}
  ],
  "map_markers": [
    {{"name": "Eiffel Tower (example)", "lat": 48.8584, "lng": 2.2945, "type": "attraction"}},
    {{"name": "Hotel Option (example)", "lat": 48.8566, "lng": 2.3522, "type": "hotel"}}
  ]
}}

Ensure the list of days in 'itinerary' matches exactly {days} days. Generate realistic lat/lng coordinates for map_markers so they render properly in Leaflet JS.
"""
        model = genai.GenerativeModel("gemini-1.5-flash")
        
        # Request structure in JSON mode
        response = model.generate_content(
            prompt,
            generation_config={"response_mime_type": "application/json"}
        )
        
        plan_data = json.loads(response.text.strip())
        logger.info("Successfully generated travel plan via Gemini API!")
        return plan_data
        
    except Exception as e:
        logger.error(f"Failed to generate travel plan via Gemini API: {e}. Falling back to local generation.")
        # Try finding standard mock first, then run procedural generator
        dest_key = destination.lower().strip()
        if dest_key in MOCK_DESTINATIONS:
            return generate_travel_plan(destination, days, budget, travelers, style, interests, transportation, hotel_pref, starting_city, api_key=None)
        else:
            return generate_procedural_itinerary(
                destination, days, budget, travelers, style, interests, transportation, hotel_pref, starting_city
            )
