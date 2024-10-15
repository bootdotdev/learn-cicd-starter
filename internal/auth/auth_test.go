package auth

import (
	"errors"
	"net/http"
	"reflect"
	"testing"
)

func TestGetAPIKeyFailed(t *testing.T) {
	fail_header := http.Header{
		"Authorization": {},
	}
	result, err := GetAPIKey(fail_header)
	if !reflect.DeepEqual(result, "") {
		t.Error("Not getting empty string when failed")
	}
	if !errors.Is(err, ErrNoAuthHeaderIncluded) {
		t.Error("Not getting ErrNoAuthHeaderIncluded error.")
	}
}

func TestGetAPIKeyPass(t *testing.T) {
	good_header := http.Header{
		"Authorization": {"ApiKey testest"},
	}
	result, err := GetAPIKey(good_header)
	if err != nil {
		t.Error("Get error from good header", err)
	}
	if result != "testest" {
		t.Error("Not get the correct api key", result)
	}
}
