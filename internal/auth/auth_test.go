package auth_test

import (
	"errors"
	"net/http"
	"reflect"
	"testing"

	"github.com/bootdotdev/learn-cicd-starter/internal/auth"
)

func TestGetAPIKey(t *testing.T) {
	t.Run("success", func(t *testing.T) {
		want := "api_key"
		header := http.Header{
			"Authorization": []string{"ApiKey api_key"},
		}
		result, err := auth.GetAPIKey(header)
		if err != nil {
			t.Fatalf("expected: %v, got: %v", want, err)
		}
		if !reflect.DeepEqual(want, result) {
			t.Fatalf("expected: %v, got: %v", want, result)
		}
	})
	t.Run("error", func(t *testing.T) {
		want := auth.ErrNoAuthHeaderIncluded
		header := http.Header{}
		_, err := auth.GetAPIKey(header)
		if err == nil {
			t.Fatalf("expected: %v, got: %v", want, err)
		} else if !errors.Is(err, auth.ErrNoAuthHeaderIncluded) {
			t.Fatalf("expected: %v, got: %v", want, err)
		}
	})
	t.Run("malformed", func(t *testing.T) {
		want := "malformed authorization header"
		header := http.Header{
			"Authorization": []string{"Bearer api_key"},
		}
		_, err := auth.GetAPIKey(header)
		if err == nil {
			t.Fatalf("expected: %v, got: %v", want, err)
		} else if want != err.Error() {
			t.Fatalf("expected: %v, got: %v", want, err.Error())
		}
	})
}
