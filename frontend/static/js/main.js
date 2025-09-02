/**
 * Traditional Swedish Fika - Main JavaScript
 * Progressive enhancement for the fika location finder
 */

class FikaApp {
    constructor() {
        this.apiBaseUrl = 'http://localhost:8000/api';
        this.currentPage = 1;
        this.currentQuery = '';
        this.currentCity = '';
        this.isLoading = false;
        
        this.init();
    }

    async init() {
        console.log('🇸🇪 Traditional Swedish Fika App Initializing...');
        
        // Set up event listeners
        this.setupEventListeners();
        
        // Load featured places
        await this.loadFeaturedPlaces();
        
        // Load city counts
        await this.loadCityCounts();
        
        console.log('✅ App initialized successfully');
    }

    setupEventListeners() {
        // Search functionality
        const searchInput = document.getElementById('search-input');
        const searchBtn = document.getElementById('search-btn');
        
        if (searchInput && searchBtn) {
            searchInput.addEventListener('keypress', (e) => {
                if (e.key === 'Enter') {
                    this.performSearch(searchInput.value.trim());
                }
            });
            
            searchBtn.addEventListener('click', () => {
                this.performSearch(searchInput.value.trim());
            });
            
            // Real-time search (debounced)
            let searchTimeout;
            searchInput.addEventListener('input', (e) => {
                clearTimeout(searchTimeout);
                const query = e.target.value.trim();
                
                if (query.length >= 2) {
                    searchTimeout = setTimeout(() => {
                        this.performSearch(query);
                    }, 500);
                } else if (query.length === 0) {
                    this.clearSearchResults();
                }
            });
        }
        
        // City card clicks
        document.querySelectorAll('.city-card').forEach(card => {
            card.addEventListener('click', (e) => {
                e.preventDefault();
                const city = card.getAttribute('data-city');
                this.searchByCity(city);
            });
        });
    }

    async performSearch(query) {
        if (!query || query.length < 2) {
            this.clearSearchResults();
            return;
        }

        this.showLoading(true);
        this.currentQuery = query;
        this.currentPage = 1;

        try {
            const response = await fetch(`${this.apiBaseUrl}/places/search?query=${encodeURIComponent(query)}&page=${this.currentPage}&per_page=20`);
            
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            
            const data = await response.json();
            this.displaySearchResults(data, query);
            
        } catch (error) {
            console.error('Search failed:', error);
            this.showError(`Search failed: ${error.message}`);
        } finally {
            this.showLoading(false);
        }
    }

    async searchByCity(cityKey) {
        // Map city keys to display names
        const cityMap = {
            'stockholm': 'Stockholm',
            'gothenburg': 'Gothenburg', 
            'malmo': 'Malmö',
            'uppsala': 'Uppsala',
            'vasteras': 'Västerås'
        };
        
        const cityName = cityMap[cityKey] || cityKey;
        this.showLoading(true);
        this.currentCity = cityName;
        this.currentPage = 1;

        try {
            const response = await fetch(`${this.apiBaseUrl}/places?city=${encodeURIComponent(cityName)}&page=${this.currentPage}&per_page=20`);
            
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            
            const data = await response.json();
            this.displaySearchResults(data, `Places in ${cityName}`);
            
        } catch (error) {
            console.error('City search failed:', error);
            this.showError(`Failed to load places in ${cityName}: ${error.message}`);
        } finally {
            this.showLoading(false);
        }
    }

    displaySearchResults(data, title) {
        const resultsSection = document.getElementById('search-results');
        const resultsTitle = document.getElementById('search-results-title');
        const resultsContainer = document.getElementById('results-container');
        
        if (!resultsSection || !resultsTitle || !resultsContainer) {
            console.error('Search results elements not found');
            return;
        }

        // Update title
        resultsTitle.textContent = `${title} (${data.total} results)`;
        
        // Clear previous results
        resultsContainer.innerHTML = '';
        
        if (data.places && data.places.length > 0) {
            data.places.forEach(place => {
                const placeCard = this.createPlaceCard(place);
                resultsContainer.appendChild(placeCard);
            });
            
            // Setup pagination
            this.setupPagination(data);
        } else {
            resultsContainer.innerHTML = `
                <div class="no-results">
                    <p>No fika places found for "${title}". Try a different search term or browse by city.</p>
                </div>
            `;
        }
        
        // Show results section
        resultsSection.style.display = 'block';
        resultsSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }

    createPlaceCard(place) {
        const card = document.createElement('div');
        card.className = 'result-card';
        
        // Generate rating stars
        const rating = place.rating || 0;
        const stars = '★'.repeat(Math.floor(rating)) + '☆'.repeat(5 - Math.floor(rating));
        
        // Format features
        const features = place.features || place.fika_specialties || [];
        const featureTags = features.slice(0, 3).map(feature => 
            `<span class="feature-tag">${this.formatFeature(feature)}</span>`
        ).join('');
        
        card.innerHTML = `
            <div class="result-header">
                <div>
                    <h3 class="result-title">${this.escapeHtml(place.name)}</h3>
                    <p class="result-location">📍 ${this.escapeHtml(place.address || place.city)}</p>
                </div>
                <div class="result-rating">
                    <span class="stars">${stars}</span>
                    <span>${rating.toFixed(1)}</span>
                </div>
            </div>
            
            ${place.description ? `<p class="result-description">${this.escapeHtml(place.description.substring(0, 150))}${place.description.length > 150 ? '...' : ''}</p>` : ''}
            
            ${featureTags ? `<div class="result-features">${featureTags}</div>` : ''}
        `;
        
        // Add click handler
        card.addEventListener('click', () => {
            this.viewPlace(place.id);
        });
        
        return card;
    }

    setupPagination(data) {
        const paginationContainer = document.getElementById('pagination');
        
        if (!paginationContainer || data.pages <= 1) {
            if (paginationContainer) {
                paginationContainer.style.display = 'none';
            }
            return;
        }
        
        paginationContainer.innerHTML = '';
        paginationContainer.style.display = 'flex';
        
        // Previous button
        const prevBtn = this.createPaginationButton('← Previous', data.page - 1, data.page === 1);
        paginationContainer.appendChild(prevBtn);
        
        // Page numbers
        const startPage = Math.max(1, data.page - 2);
        const endPage = Math.min(data.pages, data.page + 2);
        
        for (let i = startPage; i <= endPage; i++) {
            const btn = this.createPaginationButton(i.toString(), i, false, i === data.page);
            paginationContainer.appendChild(btn);
        }
        
        // Next button
        const nextBtn = this.createPaginationButton('Next →', data.page + 1, data.page === data.pages);
        paginationContainer.appendChild(nextBtn);
    }

    createPaginationButton(text, page, disabled, active = false) {
        const button = document.createElement('button');
        button.textContent = text;
        button.disabled = disabled;
        
        if (active) {
            button.classList.add('active');
        }
        
        if (!disabled) {
            button.addEventListener('click', () => {
                this.currentPage = page;
                if (this.currentQuery) {
                    this.performSearch(this.currentQuery);
                } else if (this.currentCity) {
                    this.searchByCity(this.currentCity.toLowerCase());
                }
            });
        }
        
        return button;
    }

    async loadFeaturedPlaces() {
        const featuredContainer = document.getElementById('featured-places');
        
        if (!featuredContainer) return;

        try {
            const response = await fetch(`${this.apiBaseUrl}/places?verified_only=true&per_page=6`);
            
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}`);
            }
            
            const data = await response.json();
            
            if (data.places && data.places.length > 0) {
                featuredContainer.innerHTML = '';
                
                data.places.slice(0, 3).forEach(place => {
                    const card = this.createFeaturedCard(place);
                    featuredContainer.appendChild(card);
                });
            } else {
                featuredContainer.innerHTML = `
                    <div class="loading">
                        Featured places will appear here once our database is populated with authentic Swedish fika locations.
                    </div>
                `;
            }
        } catch (error) {
            console.error('Failed to load featured places:', error);
            featuredContainer.innerHTML = `
                <div class="loading">
                    Featured places coming soon! We're currently building our database of authentic Swedish fika locations.
                </div>
            `;
        }
    }

    createFeaturedCard(place) {
        const card = document.createElement('div');
        card.className = 'featured-card';
        
        const rating = place.rating || 0;
        const stars = '★'.repeat(Math.floor(rating)) + '☆'.repeat(5 - Math.floor(rating));
        
        card.innerHTML = `
            <img class="featured-image" src="${place.images && place.images[0] ? place.images[0] : '/static/images/default-cafe.jpg'}" alt="${this.escapeHtml(place.name)}" loading="lazy">
            <div class="featured-content">
                <h3 class="featured-title">${this.escapeHtml(place.name)}</h3>
                <p class="featured-location">📍 ${this.escapeHtml(place.city)}</p>
                <p class="featured-description">${this.escapeHtml((place.description || '').substring(0, 100))}${place.description && place.description.length > 100 ? '...' : ''}</p>
                <div class="featured-rating">
                    <span class="stars">${stars}</span>
                    <span>${rating.toFixed(1)}</span>
                </div>
            </div>
        `;
        
        card.addEventListener('click', () => {
            this.viewPlace(place.id);
        });
        
        return card;
    }

    async loadCityCounts() {
        // This would normally fetch real counts from the API
        // For now, we'll keep the static counts in the HTML
        try {
            const response = await fetch(`${this.apiBaseUrl}/places/cities`);
            if (response.ok) {
                const data = await response.json();
                // Update city counts based on API response
                console.log('Cities:', data.cities);
            }
        } catch (error) {
            console.log('Using static city counts');
        }
    }

    viewPlace(placeId) {
        // In a real application, this would navigate to a detail page
        console.log(`Viewing place: ${placeId}`);
        // For now, we'll just show an alert
        alert(`Place details coming soon! ID: ${placeId}`);
    }

    clearSearchResults() {
        const resultsSection = document.getElementById('search-results');
        if (resultsSection) {
            resultsSection.style.display = 'none';
        }
        this.currentQuery = '';
        this.currentCity = '';
    }

    showLoading(show) {
        this.isLoading = show;
        
        const resultsContainer = document.getElementById('results-container');
        if (!resultsContainer) return;
        
        if (show) {
            resultsContainer.innerHTML = '<div class="loading">Searching for fika places...</div>';
        }
    }

    showError(message) {
        const resultsContainer = document.getElementById('results-container');
        if (resultsContainer) {
            resultsContainer.innerHTML = `<div class="error">${this.escapeHtml(message)}</div>`;
        }
    }

    formatFeature(feature) {
        const featureMap = {
            'wifi': 'WiFi',
            'outdoor_seating': 'Outdoor Seating', 
            'wheelchair_accessible': 'Wheelchair Accessible',
            'kanelbullar': 'Kanelbullar',
            'prinsesstarta': 'Prinsesstårta',
            'coffee': 'Coffee'
        };
        
        return featureMap[feature] || feature.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
    }

    escapeHtml(unsafe) {
        if (typeof unsafe !== 'string') return '';
        
        return unsafe
            .replace(/&/g, "&amp;")
            .replace(/</g, "&lt;")
            .replace(/>/g, "&gt;")
            .replace(/"/g, "&quot;")
            .replace(/'/g, "&#039;");
    }
}

// Initialize the app when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new FikaApp();
});

// Handle navigation for city pages
window.addEventListener('popstate', (event) => {
    if (event.state && event.state.city) {
        // Handle back/forward navigation
        const app = window.fikaApp;
        if (app) {
            app.searchByCity(event.state.city);
        }
    }
});

// Export for global access
window.FikaApp = FikaApp;