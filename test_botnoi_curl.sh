#!/bin/bash

# Test Botnoi API with curl
# Make sure to set your API key

API_KEY="${BOTNOI_API_KEY}"

if [ -z "$API_KEY" ]; then
    echo "Error: BOTNOI_API_KEY not set"
    echo "Usage: export BOTNOI_API_KEY=your_key_here"
    exit 1
fi

# Find a test MP3 file
TEST_FILE=$(find backend/uploads -name "*.mp3" | head -1)

if [ -z "$TEST_FILE" ]; then
    echo "Error: No MP3 file found in backend/uploads"
    exit 1
fi

echo "Testing Botnoi API..."
echo "API Key: ${API_KEY:0:10}..."
echo "Test file: $TEST_FILE"
echo ""

echo "=== Test 1: /gensub_upload ==="
curl -v -X POST https://voice.botnoi.ai/gensub_upload \
  -H "botnoi-token: $API_KEY" \
  -F "audio_file=@$TEST_FILE" \
  -F "max_duration=10" \
  -F "max_silence=0.3" \
  -F "language=th" \
  -F "srt=yes"

echo ""
echo ""
echo "=== Test 2: /translate ==="
curl -v -X POST https://voice.botnoi.ai/translate \
  -H "botnoi-token: $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "language": "en",
    "native_style": true,
    "simple_style": true,
    "text": "สวัสดีครับ"
  }'
