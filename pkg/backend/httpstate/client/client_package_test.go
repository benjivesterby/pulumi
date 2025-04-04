// Copyright 2025, Pulumi Corporation.
//
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
//     http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.

package client

import (
	"bytes"
	"context"
	"encoding/json"
	"errors"
	"net/http"
	"net/http/httptest"
	"testing"

	"github.com/blang/semver"
	"github.com/pulumi/pulumi/sdk/v3/go/common/apitype"
	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
)

var (
	testSchemaData  = []byte(`{"name": "test-package", "version": "1.0.0"}`)
	testReadmeData  = []byte("# Test Package\nThis is a test package")
	testInstallData = []byte("# Installation\nHow to install this package")
)

type testCase struct {
	name             string
	setupServer      func(blobStorage *httptest.Server) *httptest.Server
	setupBlobStorage func() *httptest.Server
	input            *apitype.PackagePublishOp
	errorMessage     string
	httpClient       *http.Client
}

type errorTransport struct {
	roundTripFunc func(*http.Request) (*http.Response, error)
}

func (t *errorTransport) RoundTrip(req *http.Request) (*http.Response, error) {
	return t.roundTripFunc(req)
}

var _ http.RoundTripper = &errorTransport{}

func TestPublishPackage(t *testing.T) {
	t.Parallel()

	tests := []testCase{
		{
			name: "SuccessfulPublish",
			setupBlobStorage: func() *httptest.Server {
				return httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
					w.WriteHeader(http.StatusOK)
				}))
			},
			setupServer: func(blobStorage *httptest.Server) *httptest.Server {
				return httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
					switch r.URL.Path {
					case "/api/preview/registry/packages/pulumi/test-publisher/test-package/versions":
						w.WriteHeader(http.StatusAccepted)
						response := apitype.StartPackagePublishResponse{
							OperationID: "test-operation-id",
							UploadURLs: apitype.PackageUpload{
								Schema:                    blobStorage.URL + "/upload/schema",
								Index:                     blobStorage.URL + "/upload/index",
								InstallationConfiguration: blobStorage.URL + "/upload/install",
							},
							RequiredHeaders: map[string]string{
								"Content-Type": "application/octet-stream",
							},
						}
						require.NoError(t, json.NewEncoder(w).Encode(response))

					case "/api/preview/registry/packages/pulumi/test-publisher/test-package/versions/1.0.0/complete":
						w.WriteHeader(http.StatusCreated)
					}
				}))
			},
		},
		{
			name: "FailedStartPublish",
			setupBlobStorage: func() *httptest.Server {
				return httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
					w.WriteHeader(http.StatusOK)
				}))
			},
			setupServer: func(blobStorage *httptest.Server) *httptest.Server {
				return httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
					if r.URL.Path == "/api/preview/registry/packages/pulumi/test-publisher/test-package/versions" {
						w.WriteHeader(http.StatusInternalServerError)
						_, err := w.Write([]byte("Internal Server Error"))
						require.NoError(t, err)
					}
				}))
			},
			errorMessage: "publish package failed",
		},
		{
			name: "FailedSchemaUpload",
			setupBlobStorage: func() *httptest.Server {
				return httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
					if r.URL.Path == "/upload/schema" {
						w.WriteHeader(http.StatusForbidden)
					} else {
						w.WriteHeader(http.StatusOK)
					}
				}))
			},
			setupServer: func(blobStorage *httptest.Server) *httptest.Server {
				return httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
					switch r.URL.Path {
					case "/api/preview/registry/packages/pulumi/test-publisher/test-package/versions":
						w.WriteHeader(http.StatusAccepted)
						response := apitype.StartPackagePublishResponse{
							OperationID: "test-operation-id",
							UploadURLs: apitype.PackageUpload{
								Schema:                    blobStorage.URL + "/upload/schema",
								Index:                     blobStorage.URL + "/upload/index",
								InstallationConfiguration: blobStorage.URL + "/upload/install",
							},
							RequiredHeaders: map[string]string{
								"Content-Type": "application/octet-stream",
							},
						}
						require.NoError(t, json.NewEncoder(w).Encode(response))
					}
				}))
			},
			errorMessage: "failed to upload schema",
		},
		{
			name: "FailedReadmeUpload",
			setupBlobStorage: func() *httptest.Server {
				return httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
					if r.URL.Path == "/upload/index" {
						w.WriteHeader(http.StatusForbidden)
					} else {
						w.WriteHeader(http.StatusOK)
					}
				}))
			},
			setupServer: func(blobStorage *httptest.Server) *httptest.Server {
				return httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
					switch r.URL.Path {
					case "/api/preview/registry/packages/pulumi/test-publisher/test-package/versions":
						w.WriteHeader(http.StatusAccepted)
						response := apitype.StartPackagePublishResponse{
							OperationID: "test-operation-id",
							UploadURLs: apitype.PackageUpload{
								Schema:                    blobStorage.URL + "/upload/schema",
								Index:                     blobStorage.URL + "/upload/index",
								InstallationConfiguration: blobStorage.URL + "/upload/install",
							},
							RequiredHeaders: map[string]string{
								"Content-Type": "application/octet-stream",
							},
						}
						require.NoError(t, json.NewEncoder(w).Encode(response))
					}
				}))
			},
			errorMessage: "failed to upload index",
		},
		{
			name: "FailedInstallDocsUpload",
			setupBlobStorage: func() *httptest.Server {
				return httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
					if r.URL.Path == "/upload/install" {
						w.WriteHeader(http.StatusForbidden)
					} else {
						w.WriteHeader(http.StatusOK)
					}
				}))
			},
			setupServer: func(blobStorage *httptest.Server) *httptest.Server {
				return httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
					switch r.URL.Path {
					case "/api/preview/registry/packages/pulumi/test-publisher/test-package/versions":
						w.WriteHeader(http.StatusAccepted)
						response := apitype.StartPackagePublishResponse{
							OperationID: "test-operation-id",
							UploadURLs: apitype.PackageUpload{
								Schema:                    blobStorage.URL + "/upload/schema",
								Index:                     blobStorage.URL + "/upload/index",
								InstallationConfiguration: blobStorage.URL + "/upload/install",
							},
							RequiredHeaders: map[string]string{
								"Content-Type": "application/octet-stream",
							},
						}
						require.NoError(t, json.NewEncoder(w).Encode(response))
					}
				}))
			},
			errorMessage: "failed to upload installation configuration",
		},
		{
			name: "FailedCompletePublish",
			setupBlobStorage: func() *httptest.Server {
				return httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
					w.WriteHeader(http.StatusOK)
				}))
			},
			setupServer: func(blobStorage *httptest.Server) *httptest.Server {
				return httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
					switch r.URL.Path {
					case "/api/preview/registry/packages/pulumi/test-publisher/test-package/versions":
						w.WriteHeader(http.StatusAccepted)
						response := apitype.StartPackagePublishResponse{
							OperationID: "test-operation-id",
							UploadURLs: apitype.PackageUpload{
								Schema:                    blobStorage.URL + "/upload/schema",
								Index:                     blobStorage.URL + "/upload/index",
								InstallationConfiguration: blobStorage.URL + "/upload/install",
							},
							RequiredHeaders: map[string]string{
								"Content-Type": "application/octet-stream",
							},
						}
						require.NoError(t, json.NewEncoder(w).Encode(response))
					case "/api/preview/registry/packages/pulumi/test-publisher/test-package/versions/1.0.0/complete":
						w.WriteHeader(http.StatusInternalServerError)
						_, err := w.Write([]byte("Failed to complete"))
						require.NoError(t, err)
					}
				}))
			},
			errorMessage: "failed to complete package publishing operation",
		},
		{
			name: "PublishWithoutInstallDocs",
			setupBlobStorage: func() *httptest.Server {
				return httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
					if r.URL.Path == "/upload/install" {
						// prevent uploading the install docs. If it's attempted the test will fail
						w.WriteHeader(http.StatusForbidden)
					} else {
						w.WriteHeader(http.StatusCreated)
					}
				}))
			},
			setupServer: func(blobStorage *httptest.Server) *httptest.Server {
				return httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
					switch r.URL.Path {
					case "/api/preview/registry/packages/pulumi/test-publisher/test-package/versions":
						w.WriteHeader(http.StatusAccepted)
						response := apitype.StartPackagePublishResponse{
							OperationID: "test-operation-id",
							UploadURLs: apitype.PackageUpload{
								Schema:                    blobStorage.URL + "/upload/schema",
								Index:                     blobStorage.URL + "/upload/index",
								InstallationConfiguration: blobStorage.URL + "/upload/install",
							},
							RequiredHeaders: map[string]string{
								"Content-Type": "application/octet-stream",
							},
						}
						require.NoError(t, json.NewEncoder(w).Encode(response))

					case "/api/preview/registry/packages/pulumi/test-publisher/test-package/versions/1.0.0/complete":
						w.WriteHeader(http.StatusCreated)
					}
				}))
			},
			input: &apitype.PackagePublishOp{
				Source:      "pulumi",
				Publisher:   "test-publisher",
				Name:        "test-package",
				Version:     semver.MustParse("1.0.0"),
				Schema:      bytes.NewReader(testSchemaData),
				Readme:      bytes.NewReader(testReadmeData),
				InstallDocs: nil, // No install docs
			},
		},
		{
			name: "FailedPublish",
			httpClient: &http.Client{
				Transport: &errorTransport{
					roundTripFunc: func(req *http.Request) (*http.Response, error) {
						return nil, errors.New("simulated network error")
					},
				},
			},
			errorMessage: "simulated network error",
			setupBlobStorage: func() *httptest.Server {
				return httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
					w.WriteHeader(http.StatusOK)
				}))
			},
			setupServer: func(blobStorage *httptest.Server) *httptest.Server {
				return httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
					switch r.URL.Path {
					case "/api/preview/registry/packages/pulumi/test-publisher/test-package/versions":
						w.WriteHeader(http.StatusAccepted)
						response := apitype.StartPackagePublishResponse{
							OperationID: "test-operation-id",
							UploadURLs: apitype.PackageUpload{
								Schema:                    blobStorage.URL + "/upload/schema",
								Index:                     blobStorage.URL + "/upload/index",
								InstallationConfiguration: blobStorage.URL + "/upload/install",
							},
							RequiredHeaders: map[string]string{
								"Content-Type": "application/octet-stream",
							},
						}
						require.NoError(t, json.NewEncoder(w).Encode(response))
					}
				}))
			},
		},
		{
			name: "FailedBodyRead",
			httpClient: &http.Client{
				Transport: &errorTransport{
					roundTripFunc: func(req *http.Request) (*http.Response, error) {
						// Return a response with a failing body reader
						return &http.Response{
							StatusCode: 400,
							Status:     "400 Bad Request",
							Body:       failingReadCloser{},
						}, nil
					},
				},
			},
			errorMessage: "failed to upload schema: 400 Bad Request",
			setupBlobStorage: func() *httptest.Server {
				return httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
					w.WriteHeader(http.StatusOK)
				}))
			},
			setupServer: func(blobStorage *httptest.Server) *httptest.Server {
				return httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
					switch r.URL.Path {
					case "/api/preview/registry/packages/pulumi/test-publisher/test-package/versions":
						w.WriteHeader(http.StatusAccepted)
						response := apitype.StartPackagePublishResponse{
							OperationID: "test-operation-id",
							UploadURLs: apitype.PackageUpload{
								Schema:                    blobStorage.URL + "/upload/schema",
								Index:                     blobStorage.URL + "/upload/index",
								InstallationConfiguration: blobStorage.URL + "/upload/install",
							},
							RequiredHeaders: map[string]string{
								"Content-Type": "application/octet-stream",
							},
						}
						require.NoError(t, json.NewEncoder(w).Encode(response))
					}
				}))
			},
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			t.Parallel()
			blobStorage := tt.setupBlobStorage()
			defer blobStorage.Close()
			server := tt.setupServer(blobStorage)
			defer server.Close()

			var httpClient *http.Client
			if tt.httpClient != nil {
				httpClient = tt.httpClient
			} else {
				httpClient = http.DefaultClient
			}

			// Create client pointing to our test server
			client := &Client{
				apiURL:     server.URL,
				apiToken:   "fake-token",
				httpClient: httpClient,
				restClient: &defaultRESTClient{
					client: &defaultHTTPClient{
						client: http.DefaultClient,
					},
				},
			}

			var input apitype.PackagePublishOp
			if tt.input != nil {
				input = *tt.input
			} else {
				input = apitype.PackagePublishOp{
					Source:      "pulumi",
					Publisher:   "test-publisher",
					Name:        "test-package",
					Version:     semver.MustParse("1.0.0"),
					Schema:      bytes.NewReader(testSchemaData),
					Readme:      bytes.NewReader(testReadmeData),
					InstallDocs: bytes.NewReader(testInstallData),
				}
			}

			// Call the function
			err := client.PublishPackage(context.Background(), input)

			// Check results
			if tt.errorMessage != "" {
				require.Error(t, err)
				assert.Contains(t, err.Error(), tt.errorMessage)
			} else {
				require.NoError(t, err)
			}
		})
	}
}

// A ReadCloser that always fails to read
type failingReadCloser struct{}

func (f failingReadCloser) Read(p []byte) (n int, err error) {
	return 0, errors.New("forced read error")
}

func (f failingReadCloser) Close() error {
	return nil
}
