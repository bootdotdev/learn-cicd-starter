package auth

import (
	"net/http"
	"testing"
)

func TestGetApiKey(t *testing.T) {
	type testResult struct {
		val string
		err error
	}
	type test struct {
		header http.Header
		want   testResult
	}

	headerMalformed := http.Header{}
	headerMalformed.Add("Authorization", "not a valid api key header")

	headerWithApiKey := http.Header{}
	headerWithApiKey.Add("Authorization", "ApiKey testApiKey")

	tests := []test{
		{header: http.Header{}, want: testResult{val: "", err: ErrNoAuthHeaderIncluded}},
		{header: headerMalformed, want: testResult{val: "", err: ErrMalformedAuthHeader}},
		{header: headerWithApiKey, want: testResult{val: "testApiKey", err: nil}},
	}

	for _, tc := range tests {
		gotVal, gotErr := GetAPIKey(tc.header)
		if gotVal != tc.want.val || gotErr != tc.want.err {
			t.Fatalf("expected: %v, got: %v", tc.want, testResult{val: gotVal, err: gotErr})
		}
	}
}
