package auth

import (
	"errors"
	"net/http"
	"testing"
)

func headerWithInvalidApiKey() http.Header {
	headers := http.Header{}

	headers.Add("Authorization", "invalid apikey")

	return headers
}

func headersWithValidApiKey() http.Header {
	headers := http.Header{}

	headers.Add("Authorization", "ApiKey asdasdasdasdasdasd")

	return headers
}

// TestGetAPIKey call GetAPIKey.
func TestHeadersEmpty(t *testing.T) {
	type returnValue struct {
		apiKey string
		err    error
	}
	type test struct {
		input http.Header
		want  returnValue
	}

	tests := []test{
		{input: http.Header{}, want: returnValue{apiKey: "", err: errors.New("no authorization header included")}},
		{input: headerWithInvalidApiKey(), want: returnValue{apiKey: "", err: errors.New("malformed authorization header")}},
		{input: headersWithValidApiKey(), want: returnValue{apiKey: "asdasdasdasdasdasd", err: nil}},
	}

	for _, tc := range tests {
		apiKey, err := GetAPIKey(tc.input)
		want := tc.want

		if apiKey != want.apiKey {
			t.Fatalf(`expected: %s, got: %s`, want.apiKey, apiKey)
		}

		if want.err == nil && err == nil {
			continue
		}

		if want.err != nil && err != nil && err.Error() != want.err.Error() {
			t.Fatalf(`expected: %v, got: %v`, want.err, err)
		}
	}
}
