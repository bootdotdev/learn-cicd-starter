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
    log.Println(apiKey)

    key, _ := GetAPIKey(h)

    log.Printf("Api key: %s", key)

}
