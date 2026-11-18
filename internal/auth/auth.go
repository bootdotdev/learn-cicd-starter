package auth

import (
	"errors"
	"net/http"
	"strings"
)

// GetAPIKey -
func GetAPIKey(headers http.Header) (string, error) {
	v := headers.Get("Authorization")
	if v == "" {
		return "", errors.New("no authentication info found")
	}
	vals := strings.Split(v, " ")
	if len(vals) != 2 || vals[0] != "ApiKey" {
		return "", errors.New("malformed authorization info")
	}

	return vals[1], nil
}
