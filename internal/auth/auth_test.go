package auth

import (
	"net/http"
	"testing"

	"github.com/stretchr/testify/assert"
)

func TestGetApiKey(t *testing.T) {

	const apiKey = "abcdef12345"

	header := http.Header{}
	msg, err := GetAPIKey(header)
	assert.Equal(t, msg, "")
	assert.NotNil(t, err)

	header.Set("Authorization", "API-Key "+apiKey)
	msg, err = GetAPIKey(header)
	assert.Equal(t, msg, "")
	assert.NotNil(t, err)

	header.Set("Authorization", "ApiKey "+apiKey)
	msg, err = GetAPIKey(header)
	if apiKey != msg || err != nil {
		t.Fatalf(`GetAPIKey = %q %v`, msg, err)
	}

}
