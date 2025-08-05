package auth

import (
	"errors"
	"net/http/httptest"
	"testing"
)

// No authorization header
// Authorization header is empty
// No ApiKey in the first part
// headers contains 1 part
func TestGetAPIKey(t *testing.T) {
	type test struct {
		name              string
		auth_header_key   string
		auth_header_value string
		wantString        string
		wantError         error
	}

	tests := []test{
		{
			name:              "No Authorization header",
			auth_header_key:   "",
			auth_header_value: "",
			wantString:        "",
			wantError:         ErrNoAuthHeaderIncluded,
		},
		{
			name:              "Authorization header is empty",
			auth_header_key:   "Authorization",
			auth_header_value: "",
			wantString:        "",
			wantError:         ErrNoAuthHeaderIncluded,
		},
		{
			name:              "Headers contains 1 part",
			auth_header_key:   "Authorization",
			auth_header_value: "ApiKey",
			wantString:        "",
			wantError:         ErrMalformedAuthHeader,
		},
		{
			name:              "First part is not ApiKey",
			auth_header_key:   "Authorization",
			auth_header_value: "NotKey mykey",
			wantString:        "",
			wantError:         ErrMalformedAuthHeader,
		},
		{
			name:              "Well formed authorization header",
			auth_header_key:   "Authorization",
			auth_header_value: "ApiKey mykey",
			wantString:        "mykey",
			wantError:         nil,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			req := httptest.NewRequest("GET", "/", nil)
			req.Header.Add(tt.auth_header_key, tt.auth_header_value)

			str, err := GetAPIKey(req.Header)

			if str != tt.wantString {
				t.Fatalf("got: %v; want: %v", str, tt.wantString)
			}

			if errors.Is(err, tt.wantError) {
				t.Fatalf("got: %v; want: %v", err, tt.wantError)
			}
		})
	}
}
