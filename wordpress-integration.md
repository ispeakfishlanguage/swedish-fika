# WordPress Integration Guide - Traditional Swedish Fika Register

There are several ways to integrate the Traditional Swedish Fika Register with WordPress. Choose the approach that best fits your needs.

## Option 1: WordPress Plugin (Recommended)

Create a custom plugin that connects to your FastAPI backend and displays fika locations on your WordPress site.

### Plugin Structure
```
fika-register-plugin/
├── fika-register.php          # Main plugin file
├── includes/
│   ├── api-client.php         # FastAPI backend connection
│   ├── shortcodes.php         # WordPress shortcodes
│   └── widgets.php            # WordPress widgets
├── assets/
│   ├── css/fika-styles.css    # Plugin styles
│   └── js/fika-search.js      # Search functionality
└── templates/
    ├── search-form.php        # Search form template
    └── location-card.php      # Location display template
```

### Features
- **Shortcodes**: `[fika-search]`, `[fika-city city="stockholm"]`
- **Widgets**: Fika location widget for sidebars
- **Custom Post Type**: Store favorite fika locations in WordPress
- **Admin Panel**: Configure API settings

## Option 2: Iframe Embedding

Embed your existing application directly into WordPress pages.

### Simple Iframe
```html
<iframe 
    src="https://your-fika-app.ondigitalocean.app" 
    width="100%" 
    height="800px" 
    frameborder="0"
    title="Swedish Fika Register">
</iframe>
```

### Responsive Iframe with JavaScript
```javascript
// Auto-resize iframe based on content
function resizeFikaFrame() {
    const iframe = document.getElementById('fika-iframe');
    iframe.style.height = iframe.contentWindow.document.body.scrollHeight + 'px';
}
```

## Option 3: WordPress Theme Integration

Modify your WordPress theme to include fika functionality directly.

### Theme Functions
Add to your theme's `functions.php`:

```php
// Enqueue fika scripts and styles
function fika_enqueue_scripts() {
    wp_enqueue_script('fika-search', get_template_directory_uri() . '/js/fika-search.js', array('jquery'));
    wp_enqueue_style('fika-styles', get_template_directory_uri() . '/css/fika-styles.css');
    
    // Pass API URL to JavaScript
    wp_localize_script('fika-search', 'fikaAPI', array(
        'url' => 'https://your-fika-app.ondigitalocean.app/api',
        'nonce' => wp_create_nonce('fika_nonce')
    ));
}
add_action('wp_enqueue_scripts', 'fika_enqueue_scripts');
```

## Option 4: Headless WordPress + React/Vue

Use WordPress as a headless CMS with your fika application as the frontend.

### Benefits
- WordPress admin for content management
- Your existing frontend for fika functionality
- Best of both worlds

### Architecture
```
WordPress (Headless) → REST API → Your Fika App → Display
```

## Recommended Approach: WordPress Plugin

I'll create a complete WordPress plugin for you that integrates with your FastAPI backend.

### Plugin Requirements
- PHP 7.4+
- WordPress 5.0+
- cURL support
- Your FastAPI backend deployed and accessible

### Installation Steps
1. Upload plugin to `/wp-content/plugins/`
2. Activate in WordPress admin
3. Configure API settings
4. Use shortcodes or widgets on your pages

### Shortcode Examples
```
[fika-search placeholder="Sök fika-ställen..."]
[fika-city city="stockholm" limit="6"]
[fika-featured limit="3"]
[fika-random city="gothenburg"]
```

### Widget Areas
- Sidebar fika search
- Footer fika locations
- Header featured spots

Would you like me to create the complete WordPress plugin, or would you prefer one of the other integration approaches?