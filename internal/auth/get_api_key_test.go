package auth

import (
	"testing"
	"net/http"
	"errors"
)

func TestGetAPIKey(t *testing.T) {

	tests := map[string]struct {
		headers http.Header
		want string
		wantErr bool
		expectedErr error
	}{
		"valid API key": {
			headers: http.Header{
				"Authorization": []string{"ApiKey abc123"},
			},
			want: "abc123",
		},

		"missing authorization header": {
			headers: http.Header{},
			wantErr: true,
			expectedErr: ErrNoAuthHeaderIncluded,
		
		},

		"wrong auth scheme": {
			headers: http.Header{
				"Authorization": []string{"Bearer 1234"},
			},
			wantErr: true,
		},
	}

	for name, tt := range tests {
		t.Run(name, func(t *testing.T) {
			got, err := GetAPIKey(tt.headers)

			if tt.wantErr {
				if err == nil {
					t.Fatalf("expected error, got nil")
				}

				if tt.expectedErr != nil && !errors.Is(err, tt.expectedErr) {
					t.Fatalf("expected error %v, got %v", tt.expectedErr, err)
				}		

				return
			}	

			if err != nil {
				t.Fatalf("Unexpected error: %v", err)
			}

			if got != tt.want {
	
				t.Errorf("got %q, want %q", got, tt.want)
			}

		})	
	}

}


