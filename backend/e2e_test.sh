#!/bin/bash
# End-to-end API testing script
# Usage: ./e2e_test.sh

BASE_URL="http://localhost:8000"
THREAD_ID="e2e-test-$(date +%s)"

echo "================================"
echo "BMO Chat API E2E Tests"
echo "Thread ID: $THREAD_ID"
echo "================================"
echo ""

# Health check
echo "1. Health Check"
echo "---------------"
curl -s "$BASE_URL/health" | jq .
echo -e "\n"

# Test TextProcessorTool
echo "2. TextProcessorTool - Uppercase"
echo "---------------------------------"
RESULT=$(curl -s -X POST "$BASE_URL/api/tasks" \
  -H "Content-Type: application/json" \
  -d "{\"task\": \"Convert 'hello world' to uppercase\", \"thread_id\": \"$THREAD_ID\"}")
echo "$RESULT" | jq '{id, output_text, tools_used, steps: [.execution_steps[].description]}'
TASK_ID_1=$(echo "$RESULT" | jq -r '.id')
echo -e "\n"

# Test CalculatorTool
echo "3. CalculatorTool - Arithmetic"
echo "-------------------------------"
RESULT=$(curl -s -X POST "$BASE_URL/api/tasks" \
  -H "Content-Type: application/json" \
  -d "{\"task\": \"What is 25 * 4 + 10?\", \"thread_id\": \"$THREAD_ID\"}")
echo "$RESULT" | jq '{id, output_text, tools_used, steps: [.execution_steps[].description]}'
TASK_ID_2=$(echo "$RESULT" | jq -r '.id')
echo -e "\n"

# Test WeatherMockTool
echo "4. WeatherMockTool - Weather Query"
echo "------------------------------------"
RESULT=$(curl -s -X POST "$BASE_URL/api/tasks" \
  -H "Content-Type: application/json" \
  -d "{\"task\": \"What's the weather like in San Francisco?\", \"thread_id\": \"$THREAD_ID\"}")
echo "$RESULT" | jq '{id, output_text, tools_used, steps: [.execution_steps[].description]}'
TASK_ID_3=$(echo "$RESULT" | jq -r '.id')
echo -e "\n"

# Get all tasks
echo "5. Get All Tasks (limit 3)"
echo "---------------------------"
curl -s "$BASE_URL/api/tasks?limit=3" | jq '[.[] | {id, input_text, tools_used}]'
echo -e "\n"

# Get specific task
echo "6. Get Task by ID ($TASK_ID_1)"
echo "-------------------------------"
curl -s "$BASE_URL/api/tasks/$TASK_ID_1" | jq '{id, input_text, output_text}'
echo -e "\n"

# Get tasks by thread
echo "7. Get Tasks by Thread ($THREAD_ID)"
echo "-------------------------------------"
curl -s "$BASE_URL/api/tasks/thread/$THREAD_ID" | jq '[.[] | {id, input_text}]'
echo -e "\n"

# Test streaming endpoint
echo "8. Streaming Endpoint Test"
echo "---------------------------"
echo "Streaming 'Calculate 7 * 8':"
curl -s -N -X POST "$BASE_URL/api/tasks/stream" \
  -H "Content-Type: application/json" \
  -d "{\"task\": \"Calculate 7 * 8\", \"thread_id\": \"$THREAD_ID\"}" | head -10
echo -e "\n"

# Delete a task
echo "9. Delete Task ($TASK_ID_1)"
echo "----------------------------"
curl -s -X DELETE "$BASE_URL/api/tasks/$TASK_ID_1" | jq .
echo -e "\n"

# Verify deletion
echo "10. Verify Deletion (should return 404)"
echo "----------------------------------------"
curl -s "$BASE_URL/api/tasks/$TASK_ID_1" | jq .
echo -e "\n"

echo "================================"
echo "E2E Tests Complete!"
echo "================================"
