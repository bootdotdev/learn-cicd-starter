package auth

import (
	"net/http"
	"testing"

	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
)

func TestGetAPIKey(t *testing.T) {
	// Test: Valid key
	headers := http.Header{}
	headers.Set("Authorization", "ApiKey TestKey")
	apiKey, err := GetAPIKey(headers)
	require.NoError(t, err)
	assert.Equal(t, "TestKey", apiKey)

	// Test: Missing Key
	headers = http.Header{}
	headers.Set("Authorization", "ApiKey")
	apiKey, err = GetAPIKey(headers)
	require.Error(t, err)

	// Test: Missing Header
	headers = http.Header{}
	headers.Set("SomeHeader", "ApiKey")
	apiKey, err = GetAPIKey(headers)
	require.Error(t, err)
}
