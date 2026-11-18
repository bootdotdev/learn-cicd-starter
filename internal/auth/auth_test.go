package auth

import (
	"net/http"
	"net/http/httptest"
	"testing"
)

func TestGetAPIKey(t *testing.T) {
	tests := []struct {
		name    string
		header  string
		want    string
		wantErr bool
	}{
		{name: "no header", header: "", wantErr: true},
		{name: "wrong scheme", header: "Bearer abc123", wantErr: true},
		// Function currently returns "" and NO error for an empty ApiKey value
		{name: "empty key", header: "ApiKey ", want: "", wantErr: false},
		{name: "valid", header: "ApiKey abc123", want: "abc123", wantErr: false},
	}

	for _, tc := range tests {
		t.Run(tc.name, func(t *testing.T) {
			req := httptest.NewRequest(http.MethodGet, "/", nil)
			if tc.header != "" {
				req.Header.Set("Authorization", tc.header)
			}

			// GetAPIKey takes http.Header
			got, err := GetAPIKey(req.Header)

			if tc.wantErr {
				if err == nil {
					t.Fatalf("expected an error, got key=%q", got)
				}
				return
			}

			if err != nil {
				t.Fatalf("unexpected error: %v", err)
			}
			if got != tc.want {
				t.Fatalf("want %q, got %q", tc.want, got)
			}
		})
	}
}
