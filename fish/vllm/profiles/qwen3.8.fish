set --function vllm_args \
    --model $model \
    --tensor-parallel-size 1 \
    --dtype bfloat16 \
    --kv-cache-dtype fp8 \
    --attention-backend FLASHINFER \
    --gdn-prefill-backend triton \
    --max-model-len 131072 \
    --max-num-seqs 2 \
    --max-num-batched-tokens 8192 \
    --gpu-memory-utilization 0.93 \
    --enable-chunked-prefill \
    --enable-prefix-caching \
    --seed 1 \
    --enable-auto-tool-choice \
    --tool-call-parser hermes \
    --reasoning-parser qwen3 \
    --trust-remote-code
set --function vllm_verify_log_patterns \
    'Using (FLASHINFER attention backend|FLASHINFER backend\.)' \
    'Using fp8 data type to store kv cache\.' \
    'FlashInfer resolved query dtypes:.*kv_cache_dtype=(fp8|torch\.float8_e4m3fn)' \
    'Using Triton/FLA GDN prefill kernel \(requested=triton,'
