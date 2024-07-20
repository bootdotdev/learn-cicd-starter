package auth

import (
	"net/http"
	"reflect"
	"testing"
)

func TestGetAPIKey(t *testing.T) {
	tests := map[string]struct {
		input       http.Header
		want        string
		expectError error
	}{
		"Simple":          {input: http.Header{"Authorization": []string{"ApiKey abc123"}}, want: "abc123", expectError: nil},
		"No ApiKey":       {input: http.Header{"Authorization": []string{"ApiKey"}}, want: "", expectError: ErrMalformedAuthHeader},
		"Diff prefix":     {input: http.Header{"Authorization": []string{"Bearer abc123"}}, want: "", expectError: ErrMalformedAuthHeader},
		"Empty header":    {input: http.Header{"": []string{""}}, want: "", expectError: ErrNoAuthHeaderIncluded},
		"Missing header":  {input: http.Header{}, want: "", expectError: ErrNoAuthHeaderIncluded},
		"Multiple values": {input: http.Header{"Authorization": []string{"ApiKey abc123", "ApiKey def456"}}, want: "abc123", expectError: nil},
		"Whitespace":      {input: http.Header{"Authorization": []string{"  ApiKey abc123  "}}, want: "", expectError: ErrMalformedAuthHeader},
		"Invalid format":  {input: http.Header{"Authorization": []string{"ApiKeyabc123"}}, want: "", expectError: ErrMalformedAuthHeader},
	}

	for name, test := range tests {
		t.Run(name, func(t *testing.T) {
			got, err := GetAPIKey(test.input)
			if !reflect.DeepEqual(got, test.want) {
				t.Fatalf("expected %q, got %q", test.want, got)
			}
			if (err != nil && test.expectError == nil) || (err == nil && test.expectError != nil) || (err != nil && test.expectError != nil && err.Error() != test.expectError.Error()) {
				t.Fatalf("expected error %v, got %v", test.expectError, err)
			}
		})
	}
}
