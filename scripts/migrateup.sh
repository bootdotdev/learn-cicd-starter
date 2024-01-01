if [ -f .env ]; then
    source .env
fi

cd sql/schema
goose mysql $DATABASE_URL up
