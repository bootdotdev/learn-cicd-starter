package database

import (
	"context"
	"database/sql"
	"testing"
)

type mockDBTX struct{}

func (m *mockDBTX) ExecContext(ctx context.Context, query string, args ...interface{}) (sql.Result, error) {
	return nil, nil
}

func (m *mockDBTX) PrepareContext(ctx context.Context, query string) (*sql.Stmt, error) {
	return nil, nil
}

func (m *mockDBTX) QueryContext(ctx context.Context, query string, args ...interface{}) (*sql.Rows, error) {
	return nil, nil
}

func (m *mockDBTX) QueryRowContext(ctx context.Context, query string, args ...interface{}) *sql.Row {
	return nil
}

func TestNew(t *testing.T) {
	db := New(&mockDBTX{})
	if db == nil {
		t.Errorf("New() = nil, want *Queries")
	}
}
