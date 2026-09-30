package auth

import (
	"net/http"
	"reflect"
	"testing"
)

func TestAPIKey(t *testing.T) {
	type test struct {
		header http.Header
		want   string
	}

	tests := []test{
		{header: http.Header{"Authorization": []string{"ApiKey test"}}, want: "test"},
		{header: http.Header{"Authorization": []string{"ApiKey largerkeytest"}}, want: "largerkeyest"},
	}

	for _, tc := range tests {
		got, err := GetAPIKey(tc.header)
		if err != nil {
			t.Fatalf("Error: %v", err)
		}
		if !reflect.DeepEqual(got, tc.want) {
			t.Fatalf("expected: %v, got: %v", tc.want, got)
		}
	}

}
