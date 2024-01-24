package auth

import (
	"net/http"
	"testing"

	"github.com/bootdotdev/learn-cicd-starter/internal/database"
)

type apiConfig struct {
	DB *database.Queries
}

func TestGetApiKey(t *testing.T) {
	req, _ := http.NewRequest("GET", "", nil)
	req.Header.Set("Authorization", "ApiKey value123")
	_, err := GetAPIKey(req.Header)
	if err != nil {
		t.Fatalf("%v", err)
	}
}
