DO $$ 
BEGIN
    IF NOT EXISTS (SELECT FROM pg_database WHERE datname = 'coursework') THEN
       	CREATE DATABASE coursework;
    END IF;
END $$;
\connect coursework;
CREATE TABLE IF NOT EXISTS programs (
	program_name varchar(100) PRIMARY KEY NOT NULL,
	module_1 varchar(100),
	module_2 varchar(100),
	module_3 varchar(100)
);
CREATE TABLE IF NOT EXISTS modules (
	module_name varchar(100) PRIMARY KEY NOT NULL,
	language varchar(100),
	lines integer
);