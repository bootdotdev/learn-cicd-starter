source .env

cd sql/schema
goose mysql $DATABASE_URL up
