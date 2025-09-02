<?php
/**
 * Template: City Places
 * Displays fika places for a specific city
 */

// Prevent direct access
if (!defined('ABSPATH')) {
    exit;
}

$city = isset($atts['city']) ? esc_attr($atts['city']) : 'stockholm';
$limit = isset($atts['limit']) ? intval($atts['limit']) : 6;
$show_description = isset($atts['show_description']) ? ($atts['show_description'] === 'true') : true;
$show_rating = isset($atts['show_rating']) ? ($atts['show_rating'] === 'true') : true;

// Map city keys to display names and icons
$city_info = array(
    'stockholm' => array('name' => 'Stockholm', 'icon' => '🏛️'),
    'gothenburg' => array('name' => 'Gothenburg', 'icon' => '🏗️'),
    'malmo' => array('name' => 'Malmö', 'icon' => '🌉'),
    'uppsala' => array('name' => 'Uppsala', 'icon' => '🎓'),
    'vasteras' => array('name' => 'Västerås', 'icon' => '⚡')
);

$city_display = isset($city_info[$city]) ? $city_info[$city] : array('name' => ucfirst($city), 'icon' => '🏙️');

if (!$places || !isset($places['places']) || empty($places['places'])) {
    ?>
    <div class="fika-city-section">
        <h3>
            <span class="fika-city-icon"><?php echo $city_display['icon']; ?></span>
            <?php printf(__('Fika Places in %s', 'fika-register'), $city_display['name']); ?>
        </h3>
        <div class="fika-loading">
            <?php printf(__('Loading fika places in %s...', 'fika-register'), $city_display['name']); ?>
        </div>
    </div>
    
    <script>
    jQuery(document).ready(function($) {
        // Auto-load city places
        setTimeout(function() {
            var $container = $('.fika-city-section .fika-loading').parent();
            
            $.ajax({
                url: fikaAjax.ajax_url,
                method: 'POST',
                data: {
                    action: 'fika_search',
                    nonce: fikaAjax.nonce,
                    city: '<?php echo esc_js($city_display['name']); ?>',
                    limit: <?php echo $limit; ?>
                },
                success: function(response) {
                    if (response.success && response.data.places) {
                        displayCityPlaces(response.data.places, $container);
                    } else {
                        $container.find('.fika-loading').html(
                            '<div class="fika-no-results"><?php printf(__('No fika places found in %s yet.', 'fika-register'), $city_display['name']); ?></div>'
                        );
                    }
                },
                error: function() {
                    $container.find('.fika-loading').html(
                        '<div class="fika-error"><?php printf(__('Could not load fika places in %s.', 'fika-register'), $city_display['name']); ?></div>'
                    );
                }
            });
        }, 500);
        
        function displayCityPlaces(places, $container) {
            var $grid = $('<div class="fika-places-grid"></div>');
            
            places.forEach(function(place) {
                var $card = createCityPlaceCard(place);
                $grid.append($card);
            });
            
            $container.find('.fika-loading').replaceWith($grid);
        }
        
        function createCityPlaceCard(place) {
            var rating = place.rating || 0;
            var stars = '★'.repeat(Math.floor(rating)) + '☆'.repeat(5 - Math.floor(rating));
            
            var description = '';
            <?php if ($show_description) : ?>
            if (place.description) {
                description = '<p class="fika-place-description">' + 
                    escapeHtml(place.description.substring(0, 120)) + 
                    (place.description.length > 120 ? '...' : '') + 
                '</p>';
            }
            <?php endif; ?>
            
            var rating_html = '';
            <?php if ($show_rating) : ?>
            rating_html = '<div class="fika-place-rating">' +
                '<span class="fika-stars">' + stars + '</span>' +
                '<span class="fika-rating-value">' + rating.toFixed(1) + '</span>' +
            '</div>';
            <?php endif; ?>
            
            var features = place.features || place.fika_specialties || [];
            var featureTags = features.slice(0, 2).map(function(feature) {
                return '<span class="fika-feature-tag">' + escapeHtml(formatFeature(feature)) + '</span>';
            }).join('');
            
            return $(`
                <article class="fika-place-card" data-place-id="${place.id}">
                    <div class="fika-place-header">
                        <div>
                            <h4 class="fika-place-title">${escapeHtml(place.name)}</h4>
                            <div class="fika-place-location">
                                <span>📍</span>
                                <span>${escapeHtml(place.address || place.city)}</span>
                            </div>
                        </div>
                        ${rating_html}
                    </div>
                    ${description}
                    ${featureTags ? '<div class="fika-place-features">' + featureTags + '</div>' : ''}
                </article>
            `);
        }
        
        function formatFeature(feature) {
            var featureMap = {
                'wifi': 'WiFi',
                'outdoor_seating': 'Uteservering',
                'wheelchair_accessible': 'Rullstolstillgänglig',
                'kanelbullar': 'Kanelbullar',
                'prinsesstarta': 'Prinsesstårta',
                'coffee': 'Kaffe'
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
    });
    </script>
    <?php
    return;
}
?>

<section class="fika-city-section">
    <header>
        <h3>
            <span class="fika-city-icon"><?php echo $city_display['icon']; ?></span>
            <?php printf(__('Fika Places in %s', 'fika-register'), $city_display['name']); ?>
            <?php if (isset($places['total'])) : ?>
                <small>(<?php printf(_n('%d place', '%d places', $places['total'], 'fika-register'), $places['total']); ?>)</small>
            <?php endif; ?>
        </h3>
    </header>
    
    <div class="fika-places-grid">
        <?php foreach ($places['places'] as $place) : ?>
            <article class="fika-place-card" data-place-id="<?php echo esc_attr($place['id']); ?>">
                <div class="fika-place-header">
                    <div>
                        <h4 class="fika-place-title"><?php echo esc_html($place['name']); ?></h4>
                        <div class="fika-place-location">
                            <span>📍</span>
                            <span><?php echo esc_html($place['address'] ?? $place['city']); ?></span>
                        </div>
                    </div>
                    
                    <?php if ($show_rating && isset($place['rating'])) : ?>
                        <div class="fika-place-rating">
                            <span class="fika-stars">
                                <?php
                                $rating = floatval($place['rating']);
                                echo str_repeat('★', floor($rating)) . str_repeat('☆', 5 - floor($rating));
                                ?>
                            </span>
                            <span class="fika-rating-value"><?php echo number_format($rating, 1); ?></span>
                        </div>
                    <?php endif; ?>
                </div>
                
                <?php if ($show_description && !empty($place['description'])) : ?>
                    <p class="fika-place-description">
                        <?php 
                        $description = $place['description'];
                        echo esc_html(strlen($description) > 120 ? substr($description, 0, 120) . '...' : $description); 
                        ?>
                    </p>
                <?php endif; ?>
                
                <?php 
                $features = $place['features'] ?? $place['fika_specialties'] ?? [];
                if (!empty($features)) : 
                ?>
                    <div class="fika-place-features">
                        <?php foreach (array_slice($features, 0, 3) as $feature) : ?>
                            <span class="fika-feature-tag"><?php echo esc_html($feature); ?></span>
                        <?php endforeach; ?>
                    </div>
                <?php endif; ?>
            </article>
        <?php endforeach; ?>
    </div>
    
    <?php if (isset($places['total']) && $places['total'] > $limit) : ?>
        <footer class="fika-city-footer">
            <p>
                <a href="<?php echo esc_url(home_url('/fika-places/?city=' . urlencode($city))); ?>" class="fika-view-all">
                    <?php printf(__('View all %s fika places in %s →', 'fika-register'), $places['total'], $city_display['name']); ?>
                </a>
            </p>
        </footer>
    <?php endif; ?>
</section>

<script type="application/ld+json">
{
    "@context": "https://schema.org",
    "@type": "ItemList",
    "name": "<?php printf(__('Fika Places in %s', 'fika-register'), $city_display['name']); ?>",
    "description": "<?php printf(__('Traditional Swedish fika locations in %s', 'fika-register'), $city_display['name']); ?>",
    "numberOfItems": <?php echo isset($places['total']) ? $places['total'] : count($places['places']); ?>,
    "itemListElement": [
        <?php foreach ($places['places'] as $index => $place) : ?>
        {
            "@type": "ListItem",
            "position": <?php echo $index + 1; ?>,
            "item": {
                "@type": "Restaurant",
                "name": "<?php echo esc_js($place['name']); ?>",
                "address": "<?php echo esc_js($place['address'] ?? $place['city']); ?>",
                "servesCuisine": "Swedish",
                <?php if (isset($place['rating'])) : ?>
                "aggregateRating": {
                    "@type": "AggregateRating",
                    "ratingValue": "<?php echo floatval($place['rating']); ?>",
                    "bestRating": "5"
                },
                <?php endif; ?>
                "description": "<?php echo esc_js($place['description'] ?? ''); ?>"
            }
        }<?php echo ($index < count($places['places']) - 1) ? ',' : ''; ?>
        <?php endforeach; ?>
    ]
}
</script>