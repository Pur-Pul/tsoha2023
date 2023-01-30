DROP TABLE IF EXISTS users CASCADE;
DROP TABLE IF EXISTS editors CASCADE;
DROP TABLE IF EXISTS images CASCADE;
DROP TABLE IF EXISTS posts CASCADE;

CREATE TABLE users (id SERIAL PRIMARY KEY, username TEXT, password TEXT);
CREATE TABLE editors (user_id INT, order_number INT, row_number INT, col_number INT, color TEXT);
CREATE TABLE images (image_id INT, user_id INT, row_number INT, col_number INT, color TEXT, order_number INT);
CREATE TABLE posts (id SERIAL PRIMARY KEY, image_id INT);