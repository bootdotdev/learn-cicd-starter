package auth

import (
	"net/http"
	"reflect"
	"testing"
)

func TestGetApiKey(t *testing.T) {
	var headerTestOne = http.Header{
		"Authorization": []string{"ApiKey 12345-abcde-67890-fghij"},
	}
	var headerTestTwo = http.Header{
		"Authorization": []string{"ApiKey "},
	}
	type test struct {
		input http.Header
		want  string
	}
	tests := []test{
		{input: headerTestOne, want: "12345-abcde-67890-fghij"},
		{input: headerTestTwo, want: ""},
	}
	for _, tc := range tests {
		got, err := GetAPIKey(tc.input)
		if err != nil {
			t.Fatal(err)
		}
		if !reflect.DeepEqual(tc.want, got) {
			t.Fatalf("expected: %v, got: %v", tc.want, got)
		}
	}
}
