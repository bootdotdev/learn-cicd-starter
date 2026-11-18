package main

import (
	"encoding/json"
	"log"
	"net/http"
)

// respondWithError now accepts the 4th 'err' argument to match the handler calls
func respondWithError(w http.ResponseWriter, code int, msg string, err error) {
	if code > 499 {
		log.Printf("Responding with 5XX error: %s. Error: %v", msg, err)
	}
	type errorResponse struct {
		Error string `json:"error"`
	}
	respondWithJSON(w, code, errorResponse{
		Error: msg,
	})
}

func respondWithJSON(w http.ResponseWriter, code int, payload interface{}) {
	dat, err := json.Marshal(payload)
	if err != nil {
		log.Printf("Failed to marshal JSON response: %v", payload)
		w.WriteHeader(500)
		return
	}
	w.Header().Add("Content-Type", "application/json")
	w.WriteHeader(code)

	// Capturing the error here satisfies gosec G104
	_, err = w.Write(dat)
	if err != nil {
		log.Printf("Failed to write response: %v", err)
	}
}
