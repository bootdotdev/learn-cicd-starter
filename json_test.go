package main

import (
	"net/http"
	"net/http/httptest"
	"testing"
)

func TestRespondWithError(t *testing.T) {
	// Test the function with a sample error
	w := httptest.NewRecorder()
	respondWithError(w, http.StatusBadRequest, "Bad Request", nil)

	if w.Code != http.StatusBadRequest {
		t.Errorf("Expected status code %d, got %d", http.StatusBadRequest, w.Code)
	}

	if w.Header().Get("Content-Type") != "application/json" {
		t.Errorf("Expected Content-Type 'application/json', got '%s'", w.Header().Get("Content-Type"))
	}

	if w.Body.String() != `{"error":"Bad Request"}` {
		t.Errorf("Expected body '{\"error\":\"Bad Request\"}', got '%s'", w.Body.String())
	}
}
