=== Traditional Swedish Fika Register ===
Contributors: traditionalswedishfika
Tags: fika, swedish, cafe, restaurant, directory, search, widget
Requires at least: 5.0
Tested up to: 6.4
Requires PHP: 7.4
Stable tag: 1.0.0
License: MIT
License URI: https://opensource.org/licenses/MIT

Display Swedish fika locations from your Traditional Swedish Fika Register on your WordPress site.

== Description ==

The Traditional Swedish Fika Register plugin allows you to integrate authentic Swedish fika locations into your WordPress site. Connect to your FastAPI backend to display searchable fika places across Sweden's major cities.

**Features:**

* **Shortcodes**: Easy integration with `[fika-search]`, `[fika-city]`, and `[fika-featured]`
* **Widgets**: Search and featured places widgets for sidebars
* **City-based Discovery**: Showcase fika spots in Stockholm, Gothenburg, Malmö, Uppsala, and Västerås
* **Smart Search**: Ajax-powered search with Swedish language support
* **Responsive Design**: Mobile-friendly components that work with any theme
* **SEO Optimized**: Structured data markup for better search engine visibility
* **Caching**: Built-in caching for optimal performance

**What is Fika?**

Fika is more than just a coffee break – it's a Swedish cultural institution that celebrates slowing down, connecting with others, and savoring life's simple pleasures with coffee and traditional pastries.

== Installation ==

1. Upload the plugin files to `/wp-content/plugins/fika-register/`
2. Activate the plugin through the 'Plugins' screen in WordPress
3. Configure your API settings in Settings > Fika Register
4. Use shortcodes or widgets to display fika locations

== Configuration ==

After activation, go to **Settings > Fika Register** to configure:

* **API Base URL**: URL of your Traditional Swedish Fika Register backend
* **Cache Time**: How long to cache API responses (improves performance)
* **Default City**: Default city to display when none specified

== Shortcodes ==

**Search Form**
`[fika-search placeholder="Sök fika-ställen..." show_city_filter="true"]`

**City Places**
`[fika-city city="stockholm" limit="6" show_description="true"]`

**Featured Places**
`[fika-featured limit="3" show_description="true"]`

**Available Cities:**
* stockholm
* gothenburg 
* malmo
* uppsala
* vasteras

== Widgets ==

**Fika Search Widget**
- Search form for sidebars
- Configurable placeholder text
- Optional city filter

**Featured Fika Places Widget**
- Display featured locations
- Filter by specific city
- Configurable number of places

== Frequently Asked Questions ==

= Do I need a separate backend service? =

Yes, this plugin connects to a Traditional Swedish Fika Register API backend. You can deploy your own using the provided FastAPI application.

= Can I customize the styling? =

Yes, the plugin uses CSS custom properties that you can override in your theme. All components use semantic class names for easy styling.

= Does it work with any WordPress theme? =

Yes, the plugin is designed to work with any properly coded WordPress theme. It uses progressive enhancement and doesn't require any specific theme features.

= Is it mobile-friendly? =

Yes, all components are responsive and mobile-optimized with proper touch targets and accessible interactions.

= Can I translate the plugin? =

Yes, the plugin is translation-ready with the `fika-register` text domain. Swedish translations are included.

== Screenshots ==

1. Search form with city filter
2. Featured fika places grid
3. City-specific fika locations
4. Admin settings page
5. Widget configuration

== Changelog ==

= 1.0.0 =
* Initial release
* Search functionality with city filtering
* Featured places display
* City-specific place listings
* WordPress widgets
* Admin settings panel
* SEO optimization with structured data
* Responsive design
* Caching support

== Upgrade Notice ==

= 1.0.0 =
First release of the Traditional Swedish Fika Register WordPress plugin.

== Technical Requirements ==

* WordPress 5.0+
* PHP 7.4+
* cURL support
* JavaScript enabled for search functionality

== API Backend ==

This plugin requires the Traditional Swedish Fika Register backend API. You can:

1. **Deploy your own**: Use the provided FastAPI application
2. **Use hosted service**: Connect to a deployed instance on Digital Ocean
3. **Development**: Run locally with Docker for testing

The backend provides:
* RESTful API for fika locations
* Search functionality
* City-based filtering
* Featured places endpoint
* Health checks and monitoring

== Support ==

For support and bug reports, please visit the plugin repository or contact the developers.

== Credits ==

Built with ❤️ for authentic Swedish fika experiences.

* **Swedish Fika Culture**: Traditional practices and locations
* **FastAPI**: Modern Python web framework
* **WordPress**: Content management platform

---

*"Fika is a concept, a state of mind, an attitude and an important part of Swedish culture. Many Swedes consider that it is almost essential to make time for fika every day."*