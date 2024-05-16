package auth

import (
	"errors"
	"net/http"
	"testing"

	"github.com/stretchr/testify/assert"
)

func TestGetAPIKey(t *testing.T) {
  type test struct {
    input http.Header
    want string
    err error
  }

  tests := []test{
    { input: http.Header{ "Authorization": { "ApiKey 1234" }}, want: "1234", err: nil },
    { input: http.Header{ "Authorization": { "1234" }}, want: "", err: errors.New("malformed authorization header") },
    { input: http.Header{}, want: "", err: ErrNoAuthHeaderIncluded },
  }

  for _, tc := range tests {
    got, err := GetAPIKey(tc.input)
    
    assert.Equal(t, tc.want, got)
    assert.Equal(t, tc.err, err)
  }
}
