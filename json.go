package main

import (
	"encoding/json"
	"net/http"
)

// writeJSON writes v as JSON with the given status code.
func writeJSON(w http.ResponseWriter, code int, v any) {
	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(code)

	dat, err := json.Marshal(v)
	if err != nil {
		http.Error(w, "marshal error", http.StatusInternalServerError)
		return
	}

	if _, err := w.Write(dat); err != nil {
		http.Error(w, "write error", http.StatusInternalServerError)
		return
	}
}
