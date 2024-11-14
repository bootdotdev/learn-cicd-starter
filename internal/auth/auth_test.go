package auth

import (
	"net/http"
	"reflect"
	"testing"
)

func TestApiKey(t *testing.T) {
	tests := []struct {
		name          string
		header        string
		want          string
		expectedError any
	}{
		{name: "Test API Key", header: "ApiKey Igotakey", want: "Igotakey", expectedError: nil},
		{name: "Test API Key", header: "ApiKey Igotakey12344zz.sadf323eww", want: "Igotakey12344zz.sadf323eww", expectedError: nil},
		{name: "Test malformed header", header: "Igotakey", want: "", expectedError: "malformed authorization header"},
		{name: "Test no auth header", header: "", want: "", expectedError: "no authorization header included"},
	}

	for _, test := range tests {
		header := http.Header{}
		header.Add("Authorization", test.header)
		got, err := GetAPIKey(header)
		if err != nil {
			if test.expectedError == nil {
				t.Fatal(err)
			} else {
				if err.Error() != test.expectedError {
					t.Fatalf("%s: want '%v', got '%v'\n", test.name, test.expectedError, err)
				}
			}
		}
		if !reflect.DeepEqual(test.want, got) {
			t.Fatalf("%s: want '%v', got '%v'\n", test.name, test.want, got)
		}
	}
}
