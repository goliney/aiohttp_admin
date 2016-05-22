sudo -u postgres psql -c "DROP ROLE IF EXISTS aiohttp_admin_user"
sudo -u postgres psql -c "CREATE USER aiohttp_admin_user WITH PASSWORD 'mysecretpassword';"
sudo -u postgres psql -c "DROP DATABASE IF EXISTS aiohttp_admin"
sudo -u postgres psql -c "CREATE DATABASE aiohttp_admin ENCODING 'UTF8';" 
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE aiohttp_admin TO aiohttp_admin_user;"

cat sql/create_tables.sql | sudo -u postgres psql -d aiohttpdemo_polls -a 
cat sql/sample_data.sql | sudo -u postgres psql -d aiohttpdemo_polls -a 
