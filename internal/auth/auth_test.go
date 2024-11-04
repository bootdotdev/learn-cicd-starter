package auth

import (
	"net/http"
	"testing"

	"github.com/stretchr/testify/assert"
)

func TestGetAPIKey_MalformedAuthHeader(t *testing.T) {
	headers := http.Header{
		"Authorization": []string{},
	}

	result, err := GetAPIKey(headers)
	assert.Error(t, err)
	assert.Equal(t, "", result)
}
