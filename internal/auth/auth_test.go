package auth

import (
	"errors"
	"net/http"
	"testing"
)

func TestEmptyAuthorization(t *testing.T) {
	_, err := GetAPIKey(http.Header{"Authorization": {}})
	if !errors.Is(err, ErrNoAuthHeaderIncluded) {
		t.Fatal("")
	}
}
