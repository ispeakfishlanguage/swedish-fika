<?php
/**
 * The base configuration for WordPress
 *
 * The wp-config.php creation script uses this file during the installation.
 * You don't have to use the web site, you can copy this file to "wp-config.php"
 * and fill in the values.
 *
 * This file contains the following configurations:
 *
 * * Database settings
 * * Secret keys
 * * Database table prefix
 * * Localized language
 * * ABSPATH
 *
 * @link https://wordpress.org/support/article/editing-wp-config-php/
 *
 * @package WordPress
 */

// ** Database settings - You can get this info from your web host ** //
/** The name of the database for WordPress */
define( 'DB_NAME', 'local' );

/** Database username */
define( 'DB_USER', 'root' );

/** Database password */
define( 'DB_PASSWORD', 'root' );

/** Database hostname */
define( 'DB_HOST', 'localhost' );

/** Database charset to use in creating database tables. */
define( 'DB_CHARSET', 'utf8' );

/** The database collate type. Don't change this if in doubt. */
define( 'DB_COLLATE', '' );

/**#@+
 * Authentication unique keys and salts.
 *
 * Change these to different unique phrases! You can generate these using
 * the {@link https://api.wordpress.org/secret-key/1.1/salt/ WordPress.org secret-key service}.
 *
 * You can change these at any point in time to invalidate all existing cookies.
 * This will force all users to have to log in again.
 *
 * @since 2.6.0
 */
define( 'AUTH_KEY',          'i:Ih4/CcY!2uKz2&W}I[HsuQ t7NqSn}u(bXFwH6|%4H<B^Rn?^0jU_r+VXvlpC%' );
define( 'SECURE_AUTH_KEY',   '#XG#zBkv)--9]MD#e !oTJVG&Cvmzs9IJhk_#u.fvA%W^( kW@im&I<{4i.410`3' );
define( 'LOGGED_IN_KEY',     '{mkUT!o4bB3tgV<mXzD6hp=ptZ^,#!h?@LVFE&Z]nsR(12I._KIJ!NO`ir_-mIGI' );
define( 'NONCE_KEY',         '?vWCA{YBc>w-t@*63[,=_dEr[XZCH(`>d[)jiGx#(_1`qDz*LpOZk!HY5wcd7o6w' );
define( 'AUTH_SALT',         'ET!KjdeWMr[y6gl^%KUw,u[QN1nh[qsa~]Cyyc;vk]ZIq5r/[d`c9aM{6Vaq)w)O' );
define( 'SECURE_AUTH_SALT',  'FP&J~uWFlkbq=,~K[Fl]8`.^-8Ag<5/Ke_h})O2c^_~/<#PqjmF5xm2$z!EM!2B/' );
define( 'LOGGED_IN_SALT',    's>u`!9l_ARB4kVr^@0TgY[[ ^jKKHxgUCwf:?$Z&|q/Ek ~A[#i7voO78Av<he;D' );
define( 'NONCE_SALT',        ',~5Vj]mTMW-:#F?Jg?D[Rqo=4o$~0D_*2`oUFav]9j$^31&~iu*U8V%n)SF~glnd' );
define( 'WP_CACHE_KEY_SALT', 'Xwlw&)BG=myyl(T<HJ-+ e!O|>c-[c(B>%m&DdCS;YnE/=1tygEh^@w[!Lw3}bml' );


/**#@-*/

/**
 * WordPress database table prefix.
 *
 * You can have multiple installations in one database if you give each
 * a unique prefix. Only numbers, letters, and underscores please!
 */
$table_prefix = 'wp_';


/* Add any custom values between this line and the "stop editing" line. */



/**
 * For developers: WordPress debugging mode.
 *
 * Change this to true to enable the display of notices during development.
 * It is strongly recommended that plugin and theme developers use WP_DEBUG
 * in their development environments.
 *
 * For information on other constants that can be used for debugging,
 * visit the documentation.
 *
 * @link https://wordpress.org/support/article/debugging-in-wordpress/
 */
if ( ! defined( 'WP_DEBUG' ) ) {
	define( 'WP_DEBUG', false );
}

define( 'WP_ENVIRONMENT_TYPE', 'local' );
/* That's all, stop editing! Happy publishing. */

/** Absolute path to the WordPress directory. */
if ( ! defined( 'ABSPATH' ) ) {
	define( 'ABSPATH', __DIR__ . '/' );
}

/** Sets up WordPress vars and included files. */
require_once ABSPATH . 'wp-settings.php';
