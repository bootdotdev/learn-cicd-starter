package auth // Ensure this matches the package name in your auth.go file

import (
	"net/http"
	"testing"
)

func TestGetAPIKey_Success(t *testing.T) {
	// 1. Arrange: Create a mock header with the correct "ApiKey" prefix
	headers := http.Header{}
	headers.Set("Authorization", "ApiKey red-panda-99")

	// 2. Act: Call your function
	key, err := GetAPIKey(headers)

	// 3. Assert: Verify the key is extracted and no error occurred
	if err != nil {
		t.Fatalf("Expected no error, but got: %v", err)
	}

	if key != "red-panda-99" {
		t.Errorf("Expected key 'red-panda-99', but got: %s", key)
	}
}
