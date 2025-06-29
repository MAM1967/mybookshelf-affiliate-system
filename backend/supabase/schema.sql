CREATE TABLE books_accessories (
    id SERIAL PRIMARY KEY,
    title TEXT NOT NULL,
    author TEXT NOT NULL,
    price NUMERIC NOT NULL,
    affiliate_link TEXT NOT NULL,
    image_url TEXT NOT NULL,
    category TEXT NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
