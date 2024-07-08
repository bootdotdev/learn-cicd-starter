package main

import "testing"

func TestGenerateRandomSHA(t *testing.T) {
	sha, err := generateRandomSHA256Hash()
	if err != nil {
		t.Errorf("Unexpected error generating SHA")
	}
	if len(sha) != 64 {
		t.Errorf("Expected 64 bytes, got %d", len(sha))
	}
}
