#!/bin/sh
echo "install postgres"
initdb /usr/local/var/postgres
echo "brew start"
brew services start postgresql
echo "start postgres"
pg_ctl -D /usr/local/var/postgres start
echo "create postgres user"
/usr/local/opt/postgres/bin/createuser -s postgres
python db.py