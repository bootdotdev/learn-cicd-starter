package auth

import (
	"net/http"
	"testing"
)

type returnData struct {
	apiKey string
	err    error
}

func getTestHeaders() ([]http.Header, error) {
	var headers []http.Header
	headerStr := []string{
		"apikey ajsbdjabdjsakkndklsank",
		"APIKEY fbjaskbjksabdbshj",
		"apiKey asdklnaslkdnalks asndan asklndkla",
		"apiKey asdnalkndklansd",
		"ApiKey asdlaskl asndklandkl",
		"",
		"ApiKey This_is_correct_one",
	}

	req, err := http.NewRequest("GET", "nothing", nil)
	if err != nil {
		return headers, err
	}

	for _, s := range headerStr {
		req.Header.Set("authorization", s)
		headers = append(headers, req.Header)
	}
	return headers, nil
}

func TestAuth(t *testing.T) {
	var got returnData
	headers, err := getTestHeaders()
	if err != nil {
		t.Fatalf("Error getting headers: %v", err)
	}

	for i, h := range headers {
		got.apiKey, got.err = GetAPIKey(h)
		if got.err == nil {
			if got.apiKey != "This_is_correct_one" {
				t.Fatalf("expectedApi: This_is_correct_one	expectedErr: nil\ngotApi: %v	gotErr:%v", got.apiKey, got.err)
			}
			continue
		}
		if got.err == nil {
			t.Fatalf("Test %v: expected error but got API instead: %v", i, got.apiKey)
		}
	}

}
