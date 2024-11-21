package main

import (
	"database/sql"
	"embed"
	"io"
	"log"
	"net/http"
	"os"

	"github.com/go-chi/chi"
	"github.com/go-chi/cors"
	"github.com/joho/godotenv"

	"github.com/bootdotdev/learn-cicd-starter/internal/database"

	_ "github.com/tursodatabase/libsql-client-go/libsql"
)

type apiConfig struct {
	DB *database.Queries // Database queries object
}

//go:embed static/*
var staticFiles embed.FS // Embedding static files for serving

func main() {
	// Load environment variables from .env file
	err := godotenv.Load(".env")
	if err != nil {
		log.Printf("warning: assuming default configuration. .env unreadable: %v", err)
	}

	// Get the port from the environment variable, exit if not set
	port := os.Getenv("PORT")
	if port == "" {
		log.Fatal("PORT environment variable is not set")
	}

	apiCfg := apiConfig{} // Initialize the API configuration

	// Connect to the database if DATABASE_URL is set
	dbURL := os.Getenv("DATABASE_URL")
	if dbURL == "" {
		log.Println("DATABASE_URL environment variable is not set")
		log.Println("Running without CRUD endpoints")
	} else {
		db, err := sql.Open("libsql", dbURL) // Open connection to the database
		if err != nil {
			log.Fatal(err) // Exit on error
		}
		dbQueries := database.New(db) // Create a new database queries object
		apiCfg.DB = dbQueries
		log.Println("Connected to database!") // Log successful DB connection
	}

	router := chi.NewRouter() // Initialize the router

	// Set up CORS middleware to allow cross-origin requests
	router.Use(cors.Handler(cors.Options{
		AllowedOrigins:   []string{"https://*", "http://*"}, // Allow any origin
		AllowedMethods:   []string{"GET", "POST", "PUT", "DELETE", "OPTIONS"},
		AllowedHeaders:   []string{"*"},
		ExposedHeaders:   []string{"Link"},
		AllowCredentials: false,
		MaxAge:           300, // Max cache duration for preflight requests
	}))

	// Serve the index.html file from embedded static files
	router.Get("/", func(w http.ResponseWriter, r *http.Request) {
		f, err := staticFiles.Open("static/index.html") // Open index.html file
		if err != nil {
			http.Error(w, err.Error(), http.StatusInternalServerError)
			return
		}
		defer f.Close()                          // Ensure file is closed after serving
		if _, err := io.Copy(w, f); err != nil { // Copy file contents to response
			http.Error(w, err.Error(), http.StatusInternalServerError)
		}
	})

	v1Router := chi.NewRouter() // Router for API version 1

	// Set up CRUD routes for users and notes if DB is configured
	if apiCfg.DB != nil {
		v1Router.Post("/users", apiCfg.handlerUsersCreate)                        // Route to create users
		v1Router.Get("/users", apiCfg.middlewareAuth(apiCfg.handlerUsersGet))     // Route to get users
		v1Router.Get("/notes", apiCfg.middlewareAuth(apiCfg.handlerNotesGet))     // Route to get notes
		v1Router.Post("/notes", apiCfg.middlewareAuth(apiCfg.handlerNotesCreate)) // Route to create notes
	}

	// Health check endpoint
	v1Router.Get("/healthz", handlerReadiness)

	// Mount versioned API routes under /v1
	router.Mount("/v1", v1Router)

	// Set up and start the HTTP server
	srv := &http.Server{
		Addr:    ":" + port, // Bind to the specified port
		Handler: router,
	}

	log.Printf("Serving on port: %s\n", port) // Log server start
	log.Fatal(srv.ListenAndServe())           // Start server and handle any errors
}
