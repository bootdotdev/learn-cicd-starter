package auth

import (
	"net/http"
	"testing"
)

// var ErrOnNoAuthHeaderIncluded = errors.New("no authorization header included")
//
// // GetAPIKey -
// func oGetAPIKey(headers http.Header) (string, error) {
// 	authHeader := headers.Get("Authorization")
// 	if authHeader == "" {
// 		return "", ErrNoAuthHeaderIncluded
// 	}
// 	splitAuth := strings.Split(authHeader, " ")
// 	if len(splitAuth) < 2 || splitAuth[0] != "ApiKey" {
// 		return "", errors.New("malformed authorization header")
// 	}
//
// 	return splitAuth[1], nil
// }

func Test_GetAPIKey_Failure(t *testing.T) {
	header := http.Header{}

	_, err := GetAPIKey(header)

	if err != ErrNoAuthHeaderIncluded {
		t.Errorf("expected error %v; got %v", ErrNoAuthHeaderIncluded, err)
	}
}

func Test_GetAPIKey_Success(t *testing.T) {
	header := http.Header{}
	header.Set("Authorization", "ApiKey validkey")
	key, err := GetAPIKey(header)

	if err != nil {
		t.Fatalf("expected no error: got %v", err)
	}

	expected := "validkey"
	if key != expected {
		t.Errorf("expected %v: got %v", expected, key)
	}

}
