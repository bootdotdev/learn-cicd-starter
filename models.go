package main

import (
	"time"

	"github.com/bootdotdev/learn-cicd-starter/internal/database"
)

type User struct {
	ID        string    `json:"id"`
	CreatedAt time.Time `json:"created_at"`
	UpdatedAt time.Time `json:"updated_at"`
	Name      string    `json:"name"`
	ApiKey    string    `json:"api_key"` // #nosec G117
}

func databaseUserToUser(user database.User) (User, error) {
	createdAt, err := time.Parse(time.RFC3339, user.CreatedAt)
	if err != nil {
		return User{}, err
	}

	updatedAt, err := time.Parse(time.RFC3339, user.UpdatedAt)
	if err != nil {
		return User{}, err
	}
	return User{
		ID:        user.ID,
		CreatedAt: createdAt,
		UpdatedAt: updatedAt,
		Name:      user.Name,
		ApiKey:    user.ApiKey,
	}, nil
}

type Note struct {
	ID        string    `json:"id"`
	CreatedAt time.Time `json:"created_at"`
	UpdatedAt time.Time `json:"updated_at"`
	Note      string    `json:"note"`
	UserID    string    `json:"user_id"`
}

func databaseNoteToNote(post database.Note) (Note, error) {
	createdAt, err := time.Parse(time.RFC3339, post.CreatedAt)
	if err != nil {
		return Note{}, err
	}

	updatedAt, err := time.Parse(time.RFC3339, post.UpdatedAt)
	if err != nil {
		return Note{}, err
	}
	return Note{
		ID:        post.ID,
		CreatedAt: createdAt,
		UpdatedAt: updatedAt,
		Note:      post.Note,
		UserID:    post.UserID,
	}, nil
}

func databasePostsToPosts(notes []database.Note) ([]Note, error) {
	result := make([]Note, len(notes))
	for i, note := range notes {
		var err error
		result[i], err = databaseNoteToNote(note)
		if err != nil {
			return nil, err
		}

	}
	return result, nil
}
