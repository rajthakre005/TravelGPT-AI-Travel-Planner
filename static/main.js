// TravelGPT - AI Travel Planner Frontend Logic

// Global state variables
let currentPlanData = null;
let leafletMap = null;

// Travel Quotes for Loading Screen
const TRAVEL_QUOTES = [
  "“The world is a book and those who do not travel read only one page.” — Saint Augustine",
  "“Travel makes one modest. You see what a tiny place you occupy in the world.” — Gustave Flaubert",
  "“Adventure is worthwhile.” — Aesop",
  "“Not all those who wander are lost.” — J.R.R. Tolkien",
  "“Travel is the only thing you buy that makes you richer.” — Anonymous",
  "“To travel is to live.” — Hans Christian Andersen",
  "“Life is either a daring adventure or nothing at all.” — Helen Keller",
  "“We travel not to escape life, but for life not to escape us.” — Anonymous"
];

document.addEventListener('DOMContentLoaded', () => {
  // Initialize Lucide Icons
  if (typeof lucide !== 'undefined') {
    lucide.createIcons();
  }
  
  // Theme initialization
  initTheme();
  
  // Modal handlers
  initSettingsModal();
  
  // Detect which page we are on
  const isResultPage = document.getElementById('resultsDashboard') !== null;
  
  if (isResultPage) {
    handleResultPageLoad();
  } else {
    handleIndexPageLoad();
  }
});

// ==========================================
// THEME & SETTINGS INITIALIZATION
// ==========================================
function initTheme() {
  const themeToggle = document.getElementById('themeToggle');
  if (!themeToggle) return;
  
  // Load saved theme or default to system preference
  const savedTheme = localStorage.getItem('theme');
  const systemPrefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
  const initialTheme = savedTheme || (systemPrefersDark ? 'dark' : 'light');
  
  document.documentElement.setAttribute('data-theme', initialTheme);
  updateThemeIcon(initialTheme);
  
  themeToggle.addEventListener('click', () => {
    const currentTheme = document.documentElement.getAttribute('data-theme');
    const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
    
    document.documentElement.setAttribute('data-theme', newTheme);
    localStorage.setItem('theme', newTheme);
    updateThemeIcon(newTheme);
  });
}

function updateThemeIcon(theme) {
  const themeToggle = document.getElementById('themeToggle');
  if (!themeToggle) return;
  
  if (theme === 'dark') {
    themeToggle.innerHTML = `<i data-lucide="sun"></i>`;
  } else {
    themeToggle.innerHTML = `<i data-lucide="moon"></i>`;
  }
  if (typeof lucide !== 'undefined') {
    lucide.createIcons();
  }
}

function initSettingsModal() {
  const settingsBtn = document.getElementById('settingsBtn');
  const settingsModal = document.getElementById('settingsModal');
  const modalClose = document.getElementById('modalClose');
  const saveSettings = document.getElementById('saveSettings');
  const apiKeyInput = document.getElementById('apiKeyInput');
  
  if (!settingsBtn || !settingsModal) return;
  
  // Load existing key
  const savedKey = localStorage.getItem('gemini_api_key');
  if (savedKey) {
    apiKeyInput.value = savedKey;
  }
  
  settingsBtn.addEventListener('click', () => {
    settingsModal.classList.add('active');
  });
  
  modalClose.addEventListener('click', () => {
    settingsModal.classList.remove('active');
  });
  
  // Close on backdrop click
  settingsModal.addEventListener('click', (e) => {
    if (e.target === settingsModal) {
      settingsModal.classList.remove('active');
    }
  });
  
  saveSettings.addEventListener('click', () => {
    const key = apiKeyInput.value.trim();
    if (key) {
      localStorage.setItem('gemini_api_key', key);
      showToast("API Key saved successfully!");
    } else {
      localStorage.removeItem('gemini_api_key');
      showToast("API Key removed. Fallback engine active.");
    }
    settingsModal.classList.remove('active');
  });
}

// ==========================================
// TOAST NOTIFICATIONS
// ==========================================
function showToast(message) {
  let toast = document.getElementById('toast');
  if (!toast) {
    toast = document.createElement('div');
    toast.id = 'toast';
    toast.className = 'toast';
    document.body.appendChild(toast);
  }
  
  toast.innerHTML = `<i data-lucide="info"></i> <span>${message}</span>`;
  if (typeof lucide !== 'undefined') {
    lucide.createIcons();
  }
  
  toast.classList.add('show');
  
  setTimeout(() => {
    toast.classList.remove('show');
  }, 3500);
}

// ==========================================
// INDEX (HOME) PAGE LOGIC
// ==========================================
function handleIndexPageLoad() {
  // Render trending pre-fills
  const destCards = document.querySelectorAll('.dest-card');
  destCards.forEach(card => {
    card.addEventListener('click', () => {
      const destination = card.getAttribute('data-dest');
      const startCity = card.getAttribute('data-start') || 'New York';
      
      document.getElementById('destination').value = destination;
      document.getElementById('starting_city').value = startCity;
      
      // Scroll to form
      document.getElementById('planner-form').scrollIntoView({ behavior: 'smooth' });
      showToast(`Pre-filled planner for ${destination}!`);
    });
  });
  
  // Load history list
  renderTripHistory();
  
  // Form submission handler
  const form = document.getElementById('planner-form');
  if (form) {
    form.addEventListener('submit', (e) => {
      e.preventDefault();
      
      const destination = document.getElementById('destination').value.trim();
      const startingCity = document.getElementById('starting_city').value.trim();
      const days = document.getElementById('days').value;
      const budget = document.getElementById('budget').value;
      const travelers = document.getElementById('travelers').value;
      const transportation = document.getElementById('transportation').value;
      const hotelPref = document.getElementById('hotel_pref').value;
      
      // Travel style
      const styleRadio = document.querySelector('input[name="style"]:checked');
      const style = styleRadio ? styleRadio.value : 'Solo';
      
      // Interests
      const interestCheckboxes = document.querySelectorAll('input[name="interests"]:checked');
      const interests = Array.from(interestCheckboxes).map(cb => cb.value);
      
      if (!destination || !startingCity) {
        showToast("Please enter destination and starting city.");
        return;
      }
      
      if (interests.length === 0) {
        showToast("Please select at least one interest!");
        return;
      }
      
      // Save recent metadata to search history (before generating)
      saveSearchToHistory({
        destination, startingCity, days, budget, travelers, style, interests, transportation, hotelPref
      });
      
      // Build Redirect URL
      const params = new URLSearchParams({
        destination,
        starting_city: startingCity,
        days,
        budget,
        travelers,
        style,
        interests: interests.join(','),
        transportation,
        hotel_pref: hotelPref
      });
      
      window.location.href = `/result?${params.toString()}`;
    });
  }
}

function saveSearchToHistory(searchObj) {
  let history = JSON.parse(localStorage.getItem('trip_history') || '[]');
  
  // Remove duplicate of same destination if exists
  history = history.filter(item => item.destination.toLowerCase() !== searchObj.destination.toLowerCase());
  
  // Add to front of array
  history.unshift(searchObj);
  
  // Cap at 4 items
  if (history.length > 4) {
    history.pop();
  }
  
  localStorage.setItem('trip_history', JSON.stringify(history));
}

function renderTripHistory() {
  const grid = document.getElementById('recentGrid');
  const recentSection = document.getElementById('recentTripsSection');
  if (!grid || !recentSection) return;
  
  const history = JSON.parse(localStorage.getItem('trip_history') || '[]');
  
  if (history.length === 0) {
    recentSection.style.display = 'none';
    return;
  }
  
  recentSection.style.display = 'block';
  grid.innerHTML = '';
  
  history.forEach((trip, index) => {
    const card = document.createElement('div');
    card.className = 'recent-card';
    
    // Capitalize interests
    const intString = trip.interests.slice(0, 3).join(', ');
    
    card.innerHTML = `
      <button class="recent-delete" data-index="${index}"><i data-lucide="trash-2"></i></button>
      <div class="recent-dest">${trip.destination}</div>
      <div class="recent-meta">
        <span><i data-lucide="calendar"></i> ${trip.days} Days (${trip.style})</span>
        <span><i data-lucide="users"></i> ${trip.travelers} Traveler(s)</span>
        <span><i data-lucide="compass"></i> ${intString}</span>
      </div>
    `;
    
    // Click card to search again
    card.addEventListener('click', (e) => {
      if (e.target.closest('.recent-delete')) return;
      
      const params = new URLSearchParams({
        destination: trip.destination,
        starting_city: trip.startingCity,
        days: trip.days,
        budget: trip.budget,
        travelers: trip.travelers,
        style: trip.style,
        interests: trip.interests.join(','),
        transportation: trip.transportation,
        hotel_pref: trip.hotelPref
      });
      window.location.href = `/result?${params.toString()}`;
    });
    
    grid.appendChild(card);
  });
  
  // Set up delete hooks
  const deleteBtns = grid.querySelectorAll('.recent-delete');
  deleteBtns.forEach(btn => {
    btn.addEventListener('click', (e) => {
      e.stopPropagation();
      const index = parseInt(btn.getAttribute('data-index'));
      let historyList = JSON.parse(localStorage.getItem('trip_history') || '[]');
      historyList.splice(index, 1);
      localStorage.setItem('trip_history', JSON.stringify(historyList));
      renderTripHistory();
      showToast("Trip removed from history.");
    });
  });
  
  if (typeof lucide !== 'undefined') {
    lucide.createIcons();
  }
}

// ==========================================
// RESULTS & DASHBOARD PAGE LOGIC
// ==========================================
function handleResultPageLoad() {
  const urlParams = new URLSearchParams(window.location.search);
  const destination = urlParams.get('destination');
  const startingCity = urlParams.get('starting_city');
  const days = parseInt(urlParams.get('days') || 3);
  const budget = urlParams.get('budget') || 'Moderate';
  const travelers = parseInt(urlParams.get('travelers') || 1);
  const style = urlParams.get('style') || 'Solo';
  const interests = urlParams.get('interests') ? urlParams.get('interests').split(',') : [];
  const transportation = urlParams.get('transportation') || 'Public Transit';
  const hotelPref = urlParams.get('hotel_pref') || 'Mid-range';
  
  // Setup quotes rotation during loading
  let quoteIndex = 0;
  const quoteElem = document.getElementById('loadingQuote');
  
  const quoteInterval = setInterval(() => {
    if (quoteElem) {
      quoteIndex = (quoteIndex + 1) % TRAVEL_QUOTES.length;
      quoteElem.textContent = TRAVEL_QUOTES[quoteIndex];
    }
  }, 4000);
  
  // Gather API Key
  const userApiKey = localStorage.getItem('gemini_api_key') || '';
  
  // Build POST body
  const postData = {
    destination,
    starting_city: startingCity,
    days,
    budget,
    travelers,
    style,
    interests,
    transportation,
    hotel_pref: hotelPref,
    api_key: userApiKey
  };
  
  // Fetch from our Flask Server API
  fetch('/api/generate', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify(postData)
  })
  .then(response => response.json())
  .then(res => {
    clearInterval(quoteInterval);
    if (res.success && res.plan) {
      currentPlanData = res.plan;
      
      // Hide loading, show dashboard
      const loadingScreen = document.getElementById('loadingScreen');
      const dashboard = document.getElementById('resultsDashboard');
      
      if (loadingScreen) {
        loadingScreen.style.opacity = '0';
        setTimeout(() => loadingScreen.style.display = 'none', 500);
      }
      
      if (dashboard) {
        dashboard.classList.add('visible');
      }
      
      // Populate dashboard sections
      populateDashboard(res.plan);
      initTabs();
      
      // Set up bookmark check
      updateBookmarkState(res.plan.destination);
    } else {
      showErrorState(res.error || "Failed to generate itinerary.");
    }
  })
  .catch(err => {
    clearInterval(quoteInterval);
    showErrorState(err.message || "A network error occurred. Please try again.");
  });
  
  // Action buttons on results dashboard
  setupDashboardActions();
}

function showErrorState(errorMessage) {
  const loadingScreen = document.getElementById('loadingScreen');
  if (loadingScreen) {
    loadingScreen.innerHTML = `
      <div class="loading-container" style="max-width: 600px;">
        <div style="font-size: 3.5rem; color: #ef4444; margin-bottom: 1.5rem;">
          <i data-lucide="alert-triangle"></i>
        </div>
        <h2 class="loading-title" style="color: #ef4444;">Generation Failed</h2>
        <p style="color: var(--text-muted); margin-bottom: 2rem; font-size: 1.1rem;">
          ${errorMessage}
        </p>
        <div style="display: flex; gap: 1rem; justify-content: center;">
          <a href="/" class="btn-primary" style="padding: 0.75rem 1.5rem; font-size: 1rem;">
            <i data-lucide="arrow-left"></i> Return Home
          </a>
        </div>
      </div>
    `;
    if (typeof lucide !== 'undefined') {
      lucide.createIcons();
    }
  }
}

function populateDashboard(plan) {
  // 1. Hero Block Info
  document.getElementById('planDestination').textContent = plan.destination;
  document.getElementById('planDays').innerHTML = `<i data-lucide="calendar"></i> ${plan.days} Days`;
  document.getElementById('planStyle').innerHTML = `<i data-lucide="compass"></i> ${plan.style}`;
  document.getElementById('planBudget').innerHTML = `<i data-lucide="dollar-sign"></i> ${plan.budget} Budget`;
  document.getElementById('planTravelers').innerHTML = `<i data-lucide="users"></i> ${plan.travelers} Traveler(s)`;
  document.getElementById('planStart').innerHTML = `<i data-lucide="map-pin"></i> From ${plan.starting_city}`;

  // 2. Day-by-Day Itinerary Cards
  const itineraryContainer = document.getElementById('itineraryDaysContainer');
  itineraryContainer.innerHTML = '';
  
  plan.itinerary.forEach(day => {
    const dayCard = document.createElement('div');
    dayCard.className = 'day-card';
    
    // Construct dining recommendations
    let diningHtml = '';
    if (day.restaurants && day.restaurants.length > 0) {
      let diningCards = day.restaurants.map(rest => `
        <div class="dining-card">
          <span class="dining-badge">${rest.type || 'Dining'}</span>
          <span class="dining-name">${rest.name}</span>
          <span class="dining-desc">${rest.description || 'Highly rated culinary choice.'}</span>
        </div>
      `).join('');
      
      diningHtml = `
        <div class="dining-section">
          <div class="dining-title"><i data-lucide="utensils"></i> Food Recommendations</div>
          <div class="dining-grid">
            ${diningCards}
          </div>
        </div>
      `;
    }

    dayCard.innerHTML = `
      <div class="day-header">
        <div class="day-title">
          <span>${day.day}</span> Day ${day.day} Plan
        </div>
        <div class="day-transit-summary">
          <i data-lucide="truck"></i> ${day.travel_time || 'Local transport'}
        </div>
      </div>
      <div class="day-body">
        
        <!-- Morning -->
        <div class="activity-card">
          <div class="activity-time-block">
            <div class="activity-icon-wrap"><i data-lucide="sun"></i></div>
            <div class="activity-time-lbl">${day.morning.time || 'Morning'}</div>
          </div>
          <div class="activity-detail-block">
            <div class="activity-header">
              <span class="activity-name">${day.morning.attraction}</span>
              <span class="activity-attraction-tag">Sightseeing</span>
            </div>
            <p class="activity-desc"><strong>Activity:</strong> ${day.morning.activity}</p>
            <p class="activity-desc" style="margin-top: 0.35rem; font-size: 0.85rem; color: var(--text-light);">${day.morning.description}</p>
          </div>
        </div>
        
        <!-- Afternoon -->
        <div class="activity-card">
          <div class="activity-time-block">
            <div class="activity-icon-wrap" style="color: #f59e0b; background-color: rgba(245, 158, 11, 0.08);"><i data-lucide="cloud-sun"></i></div>
            <div class="activity-time-lbl">${day.afternoon.time || 'Afternoon'}</div>
          </div>
          <div class="activity-detail-block">
            <div class="activity-header">
              <span class="activity-name">${day.afternoon.attraction}</span>
              <span class="activity-attraction-tag" style="color: #8b5cf6; background-color: rgba(139, 92, 246, 0.08);">Adventure</span>
            </div>
            <p class="activity-desc"><strong>Activity:</strong> ${day.afternoon.activity}</p>
            <p class="activity-desc" style="margin-top: 0.35rem; font-size: 0.85rem; color: var(--text-light);">${day.afternoon.description}</p>
          </div>
        </div>
        
        <!-- Evening -->
        <div class="activity-card">
          <div class="activity-time-block">
            <div class="activity-icon-wrap" style="color: #8b5cf6; background-color: rgba(139, 92, 246, 0.08);"><i data-lucide="moon"></i></div>
            <div class="activity-time-lbl">${day.evening.time || 'Evening'}</div>
          </div>
          <div class="activity-detail-block">
            <div class="activity-header">
              <span class="activity-name">${day.evening.attraction}</span>
              <span class="activity-attraction-tag" style="color: #ec4899; background-color: rgba(236, 72, 153, 0.08);">Leisure</span>
            </div>
            <p class="activity-desc"><strong>Activity:</strong> ${day.evening.activity}</p>
            <p class="activity-desc" style="margin-top: 0.35rem; font-size: 0.85rem; color: var(--text-light);">${day.evening.description}</p>
          </div>
        </div>
        
        <!-- Dining -->
        ${diningHtml}
        
      </div>
    `;
    itineraryContainer.appendChild(dayCard);
  });

  // 3. Weather Info Widget
  const weather = plan.weather;
  if (weather) {
    document.getElementById('weatherTemp').textContent = weather.temperature || 'N/A';
    document.getElementById('weatherSummary').textContent = weather.summary || 'N/A';
    document.getElementById('weatherClothing').innerHTML = `<strong>Dress Advice:</strong> ${weather.clothing_suggestions || 'Dress comfortable.'}`;
  }

  // 4. Budget Breakdown Chart & List
  const budgetInfo = plan.budget_breakdown;
  if (budgetInfo) {
    const cur = budgetInfo.currency || '$';
    document.getElementById('budgetTotalValue').textContent = `${cur} ${budgetInfo.total}`;
    
    // Draw itemized lists and calculate percentages
    const categories = ['hotel', 'food', 'transport', 'attractions', 'shopping'];
    const totalCost = budgetInfo.total || 1;
    
    categories.forEach(cat => {
      const val = budgetInfo[cat] || 0;
      const pct = Math.min(100, Math.round((val / totalCost) * 100));
      
      // Update text amounts
      const valElem = document.getElementById(`budget-val-${cat}`);
      if (valElem) valElem.textContent = `${cur} ${val}`;
      
      // Update progress bar width
      const barElem = document.getElementById(`budget-bar-${cat}`);
      if (barElem) {
        // Wait a slight delay for transition animation to look amazing
        setTimeout(() => {
          barElem.style.width = `${pct}%`;
        }, 300);
      }
    });

    // Populate savings suggestions
    const tipsList = document.getElementById('budgetSavingTipsList');
    tipsList.innerHTML = '';
    if (budgetInfo.suggestions && budgetInfo.suggestions.length > 0) {
      budgetInfo.suggestions.forEach(tip => {
        const li = document.createElement('li');
        li.textContent = tip;
        tipsList.appendChild(li);
      });
    }
  }

  // 5. Checklist Items
  const checklistContainer = document.getElementById('checklistContainer');
  checklistContainer.innerHTML = '';
  if (plan.checklist && plan.checklist.length > 0) {
    plan.checklist.forEach((item, index) => {
      const label = document.createElement('label');
      label.className = `checklist-item ${item.completed ? 'checked' : ''}`;
      label.innerHTML = `
        <input type="checkbox" ${item.completed ? 'checked' : ''} data-index="${index}">
        <span>${item.task}</span>
      `;
      
      // Event listener for checklist checking
      const checkbox = label.querySelector('input');
      checkbox.addEventListener('change', () => {
        if (checkbox.checked) {
          label.classList.add('checked');
        } else {
          label.classList.remove('checked');
        }
      });
      
      checklistContainer.appendChild(label);
    });
  }

  // 6. Tab Sections (Packing, Travel Tips, Nearby Sights)
  
  // Packing Items
  const pack = plan.packing_list;
  const packingContainer = document.getElementById('packingTabContent');
  if (pack && packingContainer) {
    let cardHTML = '';
    for (const [category, items] of Object.entries(pack)) {
      if (items && items.length > 0) {
        const catCleanName = category.replace('_', ' ').toUpperCase();
        let catIcon = 'package';
        if (category === 'clothing') catIcon = 'shirt';
        if (category === 'electronics') catIcon = 'cpu';
        if (category === 'toiletries') catIcon = 'droplet';
        if (category === 'documents') catIcon = 'file-text';
        
        let itemsHTML = items.map(item => `<li>${item}</li>`).join('');
        
        cardHTML += `
          <div class="packing-card">
            <div class="packing-category"><i data-lucide="${catIcon}"></i> ${catCleanName}</div>
            <ul class="packing-list-items">
              ${itemsHTML}
            </ul>
          </div>
        `;
      }
    }
    packingContainer.innerHTML = `<div class="packing-grid">${cardHTML}</div>`;
  }

  // Travel Tips
  const tips = plan.travel_tips;
  const tipsContainer = document.getElementById('tipsTabContent');
  if (tips && tipsContainer) {
    tipsContainer.innerHTML = `
      <div class="tips-grid">
        <div class="tip-card">
          <div class="tip-icon-wrap"><i data-lucide="hand"></i></div>
          <div class="tip-content">
            <span class="tip-lbl">Customs & Etiquette</span>
            <span class="tip-val">${tips.customs || 'N/A'}</span>
          </div>
        </div>
        <div class="tip-card">
          <div class="tip-icon-wrap" style="color: #ef4444; background-color: rgba(239, 68, 68, 0.08);"><i data-lucide="phone-call"></i></div>
          <div class="tip-content">
            <span class="tip-lbl">Emergency Contacts</span>
            <span class="tip-val">${tips.emergency_numbers || 'N/A'}</span>
          </div>
        </div>
        <div class="tip-card">
          <div class="tip-icon-wrap" style="color: #eab308; background-color: rgba(234, 179, 8, 0.08);"><i data-lucide="shield-alert"></i></div>
          <div class="tip-content">
            <span class="tip-lbl">Safety Advice</span>
            <span class="tip-val">${tips.safety || 'N/A'}</span>
          </div>
        </div>
        <div class="tip-card">
          <div class="tip-icon-wrap" style="color: #10b981; background-color: rgba(16, 185, 129, 0.08);"><i data-lucide="coins"></i></div>
          <div class="tip-content">
            <span class="tip-lbl">Currency & Finance</span>
            <span class="tip-val">${tips.currency || 'N/A'}</span>
          </div>
        </div>
        <div class="tip-card">
          <div class="tip-icon-wrap"><i data-lucide="languages"></i></div>
          <div class="tip-content">
            <span class="tip-lbl">Local Language</span>
            <span class="tip-val">${tips.language || 'N/A'}</span>
          </div>
        </div>
        <div class="tip-card">
          <div class="tip-icon-wrap" style="color: #f97316; background-color: rgba(249, 115, 22, 0.08);"><i data-lucide="sandwich"></i></div>
          <div class="tip-content">
            <span class="tip-lbl">Best Local Food</span>
            <span class="tip-val">${tips.best_foods || 'N/A'}</span>
          </div>
        </div>
        <div class="tip-card" style="grid-column: span 3;">
          <div class="tip-icon-wrap" style="color: #ef4444; background-color: rgba(239, 68, 68, 0.08);"><i data-lucide="alert-circle"></i></div>
          <div class="tip-content">
            <span class="tip-lbl">Things to Avoid</span>
            <span class="tip-val">${tips.avoid || 'N/A'}</span>
          </div>
        </div>
      </div>
    `;
  }

  // Nearby Attractions
  const nearby = plan.nearby_attractions;
  const nearbyContainer = document.getElementById('nearbyTabContent');
  if (nearby && nearbyContainer) {
    let cards = nearby.map(place => `
      <div class="nearby-card">
        <div class="nearby-card-title-row">
          <span class="nearby-card-title">${place.name}</span>
          <span class="nearby-card-dist"><i data-lucide="navigation"></i> ${place.distance}</span>
        </div>
        <p class="nearby-card-desc">${place.description}</p>
      </div>
    `).join('');
    nearbyContainer.innerHTML = `<div class="nearby-grid">${cards}</div>`;
  }

  // 7. Interactive Map Rendering
  initLeafletMap(plan.map_markers, plan.destination);

  // Redraw Lucide icons
  if (typeof lucide !== 'undefined') {
    lucide.createIcons();
  }
}

function initTabs() {
  const tabs = document.querySelectorAll('.tab-btn');
  const contents = document.querySelectorAll('.tab-content');
  
  tabs.forEach(tab => {
    tab.addEventListener('click', () => {
      // Remove active states
      tabs.forEach(t => t.classList.remove('active'));
      contents.forEach(c => c.classList.remove('active'));
      
      // Set current active
      tab.classList.add('active');
      const targetId = tab.getAttribute('data-tab') + 'TabContent';
      const target = document.getElementById(targetId);
      if (target) {
        target.classList.add('active');
      }
    });
  });
}

function initLeafletMap(markers, destinationName) {
  // Destroy old map if initialized to prevent error
  if (leafletMap !== null) {
    leafletMap.remove();
    leafletMap = null;
  }
  
  if (markers.length === 0) {
    document.getElementById('map').innerHTML = '<div style="padding: 2rem; text-align: center;">No map coordinates available for this plan.</div>';
    return;
  }

  // Find center of all markers
  let totalLat = 0;
  let totalLng = 0;
  markers.forEach(m => {
    totalLat += m.lat;
    totalLng += m.lng;
  });
  const centerLat = totalLat / markers.length;
  const centerLng = totalLng / markers.length;
  
  // Create Leaflet map object
  // Set view to center coordinates
  leafletMap = L.map('map').setView([centerLat, centerLng], 12);
  
  // Add OpenStreetMap tile layers
  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    maxZoom: 19,
    attribution: '&copy; <a href="https://openstreetmap.org/copyright">OpenStreetMap contributors</a>'
  }).addTo(leafletMap);
  
  // Custom marker icon creation helper
  // Uses colored Leaflet icons based on attraction vs hotel
  const hotelIcon = L.icon({
    iconUrl: 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-red.png',
    shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/0.7.7/images/marker-shadow.png',
    iconSize: [25, 41],
    iconAnchor: [12, 41],
    popupAnchor: [1, -34],
    shadowSize: [41, 41]
  });

  const attractionIcon = L.icon({
    iconUrl: 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-blue.png',
    shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/0.7.7/images/marker-shadow.png',
    iconSize: [25, 41],
    iconAnchor: [12, 41],
    popupAnchor: [1, -34],
    shadowSize: [41, 41]
  });

  const transportIcon = L.icon({
    iconUrl: 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-orange.png',
    shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/0.7.7/images/marker-shadow.png',
    iconSize: [25, 41],
    iconAnchor: [12, 41],
    popupAnchor: [1, -34],
    shadowSize: [41, 41]
  });
  
  // Plot markers
  const bounds = L.latLngBounds();
  
  markers.forEach(marker => {
    let icon = attractionIcon;
    if (marker.type === 'hotel') icon = hotelIcon;
    if (marker.type === 'transport') icon = transportIcon;
    
    const leafletMarker = L.marker([marker.lat, marker.lng], { icon: icon })
      .addTo(leafletMap)
      .bindPopup(`<b>${marker.name}</b><br><span style="text-transform: capitalize; font-size: 0.75rem; color: #666;">Category: ${marker.type || 'Sights'}</span>`);
      
    bounds.extend([marker.lat, marker.lng]);
  });
  
  // Fit map boundaries to fit all markers nicely
  leafletMap.fitBounds(bounds, { padding: [30, 30] });
}

// ==========================================
// BOOKMARK/FAVORITES TOGGLING
// ==========================================
function updateBookmarkState(destination) {
  const bookmarkBtn = document.getElementById('bookmarkBtn');
  if (!bookmarkBtn) return;
  
  const bookmarks = JSON.parse(localStorage.getItem('trip_bookmarks') || '[]');
  const isBookmarked = bookmarks.some(b => b.destination.toLowerCase() === destination.toLowerCase());
  
  if (isBookmarked) {
    bookmarkBtn.style.color = '#eab308'; // gold
    bookmarkBtn.style.backgroundColor = 'rgba(234, 179, 8, 0.08)';
    bookmarkBtn.style.borderColor = '#eab308';
    bookmarkBtn.innerHTML = `<i data-lucide="star-off"></i> Favorite`;
  } else {
    bookmarkBtn.style.color = ''; // reset
    bookmarkBtn.style.backgroundColor = '';
    bookmarkBtn.style.borderColor = '';
    bookmarkBtn.innerHTML = `<i data-lucide="star"></i> Favorite`;
  }
  if (typeof lucide !== 'undefined') {
    lucide.createIcons();
  }
}

function toggleBookmark() {
  if (!currentPlanData) return;
  
  const destination = currentPlanData.destination;
  let bookmarks = JSON.parse(localStorage.getItem('trip_bookmarks') || '[]');
  const index = bookmarks.findIndex(b => b.destination.toLowerCase() === destination.toLowerCase());
  
  if (index !== -1) {
    // Unbookmark
    bookmarks.splice(index, 1);
    showToast("Itinerary removed from favorites.");
  } else {
    // Bookmark
    bookmarks.push({
      destination: currentPlanData.destination,
      days: currentPlanData.days,
      style: currentPlanData.style,
      budget: currentPlanData.budget,
      travelers: currentPlanData.travelers,
      query: window.location.search
    });
    showToast("Itinerary bookmarked to favorites!");
  }
  
  localStorage.setItem('trip_bookmarks', JSON.stringify(bookmarks));
  updateBookmarkState(destination);
}

// ==========================================
// ACTIONS SETUP (PDF, SHARE, COPY)
// ==========================================
function setupDashboardActions() {
  const downloadPdfBtn = document.getElementById('downloadPdfBtn');
  const bookmarkBtn = document.getElementById('bookmarkBtn');
  const shareBtn = document.getElementById('shareBtn');
  const copyBtn = document.getElementById('copyBtn');
  
  if (downloadPdfBtn) {
    downloadPdfBtn.addEventListener('click', () => {
      if (!currentPlanData) return;
      
      showToast("Preparing PDF download... please wait.");
      downloadPdfBtn.disabled = true;
      downloadPdfBtn.innerHTML = `<i data-lucide="loader" class="animate-spin"></i> Generating...`;
      if (typeof lucide !== 'undefined') lucide.createIcons();
      
      fetch('/api/download-pdf', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(currentPlanData)
      })
      .then(res => {
        if (!res.ok) throw new Error("Failed to compile PDF.");
        return res.blob();
      })
      .then(blob => {
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `${currentPlanData.destination.replace(/\s+/g, '_')}_Itinerary.pdf`;
        document.body.appendChild(a);
        a.click();
        a.remove();
        window.URL.revokeObjectURL(url);
        showToast("PDF Downloaded!");
        
        downloadPdfBtn.disabled = false;
        downloadPdfBtn.innerHTML = `<i data-lucide="download"></i> Download PDF`;
        if (typeof lucide !== 'undefined') lucide.createIcons();
      })
      .catch(err => {
        showToast("PDF Error: " + err.message);
        downloadPdfBtn.disabled = false;
        downloadPdfBtn.innerHTML = `<i data-lucide="download"></i> Download PDF`;
        if (typeof lucide !== 'undefined') lucide.createIcons();
      });
    });
  }
  
  if (bookmarkBtn) {
    bookmarkBtn.addEventListener('click', () => {
      toggleBookmark();
    });
  }
  
  if (shareBtn) {
    shareBtn.addEventListener('click', () => {
      const shareUrl = window.location.href;
      navigator.clipboard.writeText(shareUrl)
        .then(() => {
          showToast("Shareable link copied to clipboard!");
        })
        .catch(err => {
          showToast("Failed to copy link.");
        });
    });
  }
  
  if (copyBtn) {
    copyBtn.addEventListener('click', () => {
      if (!currentPlanData) return;
      
      let text = `TRAVEGPT ITINERARY: ${currentPlanData.destination.toUpperCase()}\n`;
      text += `Duration: ${currentPlanData.days} Days | Budget: ${currentPlanData.budget} | Style: ${currentPlanData.style}\n\n`;
      
      currentPlanData.itinerary.forEach(day => {
        text += `DAY ${day.day}:\n`;
        text += `- Morning: ${day.morning.attraction} (${day.morning.activity})\n`;
        text += `- Afternoon: ${day.afternoon.attraction} (${day.afternoon.activity})\n`;
        text += `- Evening: ${day.evening.attraction} (${day.evening.activity})\n`;
        text += `- Restaurants: ${day.restaurants.map(r => r.name).join(', ')}\n`;
        text += `- Transit Time: ${day.travel_time}\n\n`;
      });
      
      navigator.clipboard.writeText(text)
        .then(() => {
          showToast("Text itinerary copied to clipboard!");
        })
        .catch(() => {
          showToast("Failed to copy text.");
        });
    });
  }
}
