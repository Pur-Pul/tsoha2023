DROP TABLE IF EXISTS users CASCADE;
DROP TABLE IF EXISTS editors CASCADE;
DROP TABLE IF EXISTS images CASCADE;
DROP TABLE IF EXISTS posts CASCADE;
DROP TABLE IF EXISTS reply_section CASCADE;
DROP TABLE IF EXISTS replies CASCADE;
DROP TABLE IF EXISTS votes CASCADE;

CREATE TABLE users (id SERIAL PRIMARY KEY, username TEXT, password TEXT);
CREATE TABLE editors (user_id INT, order_number INT, row_number INT, col_number INT, color TEXT);
CREATE TABLE images (image_id SERIAL PRIMARY KEY, user_id INT, data JSON);
CREATE TABLE posts (id SERIAL PRIMARY KEY, image_id INT, title TEXT, time TIMESTAMP default CURRENT_TIMESTAMP);
CREATE TABLE reply_section (id SERIAL PRIMARY KEY, post_id INT, reply_id INT);
CREATE TABLE replies (id SERIAL PRIMARY KEY, reply_id INT, user_id INT, content TEXT, time TIMESTAMP default CURRENT_TIMESTAMP);
CREATE TABLE votes (
    id SERIAL PRIMARY KEY,
    reply_id INT,
    user_id INT,
    points INT,
    UNIQUE(reply_id, user_id)
);
