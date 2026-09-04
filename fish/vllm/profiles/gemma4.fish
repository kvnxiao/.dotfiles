set --function vllm_args \
    --model $model \
    --max-model-len 131072 \
    --max-num-seqs 2 \
    --max-num-batched-tokens 8192 \
    --enable-chunked-prefill \
    --enable-prefix-caching \
    --kv-cache-dtype fp8 \
    --gpu-memory-utilization 0.92 \
    --async-scheduling \
    --enable-auto-tool-choice \
    --tool-call-parser gemma4 \
    --reasoning-parser gemma4 \
    --chat-template examples/tool_chat_template_gemma4.jinja \
    --limit-mm-per-prompt.image 1 \
    --limit-mm-per-prompt.audio 0 \
    --limit-mm-per-prompt.video 0
set --function vllm_verify_log_patterns \
    'Using fp8 data type to store kv cache\.'
