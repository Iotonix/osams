Set-Location ~/SRC/osams
docker run -d --name timescaledb -p 5432:5432  -v ./.databases/pgdata:/pgdata -e PGDATA=/pgdata -e POSTGRES_PASSWORD=pgosams123 timescale/timescaledb-ha:pg17