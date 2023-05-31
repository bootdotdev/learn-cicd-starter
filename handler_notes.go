package main

import (
	"encoding/json"
	"net/http"
	"time"

	"github.com/bootdotdev/learn-cicd-starter/internal/database"
	"github.com/go-chi/chi"
	"github.com/google/uuid"
)

func (cfg *apiConfig) handlerNotesGet(w http.ResponseWriter, r *http.Request, user database.User) {
	posts, err := cfg.DB.GetNotesForUser(r.Context(), user.ID)
	if err != nil {
		respondWithError(w, http.StatusInternalServerError, "Couldn't get posts for user")
		return
	}

	respondWithJSON(w, http.StatusOK, databasePostsToPosts(posts))
}

func (cfg *apiConfig) handlerNotesUpdate(w http.ResponseWriter, r *http.Request, user database.User) {
	type parameters struct {
		Note string `json:"note"`
	}
	decoder := json.NewDecoder(r.Body)
	params := parameters{}
	err := decoder.Decode(&params)
	if err != nil {
		respondWithError(w, http.StatusInternalServerError, "Couldn't decode parameters")
		return
	}

	noteID := chi.URLParam(r, "noteID")
	note, err := cfg.DB.GetNote(r.Context(), noteID)
	if err != nil {
		respondWithError(w, http.StatusNotFound, "Couldn't get note")
		return
	}
	if note.UserID != user.ID {
		respondWithError(w, http.StatusForbidden, "Can't update another user's note")
		return
	}

	err = cfg.DB.UpdateNote(r.Context(), database.UpdateNoteParams{
		UpdatedAt: time.Now().UTC(),
		Note:      params.Note,
		ID:        noteID,
	})
	if err != nil {
		respondWithError(w, http.StatusInternalServerError, "Couldn't update note")
		return
	}

	note, err = cfg.DB.GetNote(r.Context(), noteID)
	if err != nil {
		respondWithError(w, http.StatusNotFound, "Couldn't get note")
		return
	}
	respondWithJSON(w, http.StatusOK, databaseNoteToNote(note))
}

func (cfg *apiConfig) handlerNotesDelete(w http.ResponseWriter, r *http.Request, user database.User) {
	noteID := chi.URLParam(r, "noteID")
	note, err := cfg.DB.GetNote(r.Context(), noteID)
	if err != nil {
		respondWithError(w, http.StatusNotFound, "Couldn't get note")
		return
	}
	if note.UserID != user.ID {
		respondWithError(w, http.StatusForbidden, "Can't update another user's note")
		return
	}

	err = cfg.DB.DeleteNote(r.Context(), noteID)
	if err != nil {
		respondWithError(w, http.StatusInternalServerError, "Couldn't delete note")
		return
	}
	respondWithJSON(w, http.StatusOK, struct{}{})
}

func (cfg *apiConfig) handlerNotesCreate(w http.ResponseWriter, r *http.Request, user database.User) {
	type parameters struct {
		Note string `json:"note"`
	}
	decoder := json.NewDecoder(r.Body)
	params := parameters{}
	err := decoder.Decode(&params)
	if err != nil {
		respondWithError(w, http.StatusInternalServerError, "Couldn't decode parameters")
		return
	}

	id := uuid.New().String()
	err = cfg.DB.CreateNote(r.Context(), database.CreateNoteParams{
		ID:        id,
		CreatedAt: time.Now().UTC(),
		UpdatedAt: time.Now().UTC(),
		Note:      params.Note,
		UserID:    user.ID,
	})
	if err != nil {
		respondWithError(w, http.StatusInternalServerError, "Couldn't create note")
		return
	}

	note, err := cfg.DB.GetNote(r.Context(), id)
	if err != nil {
		respondWithError(w, http.StatusNotFound, "Couldn't get note")
		return
	}
	respondWithJSON(w, http.StatusOK, databaseNoteToNote(note))
}
