package auth

import (
 "errors"
 "net/http"
 "strings"
)

var ErrNoAuthHeaderIncluded = errors.New("no authorization header included")

func GetAPIKey(headers http.Header) (string, error) {
 authHeader := strings.TrimSpace(headers.Get("Authorization"))
 if authHeader == "" {
  return "", ErrNoAuthHeaderIncluded
 }

 const prefix = "ApiKey "
 if !strings.HasPrefix(authHeader, prefix) {
  return "", errors.New("malformed authorization header")
 }

 key := strings.TrimSpace(strings.TrimPrefix(authHeader, prefix))
 if key == "" {
  return "", errors.New("malformed authorization header")
 }

 return key, nil
}
