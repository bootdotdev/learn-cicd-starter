package auth

import (
	"log"
	"net/http"
	"os"
	"testing"
)

func TestAPIKey(t *testing.T) {
	h := http.Header{}

	apiKey := os.Getenv("APIKEY")
	h.Add("Authorization", apiKey)
	log.Println(apiKey)

	key, _ := GetAPIKey(h)

	log.Printf("Api key: %s", key)

}
