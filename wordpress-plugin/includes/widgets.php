<?php
/**
 * WordPress Widgets for Fika Register Plugin
 */

// Prevent direct access
if (!defined('ABSPATH')) {
    exit;
}

/**
 * Fika Search Widget
 */
class Fika_Search_Widget extends WP_Widget {
    
    public function __construct() {
        parent::__construct(
            'fika_search_widget',
            __('Fika Search', 'fika-register'),
            array(
                'description' => __('Display a search form for Swedish fika locations', 'fika-register'),
                'classname' => 'fika-search-widget'
            )
        );
    }
    
    public function widget($args, $instance) {
        $title = !empty($instance['title']) ? $instance['title'] : __('Search Fika Places', 'fika-register');
        $placeholder = !empty($instance['placeholder']) ? $instance['placeholder'] : __('Search fika places...', 'fika-register');
        $show_city_filter = isset($instance['show_city_filter']) ? (bool)$instance['show_city_filter'] : true;
        
        echo $args['before_widget'];
        
        if ($title) {
            echo $args['before_title'] . apply_filters('widget_title', $title) . $args['after_title'];
        }
        
        // Display search form
        $atts = array(
            'placeholder' => $placeholder,
            'show_city_filter' => $show_city_filter ? 'true' : 'false',
            'button_text' => __('Search', 'fika-register')
        );
        
        ob_start();
        include FIKA_PLUGIN_PATH . 'templates/search-form.php';
        echo ob_get_clean();
        
        echo $args['after_widget'];
    }
    
    public function form($instance) {
        $title = isset($instance['title']) ? $instance['title'] : __('Search Fika Places', 'fika-register');
        $placeholder = isset($instance['placeholder']) ? $instance['placeholder'] : __('Search fika places...', 'fika-register');
        $show_city_filter = isset($instance['show_city_filter']) ? (bool)$instance['show_city_filter'] : true;
        ?>
        
        <p>
            <label for="<?php echo esc_attr($this->get_field_id('title')); ?>">
                <?php _e('Title:', 'fika-register'); ?>
            </label>
            <input 
                class="widefat" 
                id="<?php echo esc_attr($this->get_field_id('title')); ?>" 
                name="<?php echo esc_attr($this->get_field_name('title')); ?>" 
                type="text" 
                value="<?php echo esc_attr($title); ?>"
            >
        </p>
        
        <p>
            <label for="<?php echo esc_attr($this->get_field_id('placeholder')); ?>">
                <?php _e('Placeholder Text:', 'fika-register'); ?>
            </label>
            <input 
                class="widefat" 
                id="<?php echo esc_attr($this->get_field_id('placeholder')); ?>" 
                name="<?php echo esc_attr($this->get_field_name('placeholder')); ?>" 
                type="text" 
                value="<?php echo esc_attr($placeholder); ?>"
            >
        </p>
        
        <p>
            <input 
                class="checkbox" 
                type="checkbox" 
                <?php checked($show_city_filter); ?> 
                id="<?php echo esc_attr($this->get_field_id('show_city_filter')); ?>" 
                name="<?php echo esc_attr($this->get_field_name('show_city_filter')); ?>"
            >
            <label for="<?php echo esc_attr($this->get_field_id('show_city_filter')); ?>">
                <?php _e('Show city filter', 'fika-register'); ?>
            </label>
        </p>
        
        <?php
    }
    
    public function update($new_instance, $old_instance) {
        $instance = array();
        $instance['title'] = (!empty($new_instance['title'])) ? sanitize_text_field($new_instance['title']) : '';
        $instance['placeholder'] = (!empty($new_instance['placeholder'])) ? sanitize_text_field($new_instance['placeholder']) : '';
        $instance['show_city_filter'] = !empty($new_instance['show_city_filter']);
        
        return $instance;
    }
}

/**
 * Fika Featured Widget
 */
class Fika_Featured_Widget extends WP_Widget {
    
    public function __construct() {
        parent::__construct(
            'fika_featured_widget',
            __('Featured Fika Places', 'fika-register'),
            array(
                'description' => __('Display featured Swedish fika locations', 'fika-register'),
                'classname' => 'fika-featured-widget'
            )
        );
    }
    
    public function widget($args, $instance) {
        $title = !empty($instance['title']) ? $instance['title'] : __('Featured Fika', 'fika-register');
        $limit = !empty($instance['limit']) ? intval($instance['limit']) : 3;
        $show_description = isset($instance['show_description']) ? (bool)$instance['show_description'] : true;
        $city = !empty($instance['city']) ? $instance['city'] : '';
        
        echo $args['before_widget'];
        
        if ($title) {
            echo $args['before_title'] . apply_filters('widget_title', $title) . $args['after_title'];
        }
        
        // Get featured places
        $places = $this->get_widget_places($city, $limit);
        
        if ($places && !empty($places['places'])) {
            echo '<div class="fika-widget fika-featured-widget-content">';
            
            foreach ($places['places'] as $place) {
                $this->render_place_item($place, $show_description);
            }
            
            echo '</div>';
            
            // View all link
            if (isset($places['total']) && $places['total'] > $limit) {
                $view_all_url = $city ? 
                    home_url('/fika-places/?city=' . urlencode($city)) : 
                    home_url('/fika-places/?featured=true');
                
                echo '<p class="fika-widget-footer">';
                echo '<a href="' . esc_url($view_all_url) . '" class="fika-view-all-small">';
                echo __('View all →', 'fika-register');
                echo '</a>';
                echo '</p>';
            }
        } else {
            echo '<div class="fika-widget-loading" data-widget-type="featured" data-widget-settings="' . esc_attr(json_encode(compact('city', 'limit', 'show_description'))) . '">';
            echo '<p>' . __('Loading fika places...', 'fika-register') . '</p>';
            echo '</div>';
        }
        
        echo $args['after_widget'];
    }
    
    private function render_place_item($place, $show_description = true) {
        $rating = isset($place['rating']) ? floatval($place['rating']) : 0;
        ?>
        <div class="fika-widget-item" data-place-id="<?php echo esc_attr($place['id']); ?>">
            <h5 class="fika-widget-place-title"><?php echo esc_html($place['name']); ?></h5>
            
            <div class="fika-widget-place-meta">
                <span class="fika-widget-location">📍 <?php echo esc_html($place['city']); ?></span>
                <?php if ($rating > 0) : ?>
                    <span class="fika-widget-rating">
                        <span class="fika-stars">
                            <?php echo str_repeat('★', floor($rating)) . str_repeat('☆', 5 - floor($rating)); ?>
                        </span>
                        <small>(<?php echo number_format($rating, 1); ?>)</small>
                    </span>
                <?php endif; ?>
            </div>
            
            <?php if ($show_description && !empty($place['description'])) : ?>
                <p class="fika-widget-description">
                    <?php 
                    $description = $place['description'];
                    echo esc_html(strlen($description) > 80 ? substr($description, 0, 80) . '...' : $description); 
                    ?>
                </p>
            <?php endif; ?>
            
            <?php 
            $features = $place['features'] ?? $place['fika_specialties'] ?? [];
            if (!empty($features)) : 
            ?>
                <div class="fika-widget-features">
                    <?php foreach (array_slice($features, 0, 2) as $feature) : ?>
                        <small class="fika-feature-tag"><?php echo esc_html($feature); ?></small>
                    <?php endforeach; ?>
                </div>
            <?php endif; ?>
        </div>
        <?php
    }
    
    private function get_widget_places($city = '', $limit = 3) {
        // This would normally use the API client
        // For now, return sample data or empty array
        return false;
    }
    
    public function form($instance) {
        $title = isset($instance['title']) ? $instance['title'] : __('Featured Fika', 'fika-register');
        $limit = isset($instance['limit']) ? intval($instance['limit']) : 3;
        $show_description = isset($instance['show_description']) ? (bool)$instance['show_description'] : true;
        $city = isset($instance['city']) ? $instance['city'] : '';
        
        $cities = array(
            '' => __('All Cities', 'fika-register'),
            'stockholm' => 'Stockholm',
            'gothenburg' => 'Gothenburg',
            'malmo' => 'Malmö',
            'uppsala' => 'Uppsala',
            'vasteras' => 'Västerås'
        );
        ?>
        
        <p>
            <label for="<?php echo esc_attr($this->get_field_id('title')); ?>">
                <?php _e('Title:', 'fika-register'); ?>
            </label>
            <input 
                class="widefat" 
                id="<?php echo esc_attr($this->get_field_id('title')); ?>" 
                name="<?php echo esc_attr($this->get_field_name('title')); ?>" 
                type="text" 
                value="<?php echo esc_attr($title); ?>"
            >
        </p>
        
        <p>
            <label for="<?php echo esc_attr($this->get_field_id('city')); ?>">
                <?php _e('City:', 'fika-register'); ?>
            </label>
            <select 
                class="widefat" 
                id="<?php echo esc_attr($this->get_field_id('city')); ?>" 
                name="<?php echo esc_attr($this->get_field_name('city')); ?>"
            >
                <?php foreach ($cities as $value => $label) : ?>
                    <option value="<?php echo esc_attr($value); ?>" <?php selected($city, $value); ?>>
                        <?php echo esc_html($label); ?>
                    </option>
                <?php endforeach; ?>
            </select>
        </p>
        
        <p>
            <label for="<?php echo esc_attr($this->get_field_id('limit')); ?>">
                <?php _e('Number of places:', 'fika-register'); ?>
            </label>
            <input 
                class="tiny-text" 
                id="<?php echo esc_attr($this->get_field_id('limit')); ?>" 
                name="<?php echo esc_attr($this->get_field_name('limit')); ?>" 
                type="number" 
                min="1" 
                max="10" 
                value="<?php echo esc_attr($limit); ?>"
            >
        </p>
        
        <p>
            <input 
                class="checkbox" 
                type="checkbox" 
                <?php checked($show_description); ?> 
                id="<?php echo esc_attr($this->get_field_id('show_description')); ?>" 
                name="<?php echo esc_attr($this->get_field_name('show_description')); ?>"
            >
            <label for="<?php echo esc_attr($this->get_field_id('show_description')); ?>">
                <?php _e('Show descriptions', 'fika-register'); ?>
            </label>
        </p>
        
        <?php
    }
    
    public function update($new_instance, $old_instance) {
        $instance = array();
        $instance['title'] = (!empty($new_instance['title'])) ? sanitize_text_field($new_instance['title']) : '';
        $instance['city'] = (!empty($new_instance['city'])) ? sanitize_text_field($new_instance['city']) : '';
        $instance['limit'] = (!empty($new_instance['limit'])) ? intval($new_instance['limit']) : 3;
        $instance['show_description'] = !empty($new_instance['show_description']);
        
        return $instance;
    }
}

// Widget styles
add_action('wp_head', function() {
    ?>
    <style>
    .fika-widget .fika-widget-item {
        margin-bottom: 16px;
        padding-bottom: 16px;
        border-bottom: 1px solid var(--fika-border, #E5E7EB);
    }
    
    .fika-widget .fika-widget-item:last-child {
        border-bottom: none;
        margin-bottom: 0;
    }
    
    .fika-widget-place-title {
        color: var(--fika-blue, #004B87);
        font-size: 14px;
        font-weight: 600;
        margin: 0 0 4px 0;
    }
    
    .fika-widget-place-meta {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 8px;
        font-size: 12px;
    }
    
    .fika-widget-location {
        color: var(--fika-text-light, #6B7280);
    }
    
    .fika-widget-rating .fika-stars {
        color: var(--fika-yellow, #FECC02);
    }
    
    .fika-widget-description {
        font-size: 12px;
        line-height: 1.4;
        color: var(--fika-text, #2C2C2C);
        margin-bottom: 8px;
    }
    
    .fika-widget-features .fika-feature-tag {
        background: var(--fika-beige, #F5E6D3);
        color: var(--fika-text, #2C2C2C);
        padding: 2px 6px;
        border-radius: 3px;
        font-size: 10px;
        font-weight: 500;
        margin-right: 4px;
    }
    
    .fika-widget-footer {
        text-align: center;
        margin-top: 12px;
        padding-top: 12px;
        border-top: 1px solid var(--fika-border, #E5E7EB);
    }
    
    .fika-view-all-small {
        color: var(--fika-blue, #004B87);
        text-decoration: none;
        font-size: 12px;
        font-weight: 500;
    }
    
    .fika-view-all-small:hover {
        text-decoration: underline;
    }
    
    .fika-widget-loading {
        text-align: center;
        padding: 20px;
        color: var(--fika-text-light, #6B7280);
        font-size: 12px;
    }
    </style>
    <?php
});
?>