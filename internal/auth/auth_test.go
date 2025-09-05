package auth

import (
	"net/http"
	"testing"
)

// func TestAut(t *testing.T) {
// 	test := map[string]struct {
// 		input string
// 		want  string
// 	}{
// 		"simple": {"input": "123456", nil, "Want": "12345"},
// 	}
//
// 	for name, tc := range test {
// 		t.Run(name, func(t *testing.T) {
// 			got := GetAPIKey(tc.input)
// 			diff := cmp.Diff(tc.want, got)
// 			if diff != "" {
// 				t.Fatal(diff)
// 			}
// 		})
// 	}
// }

func TestAut(t *testing.T) {
	headers := http.Header{}

	_, err := GetAPIKey(headers)

	if err != ErrNoAuthHeaderIncluded {
		t.Errorf("expected ErrNoAuthHeaderIncluded, got  %v", err)
	}
}
