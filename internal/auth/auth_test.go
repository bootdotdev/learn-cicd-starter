package auth

import (
	"net/http"
	"testing"

	"github.com/stretchr/testify/assert"
)

func TestGetAPIKey(t *testing.T) {
	testHeader := http.Header{}

	key, err := GetAPIKey(testHeader)
	assert.NotNil(t, err)
	assert.Equal(t, err.Error(), "no authorization header included", "expected error message to be equal")
	assert.Equal(t, key, "", "key should be ''")

	testHeader.Set("Authorization", "")
	key, err = GetAPIKey(testHeader)
	assert.NotNil(t, err)
	assert.Equal(t, err.Error(), "no authorization header included", "expected error message should be equal")
	assert.Equal(t, key, "", "key should be ''")

	testHeader.Set("Authorization", "Bearer thisismyapikey")
	key, err = GetAPIKey(testHeader)
	assert.NotNil(t, err)
	assert.Equal(t, err.Error(), "malformed authorization header", "expected error message should be equal")
	assert.Equal(t, key, "", "key should be ''")

	testHeader.Set("Authorization", "ApiKeythisismyapikey")
	key, err = GetAPIKey(testHeader)
	assert.NotNil(t, err)
	assert.Equal(t, err.Error(), "malformed authorization header", "expected error message should be equal")
	assert.Equal(t, key, "", "key should be ''")

	testHeader.Set("Authorization", "ApiKey thisismyapikey")
	key, err = GetAPIKey(testHeader)
	assert.Nil(t, err)
	assert.Equal(t, key, "thisismyapikey", "they should be equal")

}
