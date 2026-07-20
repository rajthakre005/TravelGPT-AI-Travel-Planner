# TravelGPT – AI Travel Planner

TravelGPT is a modern, responsive web application built with **Python (Flask)** on the backend and a premium **HTML5, CSS3, and Vanilla JavaScript** frontend. It leverages generative AI (or a high-fidelity local procedural fallback engine) to compile customized day-by-day travel itineraries, packing lists, expense sheets, travel advisories, and interactive maps in seconds.

---

## 🌟 Key Features

### 1. Modern Travel Landing Page
- Fully responsive design (desktop and mobile-optimized).
- Premium design language with **glassmorphic containers**, fluid gradients, and a smooth theme transition.
- **Trending Destination Cards** (Paris, Tokyo, London) that pre-populate the search forms.

### 2. Tailored Plan Customizer Form
Collects parameters including:
- Destination & Starting City
- Trip Duration (1–14 days)
- Travel Style (Solo, Budget, Adventure, Family, Luxury)
- Budget level (Budget, Moderate, Luxury) and traveler count
- Preferred local transportation & hotel styles
- Multiple checklist interest categories (History, Food, Nature, Shopping, Beaches, Trekking, Nightlife, Culture)

### 3. Dynamic Loading Screen
- Animated flying plane circling progress indicators.
- Displays rotating famous travel quotes and tips during the planning phase to keep users engaged.

### 4. Interactive Route Map
- Fully functional map powered by **Leaflet.js** and OpenStreetMap.
- Plots markers for attractions, airports, transit connections, and hotels without needing expensive Google Maps API Keys.

### 5. Detailed Itinerary Grid
- Structured day-by-day morning, afternoon, and evening slots with duration advice.
- Restaurant suggestions mapped directly with descriptions.

### 6. Interactive Widgets
- **Live Checklist:** Interactive list to tick off pre-trip tasks.
- **Interactive Budget Panel:** Dynamically styled bars visualizing expenditures (Hotel, Food, Transport, Attractions, Shopping) along with custom saving advice.
- **Weather Panel:** Forecast highlights, temperature, and specific packing-wardrobe advice.

### 7. Expandable Details Tabs
- **Packing List:** Broken down into Categories (Clothing, Electronics, Toiletries, Documents, Activity-specific).
- **Travel Tips:** Grid cards covering local customs, safety tips, emergency contacts, local currencies, languages, and things to avoid.
- **Nearby Sights:** Extra suggested day trips outside the main city.

### 8. Download & Export
- **PDF Itinerary Compilation:** Generates structured multi-page PDF files using **ReportLab** Flowables and prints page numbers using a two-pass canvas.
- **Copy text itinerary** or copy shareable link coordinates directly to clipboard.
- **Trip History & Bookmarks:** Stores past itineraries and bookmarked favorites locally in the browser's `localStorage` for offline recall.

---

## 🛠️ Technologies Used

### Backend
- **Python 3.13+**
- **Flask (v3.0.3):** Routing and endpoint controllers.
- **ReportLab (v4.2.2):** High-quality PDF document layout and assembly.
- **Google Generative AI SDK (v0.8.3):** Gemini 1.5 Flash structured json mode API integration.
- **Python Dotenv:** For configuration management.
- **Requests:** For OpenStreetMapNominatim Nominatim geolocating API lookup.

### Frontend
- **HTML5 & Vanilla CSS3:** Styled with customized HSL custom properties, transitions, and media grids (no external tailwind packages).
- **Vanilla JavaScript:** Handle state management, AJAX async loaders, localStorage caching, and component actions.
- **Leaflet.js & OpenStreetMap:** Map rendering and marker plots.
- **Lucide Icons:** Modern vector web graphics.

---

## 📁 Folder Structure

```
travel-planner/
│
├── app.py                 # Main Flask server & PDF layout generator
├── requirements.txt       # Python package dependencies
├── README.md              # Documentation
│
├── templates/             # HTML Jinja2 templates
│   ├── index.html         # Landing page and form input
│   └── result.html        # Loading screen & dashboard output
│
├── static/                # Static assets
│   ├── css/
│   │   └── style.css      # Core stylesheet with theme system
│   └── js/
│       └── main.js        # Main JavaScript client orchestrator
│
└── utils/
    └── planner.py         # AI Prompting engine & procedural generators
```

---

## 🚀 Installation & Local Execution

### Prerequisites
Make sure you have **Python 3.8+** installed on your system.

### 1. Clone or Copy Workspace Files
Ensure you are in the project folder:
```bash
cd travel-planner
```

### 2. Create and Activate Virtual Environment
On Windows:
```bash
python -m venv venv
venv\Scripts\activate
```
On macOS/Linux:
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Set Environment Variables (Optional)
To enable the live **Gemini API** for custom AI generation, create a `.env` file in the root folder or set your terminal environment:
```env
GEMINI_API_KEY=your_gemini_api_key_here
```
*Note: If no API key is specified, the application will automatically activate its highly optimized procedural database to instantly plan trips for any city.*

### 5. Run the Application
```bash
python app.py
```

Open your browser and navigate to:
[http://127.0.0.1:5000](http://127.0.0.1:5000)

---

## 🔮 Future Enhancements
- **Dynamic Hotel & Flight Booking Redirects:** Direct affiliate links to booking platforms.
- **Multi-City Itinerary:** Grouping plans across multiple cities or countries in a single trip.
- **Collaborative Planning:** Real-time sharing with other travelers to edit checkboxes/itinerary details together.
- **GPS Location-based Tips:** Integrates coordinates with mobile browsers to suggest activities near your current coordinates.

---

## 📄 License
This project is licensed under the MIT License - see the LICENSE file for details.
