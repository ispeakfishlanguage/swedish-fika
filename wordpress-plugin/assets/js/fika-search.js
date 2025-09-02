/**
 * Traditional Swedish Fika - WordPress Plugin JavaScript
 */

(function($) {
    'use strict';
    
    // Initialize when document is ready
    $(document).ready(function() {
        initFikaSearch();
        initFikaWidgets();
    });
    
    function initFikaSearch() {
        // Handle search form submissions
        $('.fika-search-form').on('submit', function(e) {
            e.preventDefault();
            
            const $form = $(this);
            const $input = $form.find('.fika-search-input');
            const $cityFilter = $form.find('.fika-city-filter select');
            const $resultsContainer = $form.siblings('.fika-search-results');
            
            const query = $input.val().trim();
            const city = $cityFilter.length ? $cityFilter.val() : '';
            
            if (query.length === 0 && city === '') {
                showError($resultsContainer, fikaAjax.error_text);
                return;
            }
            
            performSearch(query, city, $resultsContainer);
        });
        
        // Handle real-time search (debounced)
        let searchTimeout;
        $('.fika-search-input').on('input', function() {
            const $input = $(this);
            const $form = $input.closest('.fika-search-form');
            const $resultsContainer = $form.siblings('.fika-search-results');
            const query = $input.val().trim();
            
            clearTimeout(searchTimeout);
            
            if (query.length >= 2) {
                searchTimeout = setTimeout(function() {
                    performSearch(query, '', $resultsContainer);
                }, 500);
            } else if (query.length === 0) {
                $resultsContainer.empty();
            }
        });
        
        // Handle city filter changes
        $('.fika-city-filter select').on('change', function() {
            const $select = $(this);
            const $form = $select.closest('.fika-search-form');
            const $input = $form.find('.fika-search-input');
            const $resultsContainer = $form.siblings('.fika-search-results');
            
            const city = $select.val();
            const query = $input.val().trim();
            
            if (city !== '' || query !== '') {
                performSearch(query, city, $resultsContainer);
            }
        });
    }
    
    function initFikaWidgets() {
        // Handle widget interactions
        $('.fika-widget').each(function() {
            const $widget = $(this);
            
            // Lazy load widget content if needed
            if ($widget.hasClass('fika-lazy-load')) {
                loadWidgetContent($widget);
            }
        });
    }
    
    function performSearch(query, city, $resultsContainer) {
        showLoading($resultsContainer);
        
        $.ajax({
            url: fikaAjax.ajax_url,
            method: 'POST',
            data: {
                action: 'fika_search',
                nonce: fikaAjax.nonce,
                query: query,
                city: city
            },
            success: function(response) {
                if (response.success) {
                    displaySearchResults(response.data, $resultsContainer);
                } else {
                    showError($resultsContainer, response.data || fikaAjax.error_text);
                }
            },
            error: function(xhr, status, error) {
                console.error('Fika search error:', error);
                showError($resultsContainer, fikaAjax.error_text);
            }
        });
    }
    
    function displaySearchResults(data, $container) {
        $container.empty();
        
        if (!data || !data.places || data.places.length === 0) {
            $container.html('<div class="fika-no-results">Inga fika-ställen hittades. Försök med ett annat sökord.</div>');
            return;
        }
        
        const $grid = $('<div class="fika-places-grid"></div>');
        
        data.places.forEach(function(place) {
            const $card = createPlaceCard(place);
            $grid.append($card);
        });
        
        $container.append($grid);
        
        // Show pagination if available
        if (data.pages > 1) {
            const $pagination = createPagination(data);
            $container.append($pagination);
        }
    }
    
    function createPlaceCard(place) {
        const rating = place.rating || 0;
        const stars = '★'.repeat(Math.floor(rating)) + '☆'.repeat(5 - Math.floor(rating));
        
        const features = place.features || place.fika_specialties || [];
        const featureTags = features.slice(0, 3).map(function(feature) {
            return '<span class="fika-feature-tag">' + escapeHtml(formatFeature(feature)) + '</span>';
        }).join('');
        
        const description = place.description ? 
            '<p class="fika-place-description">' + escapeHtml(place.description.substring(0, 150)) + 
            (place.description.length > 150 ? '...' : '') + '</p>' : '';
        
        return $(`
            <div class="fika-place-card" data-place-id="${place.id}">
                <div class="fika-place-header">
                    <div>
                        <h4 class="fika-place-title">${escapeHtml(place.name)}</h4>
                        <div class="fika-place-location">
                            <span>📍</span>
                            <span>${escapeHtml(place.address || place.city)}</span>
                        </div>
                    </div>
                    <div class="fika-place-rating">
                        <span class="fika-stars">${stars}</span>
                        <span class="fika-rating-value">${rating.toFixed(1)}</span>
                    </div>
                </div>
                ${description}
                ${featureTags ? '<div class="fika-place-features">' + featureTags + '</div>' : ''}
            </div>
        `);
    }
    
    function createPagination(data) {
        const $pagination = $('<div class="fika-pagination"></div>');
        
        // Previous button
        if (data.page > 1) {
            const $prevBtn = $('<button class="fika-page-btn" data-page="' + (data.page - 1) + '">← Föregående</button>');
            $pagination.append($prevBtn);
        }
        
        // Page numbers
        const startPage = Math.max(1, data.page - 2);
        const endPage = Math.min(data.pages, data.page + 2);
        
        for (let i = startPage; i <= endPage; i++) {
            const $pageBtn = $('<button class="fika-page-btn' + (i === data.page ? ' active' : '') + '" data-page="' + i + '">' + i + '</button>');
            $pagination.append($pageBtn);
        }
        
        // Next button
        if (data.page < data.pages) {
            const $nextBtn = $('<button class="fika-page-btn" data-page="' + (data.page + 1) + '">Nästa →</button>');
            $pagination.append($nextBtn);
        }
        
        // Handle pagination clicks
        $pagination.on('click', '.fika-page-btn', function() {
            const page = $(this).data('page');
            // Implement pagination logic here
            console.log('Load page:', page);
        });
        
        return $pagination;
    }
    
    function loadWidgetContent($widget) {
        const widgetType = $widget.data('widget-type');
        const widgetSettings = $widget.data('widget-settings');
        
        $.ajax({
            url: fikaAjax.ajax_url,
            method: 'POST',
            data: {
                action: 'fika_load_widget',
                nonce: fikaAjax.nonce,
                widget_type: widgetType,
                settings: widgetSettings
            },
            success: function(response) {
                if (response.success) {
                    $widget.html(response.data);
                } else {
                    $widget.html('<div class="fika-error">Widget kunde inte laddas</div>');
                }
            },
            error: function() {
                $widget.html('<div class="fika-error">Widget kunde inte laddas</div>');
            }
        });
    }
    
    function showLoading($container) {
        $container.html('<div class="fika-loading">' + fikaAjax.loading_text + '</div>');
    }
    
    function showError($container, message) {
        $container.html('<div class="fika-error">' + escapeHtml(message) + '</div>');
    }
    
    function formatFeature(feature) {
        const featureMap = {
            'wifi': 'WiFi',
            'outdoor_seating': 'Uteservering',
            'wheelchair_accessible': 'Rullstolstillgänglig',
            'kanelbullar': 'Kanelbullar',
            'prinsesstarta': 'Prinsesstårta',
            'coffee': 'Kaffe',
            'tea': 'Te',
            'pastries': 'Bakverk',
            'sandwiches': 'Smörgåsar',
            'lunch': 'Lunch',
            'breakfast': 'Frukost'
        };
        
        return featureMap[feature] || feature.replace(/_/g, ' ').replace(/\b\w/g, function(l) {
            return l.toUpperCase();
        });
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
    
})(jQuery);