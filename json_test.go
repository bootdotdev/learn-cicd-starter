package main

import (
	"encoding/json"
	"io/ioutil"
	"net/http"
	"net/http/httptest"
	"testing"
)

func TestRespondWithError(t *testing.T) {
	w := httptest.NewRecorder()
	respondWithError(w, http.StatusBadRequest, "bad request error")

	if w.Code != http.StatusBadRequest {
		t.Errorf("expected status code %d, got %d", http.StatusBadRequest, w.Code)
	}

	responseBody, _ := ioutil.ReadAll(w.Body)
	expectedResponse := map[string]string{"error": "bad request error"}
	var actualResponse map[string]string
	err := json.Unmarshal(responseBody, &actualResponse)
	if err != nil {
		t.Fatalf("error unmarshalling response body: %v", err)
	}

	if actualResponse["error"] != expectedResponse["error"] {
		t.Errorf("expected error message '%s', got '%s'", expectedResponse["error"], actualResponse["error"])
	}
}

func TestRespondWithJSONSuccess(t *testing.T) {
	w := httptest.NewRecorder()
	payload := map[string]string{"message": "success"}
	respondWithJSON(w, http.StatusOK, payload)

	if w.Code != http.StatusOK {
		t.Errorf("expected status code %d, got %d", http.StatusOK, w.Code)
	}

	responseBody, _ := ioutil.ReadAll(w.Body)
	var actualResponse map[string]string
	err := json.Unmarshal(responseBody, &actualResponse)
	if err != nil {
		t.Fatalf("error unmarshalling response body: %v", err)
	}

	if actualResponse["message"] != payload["message"] {
		t.Errorf("expected message '%s', got '%s'", payload["message"], actualResponse["message"])
	}
}

func TestRespondWithJSONMarshalError(t *testing.T) {
	w := httptest.NewRecorder()
	payload := make(chan int) // JSON marshalling will fail on a channel
	respondWithJSON(w, http.StatusOK, payload)

	if w.Code != http.StatusInternalServerError {
		t.Errorf("expected status code %d, got %d", http.StatusInternalServerError, w.Code)
	}
}
