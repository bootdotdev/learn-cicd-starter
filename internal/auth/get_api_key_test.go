package auth

import (
    "net/http"
    "testing"
)

func TestGetAPIKey_Success(t *testing.T) {
    headers := http.Header{}
    headers.Set("Authorization", "ApiKey my-secret-key")

    got, err := GetAPIKey(headers)
    if err != nil {
        t.Fatalf("expected no error, got %v", err)
    }
    if got != "my-secret-key" {
        t.Fatalf("expected API key %q, got %q", "my-secret-key", got)
    }
}

func TestGetAPIKey_Errors(t *testing.T) {
    tests := []struct {
        name      string
        header    string
        wantErr   bool
        wantError error
    }{
        {
            name:      "missing authorization header",
            header:    "",
            wantErr:   true,
            wantError: ErrNoAuthHeaderIncluded,
        },
        {
            name:      "malformed authorization header",
            header:    "Bearer token123",
            wantErr:   true,
            wantError: nil,
        },
    }

    for _, tt := range tests {
        t.Run(tt.name, func(t *testing.T) {
            headers := http.Header{}
            if tt.header != "" {
                headers.Set("Authorization", tt.header)
            }

            _, err := GetAPIKey(headers)
            if tt.wantErr {
                if err == nil {
                    t.Fatalf("expected error, got nil")
                }
                if tt.wantError != nil && err != tt.wantError {
                    t.Fatalf("expected error %v, got %v", tt.wantError, err)
                }
                return
            }

            if err != nil {
                t.Fatalf("expected no error, got %v", err)
            }
        })
    }
}
