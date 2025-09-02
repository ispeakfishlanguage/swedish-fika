-- Traditional Swedish Fika Database Schema
-- Initial setup for PostgreSQL database

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "postgis" SCHEMA public;
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- Create categories table
CREATE TABLE categories (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(100) NOT NULL UNIQUE,
    description TEXT,
    icon VARCHAR(50),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create places table
CREATE TABLE places (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,
    description TEXT,
    address VARCHAR(500),
    city VARCHAR(100) NOT NULL,
    region VARCHAR(100),
    
    -- Geographic coordinates
    latitude DECIMAL(10, 8),
    longitude DECIMAL(11, 8),
    
    -- Contact information
    phone VARCHAR(50),
    website VARCHAR(255),
    
    -- Business details
    opening_hours JSONB,
    fika_specialties TEXT[],
    price_range INTEGER CHECK (price_range >= 1 AND price_range <= 4),
    
    -- Ratings and verification
    rating DECIMAL(3, 2) CHECK (rating >= 0 AND rating <= 5),
    review_count INTEGER DEFAULT 0,
    verified BOOLEAN DEFAULT FALSE,
    
    -- Additional features
    features TEXT[],
    images TEXT[],
    
    -- SEO and metadata
    slug VARCHAR(255) UNIQUE,
    meta_description TEXT,
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create reviews table
CREATE TABLE reviews (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    place_id UUID REFERENCES places(id) ON DELETE CASCADE,
    
    -- Reviewer information
    user_name VARCHAR(100),
    
    -- Review content
    rating INTEGER NOT NULL CHECK (rating >= 1 AND rating <= 5),
    comment TEXT,
    fika_items TEXT[],
    
    -- Visit details
    visit_date DATE,
    visit_time VARCHAR(20) CHECK (visit_time IN ('morning', 'afternoon', 'evening')),
    
    -- Moderation
    moderated INTEGER DEFAULT 0 CHECK (moderated IN (-1, 0, 1)), -- -1: rejected, 0: pending, 1: approved
    moderated_at TIMESTAMP WITH TIME ZONE,
    
    -- Additional fields
    helpful_count INTEGER DEFAULT 0,
    language VARCHAR(10) DEFAULT 'sv',
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create place_categories junction table
CREATE TABLE place_categories (
    place_id UUID REFERENCES places(id) ON DELETE CASCADE,
    category_id UUID REFERENCES categories(id) ON DELETE CASCADE,
    PRIMARY KEY (place_id, category_id)
);

-- Create indexes for performance
CREATE INDEX idx_places_city ON places(city);
CREATE INDEX idx_places_verified ON places(verified) WHERE verified = TRUE;
CREATE INDEX idx_places_rating ON places(rating DESC) WHERE rating IS NOT NULL;
CREATE INDEX idx_places_location ON places USING GIST (ST_Point(longitude::float8, latitude::float8));
CREATE INDEX idx_places_fts ON places USING GIN (to_tsvector('english', name || ' ' || COALESCE(description, '')));

CREATE INDEX idx_reviews_place_id ON reviews(place_id);
CREATE INDEX idx_reviews_moderated ON reviews(moderated) WHERE moderated = 1;
CREATE INDEX idx_reviews_created ON reviews(created_at DESC);

-- Create triggers for updated_at timestamps
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_places_updated_at BEFORE UPDATE ON places
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_reviews_updated_at BEFORE UPDATE ON reviews
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Insert initial categories
INSERT INTO categories (name, description, icon) VALUES
('Traditional Konditori', 'Historic Swedish pastry shops', '🏛️'),
('Modern Café', 'Contemporary coffee shops with Swedish influences', '☕'),
('Bakery', 'Fresh baked Swedish pastries daily', '🥐'),
('Coffee Roastery', 'Specialty coffee with traditional fika', '🫘'),
('Garden Café', 'Outdoor fika experience', '🌸'),
('University Café', 'Student-friendly fika spots', '🎓'),
('Waterfront', 'Cafés with scenic water views', '🌊'),
('Historic Building', 'Fika in buildings with historical significance', '🏰');

-- Insert sample places for development
INSERT INTO places (
    name, description, address, city, latitude, longitude, 
    fika_specialties, price_range, rating, verified, features
) VALUES
-- Stockholm
('Vete-Katten', 'Historic konditori serving traditional Swedish pastries since 1928. Famous for their princess cake and cinnamon buns.', 'Kungsgatan 55, 111 22 Stockholm', 'Stockholm', 59.3326, 18.0649, 
 ARRAY['Prinsesstårta', 'Kanelbullar', 'Mazarin'], 3, 4.5, TRUE, 
 ARRAY['historic', 'traditional', 'central_location']),

('Drop Coffee', 'Modern specialty coffee roastery with excellent single-origin beans and traditional Swedish pastries.', 'Wollmar Yxkullsgatan 10, 118 50 Stockholm', 'Stockholm', 59.3165, 18.0707,
 ARRAY['Single-origin coffee', 'Kanelbullar', 'Cardamom buns'], 3, 4.4, TRUE,
 ARRAY['specialty_coffee', 'modern', 'wifi']),

-- Gothenburg  
('Café Husaren', 'Famous for serving the largest cinnamon buns in Gothenburg. A must-visit spot in the historic Haga district.', 'Haga Nygata 28, 413 01 Göteborg', 'Gothenburg', 57.6987, 11.9709,
 ARRAY['Giant Kanelbullar', 'Traditional pastries'], 2, 4.6, TRUE,
 ARRAY['famous_buns', 'historic_district', 'outdoor_seating']),

-- Malmö
('Lilla Kafferosteriet', 'Cozy coffee roastery in Malmö serving excellent coffee with Swedish and international pastries.', 'Baltzarsgatan 24, 211 36 Malmö', 'Malmö', 55.6059, 13.0007,
 ARRAY['Freshly roasted coffee', 'Kanelbullar', 'International pastries'], 3, 4.3, TRUE,
 ARRAY['coffee_roastery', 'cozy', 'international_flair']),

-- Uppsala
('Guntherska Hovkonditori', 'Uppsala\'s premier konditori with over 150 years of tradition, located in a beautiful historic building.', 'Fyristorg 8, 753 20 Uppsala', 'Uppsala', 59.8586, 17.6389,
 ARRAY['Traditional Swedish cakes', 'Seasonal specialties'], 3, 4.4, TRUE,
 ARRAY['historic', 'traditional', 'elegant']),

-- Västerås
('Café Alma', 'Local favorite serving traditional Swedish fika in a warm, welcoming atmosphere.', 'Stora Gatan 35, 722 12 Västerås', 'Västerås', 59.6162, 16.5528,
 ARRAY['Home-style baking', 'Kanelbullar', 'Coffee'], 2, 4.2, TRUE,
 ARRAY['local_favorite', 'homestyle', 'friendly']);

-- Link places to categories
INSERT INTO place_categories (place_id, category_id)
SELECT p.id, c.id FROM places p, categories c 
WHERE (p.name = 'Vete-Katten' AND c.name = 'Traditional Konditori')
   OR (p.name = 'Drop Coffee' AND c.name = 'Coffee Roastery')
   OR (p.name = 'Café Husaren' AND c.name = 'Traditional Konditori')
   OR (p.name = 'Lilla Kafferosteriet' AND c.name = 'Coffee Roastery')
   OR (p.name = 'Guntherska Hovkonditori' AND c.name = 'Traditional Konditori')
   OR (p.name = 'Café Alma' AND c.name = 'Modern Café');

-- Insert sample reviews for development
INSERT INTO reviews (place_id, user_name, rating, comment, fika_items, visit_date, moderated)
SELECT p.id, 'Erik L.', 5, 'Amazing traditional Swedish pastries! The prinsesstårta was absolutely perfect.', 
       ARRAY['Prinsesstårta', 'Coffee'], '2024-01-15', 1
FROM places p WHERE p.name = 'Vete-Katten';

INSERT INTO reviews (place_id, user_name, rating, comment, fika_items, visit_date, moderated)
SELECT p.id, 'Anna S.', 4, 'Great coffee and the cinnamon buns are huge! Perfect for sharing.', 
       ARRAY['Giant Kanelbullar', 'Coffee'], '2024-01-20', 1
FROM places p WHERE p.name = 'Café Husaren';

-- Create view for place statistics
CREATE VIEW place_stats AS
SELECT 
    p.id,
    p.name,
    p.city,
    COUNT(r.id) as total_reviews,
    AVG(r.rating) as avg_rating,
    COUNT(CASE WHEN r.rating = 5 THEN 1 END) as five_star_reviews,
    COUNT(CASE WHEN r.rating = 4 THEN 1 END) as four_star_reviews,
    COUNT(CASE WHEN r.rating = 3 THEN 1 END) as three_star_reviews,
    COUNT(CASE WHEN r.rating = 2 THEN 1 END) as two_star_reviews,
    COUNT(CASE WHEN r.rating = 1 THEN 1 END) as one_star_reviews
FROM places p
LEFT JOIN reviews r ON p.id = r.place_id AND r.moderated = 1
GROUP BY p.id, p.name, p.city;

-- Update review counts and ratings
UPDATE places 
SET review_count = stats.total_reviews,
    rating = ROUND(stats.avg_rating, 2)
FROM place_stats stats 
WHERE places.id = stats.id;

-- Create full-text search function
CREATE OR REPLACE FUNCTION search_places(search_query TEXT)
RETURNS TABLE(
    place_id UUID,
    name VARCHAR,
    description TEXT,
    city VARCHAR,
    rating DECIMAL,
    rank REAL
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        p.id,
        p.name,
        p.description,
        p.city,
        p.rating,
        ts_rank_cd(to_tsvector('english', p.name || ' ' || COALESCE(p.description, '')), 
                   plainto_tsquery('english', search_query)) as rank
    FROM places p
    WHERE to_tsvector('english', p.name || ' ' || COALESCE(p.description, '')) @@ plainto_tsquery('english', search_query)
    ORDER BY rank DESC;
END;
$$ LANGUAGE plpgsql;

COMMIT;