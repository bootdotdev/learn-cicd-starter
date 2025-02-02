package auth

import (
	"errors"
	"net/http"
	"testing"
)

func TestGetAPIKey(t *testing.T) {
	tests := []struct {
		name    string
		headers http.Header
		want    string
		wantErr error
	}{
		{
			name:    "no authorization header",
			headers: http.Header{},
			want:    "",
			wantErr: ErrNoAuthHeaderIncluded,
		},
		{
			name: "malformed header - only prefix",
			headers: http.Header{
				"Authorization": []string{"ApiKey"},
			},
			want:    "",
			wantErr: errors.New("malformed authorization header"),
		},
		{
			name: "malformed header - wrong type",
			headers: http.Header{
				"Authorization": []string{"Bearer token"},
			},
			want:    "",
			wantErr: errors.New("malformed authorization header"),
		},
		{
			name: "valid header",
			headers: http.Header{
				"Authorization": []string{"ApiKey valid-key"},
			},
			want:    "valid-key",
			wantErr: nil,
		},
		{
			name: "extra spaces in header",
			headers: http.Header{
				"Authorization": []string{"ApiKey   valid-key  "},
			},
			want:    "valid-key",
			wantErr: nil,
		},
		{
			name: "multiple parts",
			headers: http.Header{
				"Authorization": []string{"ApiKey valid-key extra-part"},
			},
			want:    "valid-key",
			wantErr: nil,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			got, err := GetAPIKey(tt.headers)
			if got != tt.want {
				t.Errorf("got %q, want %q", got, tt.want)
			}

			if tt.wantErr != nil {
				if err == nil {
					t.Fatal("expected error, got nil")
				}

				// Handle sentinel error specifically
				if errors.Is(tt.wantErr, ErrNoAuthHeaderIncluded) {
					if !errors.Is(err, ErrNoAuthHeaderIncluded) {
						t.Errorf("got error %v, want %v", err, tt.wantErr)
					}
				} else if err.Error() != tt.wantErr.Error() {
					t.Errorf("got error %q, want %q", err.Error(), tt.wantErr.Error())
				}
			} else {
				if err != nil {
					t.Errorf("unexpected error: %v", err)
				}
			}
		})
	}
}
