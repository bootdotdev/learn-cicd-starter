package auth

import (
	"net/http"
	"net/http/httptest"
	"testing"
)

func TestGetAPIKey(T *testing.T){
	req := httptest.NewRequest(http.MethodGet, "/api/v1/users", nil)
	req.Header.Set("X-Request-Id", "Test-Header")
	res := httptest.NewRecorder()
	result := res.Result()
 
	_, err := GetAPIKey(result.Header)
	if err == nil {
		T.Errorf("Should not work: %v", err)
	} else {
		T.Logf("Authorization malformating test successuffly fail")
	}

}