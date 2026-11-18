package auth

import (
	"errors"
	"net/http"
	"testing"
)

func TestGetAPIKey(t *testing.T) {
	tests := []struct {
		name       string
		headers    http.Header
		wantKey    string
		wantErr    bool
		wantErrIs  error
		wantErrMsg string
	}{
		// 用例 1：缺失 Authorization 头
		{
			name:      "缺失 Authorization 头",
			headers:   http.Header{},
			wantKey:   "",
			wantErr:   true,
			wantErrIs: ErrNoAuthHeaderIncluded,
		},
		// 用例 2A：前缀错误
		{
			name:       "前缀错误 Bearer 而非 ApiKey",
			headers:    http.Header{"Authorization": []string{"Bearer 12345"}},
			wantKey:    "",
			wantErr:    true,
			wantErrMsg: "malformed authorization header",
		},
		// 用例 2B：只有前缀无 Token
		{
			name:       "只有前缀无 Token",
			headers:    http.Header{"Authorization": []string{"ApiKey"}},
			wantKey:    "",
			wantErr:    true,
			wantErrMsg: "malformed authorization header",
		},
		// 用例 2C：随机内容
		{
			name:       "内容完全随机",
			headers:    http.Header{"Authorization": []string{"randomstuff"}},
			wantKey:    "",
			wantErr:    true,
			wantErrMsg: "malformed authorization header",
		},
		// 用例 3：成功路径
		{
			name:    "格式正确应返回 Key",
			headers: http.Header{"Authorization": []string{"ApiKey 12345-abcde"}},
			wantKey: "12345-abcde",
			wantErr: false,
		},
	}
	// 遍历所有用例
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			gotKey, err := GetAPIKey(tt.headers)

			// 断言 key
			if gotKey != tt.wantKey {
				t.Errorf("key = %q, want %q", gotKey, tt.wantKey)
			}

			// 断言错误存在性
			if (err != nil) != tt.wantErr {
				t.Errorf("error = %v, wantErr = %v", err, tt.wantErr)
				return
			}

			// 断言哨定错误（errors.Is）
			if tt.wantErrIs != nil && !errors.Is(err, tt.wantErrIs) {
				t.Errorf("error = %v, want errors.Is match %v", err, tt.wantErrIs)
			}

			// 断言错误消息内容
			if tt.wantErrMsg != "" && err != nil && err.Error() != tt.wantErrMsg {
				t.Errorf("error msg = %q, want %q", err.Error(), tt.wantErrMsg)
			}
		})
	}
}
