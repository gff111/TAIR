import torch
import torch.nn as nn
from accelerate import Accelerator

# 初始化加速器
accelerator = Accelerator()

# 定义简单模型
model = nn.Sequential(
    nn.Conv2d(3, 64, kernel_size=3),
    nn.ReLU(),
    nn.Linear(64, 10)
)

# 模拟输入数据
inputs = torch.randn(2, 3, 32, 32).to(accelerator.device)
labels = torch.randint(0, 10, (2,)).to(accelerator.device)

# 准备训练组件
criterion = nn.CrossEntropyLoss()
optimizer = torch.optim.Adam(model.parameters())

# 使用accelerator包装
model, optimizer, inputs, labels = accelerator.prepare(
    model, optimizer, inputs, labels
)

# 前向传播
outputs = model(inputs)
loss = criterion(outputs, labels)

# 反向传播（这一步会触发错误）
accelerator.backward(loss)  # 对应报错中的 accelerator.backward(total_loss)