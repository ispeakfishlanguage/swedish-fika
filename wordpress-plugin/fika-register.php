<?php
/**
 * Plugin Name: Traditional Swedish Fika Register
 * Description: Display Swedish fika locations from your FastAPI backend in WordPress
 * Version: 1.0.0
 * Author: Traditional Swedish Fika
 * License: MIT
 * Text Domain: fika-register
 */

// Prevent direct access
if (!defined('ABSPATH')) {
    exit;
}

// Define plugin constants
define('FIKA_PLUGIN_URL', plugin_dir_url(__FILE__));
define('FIKA_PLUGIN_PATH', plugin_dir_path(__FILE__));
define('FIKA_VERSION', '1.0.0');

class FikaRegisterPlugin {
    
    public function __construct() {
        add_action('init', array($this, 'init'));
        add_action('wp_enqueue_scripts', array($this, 'enqueue_scripts'));
        add_action('admin_menu', array($this, 'admin_menu'));
        add_action('admin_init', array($this, 'admin_init'));
        
        // Register shortcodes
        add_shortcode('fika-search', array($this, 'search_shortcode'));
        add_shortcode('fika-city', array($this, 'city_shortcode'));
        add_shortcode('fika-featured', array($this, 'featured_shortcode'));
        
        // Register AJAX handlers
        add_action('wp_ajax_fika_search', array($this, 'ajax_search'));
        add_action('wp_ajax_nopriv_fika_search', array($this, 'ajax_search'));
        
        // Register widgets
        add_action('widgets_init', array($this, 'register_widgets'));
    }
    
    public function init() {
        // Load text domain for translations
        load_plugin_textdomain('fika-register', false, dirname(plugin_basename(__FILE__)) . '/languages');
    }
    
    public function enqueue_scripts() {
        wp_enqueue_style('fika-styles', FIKA_PLUGIN_URL . 'assets/css/fika-styles.css', array(), FIKA_VERSION);
        wp_enqueue_script('fika-script', FIKA_PLUGIN_URL . 'assets/js/fika-search.js', array('jquery'), FIKA_VERSION, true);
        
        // Pass settings to JavaScript
        wp_localize_script('fika-script', 'fikaAjax', array(
            'ajax_url' => admin_url('admin-ajax.php'),
            'nonce' => wp_create_nonce('fika_nonce'),
            'api_url' => get_option('fika_api_url', 'https://your-fika-app.ondigitalocean.app/api'),
            'loading_text' => __('Loading fika places...', 'fika-register'),
            'error_text' => __('Error loading fika places', 'fika-register')
        ));
    }
    
    public function admin_menu() {
        add_options_page(
            __('Fika Register Settings', 'fika-register'),
            __('Fika Register', 'fika-register'),
            'manage_options',
            'fika-register',
            array($this, 'admin_page')
        );
    }
    
    public function admin_init() {
        register_setting('fika_register_settings', 'fika_api_url');
        register_setting('fika_register_settings', 'fika_cache_time');
        register_setting('fika_register_settings', 'fika_default_city');
        
        add_settings_section(
            'fika_api_section',
            __('API Settings', 'fika-register'),
            null,
            'fika-register'
        );
        
        add_settings_field(
            'fika_api_url',
            __('API Base URL', 'fika-register'),
            array($this, 'api_url_field'),
            'fika-register',
            'fika_api_section'
        );
        
        add_settings_field(
            'fika_cache_time',
            __('Cache Time (minutes)', 'fika-register'),
            array($this, 'cache_time_field'),
            'fika-register',
            'fika_api_section'
        );
        
        add_settings_field(
            'fika_default_city',
            __('Default City', 'fika-register'),
            array($this, 'default_city_field'),
            'fika-register',
            'fika_api_section'
        );
    }
    
    public function admin_page() {
        ?>
        <div class="wrap">
            <h1><?php _e('Fika Register Settings', 'fika-register'); ?></h1>
            <form method="post" action="options.php">
                <?php
                settings_fields('fika_register_settings');
                do_settings_sections('fika-register');
                submit_button();
                ?>
            </form>
            
            <div class="fika-test-connection">
                <h3><?php _e('Test API Connection', 'fika-register'); ?></h3>
                <button type="button" id="test-fika-connection" class="button">
                    <?php _e('Test Connection', 'fika-register'); ?>
                </button>
                <div id="connection-result"></div>
            </div>
        </div>
        
        <script>
        jQuery(document).ready(function($) {
            $('#test-fika-connection').click(function() {
                var $button = $(this);
                var $result = $('#connection-result');
                
                $button.prop('disabled', true).text('<?php _e('Testing...', 'fika-register'); ?>');
                $result.html('<p><?php _e('Testing connection...', 'fika-register'); ?></p>');
                
                $.ajax({
                    url: fikaAjax.ajax_url,
                    method: 'POST',
                    data: {
                        action: 'fika_test_connection',
                        nonce: fikaAjax.nonce
                    },
                    success: function(response) {
                        if (response.success) {
                            $result.html('<p style="color: green;"><?php _e('✅ Connection successful!', 'fika-register'); ?></p>');
                        } else {
                            $result.html('<p style="color: red;">❌ ' + response.data + '</p>');
                        }
                    },
                    error: function() {
                        $result.html('<p style="color: red;"><?php _e('❌ Connection failed', 'fika-register'); ?></p>');
                    },
                    complete: function() {
                        $button.prop('disabled', false).text('<?php _e('Test Connection', 'fika-register'); ?>');
                    }
                });
            });
        });
        </script>
        <?php
    }
    
    public function api_url_field() {
        $value = get_option('fika_api_url', 'https://your-fika-app.ondigitalocean.app/api');
        echo '<input type="url" name="fika_api_url" value="' . esc_attr($value) . '" class="regular-text" />';
        echo '<p class="description">' . __('Base URL of your Fika Register API', 'fika-register') . '</p>';
    }
    
    public function cache_time_field() {
        $value = get_option('fika_cache_time', '30');
        echo '<input type="number" name="fika_cache_time" value="' . esc_attr($value) . '" min="1" max="1440" />';
        echo '<p class="description">' . __('How long to cache API responses (1-1440 minutes)', 'fika-register') . '</p>';
    }
    
    public function default_city_field() {
        $value = get_option('fika_default_city', 'stockholm');
        $cities = array(
            'stockholm' => 'Stockholm',
            'gothenburg' => 'Gothenburg',
            'malmo' => 'Malmö',
            'uppsala' => 'Uppsala',
            'vasteras' => 'Västerås'
        );
        
        echo '<select name="fika_default_city">';
        foreach ($cities as $key => $label) {
            echo '<option value="' . esc_attr($key) . '"' . selected($value, $key, false) . '>' . esc_html($label) . '</option>';
        }
        echo '</select>';
    }
    
    // Shortcode: [fika-search]
    public function search_shortcode($atts) {
        $atts = shortcode_atts(array(
            'placeholder' => __('Search Swedish fika places...', 'fika-register'),
            'button_text' => __('Search', 'fika-register'),
            'show_city_filter' => 'true'
        ), $atts);
        
        ob_start();
        include FIKA_PLUGIN_PATH . 'templates/search-form.php';
        return ob_get_clean();
    }
    
    // Shortcode: [fika-city city="stockholm" limit="6"]
    public function city_shortcode($atts) {
        $atts = shortcode_atts(array(
            'city' => get_option('fika_default_city', 'stockholm'),
            'limit' => '6',
            'show_description' => 'true',
            'show_rating' => 'true'
        ), $atts);
        
        $places = $this->get_city_places($atts['city'], $atts['limit']);
        
        ob_start();
        include FIKA_PLUGIN_PATH . 'templates/city-places.php';
        return ob_get_clean();
    }
    
    // Shortcode: [fika-featured limit="3"]
    public function featured_shortcode($atts) {
        $atts = shortcode_atts(array(
            'limit' => '3',
            'show_description' => 'true'
        ), $atts);
        
        $places = $this->get_featured_places($atts['limit']);
        
        ob_start();
        include FIKA_PLUGIN_PATH . 'templates/featured-places.php';
        return ob_get_clean();
    }
    
    public function ajax_search() {
        check_ajax_referer('fika_nonce', 'nonce');
        
        $query = sanitize_text_field($_POST['query'] ?? '');
        $city = sanitize_text_field($_POST['city'] ?? '');
        
        if (empty($query) && empty($city)) {
            wp_send_json_error(__('Please provide a search query or city', 'fika-register'));
        }
        
        $results = $this->search_places($query, $city);
        
        if ($results === false) {
            wp_send_json_error(__('Failed to search places', 'fika-register'));
        }
        
        wp_send_json_success($results);
    }
    
    public function register_widgets() {
        register_widget('Fika_Search_Widget');
        register_widget('Fika_Featured_Widget');
    }
    
    // API Helper Methods
    private function api_request($endpoint, $params = array()) {
        $api_url = get_option('fika_api_url');
        if (empty($api_url)) {
            return false;
        }
        
        $cache_key = 'fika_api_' . md5($endpoint . serialize($params));
        $cache_time = get_option('fika_cache_time', 30) * MINUTE_IN_SECONDS;
        
        // Try to get from cache first
        $cached = get_transient($cache_key);
        if ($cached !== false) {
            return $cached;
        }
        
        $url = rtrim($api_url, '/') . '/' . ltrim($endpoint, '/');
        if (!empty($params)) {
            $url .= '?' . http_build_query($params);
        }
        
        $response = wp_remote_get($url, array(
            'timeout' => 30,
            'headers' => array(
                'User-Agent' => 'WordPress Fika Plugin/' . FIKA_VERSION
            )
        ));
        
        if (is_wp_error($response)) {
            return false;
        }
        
        $body = wp_remote_retrieve_body($response);
        $data = json_decode($body, true);
        
        if (json_last_error() !== JSON_ERROR_NONE) {
            return false;
        }
        
        // Cache successful responses
        if (wp_remote_retrieve_response_code($response) === 200) {
            set_transient($cache_key, $data, $cache_time);
        }
        
        return $data;
    }
    
    private function get_city_places($city, $limit = 6) {
        return $this->api_request('places', array(
            'city' => $city,
            'per_page' => $limit
        ));
    }
    
    private function get_featured_places($limit = 3) {
        return $this->api_request('places', array(
            'verified_only' => 'true',
            'per_page' => $limit
        ));
    }
    
    private function search_places($query, $city = '') {
        $params = array('per_page' => 20);
        
        if (!empty($query)) {
            $params['query'] = $query;
        }
        if (!empty($city)) {
            $params['city'] = $city;
        }
        
        return $this->api_request('places/search', $params);
    }
}

// Initialize the plugin
new FikaRegisterPlugin();

// Include widget classes
require_once FIKA_PLUGIN_PATH . 'includes/widgets.php';
?>