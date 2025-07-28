
CUDA_VISIBLE_DEVICES=3 accelerate launch val_patches.py         --config configs/val/val_terediff_patches.yaml \
                                                        --config_testr testr/configs/TESTR/TESTR_R_50_Polygon_Chinese.yaml \

