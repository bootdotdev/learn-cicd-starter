package auth

import (
	"fmt"
	"net/http"
	"testing"
)

func TestGetAPIKey(t *testing.T) {
	testCases := []struct {
		name   string
		header http.Header
		want   string
	}{
		{name: "abcd", header: http.Header{"Authorization": []string{"ApiKey abcd"}}, want: "abcd"},
		{name: "succeed", header: http.Header{"Authorization": []string{"ApiKey succeed"}}, want: "succeed"},
	}

	fmt.Println("foo")
	for _, tc := range testCases {
		t.Run(tc.name, func(t *testing.T) {
			key, err := GetAPIKey(tc.header)
			if err != nil {
				t.Fatal(err)
			}
			if key != tc.want {
				t.Errorf("GetAPIKey(%+v) == %+v, want %+v", tc.header, key, tc.want)
			}
		})
	}
}
