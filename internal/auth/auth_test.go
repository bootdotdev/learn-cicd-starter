package auth

import (
	"fmt"
	"net/http"
	"testing"
)

func TestGetAPIKey(t *testing.T) {
	t.Run("returns api key", func(t *testing.T) {
		want := "Test_Key"

		headers := http.Header{}
		headers.Add("Authorization", fmt.Sprintf("ApiKey %s", want))

		got, _ := GetAPIKey(headers)

		if got != want {
			t.Errorf("wanted apiKey %s, got %s", want, got)
		}
	})
}
