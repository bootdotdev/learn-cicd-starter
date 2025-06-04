package auth

import (
	"github.com/bootdotdev/learn-cicd-starter/internal/auth"
	"net/http"
	"testing"
)

func TestGetAPIKey(t *testing.T) {
	tests := []struct {
		name    string
		headers http.Header
		want    string
		wantErr bool
	}{
		// 合法的API Key
		{
			name: "valid api key",
			headers: http.Header{
				"Authorization": {"ApiKey valid_key_123"},
			},
			want:    "valid_key_123",
			wantErr: false,
		},
		// 无Authorization头
		//{
		//	name:    "missing authorization header",
		//	headers: http.Header{},
		//	want:    "",
		//	wantErr: true,
		//},
		//// 只有ApiKey，没有具体的key值
		//{
		//	name: "only ApiKey",
		//	headers: http.Header{
		//		"Authorization": {"ApiKey"},
		//	},
		//	want:    "",
		//	wantErr: true,
		//},
		//// 错误的前缀
		//{
		//	name: "invalid prefix",
		//	headers: http.Header{
		//		"Authorization": {"Bearer valid_key_123"},
		//	},
		//	want:    "",
		//	wantErr: true,
		//},
		// 没有空格分隔
		//{
		//	name: "no space",
		//	headers: http.Header{
		//		"Authorization": {"ApiKeyvalid_key_123"},
		//	},
		//	want:    "",
		//	wantErr: true,
		//},
		// 多空格分隔
		//{
		//	name: "multiple spaces",
		//	headers: http.Header{
		//		"Authorization": {"ApiKey  valid_key_123"},
		//	},
		//	want:    "valid_key_123",
		//	wantErr: false,
		//},
		// 多个Authorization头（取第一个）
		//{
		//	name: "multiple headers",
		//	headers: http.Header{
		//		"Authorization": {"ApiKey key1", "ApiKey key2"},
		//	},
		//	want:    "key1",
		//	wantErr: false,
		//},
		// 空值
		{
			name: "empty value",
			headers: http.Header{
				"Authorization": {""},
			},
			want:    "",
			wantErr: true,
		},
		// 包含多个空格的key
		//{
		//	name: "key with spaces",
		//	headers: http.Header{
		//		"Authorization": {"ApiKey key with spaces"},
		//	},
		//	want:    "key with spaces",
		//	wantErr: false,
		//},
		// 区分大小写
		{
			name: "case sensitive",
			headers: http.Header{
				"Authorization": {"apikey valid_key_123"},
			},
			want:    "",
			wantErr: true,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			got, err := auth.GetAPIKey(tt.headers)
			if (err != nil) != tt.wantErr {
				t.Errorf("GetAPIKey() error = %v, wantErr %v", err, tt.wantErr)
				return
			}
			if got != tt.want {
				t.Errorf("GetAPIKey() = %v, want %v", got, tt.want)
			}
		})
	}
}
