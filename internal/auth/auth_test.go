package auth

import (
	"net/http"
	"testing"
)

func TestGetAPIKey(t *testing.T) {
	headerMap := map[string][]string{
		"Authorization": {"ApiKey abc123"},
	}

	input := []struct {
		header      http.Header
		expectedKey string
	}{
		{
			header:      headerMap,
			expectedKey: "abc123",
		},
	}

	for _, tt := range input {
		apiKey, err := GetAPIKey(tt.header)
		if apiKey != tt.expectedKey {
			t.Fatalf("the actual apiKey=%s does not match the expected=%s\nError:%v", apiKey, tt.expectedKey, err)
		}
	}
}
