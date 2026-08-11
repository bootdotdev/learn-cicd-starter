package auth_test

import (
	"net/http"
	"testing"

	"github.com/bootdotdev/learn-cicd-starter/internal/auth"
)

func TestGetAPIKeyNoHeader(t *testing.T) {
	_, err := auth.GetAPIKey(http.Header{})

	if err == nil {
		t.Errorf("Get API Key worked despite no headers")
	}

}

func TestGetAPIKey(t *testing.T) {
	_, err := auth.GetAPIKey(http.Header{
		"Authorization": []string{"ApiKey aslhdklash23908743kjshdf"},
	})

	if err != nil {
		t.Errorf("It should work")
	}
}
