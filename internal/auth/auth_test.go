package auth

import (
	"net/http"
	"reflect"
	"testing"
)

func TestAuth(t *testing.T) {
	tests := map[string]struct {
		input http.Header
		want  string
	}{
		"Empty headers": {input: http.Header{}, want: ""},
	}

	for name, tc := range tests {
		t.Run(name, func(t *testing.T) {
			got, _ := GetAPIKey(tc.input)
			if !reflect.DeepEqual(got, tc.want) {
				t.Fatalf("Expected %#v, got %#v", got, tc.want)
			}
		})

	}

}
