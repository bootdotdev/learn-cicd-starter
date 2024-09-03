package auth

import (
	"net/http"
	"testing"
)

func TestGetApiKey(t *testing.T) {
	headers := http.Header{}
	headers.Add("Authorization", "ApiKey WhateverKey")

	key, err := GetAPIKey(headers)
	if err != nil {
		t.Fatal(err)
	}

	if key != "WhateverKey" {
		t.Fatal("Api Key does not equal 'WhateverKey'")
	}

	headers = http.Header{}

	key, err = GetAPIKey(headers)
	if err == nil {
		t.Fatal("GetAPIKey should fail with error when not given an Auth header")
	}
}
