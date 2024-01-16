package auth

import (
	"crypto/rand"
	"net/http"
	"testing"
)

func TestGetAPIKey(t *testing.T) {
	var apiKey string
	keyBuf := make([]byte, 32)
	if _, err := rand.Read(keyBuf); err != nil {
		t.Fatal("rand.Read failed")
	}
	apiKey = string(keyBuf)

	tests := []struct {
		name    string
		headers map[string]string
		want    string
	}{
		{"Empty header", map[string]string{}, ""},
		{"Malformed authorization", map[string]string{"Authorization": apiKey}, ""},
		{"Valid authorization", map[string]string{"Authorization": "ApiKey " + apiKey}, apiKey},
	}

	for _, test := range tests {
		t.Run(test.name, func(t *testing.T) {
			headers := make(http.Header)
			for key, val := range test.headers {
				headers.Add(key, val)
			}

			key, err := GetAPIKey(headers)
			if key != test.want {
				t.Fatal(err)
			}
		})
	}
}
