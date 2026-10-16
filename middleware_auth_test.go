package main

import (
	"net/http"
	"net/http/httptest"
	"testing"

	"github.com/bootdotdev/learn-cicd-starter/internal/database"
)

func TestAuthMiddleware(t *testing.T) {
	tests := []struct {
		name     string
		token    string
		expected int
	}{
		{
			name:     "invalid token",
			token:    "Bearer invalid",
			expected: http.StatusUnauthorized,
		},
	}

	apiCfg := apiConfig{}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			req := httptest.NewRequest(http.MethodGet, "/", nil)
			req.Header.Set("Authorization", tt.token)
			rr := httptest.NewRecorder()

			nextHandler := func(w http.ResponseWriter, r *http.Request, user database.User) {
				w.WriteHeader(http.StatusOK)
			}
			handler := apiCfg.middlewareAuth(nextHandler)
			handler.ServeHTTP(rr, req)

			if rr.Code != tt.expected {
				t.Errorf("expected status code %d, got %d", tt.expected, rr.Code)
			}
		})
	}
}
