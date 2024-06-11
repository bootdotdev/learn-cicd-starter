package auth

import (
	"net/http"
	"testing"
)

func TestGetAPIKey(t *testing.T) {
	t.Run("valid authorization header", func(t *testing.T) {
		headers := http.Header{}
		headers.Set("Authorization", "ApiKey 123456")
		got, err := GetAPIKey(headers)
		if err != nil {
			t.Errorf("GetAPIKey() error = %v", err)
			return
		}
		want := "123456"
		if got != want {
			t.Errorf("GetAPIKey() = %v, want %v", got, want)
		}
	})

	t.Run("no authorization header", func(t *testing.T) {
		headers := http.Header{}
		got, err := GetAPIKey(headers)
		if err == nil {
			t.Errorf("GetAPIKey() expected error, got nil")
			return
		}
		if got != "" {
			t.Errorf("GetAPIKey() = %v, want empty string", got)
		}
	})

	t.Run("malformed authorization header", func(t *testing.T) {
		headers := http.Header{}
		headers.Set("Authorization", "Invalid 123456")
		got, err := GetAPIKey(headers)
		if err == nil {
			t.Errorf("GetAPIKey() expected error, got nil")
			return
		}
		if got != "" {
			t.Errorf("GetAPIKey() = %v, want empty string", got)
		}
	})
}
