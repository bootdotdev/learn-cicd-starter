package apikey

import (
	"database/sql"
	"net/url"
	"os"
	"strings"

	"github.com/go-chi/chi"
	"github.com/go-chi/cors"
	"github.com/joho/godotenv"

	"github.com/bootdotdev/learn-cicd-starter/internal/database"

	_ "github.com/go-sql-driver/mysql"
)

type apiConfig struct {
	DB *database.Queries
}