package auth

import (
	"errors"
	"net/http"
	"testing"
)

func TestGetAPIKey(t *testing.T) {
	t.Run("ExtractingAuthorizationHeader", func(t *testing.T) {
		cases := []http.Header{
			{},
			// {
			// 	"authorization": []string{},
			// },
			{
				"Content-Type": []string{"application/json"},
			},
			// {
			// 	"Content-Type":  []string{"application/json"},
			// 	"authorization": []string{},
			// },
		}

		for _, headers := range cases {
			apiKey, err := GetAPIKey(headers)

			if apiKey != "" {
				t.Errorf("expected empty ApiKey, got %s", apiKey)
			}

			if err == nil {
				t.Error("expected error, got nil")
			}

			expectedErr := ErrNoAuthHeaderIncluded

			if !errors.Is(err, expectedErr) {
				t.Errorf("expected error '%s', got '%s'", expectedErr, err)
			}
		}
	})

	t.Run("ExtractingAPIKey", func(t *testing.T) {
		cases := []http.Header{
			{
				"Authorization": []string{"header"},
			},
			{
				"Authorization": []string{"ApiKey"},
			},
			{
				"Authorization": []string{"qwerty 1234"},
			},
		}

		for _, headers := range cases {
			apiKey, err := GetAPIKey(headers)

			if apiKey != "" {
				t.Errorf("expected empty ApiKey, got %s", apiKey)
			}

			if err == nil {
				t.Error("expected error, got nil")
			}

			expectedErr := errors.New("malformed authorization header")

			if err.Error() != expectedErr.Error() {
				t.Errorf("expected error '%s', got '%s'", expectedErr.Error(), err.Error())
			}
		}
	})
}
