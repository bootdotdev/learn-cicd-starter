package main

import (
	"encoding/json"
	"net/http"
)

// respondWithError sends a JSON error with optional internal details.
func respondWithError(w http.ResponseWriter, code int, message string, err error) {
	payload := map[string]string{"error": message}
	if err != nil {
		payload["details"] = err.Error()
	}
	respondWithJSON(w, code, payload)
}

// respondWithJSON writes v as JSON with proper error handling (gosec-safe).
func respondWithJSON(w http.ResponseWriter, code int, v any) {
	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(code)

	data, err := json.Marshal(v)
	if err != nil {
		http.Error(w, "marshal error", http.StatusInternalServerError)
		return
	}
	if _, err := w.Write(data); err != nil {
		http.Error(w, "write error", http.StatusInternalServerError)
		return
	}
}
