<?php
/**
 * Template: Featured Places
 * Displays featured fika places
 */

// Prevent direct access
if (!defined('ABSPATH')) {
    exit;
}

$limit = isset($atts['limit']) ? intval($atts['limit']) : 3;
$show_description = isset($atts['show_description']) ? ($atts['show_description'] === 'true') : true;

if (!$places || !isset($places['places']) || empty($places['places'])) {
    ?>
    <section class="fika-featured-section">
        <header>
            <h3><?php _e('Featured Fika Experiences', 'fika-register'); ?></h3>
        </header>
        <div class="fika-loading">
            <?php _e('Loading featured fika places...', 'fika-register'); ?>
        </div>
    </section>
    
    <script>
    jQuery(document).ready(function($) {
        // Auto-load featured places
        setTimeout(function() {
            var $container = $('.fika-featured-section .fika-loading').parent();
            
            $.ajax({
                url: fikaAjax.ajax_url,
                method: 'POST',
                data: {
                    action: 'fika_search',
                    nonce: fikaAjax.nonce,
                    featured: 'true',
                    limit: <?php echo $limit; ?>
                },
                success: function(response) {
                    if (response.success && response.data.places) {
                        displayFeaturedPlaces(response.data.places, $container);
                    } else {
                        $container.find('.fika-loading').html(
                            '<div class="fika-no-results"><?php _e('Featured places coming soon!', 'fika-register'); ?></div>'
                        );
                    }
                },
                error: function() {
                    $container.find('.fika-loading').html(
                        '<div class="fika-error"><?php _e('Could not load featured places.', 'fika-register'); ?></div>'
                    );
                }
            });
        }, 300);
        
        function displayFeaturedPlaces(places, $container) {
            var $grid = $('<div class="fika-places-grid"></div>');
            
            places.forEach(function(place) {
                var $card = createFeaturedPlaceCard(place);
                $grid.append($card);
            });
            
            $container.find('.fika-loading').replaceWith($grid);
        }
        
        function createFeaturedPlaceCard(place) {
            var rating = place.rating || 0;
            var stars = '★'.repeat(Math.floor(rating)) + '☆'.repeat(5 - Math.floor(rating));
            
            var description = '';
            <?php if ($show_description) : ?>
            if (place.description) {
                description = '<p class="fika-place-description">' + 
                    escapeHtml(place.description.substring(0, 100)) + 
                    (place.description.length > 100 ? '...' : '') + 
                '</p>';
            }
            <?php endif; ?>
            
            var features = place.features || place.fika_specialties || [];
            var featureTags = features.slice(0, 2).map(function(feature) {
                return '<span class="fika-feature-tag">' + escapeHtml(formatFeature(feature)) + '</span>';
            }).join('');
            
            var imageHtml = '';
            if (place.images && place.images[0]) {
                imageHtml = '<img class="fika-place-image" src="' + escapeHtml(place.images[0]) + '" alt="' + escapeHtml(place.name) + '" loading="lazy">';
            }
            
            return $(`
                <article class="fika-place-card fika-featured-card" data-place-id="${place.id}">
                    ${imageHtml}
                    <div class="fika-place-content">
                        <div class="fika-place-header">
                            <div>
                                <h4 class="fika-place-title">${escapeHtml(place.name)}</h4>
                                <div class="fika-place-location">
                                    <span>📍</span>
                                    <span>${escapeHtml(place.city)}</span>
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

<section class="fika-featured-section">
    <header>
        <h3><?php _e('Featured Fika Experiences', 'fika-register'); ?></h3>
        <p class="fika-section-description">
            <?php _e('Discover our carefully selected traditional Swedish fika locations', 'fika-register'); ?>
        </p>
    </header>
    
    <div class="fika-places-grid fika-featured-grid">
        <?php foreach ($places['places'] as $place) : ?>
            <article class="fika-place-card fika-featured-card" data-place-id="<?php echo esc_attr($place['id']); ?>">
                <?php if (!empty($place['images']) && !empty($place['images'][0])) : ?>
                    <img 
                        class="fika-place-image" 
                        src="<?php echo esc_url($place['images'][0]); ?>" 
                        alt="<?php echo esc_attr($place['name']); ?>"
                        loading="lazy"
                    >
                <?php endif; ?>
                
                <div class="fika-place-content">
                    <div class="fika-place-header">
                        <div>
                            <h4 class="fika-place-title"><?php echo esc_html($place['name']); ?></h4>
                            <div class="fika-place-location">
                                <span>📍</span>
                                <span><?php echo esc_html($place['city']); ?></span>
                            </div>
                        </div>
                        
                        <?php if (isset($place['rating'])) : ?>
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
                            echo esc_html(strlen($description) > 100 ? substr($description, 0, 100) . '...' : $description); 
                            ?>
                        </p>
                    <?php endif; ?>
                    
                    <?php 
                    $features = $place['features'] ?? $place['fika_specialties'] ?? [];
                    if (!empty($features)) : 
                    ?>
                        <div class="fika-place-features">
                            <?php foreach (array_slice($features, 0, 2) as $feature) : ?>
                                <span class="fika-feature-tag"><?php echo esc_html($feature); ?></span>
                            <?php endforeach; ?>
                        </div>
                    <?php endif; ?>
                </div>
            </article>
        <?php endforeach; ?>
    </div>
    
    <footer class="fika-featured-footer">
        <p>
            <a href="<?php echo esc_url(home_url('/fika-places/?featured=true')); ?>" class="fika-view-all">
                <?php _e('Explore all featured fika experiences →', 'fika-register'); ?>
            </a>
        </p>
    </footer>
</section>

<style>
.fika-featured-grid .fika-featured-card {
    display: flex;
    flex-direction: column;
    overflow: hidden;
}

.fika-place-image {
    width: 100%;
    height: 200px;
    object-fit: cover;
    border-radius: 6px 6px 0 0;
}

.fika-place-content {
    padding: 16px;
    flex: 1;
    display: flex;
    flex-direction: column;
}

.fika-section-description {
    color: var(--fika-text-light);
    margin-bottom: 20px;
    font-style: italic;
}

.fika-featured-footer {
    text-align: center;
    margin-top: 24px;
}

.fika-view-all {
    color: var(--fika-blue);
    text-decoration: none;
    font-weight: 500;
    padding: 8px 16px;
    border: 1px solid var(--fika-blue);
    border-radius: 4px;
    transition: all 0.2s ease;
}

.fika-view-all:hover {
    background: var(--fika-blue);
    color: var(--fika-white);
}

@media (max-width: 768px) {
    .fika-featured-grid {
        grid-template-columns: 1fr;
    }
    
    .fika-place-image {
        height: 160px;
    }
}
</style>

<script type="application/ld+json">
{
    "@context": "https://schema.org",
    "@type": "ItemList",
    "name": "<?php _e('Featured Swedish Fika Places', 'fika-register'); ?>",
    "description": "<?php _e('Carefully selected traditional Swedish fika locations', 'fika-register'); ?>",
    "numberOfItems": <?php echo count($places['places']); ?>,
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
                <?php if (!empty($place['images']) && !empty($place['images'][0])) : ?>
                "image": "<?php echo esc_js($place['images'][0]); ?>",
                <?php endif; ?>
                "description": "<?php echo esc_js($place['description'] ?? ''); ?>"
            }
        }<?php echo ($index < count($places['places']) - 1) ? ',' : ''; ?>
        <?php endforeach; ?>
    ]
}
</script>