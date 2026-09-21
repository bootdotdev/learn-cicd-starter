package auth

import (
	"net/http"
	"testing"
)

func TestGetAPIKey(t *testing.T) {
	tests := []struct {
		header      string
		headerValue string
		wantKey     string
		wantErr     bool
	}{
		{"Authorization", "ApiKey abc123", "abc123", false},
		{"Authorization", "ApiKey abc123 extra", "abc123", false},
		{"Authorization", "abc123 123", "abc123", true},
		{"Authorization", "ApiKey123", "abc123", true},
		{"Authorization ApiKey", "abc123", "abc123", true},
		{"abc123", "abc123", "abc123", true},
		{"", "", "", true},
		// cases here
	}
	for _, testEntry := range tests {
		headers := http.Header{}
		headers.Set(testEntry.header, testEntry.headerValue)

		key, err := GetAPIKey(headers)

		if err != nil {
			if !testEntry.wantErr {
				t.Errorf("%+v expected no error, got %v", testEntry, err)
			}
			continue
		}

		if testEntry.wantErr {
			t.Errorf("%+v expected an error, got nil, key: %v", testEntry, key)
			continue
		}

		if key != testEntry.wantKey {
			t.Errorf("%+v expected key %q, got %q", testEntry, testEntry.wantKey, key)
		}
	}
}
