package auth_test

import (
	"net/http"
	"testing"

	"github.com/bootdotdev/learn-cicd-starter/internal/auth"
)

func TestGetAPIKey(t *testing.T) {

	type test struct {
		name      string
		input     http.Header
		wantKey   string
		wantError bool
	}

	tests := []test{
		{
			name: "Good Header",
			input: http.Header{
				"Authorization": []string{"ApiKey test"},
			},
			wantKey:   "test",
			wantError: false,
		},
		{
			name: "Absent Authorization Header",
			input: http.Header{
				"Authorization": []string{"ApiKey test"},
			},
			wantKey:   "",
			wantError: true,
		},
		{
			name: "Malformed Authorization Header",
			input: http.Header{
				"Authorization": []string{"ApiKeymalform"},
			},
			wantKey:   "",
			wantError: true,
		},
	}

	for _, test := range tests {

		t.Run(test.name, func(t *testing.T) {
			key, err := auth.GetAPIKey(test.input)
			if (err != nil) != test.wantError {
				t.Errorf("GetAPIKey() error = %v, wantErr = %v", err, test.wantError)
				return
			}

			if key != test.wantKey {
				t.Errorf("GetAPIKey() gotKey = %v, wantKey = %s", key, test.wantKey)
				return
			}
		})

	}

}
