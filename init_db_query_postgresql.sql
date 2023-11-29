DROP TABLE If EXISTS users;

CREATE TABLE users (
	id SERIAL NOT NULL,
	email varchar(200) NOT NULL,
	username varchar(45) NOT NULL,
	hashed_password varchar(200) NOT NULL,
	is_active boolean DEFAULT FALSE,
	is_admin boolean DEFAULT FALSE,
	PRIMARY KEY (id)
);

DROP TABLE If EXISTS items;

CREATE TABLE items (
	id SERIAL,
	name varchar(200) NOT NULL,
	date_created varchar(200) DEFAULT NULL,
	is_deleted boolean DEFAULT FALSE,
	PRIMARY KEY (id),
	FOREIGN KEY (owner_id) REFERENCES users(id)
 );