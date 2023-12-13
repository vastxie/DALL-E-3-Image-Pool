## DALL-E 3 绘图池
OpenAI DALL-E 3 中转绘图池，基于多 sess/key + 腾讯云。

## 项目介绍

DALL-E 3 绘图池是一个基于 Flask 构建的 Web 应用，它提供了一个 RESTful API 接口，用于生成使用 OpenAI 的 DALL-E 3 模型创建的图像，并自动将生成的图像上传到腾讯云图床。这个项目能够解决 DALL-E 3 图像链接过段时间失效的问题，并提供以下主要功能：

- **DALL-E 3 绘图**：使用 DALL-E 3 模型根据用户提供的提示生成图像。
- **多 API 密钥轮询**：支持配置多个 API 密钥，轮询使用，以提高请求成功率。
- **密钥失效自动删除**：一旦检测到 API 密钥失效，自动从密钥列表中删除。
- **失败自动重试**：如果生成图像请求失败，将自动重试，直到达到最大重试次数。
- **图像上传至腾讯云图床**：生成的图像会被上传到腾讯云图床。

## 安装步骤

要安装并运行 DALL-E 3 绘图池，请按照以下步骤操作：

1. **克隆仓库**：
```
git clone https://github.com/vastxie/DALL-E-3-Image-Pool.git
cd DALL-E-3-Image-Pool
```

2. **安装依赖**：
```
pip install -r requirements.txt
```

3. **配置环境变量**：
在项目根目录下创建一个 `.env` 文件，并配置以下变量：
```
COS_SECRET_ID=[您的腾讯云 Secret ID]
COS_SECRET_KEY=[您的腾讯云 Secret Key]
COS_REGION=[腾讯云 Bucket 所在地区]
COS_BUCKET_NAME=[腾讯云 Bucket 名称]
SERVICE_API_KEY=[服务 API 密钥]
```

4. **启动应用**：
```
python app.py
```

5. **使用 API**：
发送 POST 请求到 `http(s):ip地址:5000/v1/images/generations` 端点，包含所需的图像生成参数。

## 使用说明

要使用 API 生成图像，请确保您已经获取了相应的 OpenAI API 密钥，并将其添加到 `api_keys.txt` 文件中。每个密钥应该独占一行。

---

文档由 ChatGPT 编写。
