<?php
/**
 * Template: Search Form
 * Displays the fika search form
 */

// Prevent direct access
if (!defined('ABSPATH')) {
    exit;
}

$placeholder = isset($atts['placeholder']) ? esc_attr($atts['placeholder']) : __('Search Swedish fika places...', 'fika-register');
$button_text = isset($atts['button_text']) ? esc_html($atts['button_text']) : __('Search', 'fika-register');
$show_city_filter = isset($atts['show_city_filter']) ? ($atts['show_city_filter'] === 'true') : true;

$cities = array(
    '' => __('All Cities', 'fika-register'),
    'stockholm' => 'Stockholm',
    'gothenburg' => 'Gothenburg',
    'malmo' => 'Malmö',
    'uppsala' => 'Uppsala',
    'vasteras' => 'Västerås'
);
?>

<div class="fika-search-container">
    <form class="fika-search-form" role="search">
        <div class="fika-search-input-group">
            <label for="fika-search-input" class="fika-sr-only">
                <?php _e('Search for fika places', 'fika-register'); ?>
            </label>
            <input 
                type="text" 
                id="fika-search-input"
                class="fika-search-input" 
                placeholder="<?php echo $placeholder; ?>"
                name="fika_query"
                autocomplete="off"
            >
            
            <?php if ($show_city_filter) : ?>
                <div class="fika-city-filter">
                    <label for="fika-city-select" class="fika-sr-only">
                        <?php _e('Filter by city', 'fika-register'); ?>
                    </label>
                    <select id="fika-city-select" name="fika_city">
                        <?php foreach ($cities as $value => $label) : ?>
                            <option value="<?php echo esc_attr($value); ?>"><?php echo esc_html($label); ?></option>
                        <?php endforeach; ?>
                    </select>
                </div>
            <?php endif; ?>
        </div>
        
        <button type="submit" class="fika-search-button">
            <span><?php echo $button_text; ?></span>
        </button>
    </form>
    
    <div class="fika-search-results" aria-live="polite" aria-label="<?php _e('Search results', 'fika-register'); ?>">
        <!-- Search results will be loaded here -->
    </div>
</div>

<script type="application/ld+json">
{
    "@context": "https://schema.org",
    "@type": "WebSite",
    "url": "<?php echo home_url(); ?>",
    "potentialAction": {
        "@type": "SearchAction",
        "target": "<?php echo home_url(); ?>/?s={search_term_string}",
        "query-input": "required name=search_term_string"
    }
}
</script>