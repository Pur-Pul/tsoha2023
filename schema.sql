DROP TABLE IF EXISTS users CASCADE;
DROP TABLE IF EXISTS editors CASCADE;

CREATE TABLE users (id SERIAL PRIMARY KEY, username TEXT, password TEXT);
CREATE TABLE editors (user_id INT, order_number INT, row_number INT, col_number INT, color TEXT);