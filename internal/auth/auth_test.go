package auth

import (
	"crypto/rand"
	"encoding/hex"
	"fmt"
	"net/http"
	"strings"
	"testing"
)

func TestGetAPIKey(t *testing.T) {

	for i := 0; i < 5; i++ {
		length := 10
		b := make([]byte, length)
		_, err := rand.Read(b)
		if err != nil {
			t.Fatalf("Didet Generate Key: %v", err)
		}
		aut1 := hex.EncodeToString(b)

		testHeat := http.Header{}
		testHeat.Add("Authorization", fmt.Sprintf("ApiKey %v", aut1))

		aut2, err := GetAPIKey(testHeat)

		if err != nil {
			t.Fatalf("Got Error: %v", err)
		}
		if aut1 != aut2 {
			t.Fatalf("expected: %v, got: %v", aut1, aut2)
		}
		t.Log(aut1)
	}
}

func TestMalformed(t *testing.T) {

	for i := 0; i < 5; i++ {
		length := 10
		b := make([]byte, length)
		_, err := rand.Read(b)
		if err != nil {
			t.Fatalf("Didet Generate Key: %v", err)
		}
		aut1 := hex.EncodeToString(b)

		testHeat := http.Header{}
		testHeat.Add("Authorization", fmt.Sprintf("ApiKeys %v", aut1))

		_, err = GetAPIKey(testHeat)

		if err == nil {
			t.Fatalf("Got No Error: %v", err)
		}
	}
}

// Boot tests:

func TestGetAPIKey_Boot(t *testing.T) {
	tests := []struct {
		key       string
		value     string
		expect    string
		expectErr string
	}{
		{
			expectErr: "no authorization header",
		},
		{
			key:       "Authorization",
			expectErr: "no authorization header",
		},
		{
			key:       "Authorization",
			value:     "-",
			expectErr: "malformed authorization header",
		},
		{
			key:       "Authorization",
			value:     "Bearer xxxxxx",
			expectErr: "malformed authorization header",
		},
		{
			key:       "Authorization",
			value:     "ApiKey xxxxxx",
			expect:    "xxxxxx",
			expectErr: "not expecting an error",
		},
	}

	for i, test := range tests {
		t.Run(fmt.Sprintf("TestGetAPIKey Case #%v:", i), func(t *testing.T) {
			header := http.Header{}
			header.Add(test.key, test.value)

			output, err := GetAPIKey(header)
			if err != nil {
				if strings.Contains(err.Error(), test.expectErr) {
					return
				}
				t.Errorf("Unexpected: TestGetAPIKey:%v\n", err)
				return
			}

			if output != test.expect {
				t.Errorf("Unexpected: TestGetAPIKey:%s", output)
				return
			}
		})
	}
}
