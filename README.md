### 环境准备

- 创建docker网络

```shell
docker network create infra-net
```

- docker启动Qdrant

```shell
docker run -d \
  --name qdrant \
  --network infra-net \
  --restart unless-stopped \
  -p 6333:6333 \
  -p 6334:6334 \
  -v qdrant-data:/qdrant/storage \
  qdrant/qdrant:v1.8.4

# 验证
curl http://localhost:6333/healthz
```


- 安装embedding服务

```shell
# 官网下载 Ollama
https://ollama.com/download

# 拉取模型
ollama run mxbai-embed-large

# 验证环境
ollama run mxbai-embed-large "广东省电视业务支持用户主动申请停机保号"
```

- 查看模型维度

```shell
# 查看模型维度
curl http://localhost:11434/api/show -d '{
  "name": "mxbai-embed-large"
}' | json_pp
```

### 初始化python3项目

- 创建项目结构

```shell
# 确认本机有python3
python3 --version
which python3

# 初始化目录
cd question-to-answer

mkdir -p app tests
touch app/__init__.py
touch README.md
```

- 创建虚拟环境

```shell
# 项目根目录执行
python3 -m venv .venv

# 激活虚拟环境
source .venv/bin/activate

# 验证 which python 指向 .../question-to-answer/.venv/bin/python
# 验证 版本是你刚才的 Python3 版本
which python
python --version

```

- 安装依赖

```shell
pip install fastapi "uvicorn[standard]" qdrant-client requests python-dotenv

# 验证安装 
python -c "import fastapi, uvicorn, qdrant_client, requests; print('deps ok')"

```


### 项目运行

- 初始化数据

```shell
source .venv/bin/activate
python -m app.ingest

# 验证
curl -s http://127.0.0.1:6333/collections | head

# {"result":{"collections":[{"name":"policy_qa"}]},"status":"ok","time":3e-6}%
```

- 启动服务

```shell
uvicorn app.main:app --reload --port 10082

```

- 测试

```
curl -s http://127.0.0.1:10082/answer \
  -H "Content-Type: application/json" \
  -d '{"question":"广东省电视停机保号最长多久？"}' | json_pp

```

### 测试
