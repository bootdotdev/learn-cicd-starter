package auth

import (
    "net/http"
    "testing"
	"os"
    "log"
)

func TestAPIKey(t *testing.T) {
    h := http.Header{}

    apiKey := os.Getenv("APIKEY")
    h.Add("Authorization", apiKey)

    key, err := GetAPIKey(h)
    if err != nil {
        t.Fatal("Could not load API key")
    }

    log.Printf("Api key: %s", key)

}
