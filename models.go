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
	ApiKey    string    `json:"api_key"`
}

func databaseUserToUser(user database.User) User {
	return User{
		ID:        user.ID,
		CreatedAt: user.CreatedAt,
		UpdatedAt: user.UpdatedAt,
		Name:      user.Name,
		ApiKey:    user.ApiKey,
	}
}

type Note struct {
	ID        string    `json:"id"`
	CreatedAt time.Time `json:"created_at"`
	UpdatedAt time.Time `json:"updated_at"`
	Note      string    `json:"note"`
	UserID    string    `json:"user_id"`
}

func databaseNoteToNote(post database.Note) Note {
	return Note{
		ID:        post.ID,
		CreatedAt: post.CreatedAt,
		UpdatedAt: post.UpdatedAt,
		Note:      post.Note,
		UserID:    post.UserID,
	}
}

func databasePostsToPosts(notes []database.Note) []Note {
	result := make([]Note, len(notes))
	for i, note := range notes {
		result[i] = databaseNoteToNote(note)
	}
	return result
}
