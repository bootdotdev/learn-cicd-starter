package auth

import (
	"testing"
)

func TestGetAPIKey(t *testing.T) {
	tests := []struct {
		name   string
		input  map[string][]string
		result string
	}{
		{
			name: "correct header",
			input: map[string][]string{
				"Authorization": {"ApiKey test"},
			},
			result: "testa",
		},
		{
			name: "incorrect header",
			input: map[string][]string{
				"Authorization": {"NoApiKey test"},
			},
			result: "",
		},
	}

	for _, test := range tests {
		got, _ := GetAPIKey(test.input)
		if got != test.result {
			t.Fatalf("%s failed", test.name)
		}
	}

}
