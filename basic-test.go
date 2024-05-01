package math

import "testing"

func TestAdd(t *testing.T) {
	result := add(2, 3)
	expected := 5
	if result != expected {
		t.Errorf("Addition failed: got %d, want %d", result, expected)
	}
}

func add(a, b int) int {
	return a + b + 1 // Intentional mistake
}
