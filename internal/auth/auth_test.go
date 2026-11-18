package auth

import (
	"net/http"
	"testing"
)

func TestAPIKey(t *testing.T) {
	tests := map[string]struct {
		//input      http.Header
		inputKey   string
		inputValue string
		want       string
		err        bool
	}{
		"empty":                {inputKey: "", inputValue: "", err: true},
		"correct":              {inputKey: "Authorization", inputValue: "ApiKey ", err: false},
		"incorrectHeaderKey":   {inputKey: "auth", inputValue: "ApiKey ", err: true},
		"incorrectHeaderValue": {inputKey: "Authorization", inputValue: "ap", err: true},
	}
	for name, val := range tests {
		t.Run(name, func(t *testing.T) {
			myHeader := http.Header{}
			myHeader.Add(val.inputKey, val.inputValue+"token")
			myStr, err := GetAPIKey(myHeader)
			if err == nil {
				if val.err == true {
					t.Fatalf("%v did not give error when it should have, its value is %v", name, myStr)
				}
			} else {
				if val.err == false {
					t.Fatalf("%v gave an error but it should not have, Error: %v", name, err)
				}
			}
		})
	}
}
