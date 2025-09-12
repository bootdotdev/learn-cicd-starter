package auth

import (
	"net/http"
	"testing"

	"github.com/stretchr/testify/assert"
)

func TestGetAPIKey(t *testing.T) {
	// Nil auth
	testHeader := http.Header{}
	_, err := GetAPIKey(testHeader)
	assert.Error(t, err)
	assert.Equal(t, ErrNoAuthHeaderIncluded, err)

	// Malformed auth header
	testHeader.Add("Authorization", "bad")
	_, err = GetAPIKey(testHeader)
	assert.Error(t, err)
	assert.Equal(t, "malformed authorization header", err.Error())

	// Happy path
	goodHeader := http.Header{}
	goodHeader.Add("Authorization", "ApiKey token")
	apikey, err := GetAPIKey(goodHeader)
	assert.NoError(t, err)
	assert.Equal(t, "token", apikey)
}
