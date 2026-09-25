package auth_test

import (
	"net/http"
	"testing"

	"github.com/bootdotdev/learn-cicd-starter/internal/auth"
	"github.com/stretchr/testify/assert"
)

func TestGetAPIKeyNoValue(t *testing.T) {
	header := make(http.Header)

	header.Set("Authorization", "")
	res, err := auth.GetAPIKey(header)

	assert.Equal(t, "", res)
	assert.Equal(t, auth.ErrNoAuthHeaderIncluded, err)
}

func TestGetAPIKeyNoHeader(t *testing.T) {
	header := make(http.Header)

	header.Set("Content-Type", "application/json")
	res, err := auth.GetAPIKey(header)

	assert.Equal(t, "", res)
	assert.Equal(t, auth.ErrNoAuthHeaderIncluded, err)
}

func TestGetAPIKeyValid(t *testing.T) {
	header := make(http.Header)

	header.Set("Authorization", "ApiKey super-secret-key")
	res, err := auth.GetAPIKey(header)

	assert.Equal(t, "super-secret-key", res)
	assert.Equal(t, nil, err)
}
