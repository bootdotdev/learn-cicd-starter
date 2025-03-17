package main

import (
	"net/http"
	"net/http/httptest"
	"testing"
)

func Test_handlerReadiness(t *testing.T) {
	tests := []struct {
		name string
	}{
		{"Basic readiness test"},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			req, err := http.NewRequest("GET", "/readiness", nil)
			if err != nil {
				t.Fatal(err)
			}

			rr := httptest.NewRecorder()
			handler := http.HandlerFunc(handlerReadiness)

			handler.ServeHTTP(rr, req)

			if status := rr.Code; status != http.StatusOK {
				t.Errorf("handlerReadiness returned wrong status code: got %v want %v",
					status, http.StatusOK)
			}

			expected := `{"status":"ok"}`
			if rr.Body.String() != expected {
				t.Errorf("handlerReadiness returned unexpected body: got %v want %v",
					rr.Body.String(), expected)
			}
		})
	}
}
