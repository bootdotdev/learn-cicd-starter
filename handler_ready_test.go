package main

import (
	"encoding/json"
	"net/http"
	"net/http/httptest"
	"testing"
)

func TestHandleNotesGet(t *testing.T) {
	req, _ := http.NewRequest("GET", "/healthz", nil)
	rr := httptest.NewRecorder()

	handlerReadiness(rr, req)

	var got map[string]string
	json.Unmarshal(rr.Body.Bytes(), &got)

	if got["status"] != "ok" {
		t.Errorf("Expected the 'status' key of the response to be set to 'ok'. Got '%s'", got["error"])
	}
}
