package main

import (
	"fmt"
	"net/http"
	"reflect"
	"testing"
	"time"

	"github.com/bootdotdev/learn-cicd-starter/internal/auth"
	"github.com/bootdotdev/learn-cicd-starter/internal/database"
)

func TestGetApiKey(t *testing.T) {
	apiKey, err := generateRandomSHA256Hash()
	if err != nil {
		return
	}

	cases := []struct {
		input http.Header
		want  string
	}{
		{input: http.Header{"Authorization": []string{fmt.Sprintf("ApiKey %v", apiKey)}},
			want: apiKey,
		},
	}

	for i, c := range cases {
		t.Run(fmt.Sprintf("Testing case number %v", i), func(t *testing.T) {
			got, err := auth.GetAPIKey(c.input)
			if err != nil {
				t.Errorf("No proper APIkey in the authorization header provided")
			}
			if !reflect.DeepEqual(c.want, got) {
				t.Errorf("Could not fetch the ApiKey")
			}

		})

	}

}

func TestDBNotestoNotes(t *testing.T) {
	example_time, err := time.Parse(time.RFC3339, "2024-06-18T18:19:06-07:00")
	if err != nil {
		fmt.Printf("Wrong time format: %v\n", example_time)
	}

	cases := []struct {
		input database.Note
		want  Note
	}{
		{input: database.Note{
			ID:        "1",
			CreatedAt: "2024-06-18T18:19:06-07:00",
			UpdatedAt: "2024-06-18T18:19:06-07:00",
			Note:      "Hello this is Julian",
			UserID:    "1",
		},
			want: Note{
				ID:        "1",
				CreatedAt: example_time,
				UpdatedAt: example_time,
				Note:      "Hello this is Julian",
				UserID:    "1",
			},
		},
	}
	for i, c := range cases {
		t.Run(fmt.Sprintf("Test Case number %v", i), func(t *testing.T) {
			got, err := databaseNoteToNote(c.input)
			if err != nil {
				t.Errorf("Could parse the time correctly")
			}
			if !reflect.DeepEqual(c.want, got) {
				t.Errorf("Could not transform the Structs")
			}

		})
	}

}

func TestDBPoststoPosts(t *testing.T) {
	example_time, err := time.Parse(time.RFC3339, "2024-06-18T18:19:06-07:00")
	if err != nil {
		fmt.Printf("Wrong time format: %v\n", example_time)
	}

	cases := []struct {
		input []database.Note
		want  []Note
	}{
		{
			input: []database.Note{
				{
					ID:        "1",
					CreatedAt: "2024-06-18T18:19:06-07:00",
					UpdatedAt: "2024-06-18T18:19:06-07:00",
					Note:      "Hello this is Julian",
					UserID:    "1",
				},
			},
			want: []Note{
				{
					ID:        "1",
					CreatedAt: example_time,
					UpdatedAt: example_time,
					Note:      "Hello this is Julian",
					UserID:    "1",
				},
			},
		},
		// changes the Note field to now get a false test, see if the tests are working
		//{
		//	input: []database.Note{
		//		{
		//			ID:        "1",
		//			CreatedAt: "2024-06-18T18:19:06-07:00",
		//			UpdatedAt: "2024-06-18T18:19:06-07:00",
		//			Note:      "Hello this is Sebi",
		//			UserID:    "1",
		//		},
		//	},
		//	want: []Note{
		//		{
		//			ID:        "1",
		//			CreatedAt: example_time,
		//			UpdatedAt: example_time,
		//			Note:      "Hello this is Julian",
		//			UserID:    "1",
		//		},
		//	},
		//},
	}

	for i, c := range cases {
		t.Run(fmt.Sprintf("Test case number %v:", i), func(t *testing.T) {
			got, err := databasePostsToPosts(c.input)
			if err != nil {
				t.Errorf("Could transform the structs")
			}
			if !reflect.DeepEqual(c.want, got) {
				t.Errorf("Could not get the expected slice")
			}

		})
	}
}
