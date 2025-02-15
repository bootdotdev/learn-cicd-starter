package sqliteparserutils

import (
	"github.com/antlr/antlr4/runtime/Go/antlr/v4"
	"github.com/libsql/sqlite-antlr4-parser/sqliteparser"
)

// TODO: Shell test begin transaction on shell

type SplitStatementExtraInfo struct {
	IncompleteCreateTriggerStatement bool
	IncompleteMultilineComment       bool
	LastTokenType                    int
}

func SplitStatement(statement string) (stmts []string, extraInfo SplitStatementExtraInfo) {
	tokenStream := createTokenStream(statement)

	stmtIntervals := make([]*antlr.Interval, 0)
	currentIntervalStart := -1
	insideCreateTriggerStmt := false
	insideMultilineComment := false

	var previousToken antlr.Token
	var currentToken antlr.Token
	for currentToken = tokenStream.LT(1); currentToken.GetTokenType() != antlr.TokenEOF; currentToken = tokenStream.LT(1) {
		// We break loop here because we're sure multiline comment didn't finished, otherwise lexer would have just ignored
		// it
		if atIncompleteMultilineCommentStart(tokenStream) {
			insideMultilineComment = true
			break
		}

		if currentIntervalStart == -1 {
			if currentToken.GetTokenType() == sqliteparser.SQLiteLexerSCOL {
				previousToken = currentToken
				tokenStream.Consume()
				continue
			}
			currentIntervalStart = currentToken.GetTokenIndex()

			if atCreateTriggerStart(tokenStream) {
				insideCreateTriggerStmt = true
				previousToken = currentToken
				tokenStream.Consume()
				continue
			}

		}

		if insideCreateTriggerStmt {
			if currentToken.GetTokenType() == sqliteparser.SQLiteLexerEND_ {
				insideCreateTriggerStmt = false
			}
		} else if currentToken.GetTokenType() == sqliteparser.SQLiteLexerSCOL {
			stmtIntervals = append(stmtIntervals, antlr.NewInterval(currentIntervalStart, previousToken.GetTokenIndex()))
			currentIntervalStart = -1
		}

		previousToken = currentToken
		tokenStream.Consume()
	}

	if currentIntervalStart != -1 && previousToken != nil {
		stmtIntervals = append(stmtIntervals, antlr.NewInterval(currentIntervalStart, previousToken.GetTokenIndex()))
	}

	stmts = make([]string, 0)
	for _, stmtInterval := range stmtIntervals {
		stmts = append(stmts, tokenStream.GetTextFromInterval(stmtInterval))
	}

	lastTokenType := antlr.TokenInvalidType
	if previousToken != nil {
		lastTokenType = previousToken.GetTokenType()
	}
	return stmts, SplitStatementExtraInfo{IncompleteCreateTriggerStatement: insideCreateTriggerStmt, IncompleteMultilineComment: insideMultilineComment, LastTokenType: lastTokenType}
}

func atCreateTriggerStart(tokenStream antlr.TokenStream) bool {
	if tokenStream.LT(1).GetTokenType() != sqliteparser.SQLiteLexerCREATE_ {
		return false
	}

	if tokenStream.LT(2).GetTokenType() == sqliteparser.SQLiteLexerTRIGGER_ {
		return true
	}

	if tokenStream.LT(2).GetTokenType() == sqliteparser.SQLiteLexerTEMP_ || tokenStream.LT(2).GetTokenType() == sqliteparser.SQLiteLexerTEMPORARY_ &&
		tokenStream.LT(3).GetTokenType() == sqliteparser.SQLiteLexerTRIGGER_ {
		return true
	}

	return false

}

// Note: Only starts for incomplete multiline comments will be detected cause lexer automatically ignores complete
// multiline comments
func atIncompleteMultilineCommentStart(tokenStream antlr.TokenStream) bool {
	if tokenStream.LT(1).GetTokenType() != sqliteparser.SQLiteLexerDIV {
		return false
	}

	if tokenStream.LT(2).GetTokenType() == sqliteparser.SQLiteLexerSTAR {
		return true
	}

	return false
}

func createTokenStream(statement string) *antlr.CommonTokenStream {
	statementStream := antlr.NewInputStream(statement)

	lexer := sqliteparser.NewSQLiteLexer(statementStream)
	return antlr.NewCommonTokenStream(lexer, 0)
}
