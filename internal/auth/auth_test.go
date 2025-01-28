package auth

import (
	"fmt"
	"net/http"
	"testing"
)

func TestGetAPIKey(t *testing.T) {
	// Arrange: Set up necessary input
	input := http.Header{}
	input.Add("Content-Type", "application/json")
	expected := ""

	// Act: Call the function being tested
	result , status:= GetAPIKey(input)
	fmt.Sprintf("RESULT [%v] STATUS [%v]",result, status)

	// Assert: Compare the result to the expected output
	if result != expected {

		t.Errorf("GetAPIKey(%v) = [%v]; want %v", input, result, expected)
	}
}
