package calculator

import (
	"reflect"
	"testing"
)

func TestAdd(t *testing.T) {
	tests := map[string]struct {
		inputA int
		inputB int
		want   int
	}{
		"simple":    {inputA: 1, inputB: 2, want: 3},
		"wrong sep": {inputA: 5, inputB: 5, want: 10},
	}

	for name, tc := range tests {
		t.Run(name, func(t *testing.T) {
			got := Add(tc.inputA, tc.inputB)
			if !reflect.DeepEqual(tc.want, got) {
				t.Fatalf("expected: %v, got: %v", tc.want, got)
			}
		})
	}
}
