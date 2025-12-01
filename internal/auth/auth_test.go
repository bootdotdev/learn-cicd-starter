package auth

import (
	"net/http"
	"testing"
)

func TestGetAPIKey(t *testing.T) {
	headers := make(http.Header)
	headers.Add("Authorization", "ApiKey 010101")

	result, err := GetAPIKey(headers)
	if result != "010101" {
		t.Errorf("GetAPIKey did not obtain key: %v", err)
	}

}

func TestEmptyHeader(t *testing.T) {
	header := make(http.Header)
	header.Add("Content-Type", "application/json")

	result, err := GetAPIKey(header)
	if err == nil {
		t.Errorf("no api key in header, should have errored: %v", err)
	}
	if result != "" {
		t.Errorf("no api key in header, should return empty; %v", result)
	}

}

func TestMislabel(t *testing.T) {
	headers := make(http.Header)
	headers.Add("Authorization", "apiey 010101")

	result, err := GetAPIKey(headers)
	if err == nil {
		t.Errorf("mislabeled header, should have errored: %v", err)
	}
	if result != "" {
		t.Errorf("mislabeled header, should return empty; %v", result)
	}
}

func TestAuthorizationNoAPI(t *testing.T) {
	headers := make(http.Header)
	headers.Add("Authorization", "ApiKey")

	result, err := GetAPIKey(headers)
	if err == nil {
		t.Errorf("authorization value length less than 2, should have errored: %v", err)
	}
	if result != "" {
		t.Errorf("authorization value length less than 2, should return empty; %v", result)
	}

}
