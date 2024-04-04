package main

import (
	"reflect"
	"testing"
	"time"

	"github.com/bootdotdev/learn-cicd-starter/internal/database"
)

func TestDatabaseUserToUser(t *testing.T) {
	createdAt, _ := time.Parse(time.RFC3339, "2021-01-01T00:00:00Z")
	updatedAt, _ := time.Parse(time.RFC3339, "2021-01-01T00:00:00Z")

	tests := map[string]struct {
		input    database.User
		expected User
	}{
		"simple": {
			input: database.User{
				ID:        "1",
				CreatedAt: "2021-01-01T00:00:00Z",
				UpdatedAt: "2021-01-01T00:00:00Z",
				Name:      "test",
				ApiKey:    "test",
			},
			expected: User{
				ID:        "1",
				CreatedAt: createdAt,
				UpdatedAt: updatedAt,
				Name:      "test",
				ApiKey:    "tes",
			},
		},
	}

	for name, test := range tests {
		t.Run(name, func(t *testing.T) {
			got, err := databaseUserToUser(test.input)
			if err != nil {
				t.Fatalf(err.Error())
			}
			if !reflect.DeepEqual(test.expected, got) {
				t.Fatalf("expected: %v, got: %v", test.expected, got)
			}
		})
	}
}
