// Code generated by sqlc. DO NOT EDIT.
// versions:
//   sqlc v1.25.0

package database

import ()

type Note struct {
	ID        string
	CreatedAt string
	UpdatedAt string
	Note      string
	UserID    string
}

type User struct {
	ID        string
	CreatedAt string
	UpdatedAt string
	Name      string
	ApiKey    string
}
