package auth

import (
	"net/http"
	"reflect"
	"testing"
)

func TestEmpty(t *testing.T) {
	got, _ := GetAPIKey(http.Header{})
	want := ""
	if !reflect.DeepEqual(want, got) {
		t.Fatalf("expected: %v, got: %v", want, got)
	}
}

func TestEmptyAuth(t *testing.T) {
	var test_header = http.Header{}
	test_header.Add("Authorization", "")
	got, _ := GetAPIKey(test_header)
	want := ""
	if !reflect.DeepEqual(want, got) {
		t.Fatalf("expected: %v, got: %v", want, got)
	}
}

func TestCorrectAuth(t *testing.T) {
	var test_header = http.Header{}
	test_header.Add("Authorization", "ApiKey AGjdgdagd843qjfagdkadgkjdg93tadjdkgsgda9dgasfgdkagahfsas")
	got, _ := GetAPIKey(test_header)
	want := "AGjdgdagd843qjfagdkadgkjdg93tadjdkgsgda9dgasfgdkagahfsas"
	if !reflect.DeepEqual(want, got) {
		t.Fatalf("expected: %v, got: %v", want, got)
	}
}
