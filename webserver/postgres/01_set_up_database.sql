CREATE DATABASE jodlplatform;
CREATE USER jodlgang WITH PASSWORD 'tothemoon';
ALTER ROLE jodlgang SET client_encoding to 'utf8';
ALTER ROLE jodlgang SET default_transaction_isolation TO 'read committed';
ALTER ROLE jodlgang SET timezone TO 'UTC';
GRANT ALL PRIVILEGES ON DATABASE jodlplatform TO jodlgang;
