CUDA_LAUNCH_BLOCKING=1 CUDA_VISIBLE_DEVICES=3 accelerate launch train.py \
    --config configs/train/train_stage2_terediff_chinese.yaml \
    --config_testr testr/configs/TESTR/TESTR_R_50_Polygon_Chinese.yaml