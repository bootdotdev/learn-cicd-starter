package auth

import (
	"net/http"
	"testing"

	"github.com/stretchr/testify/assert"
)

func Test_GetAPIKt(t *testing.T) {
	handler := http.Header{}
	handler.Set("Authorization", "")

	t.Run("No Authorization Header Included", func(t *testing.T) {
		_, err := GetAPIKey(handler)
		assert.Equal(t, err, ErrNoAuthHeaderIncluded)
	})

	handler.Set("Authorization", "Bearer some_token")

	t.Run("Malformed Authorization Header", func(t *testing.T) {
		_, err := GetAPIKey(handler)
		assert.EqualError(t, err, "malformed authorization header")
	})

}
