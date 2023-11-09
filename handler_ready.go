package main

import "net/http"

// handlerReadiness returns a JSON status. Use it to ensure the server is ready
// for incoming requests.
func handlerReadiness(w http.ResponseWriter, r *http.Request) {
	respondWithJSON(w, http.StatusOK, map[string]string{"status": "ok"})
}
