package auth

import (
	"log"
	"net/http"
	"reflect"
	"testing"
)

func TestGetAPIKey(t *testing.T) {
	type test struct {
		input http.Header
		want  string
		want2 error
	}

	req, err := http.NewRequest("GET", "google.com", nil)
	if err != nil {
		log.Fatal("Unable to create request")
	}
	req.Header.Set("Authorization", "ApiKey HelloDave")

	req2, _ := http.NewRequest("GET", "google.com", nil)

	tests := []test{
		{input: req.Header, want: "HelloDave", want2: nil},
		{input: req2.Header, want: "", want2: ErrNoAuthHeaderIncluded},
	}

	for _, tc := range tests {
		got, err := GetAPIKey(tc.input)
		if !reflect.DeepEqual(tc.want, got) {
			t.Fatalf("expected: %v, got: %v\n", tc.want, got)
			return
		}
		if tc.want2 != err {
			t.Fatalf("expected: %v, got: %v\n", tc.want2, err)
		}
	}
}
