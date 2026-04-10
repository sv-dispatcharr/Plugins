// probe.go — bundled HTTP/TCP health probe for the Go Healthcheck plugin.
// Reads a JSON payload from stdin ({urls: [...], timeout_ms: N}),
// probes each URL concurrently, and writes a JSON result array to stdout.
//
// This file is intentionally written in Go to exercise the CodeQL workflow's
// Go language detection path (go should appear in the scanned-languages list).

package main

import (
	"encoding/json"
	"fmt"
	"io"
	"net/http"
	"os"
	"sync"
	"time"
)

type Input struct {
	URLs      []string `json:"urls"`
	TimeoutMs int      `json:"timeout_ms"`
}

type Result struct {
	URL       string `json:"url"`
	Status    int    `json:"status,omitempty"`
	LatencyMs int64  `json:"latency_ms"`
	Error     string `json:"error,omitempty"`
}

func probe(url string, client *http.Client) Result {
	start := time.Now()
	resp, err := client.Get(url)
	latency := time.Since(start).Milliseconds()
	if err != nil {
		return Result{URL: url, LatencyMs: latency, Error: err.Error()}
	}
	defer resp.Body.Close()
	io.Copy(io.Discard, resp.Body)
	return Result{URL: url, Status: resp.StatusCode, LatencyMs: latency}
}

func main() {
	raw, err := io.ReadAll(os.Stdin)
	if err != nil {
		fmt.Fprintf(os.Stderr, "read stdin: %v\n", err)
		os.Exit(1)
	}

	var input Input
	if err := json.Unmarshal(raw, &input); err != nil {
		fmt.Fprintf(os.Stderr, "parse input: %v\n", err)
		os.Exit(1)
	}

	timeout := time.Duration(input.TimeoutMs) * time.Millisecond
	if timeout <= 0 {
		timeout = 3 * time.Second
	}
	client := &http.Client{Timeout: timeout}

	results := make([]Result, len(input.URLs))
	var wg sync.WaitGroup
	for i, u := range input.URLs {
		wg.Add(1)
		go func(idx int, url string) {
			defer wg.Done()
			results[idx] = probe(url, client)
		}(i, u)
	}
	wg.Wait()

	out, _ := json.MarshalIndent(results, "", "  ")
	fmt.Println(string(out))
}
