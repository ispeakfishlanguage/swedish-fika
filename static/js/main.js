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

        // Demo search data with Unsplash images
        const allDemoPlaces = [
            {
                id: 1,
                name: "Café Saturnus",
                address: "Eriksbergsgatan 6, Östermalm",
                city: "Stockholm",
                description: "Famous for their giant cinnamon buns and traditional Swedish atmosphere.",
                rating: 4.7,
                features: ["kanelbullar", "wifi", "outdoor_seating"],
                images: ["https://images.unsplash.com/photo-1554118811-1e0d58224f24?w=400&h=300&fit=crop"]
            },
            {
                id: 2,
                name: "Vete-Katten",
                address: "Kungsgatan 55, Norrmalm",
                city: "Stockholm",
                description: "Historic konditori serving traditional Swedish pastries since 1928.",
                rating: 4.5,
                features: ["prinsesstarta", "traditional", "historic"],
                images: ["https://images.unsplash.com/photo-1578662996442-48f60103fc96?w=400&h=300&fit=crop"]
            },
            {
                id: 3,
                name: "Konditori Hollandia",
                address: "Kungsportsavenyen 36",
                city: "Gothenburg",
                description: "Historic bakery serving traditional Swedish pastries since 1920.",
                rating: 4.8,
                features: ["traditional", "historic", "kanelbullar"],
                images: ["https://images.unsplash.com/photo-1578662996442-48f60103fc96?w=400&h=300&fit=crop"]
            },
            {
                id: 4,
                name: "Café Husaren",
                address: "Haga Nygata 28, Haga",
                city: "Gothenberg",
                description: "Famous for their enormous cinnamon buns - the largest in Sweden!",
                rating: 4.7,
                features: ["giant_kanelbullar", "famous", "tourist_favorite"],
                images: ["https://images.unsplash.com/photo-1509440159596-0249088772ff?w=400&h=300&fit=crop"]
            },
            {
                id: 5,
                name: "Lilla Kafferosteriet",
                address: "Södermannagatan 21, Södermalm",
                city: "Stockholm",
                description: "Small specialty coffee roaster with cozy atmosphere.",
                rating: 4.6,
                features: ["specialty_coffee", "fresh_pastries", "cozy"],
                images: ["https://images.unsplash.com/photo-1501339847302-ac426a4a7cbb?w=400&h=300&fit=crop"]
            }
        ];

        // Filter demo places based on search query
        const filteredPlaces = allDemoPlaces.filter(place => {
            const searchText = query.toLowerCase();
            return (
                place.name.toLowerCase().includes(searchText) ||
                place.city.toLowerCase().includes(searchText) ||
                place.description.toLowerCase().includes(searchText) ||
                place.features.some(feature => feature.toLowerCase().includes(searchText))
            );
        });

        const demoData = {
            places: filteredPlaces,
            total: filteredPlaces.length,
            page: 1,
            pages: 1
        };

        setTimeout(() => {
            this.displaySearchResults(demoData, `Search results for "${query}"`);
            this.showLoading(false);
        }, 300);
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

        // Get all demo places and filter by city
        const allPlaces = getAllDemoPlaces();
        const cityDemoData = {
            'Stockholm': allPlaces.filter(place => place.city === 'Stockholm'),
            'Gothenburg': allPlaces.filter(place => place.city === 'Gothenburg'),
            'Malmö': allPlaces.filter(place => place.city === 'Malmö'),
            'Uppsala': allPlaces.filter(place => place.city === 'Uppsala'),
            'Västerås': allPlaces.filter(place => place.city === 'Västerås')
        };

        const demoData = {
            places: cityDemoData[cityName] || [],
            total: cityDemoData[cityName]?.length || 0,
            page: 1,
            pages: 1
        };

        setTimeout(() => {
            this.displaySearchResults(demoData, `Places in ${cityName}`);
            this.showLoading(false);
        }, 500);
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

        // Demo data with Unsplash images
        const demoPlaces = [
            {
                id: 1,
                name: "Café Saturnus",
                city: "Stockholm",
                description: "Famous for their giant cinnamon buns and traditional Swedish atmosphere in Östermalm.",
                rating: 4.7,
                features: ["kanelbullar", "wifi", "outdoor_seating"],
                images: ["https://images.unsplash.com/photo-1554118811-1e0d58224f24?w=400&h=300&fit=crop&auto=format"]
            },
            {
                id: 2,
                name: "Konditori Hollandia",
                city: "Gothenburg",
                description: "Historic bakery serving traditional Swedish pastries since 1920 in the heart of Gothenburg.",
                rating: 4.8,
                features: ["prinsesstarta", "traditional", "historic"],
                images: ["https://images.unsplash.com/photo-1578662996442-48f60103fc96?w=400&h=300&fit=crop&auto=format"]
            },
            {
                id: 3,
                name: "Lilla Kafferosteriet",
                city: "Stockholm",
                description: "Small specialty coffee roaster with cozy atmosphere and freshly baked Swedish pastries.",
                rating: 4.6,
                features: ["specialty_coffee", "fresh_pastries", "cozy"],
                images: ["https://images.unsplash.com/photo-1501339847302-ac426a4a7cbb?w=400&h=300&fit=crop&auto=format"]
            }
        ];

        featuredContainer.innerHTML = '';
        
        demoPlaces.forEach(place => {
            const card = this.createFeaturedCard(place);
            featuredContainer.appendChild(card);
        });
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
    const app = new FikaApp();
    window.fikaApp = app; // Make globally accessible
    
    // Initialize filter navigation
    initializeFilterNavigation(app);
    
    // Initialize brand link
    initializeBrandLink(app);
});

// Filter Navigation System
function initializeFilterNavigation(app) {
    // Bootstrap dropdowns are handled automatically, we just need to handle the filter clicks
    
    // About button handler
    const aboutBtn = document.getElementById('about-fika-btn');
    if (aboutBtn) {
        aboutBtn.addEventListener('click', (e) => {
            e.preventDefault();
            const aboutSection = document.getElementById('about-fika');
            if (aboutSection) {
                aboutSection.scrollIntoView({ behavior: 'smooth' });
            }
        });
    }
    
    // City filters
    document.querySelectorAll('.city-filter').forEach(btn => {
        btn.addEventListener('click', (e) => {
            e.preventDefault();
            console.log('City filter clicked:', e.target.dataset.city);
            handleFilterClick(e, 'city-filter');
            const city = e.target.dataset.city;
            
            // Update dropdown toggle text
            const citiesToggle = e.target.closest('.dropdown').querySelector('.dropdown-toggle');
            if (citiesToggle) {
                citiesToggle.textContent = city === 'all' ? 'All Cities' : e.target.textContent;
            }
            
            if (city === 'all') {
                app.loadFeaturedPlaces();
                showAllSections();
            } else {
                app.searchByCity(city);
            }
        });
    });
    
    // Feature filters (seating)
    document.querySelectorAll('.feature-filter').forEach(btn => {
        btn.addEventListener('click', (e) => {
            e.preventDefault();
            handleFilterClick(e, 'feature-filter');
            const feature = e.target.dataset.feature;
            
            // Update dropdown toggle text
            const seatingToggle = e.target.closest('.dropdown').querySelector('.dropdown-toggle');
            if (seatingToggle) {
                seatingToggle.textContent = e.target.textContent;
            }
            
            filterByFeature(feature, app);
        });
    });
    
    // Specialty filters
    document.querySelectorAll('.specialty-filter').forEach(btn => {
        btn.addEventListener('click', (e) => {
            e.preventDefault();
            handleFilterClick(e, 'specialty-filter');
            const specialty = e.target.dataset.specialty;
            
            // Update dropdown toggle text
            const specialtiesToggle = e.target.closest('.dropdown').querySelector('.dropdown-toggle');
            if (specialtiesToggle) {
                specialtiesToggle.textContent = e.target.textContent;
            }
            
            filterBySpecialty(specialty, app);
        });
    });
}

function handleFilterClick(event, filterClass) {
    // Remove active class from all buttons in this filter group
    document.querySelectorAll(`.${filterClass}`).forEach(btn => {
        btn.classList.remove('active');
    });
    
    // Add active class to clicked button
    event.target.classList.add('active');
}

function filterByFeature(feature, app) {
    const allPlaces = getAllDemoPlaces();
    
    let filteredPlaces;
    if (feature === 'all') {
        app.loadFeaturedPlaces();
        showAllSections();
        return;
    } else {
        filteredPlaces = allPlaces.filter(place => {
            const features = place.features || [];
            return features.includes(feature);
        });
    }
    
    const featureNames = {
        'outdoor_seating': 'Outdoor Seating',
        'indoor_seating': 'Indoor Seating'
    };
    
    displayFilteredResults(filteredPlaces, `Places with ${featureNames[feature] || feature}`);
}

function filterBySpecialty(specialty, app) {
    const allPlaces = getAllDemoPlaces();
    
    const filteredPlaces = allPlaces.filter(place => {
        const features = place.features || [];
        return features.includes(specialty);
    });
    
    const specialtyNames = {
        'kanelbullar': 'Kanelbullar (Cinnamon Buns)',
        'prinsesstarta': 'Prinsesstårta (Princess Cake)', 
        'wifi': 'WiFi Available'
    };
    
    displayFilteredResults(filteredPlaces, `Places with ${specialtyNames[specialty] || specialty}`);
}

function getAllDemoPlaces() {
    // This mirrors the demo data from the app's searchByCity method
    const stockholmPlaces = [
        {
            id: 1,
            name: "Café Saturnus",
            city: "Stockholm",
            address: "Eriksbergsgatan 6, Östermalm",
            description: "Famous for their giant cinnamon buns and traditional Swedish atmosphere in Östermalm.",
            rating: 4.7,
            features: ["kanelbullar", "wifi", "outdoor_seating"]
        },
        {
            id: 2,
            name: "Vete-Katten",
            city: "Stockholm", 
            address: "Kungsgatan 55, Norrmalm",
            description: "Historic konditori since 1928, serving traditional Swedish pastries and coffee.",
            rating: 4.5,
            features: ["prinsesstarta", "kanelbullar", "indoor_seating"]
        },
        {
            id: 3,
            name: "Rosendals Trädgård",
            city: "Stockholm",
            address: "Rosendalsterrassen 38, Djurgården", 
            description: "Garden café with organic pastries and beautiful greenhouse setting.",
            rating: 4.6,
            features: ["outdoor_seating", "wifi"]
        },
        {
            id: 4,
            name: "Chokladkoppen",
            city: "Stockholm",
            address: "Stortorget 18, Gamla Stan",
            description: "Charming café in the heart of Old Town, perfect for traditional fika with hot chocolate.",
            rating: 4.3,
            features: ["indoor_seating", "coffee", "kanelbullar"]
        },
        {
            id: 5,
            name: "Café Pascal",
            city: "Stockholm",
            address: "Norrtullsgatan 4, Vasastan",
            description: "French-inspired café with excellent coffee and homemade pastries in trendy Vasastan.",
            rating: 4.4,
            features: ["coffee", "wifi", "indoor_seating"]
        },
        {
            id: 6,
            name: "Fabrique Bakery",
            city: "Stockholm",
            address: "Kungsgatan 25, Norrmalm",
            description: "Artisan bakery known for fresh bread and authentic Swedish cardamom buns.",
            rating: 4.2,
            features: ["kanelbullar", "indoor_seating"]
        },
        {
            id: 7,
            name: "Grillska Huset",
            city: "Stockholm",
            address: "Stortorget 3, Gamla Stan",
            description: "Traditional Swedish café in a historic building with classic fika atmosphere.",
            rating: 4.1,
            features: ["prinsesstarta", "indoor_seating", "kanelbullar"]
        },
        {
            id: 8,
            name: "Café Rival",
            city: "Stockholm",
            address: "Mariatorget 3, Södermalm",
            description: "Stylish café in trendy Södermalm with great coffee and modern Swedish pastries.",
            rating: 4.5,
            features: ["coffee", "wifi", "outdoor_seating"]
        },
        {
            id: 9,
            name: "Konditori Hollandia",
            city: "Stockholm",
            address: "Upplandsgatan 28, Vasastan",
            description: "Family-run konditori serving traditional Swedish cakes and pastries since 1952.",
            rating: 4.6,
            features: ["prinsesstarta", "kanelbullar", "indoor_seating"]
        },
        {
            id: 10,
            name: "String Café",
            city: "Stockholm",
            address: "Nytorget 19, Södermalm",
            description: "Modern coffee shop with specialty beans and minimalist Scandinavian design.",
            rating: 4.4,
            features: ["coffee", "wifi", "indoor_seating"]
        }
    ];
    
    const gothenburgPlaces = [
        {
            id: 11,
            name: "Da Matteo",
            city: "Gothenburg",
            address: "Magasinsgatan 17A, Centrum",
            description: "Italian-inspired coffee roastery with excellent kanelbullar and cozy atmosphere.",
            rating: 4.8,
            features: ["kanelbullar", "wifi", "indoor_seating"]
        },
        {
            id: 12,
            name: "Café Husaren", 
            city: "Gothenburg",
            address: "Haga Nygata 28, Haga",
            description: "Famous for the largest cinnamon buns in Sweden, a true Gothenburg institution.",
            rating: 4.4,
            features: ["kanelbullar", "outdoor_seating"]
        },
        {
            id: 13,
            name: "Café Magasinet",
            city: "Gothenburg",
            address: "Tredje Långgatan 8, Majorna",
            description: "Industrial-chic café in Majorna with locally roasted coffee and fresh pastries.",
            rating: 4.5,
            features: ["coffee", "industrial_design", "indoor_seating"]
        },
        {
            id: 14,
            name: "Rosenkaffe",
            city: "Gothenburg",
            address: "Rosenlundsgatan 6, Centrum",
            description: "Specialty coffee roastery and café with award-winning baristas and prinsesstårta.",
            rating: 4.7,
            features: ["coffee", "prinsesstarta", "wifi"]
        },
        {
            id: 15,
            name: "Café Kringlan",
            city: "Gothenburg",
            address: "Första Långgatan 28, Majorna",
            description: "Cozy neighborhood café known for their homemade kanelbullar and friendly atmosphere.",
            rating: 4.3,
            features: ["kanelbullar", "neighborhood", "outdoor_seating"]
        },
        {
            id: 16,
            name: "Blackbird Coffee",
            city: "Gothenburg",
            address: "Kungsgatan 7, Centrum",
            description: "Australian-style coffee house with flat whites and Swedish pastries.",
            rating: 4.6,
            features: ["coffee", "australian_style", "indoor_seating"]
        },
        {
            id: 17,
            name: "Café Rondo",
            city: "Gothenburg",
            address: "Chalmersgatan 12, Vasastaden",
            description: "Student favorite near Chalmers University with affordable fika and study-friendly atmosphere.",
            rating: 4.2,
            features: ["student_friendly", "wifi", "indoor_seating"]
        },
        {
            id: 18,
            name: "Konditori Caroli",
            city: "Gothenburg",
            address: "Östra Hamngatan 18, Centrum",
            description: "Traditional Swedish konditori since 1952, famous for their handmade prinsesstårta.",
            rating: 4.5,
            features: ["prinsesstarta", "traditional", "historic"]
        },
        {
            id: 19,
            name: "Café Kanel",
            city: "Gothenburg",
            address: "Vasagatan 32, Vasastaden",
            description: "Warm, inviting café specializing in cinnamon-based treats and organic coffee.",
            rating: 4.4,
            features: ["kanelbullar", "organic", "cozy"]
        },
        {
            id: 20,
            name: "The Coffee Factory",
            city: "Gothenburg",
            address: "Klippan 1B, Klippan",
            description: "Industrial coffee roastery with tours, tastings, and exceptional Swedish pastries.",
            rating: 4.7,
            features: ["coffee", "tours", "industrial"]
        }
    ];
    
    const malmoPlaces = [
        {
            id: 21,
            name: "Lilla Kafferosteriet",
            city: "Malmö",
            address: "Baltzarsgatan 24, Centrum",
            description: "Small coffee roastery with excellent single-origin beans and homemade pastries.",
            rating: 4.6,
            features: ["wifi", "indoor_seating"]
        },
        {
            id: 22,
            name: "Café Sirap",
            city: "Malmö",
            address: "Stora Nygatan 35, Gamla Staden",
            description: "Charming vintage café with traditional Swedish fika culture and outdoor seating.",
            rating: 4.3,
            features: ["prinsesstarta", "outdoor_seating"]
        },
        {
            id: 23,
            name: "Hollandia",
            city: "Malmö",
            address: "Södergatan 64, Centrum",
            description: "Historic café and konditori since 1922, famous for their traditional prinsesstårta.",
            rating: 4.7,
            features: ["prinsesstarta", "historic", "traditional"]
        },
        {
            id: 24,
            name: "Café Pronto",
            city: "Malmö",
            address: "Davidshallsgatan 9, Davidshall",
            description: "Italian-Swedish fusion café with excellent espresso and kanelbullar.",
            rating: 4.4,
            features: ["kanelbullar", "espresso", "fusion"]
        },
        {
            id: 25,
            name: "Mood Coffee Bar",
            city: "Malmö",
            address: "Rörsjögatan 14, Möllevången",
            description: "Hip coffee bar in multicultural Möllevången with specialty roasts and vegan pastries.",
            rating: 4.5,
            features: ["coffee", "vegan", "multicultural"]
        },
        {
            id: 26,
            name: "Café Ariman",
            city: "Malmö",
            address: "Storgatan 17, Centrum",
            description: "Persian-Swedish café blend with unique pastries and strong coffee traditions.",
            rating: 4.3,
            features: ["international", "strong_coffee", "unique_pastries"]
        },
        {
            id: 27,
            name: "Bullar & Bamba",
            city: "Malmö",
            address: "Amiralsgatan 23, Centrum",
            description: "Modern bakery café specializing in creative takes on traditional kanelbullar.",
            rating: 4.6,
            features: ["kanelbullar", "modern", "creative"]
        },
        {
            id: 28,
            name: "St. Jakobs Stenugnsbageri",
            city: "Malmö",
            address: "S:t Paulsgatan 25, S:t Pauli",
            description: "Stone-oven bakery with artisanal breads, traditional pastries, and outdoor courtyard.",
            rating: 4.4,
            features: ["artisanal", "outdoor_seating", "stone_oven"]
        },
        {
            id: 29,
            name: "Café Kopparkanna",
            city: "Malmö",
            address: "Kalendegatan 12, Gamla Staden",
            description: "Cozy old town café with copper details, serving traditional Swedish fika in historic setting.",
            rating: 4.5,
            features: ["historic", "traditional", "cozy"]
        },
        {
            id: 30,
            name: "Nordic Roastery",
            city: "Malmö",
            address: "Industrigatan 8, Västra Hamnen",
            description: "Minimalist Scandinavian roastery in modern Västra Hamnen with harbor views.",
            rating: 4.7,
            features: ["coffee", "harbor_views", "scandinavian_design"]
        }
    ];
    
    return [...stockholmPlaces, ...gothenburgPlaces, ...malmoPlaces];
}

function displayFilteredResults(places, title) {
    // Hide main sections
    const hero = document.querySelector('.hero');
    const featured = document.querySelector('.featured');
    const aboutFika = document.querySelector('.about-fika');
    
    if (hero) hero.style.display = 'none';
    if (featured) featured.style.display = 'none';
    if (aboutFika) aboutFika.style.display = 'none';
    
    const searchResults = document.getElementById('search-results');
    const resultsTitle = document.getElementById('search-results-title');
    const resultsContainer = document.getElementById('results-container');
    
    if (resultsTitle) resultsTitle.textContent = title;
    if (searchResults) searchResults.style.display = 'block';
    
    if (places.length === 0) {
        if (resultsContainer) {
            resultsContainer.innerHTML = `
                <div class="no-results">
                    <p>No fika places found with these criteria. Try different filters!</p>
                </div>
            `;
        }
        return;
    }
    
    if (resultsContainer) {
        resultsContainer.innerHTML = places.map(place => createPlaceCard(place)).join('');
    }
}

function createPlaceCard(place) {
    const rating = place.rating || 0;
    const stars = '★'.repeat(Math.floor(rating)) + '☆'.repeat(5 - Math.floor(rating));
    
    return `
        <article class="place-card" data-place-id="${place.id}">
            <div class="place-header">
                <div>
                    <h3 class="place-name">${escapeHtml(place.name)}</h3>
                    <p class="place-location">${escapeHtml(place.address || place.city)}</p>
                </div>
                <div class="place-rating">
                    <span class="stars">${stars}</span>
                    <span class="rating-value">${rating.toFixed(1)}</span>
                </div>
            </div>
            <p class="place-description">${escapeHtml(place.description || '')}</p>
            ${place.features && place.features.length > 0 ? 
                `<div class="place-features">
                    ${place.features.slice(0, 3).map(feature => 
                        `<span class="feature-tag">${escapeHtml(formatFeature(feature))}</span>`
                    ).join('')}
                </div>` 
                : ''
            }
        </article>
    `;
}

function formatFeature(feature) {
    const featureMap = {
        'wifi': 'WiFi',
        'outdoor_seating': 'Uteservering',
        'indoor_seating': 'Inomhus',
        'wheelchair_accessible': 'Rullstolstillgänglig',
        'kanelbullar': 'Kanelbullar',
        'prinsesstarta': 'Prinsesstårta',
        'coffee': 'Kaffe'
    };
    
    return featureMap[feature] || feature.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
}

function escapeHtml(unsafe) {
    if (typeof unsafe !== 'string') return '';
    return unsafe
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
}

function showAllSections() {
    // Show main sections
    const hero = document.querySelector('.hero');
    const featured = document.querySelector('.featured');
    const aboutFika = document.querySelector('.about-fika');
    const searchResults = document.getElementById('search-results');
    
    if (hero) hero.style.display = 'flex';
    if (featured) featured.style.display = 'block';
    if (aboutFika) aboutFika.style.display = 'block';
    if (searchResults) searchResults.style.display = 'none';
}

function initializeBrandLink(app) {
    const brandLink = document.querySelector('.brand-link');
    if (brandLink) {
        brandLink.addEventListener('click', (e) => {
            e.preventDefault();
            
            // Reset all filters to default state
            document.querySelectorAll('.filter-btn').forEach(btn => {
                btn.classList.remove('active');
            });
            
            // Set "All Cities" and "All Types" as active
            const allCitiesBtn = document.querySelector('.city-filter[data-city="all"]');
            const allTypesBtn = document.querySelector('.feature-filter[data-feature="all"]');
            
            if (allCitiesBtn) allCitiesBtn.classList.add('active');
            if (allTypesBtn) allTypesBtn.classList.add('active');
            
            // Clear search input
            const searchInput = document.getElementById('search-input');
            if (searchInput) searchInput.value = '';
            
            // Show all sections and load featured places
            showAllSections();
            app.loadFeaturedPlaces();
            
            // Scroll to top smoothly
            window.scrollTo({
                top: 0,
                behavior: 'smooth'
            });
        });
    }
}

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

// Contact Form Handling
function initializeContactForm() {
    const contactForm = document.getElementById('contact-form');
    if (!contactForm) return;
    
    contactForm.addEventListener('submit', function(e) {
        e.preventDefault();
        
        // Get form data
        const formData = new FormData(contactForm);
        const data = {
            firstName: formData.get('firstName'),
            lastName: formData.get('lastName'),
            email: formData.get('email'),
            subject: formData.get('subject'),
            message: formData.get('message'),
            newsletter: formData.get('newsletter') === 'on'
        };
        
        // Show loading state
        const submitBtn = contactForm.querySelector('button[type="submit"]');
        const originalText = submitBtn.textContent;
        submitBtn.textContent = 'Sending...';
        submitBtn.disabled = true;
        
        // Simulate form submission (replace with actual endpoint)
        setTimeout(() => {
            // Show success message
            showContactFormMessage('Thank you for your message! We\'ll get back to you within 24-48 hours.', 'success');
            
            // Reset form
            contactForm.reset();
            
            // Reset button
            submitBtn.textContent = originalText;
            submitBtn.disabled = false;
        }, 1500);
        
        // In a real implementation, you would send the data to your server:
        // fetch('/api/contact', {
        //     method: 'POST',
        //     headers: { 'Content-Type': 'application/json' },
        //     body: JSON.stringify(data)
        // })
        // .then(response => response.json())
        // .then(data => {
        //     if (data.success) {
        //         showContactFormMessage('Thank you for your message!', 'success');
        //         contactForm.reset();
        //     } else {
        //         showContactFormMessage('Sorry, there was an error sending your message. Please try again.', 'error');
        //     }
        // })
        // .catch(error => {
        //     showContactFormMessage('Sorry, there was an error sending your message. Please try again.', 'error');
        // })
        // .finally(() => {
        //     submitBtn.textContent = originalText;
        //     submitBtn.disabled = false;
        // });
    });
}

function showContactFormMessage(message, type) {
    // Remove existing message
    const existingMessage = document.querySelector('.contact-form-message');
    if (existingMessage) {
        existingMessage.remove();
    }
    
    // Create message element
    const messageElement = document.createElement('div');
    messageElement.className = `alert ${type === 'success' ? 'alert-success' : 'alert-danger'} contact-form-message mt-3`;
    messageElement.textContent = message;
    
    // Insert after form
    const contactForm = document.getElementById('contact-form');
    contactForm.insertAdjacentElement('afterend', messageElement);
    
    // Auto-remove after 5 seconds
    setTimeout(() => {
        if (messageElement.parentNode) {
            messageElement.remove();
        }
    }, 5000);
}

// Initialize contact form when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    initializeContactForm();
});

// Export for global access
window.FikaApp = FikaApp;