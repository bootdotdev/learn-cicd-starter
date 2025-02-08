package main

import (
	"database/sql"
	"embed"
	"io"
	"log"
	"net/http"
	"os"
	"strings"
	"time"

	"github.com/go-chi/chi"
	"github.com/go-chi/cors"

	"github.com/bootdotdev/learn-cicd-starter/internal/database"

	_ "github.com/tursodatabase/libsql-client-go/libsql"
)

type apiConfig struct {
	DB *database.Queries
}

//go:embed static/*
var staticFiles embed.FS

func getCurrentDirectory() string {
	dir, err := os.Getwd()
	if err != nil {
		return err.Error()
	}
	return dir
}

func listFiles(dir string) string {
	files, err := os.ReadDir(dir)
	if err != nil {
		return err.Error()
	}
	var fileNames []string
	for _, file := range files {
		fileNames = append(fileNames, file.Name())
	}
	return strings.Join(fileNames, ", ")
}

func main() {
	log.Printf("Starting application...")
	log.Printf("Current working directory: %s", getCurrentDirectory())
	log.Printf("Files in current directory: %s", listFiles("."))

	port := os.Getenv("PORT")
	if port == "" {
		log.Println("PORT environment variable not set, defaulting to 8080")
		port = "8080"
	}

	apiCfg := apiConfig{}

	// https://github.com/libsql/libsql-client-go/#open-a-connection-to-sqld
	// libsql://[your-database].turso.io?authToken=[your-auth-token]
	dbURL := os.Getenv("DATABASE_URL")
	if dbURL == "" {
		log.Println("DATABASE_URL environment variable is not set")
		log.Println("Running without CRUD endpoints")
	} else {
		db, err := sql.Open("libsql", dbURL)
		if err != nil {
			log.Fatal(err)
		}
		dbQueries := database.New(db)
		apiCfg.DB = dbQueries
		log.Println("Connected to database!")
	}

	router := chi.NewRouter()

	router.Use(cors.Handler(cors.Options{
		AllowedOrigins:   []string{"https://*", "http://*"},
		AllowedMethods:   []string{"GET", "POST", "PUT", "DELETE", "OPTIONS"},
		AllowedHeaders:   []string{"*"},
		ExposedHeaders:   []string{"Link"},
		AllowCredentials: false,
		MaxAge:           300,
	}))

	router.Get("/", func(w http.ResponseWriter, r *http.Request) {
		f, err := staticFiles.Open("static/index.html")
		if err != nil {
			http.Error(w, err.Error(), http.StatusInternalServerError)
			return
		}
		defer f.Close()
		if _, err := io.Copy(w, f); err != nil {
			http.Error(w, err.Error(), http.StatusInternalServerError)
		}
	})

	v1Router := chi.NewRouter()

	if apiCfg.DB != nil {
		v1Router.Post("/users", apiCfg.handlerUsersCreate)
		v1Router.Get("/users", apiCfg.middlewareAuth(apiCfg.handlerUsersGet))
		v1Router.Get("/notes", apiCfg.middlewareAuth(apiCfg.handlerNotesGet))
		v1Router.Post("/notes", apiCfg.middlewareAuth(apiCfg.handlerNotesCreate))
	}

	v1Router.Get("/healthz", handlerReadiness)

	router.Mount("/v1", v1Router)
	srv := &http.Server{
		Addr:              "0.0.0.0:" + port, // explicitly bind to all interfaces
		Handler:           router,
		ReadHeaderTimeout: 5 * time.Second,
	}

	log.Printf("Serving on port: %s\n", port)
	log.Fatal(srv.ListenAndServe())
}
