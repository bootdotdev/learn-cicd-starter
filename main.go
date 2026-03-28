package main

import (
	"context"
	"database/sql"
	"embed"
	"io"
	"log"
	"net/http"
	"os"
	"os/signal"
	"strconv"
	"syscall"
	"time"

	"github.com/go-chi/chi"
	"github.com/go-chi/cors"
	"github.com/joho/godotenv"

	"github.com/bootdotdev/learn-cicd-starter/internal/database"

	_ "github.com/tursodatabase/libsql-client-go/libsql"
)

type apiConfig struct {
	DB *database.Queries
}

//go:embed static/*
var staticFiles embed.FS

func main() {
	_ = godotenv.Load(".env") // avoid leaking env load errors

	portStr := os.Getenv("PORT")
	if portStr == "" {
		log.Fatal("PORT must be set")
	}

	// ✅ FIX: validate & sanitize port (G706)
	port, err := strconv.Atoi(portStr)
	if err != nil || port <= 0 || port > 65535 {
		log.Fatal("invalid PORT")
	}

	apiCfg := apiConfig{}

	dbURL := os.Getenv("DATABASE_URL")
	if dbURL != "" {
		db, err := sql.Open("libsql", dbURL)
		if err != nil {
			log.Fatal("failed to initialize DB")
		}

		// ✅ FIX: verify DB connection
		if err := db.Ping(); err != nil {
			log.Fatal("failed to connect to DB")
		}

		apiCfg.DB = database.New(db)
		log.Println("Connected to database")
	}

	router := chi.NewRouter()

	// ✅ FIX: restrict CORS
	router.Use(cors.Handler(cors.Options{
		AllowedOrigins: []string{"https://yourdomain.com"}, // change for your env
		AllowedMethods: []string{"GET", "POST"},
		AllowedHeaders: []string{"Content-Type", "Authorization"},
		MaxAge:         300,
	}))

	// ✅ FIX: add security headers
	router.Use(func(next http.Handler) http.Handler {
		return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
			w.Header().Set("X-Content-Type-Options", "nosniff")
			w.Header().Set("X-Frame-Options", "DENY")
			w.Header().Set("Content-Security-Policy", "default-src 'self'")
			next.ServeHTTP(w, r)
		})
	})

	router.Get("/", func(w http.ResponseWriter, r *http.Request) {
		f, err := staticFiles.Open("static/index.html")
		if err != nil {
			http.Error(w, "internal server error", http.StatusInternalServerError) // ✅ no leak
			return
		}
		defer f.Close()

		if _, err := io.Copy(w, f); err != nil {
			http.Error(w, "internal server error", http.StatusInternalServerError)
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

	// ✅ FIX: secure HTTP server config (timeouts)
	srv := &http.Server{
		Addr:              ":" + strconv.Itoa(port),
		Handler:           router,
		ReadTimeout:       5 * time.Second,
		WriteTimeout:      10 * time.Second,
		IdleTimeout:       120 * time.Second,
		ReadHeaderTimeout: 2 * time.Second,
	}

	// ✅ FIX: run server safely
	go func() {
		log.Printf("Serving on port: %d\n", port) // safe logging
		if err := srv.ListenAndServe(); err != nil && err != http.ErrServerClosed {
			log.Fatal(err)
		}
	}()

	// ✅ FIX: graceful shutdown
	stop := make(chan os.Signal, 1)
	signal.Notify(stop, syscall.SIGINT, syscall.SIGTERM)

	<-stop

	ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
	defer cancel()

	log.Println("Shutting down server...")
	if err := srv.Shutdown(ctx); err != nil {
		log.Println("Graceful shutdown failed:", err)
	}
}
