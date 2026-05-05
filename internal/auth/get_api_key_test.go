package auth

import (
	"errors"
	"net/http"
	"testing"
)

func TestGetAPIKey(t *testing.T) {
	t.Parallel()

	tests := []struct {
		name       string
		headerVal  string
		omitHeader bool
		wantKey    string
		wantErr    error
	}{
		{
			name:      "valid ApiKey header",
			headerVal: "ApiKey secret-key-123",
			wantKey:   "secret-key-123",
			wantErr:   nil,
		},
		{
			name:       "missing authorization header",
			omitHeader: true,
			wantKey:    "",
			wantErr:    ErrNoAuthHeaderIncluded,
		},
		{
			name:      "malformed single token",
			headerVal: "ApiKeyOnly",
			wantKey:   "",
			wantErr:   errors.New("malformed authorization header"),
		},
		{
			name:      "wrong scheme Bearer",
			headerVal: "Bearer token",
			wantKey:   "",
			wantErr:   errors.New("malformed authorization header"),
		},
		{
			name:      "ApiKey with no key part",
			headerVal: "ApiKey",
			wantKey:   "",
			wantErr:   errors.New("malformed authorization header"),
		},
		{
			name:      "ApiKey with trailing space yields empty key",
			headerVal: "ApiKey ",
			wantKey:   "",
			wantErr:   nil,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			t.Parallel()
			h := http.Header{}
			if !tt.omitHeader {
				h.Set("Authorization", tt.headerVal)
			}

			got, err := GetAPIKey(h)

			if tt.wantErr != nil {
				if err == nil {
					t.Fatalf("GetAPIKey() err = nil, want %v", tt.wantErr)
				}
				if tt.wantErr == ErrNoAuthHeaderIncluded {
					if !errors.Is(err, ErrNoAuthHeaderIncluded) {
						t.Fatalf("GetAPIKey() err = %v, want ErrNoAuthHeaderIncluded", err)
					}
				} else if err.Error() != tt.wantErr.Error() {
					t.Fatalf("GetAPIKey() err = %q, want %q", err.Error(), tt.wantErr.Error())
				}
				if got != "" {
					t.Fatalf("GetAPIKey() key = %q, want empty", got)
				}
				return
			}

			if err != nil {
				t.Fatalf("GetAPIKey() err = %v, want nil", err)
			}
			if got != tt.wantKey {
				t.Fatalf("GetAPIKey() key = %q, want %q", got, tt.wantKey)
			}
		})
	}
}
