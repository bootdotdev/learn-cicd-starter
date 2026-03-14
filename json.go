package main

import (
	"encoding/json"
	"log"
	"net/http"
)

func respondWithError(w http.ResponseWriter, code int, msg string, logErr error) {
	if logErr != nil {
		log.Println(logErr)
	}
	if code > 499 {
		log.Printf("Responding with 5XX error: %s", msg)
	}
	type errorResponse struct {
		Error string `json:"error"`
	}
	respondWithJSON(w, code, errorResponse{
		Error: msg,
	})
}

func respondWithJSON(w http.ResponseWriter, code int, payload interface{}) {
	w.Header().Set("Content-Type", "application/json; charset=utf-8")

	dat, err := json.Marshal(payload)
	if err != nil {
		log.Printf("error marshalling json: %v", err)
		w.WriteHeader(http.StatusInternalServerError)
		return
	}

	w.WriteHeader(code)
	n, err := w.Write(dat)
	if err != nil {
		// client likely disconnected or socket failed; headers already sent, so just log
		log.Printf("error writing response: %v", err)
		return
	}
	if n != len(dat) {
		log.Printf("partial write: wrote %d of %d bytes", n, len(dat))
	}
}
