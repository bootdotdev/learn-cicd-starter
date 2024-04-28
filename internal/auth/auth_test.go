package auth

import (
	"fmt"
	"net/http"
	"testing"

	"github.com/stretchr/testify/assert"
)

func TestGetAuth(t *testing.T) {
	t.Run("get api key success", func(t *testing.T) {
		apiKey := "test-api-key"
		headers := http.Header{
			"Authorization": {fmt.Sprintf("ApiKey %s", apiKey)},
		}

		result, err := GetAPIKey(headers)

		assert.NoError(t, err)
		assert.Equal(t, apiKey, result)
	})

	t.Run("get api key no header error", func(t *testing.T) {
		result, err := GetAPIKey(nil)

		assert.Equal(t, err, ErrNoAuthHeaderIncluded)
		assert.Equal(t, "", result)
	})

	t.Run("get api key malformed header error", func(t *testing.T) {
		headers := http.Header{
			"Authorization": {"WrongApiKey api-key"},
		}

		result, err := GetAPIKey(headers)

		assert.EqualError(t, err, "malformed authorization header")
		assert.Equal(t, "", result)
	})

}
