#!/bin/sh
export CUDA_VISIBLE_DEVICES=6,7 && export HF_ENDPOINT=https://hf-mirror.com && python llm_planning.py \
    --api_key '' \
    --parse_user_requirement_model "gpt-4o-mini-2024-07-18" \
    --planning_model "gpt-4o-mini-2024-07-18" \
    --output-dir 'planning_result/layout_1' \
    --image-path 'layouts/layout_1.png' \
    --itr 5 \
    --user-input "This is a residential area with supporting facilities and a modern architectural style, emphasizing the combination of functionality and aesthetics. The residential area is equipped with green spaces, children's playgrounds, fitness facilities, and a commercial center to meet the daily needs of residents." \
    --change_threshold 0.15