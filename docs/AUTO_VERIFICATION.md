# AI 配置自动验证功能说明

## 功能概述

保存 AI 配置接口 (`POST /api/user/ai-config`) 现在会**自动验证 API Key 有效性**，只有在验证通过后才会保存配置，避免用户保存无效的 API Key。

## 工作流程

```
用户提交 AI 配置
    ↓
【步骤1】验证 API Key
    ↓
验证失败？
    ↓ 是 → 返回 401/429/504 等错误，不保存配置
    ↓ 否
【步骤2】保存配置到数据库
    ↓
返回保存成功
```

## 错误处理

| 场景 | 返回状态码 | 说明 |
|------|-----------|------|
| API Key 无效或已过期 | 401 | 配置不会被保存 |
| API 请求频率超限 | 429 | 配置不会被保存 |
| API 请求超时 | 504 | 配置不会被保存 |
| API 服务器错误 | 502 | 配置不会被保存 |
| 不支持的提供商 | 400 | 配置不会被保存 |
| 验证成功 | 200 | 配置成功保存 |

## 接口说明

### 保存 AI 配置

**接口地址**：`POST /api/user/ai-config`

**请求参数**：
```json
{
  "provider": "deepseek",
  "api_key": "sk-xxxxx",
  "model_name": "deepseek-chat"  // 可选
}
```

**成功响应（200）**：
```json
{
  "code": 200,
  "message": "AI 配置保存成功",
  "data": {
    "provider": "deepseek",
    "model_name": "deepseek-chat",
    "updated_at": "2026-03-02T14:30:00.000000",
    "verified": true  // 标识已通过验证
  },
  "timestamp": 1772424710405
}
```

**失败响应（401 - API Key 无效）**：
```json
{
  "code": 401,
  "message": "API Key 无效或已过期",
  "data": {
    "provider": "deepseek"
  },
  "timestamp": 1772424710405
}
```

**失败响应（504 - 验证超时）**：
```json
{
  "code": 504,
  "message": "API 请求超时，请检查网络连接",
  "timestamp": 1772424710405
}
```

## 前端使用建议

### 1. 优化用户体验

```typescript
// 保存时显示验证和保存状态
interface SaveAIConfigState {
  isVerifying: boolean;
  isSaving: boolean;
  error: string | null;
}

async function saveAIConfig(config: AIConfigRequest) {
  try {
    // 发送请求（后端会自动验证）
    const response = await fetch('/api/user/ai-config', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(config)
    });

    const result = await response.json();

    if (result.code === 200) {
      toast.success('AI 配置保存成功', {
        description: `${config.provider} API Key 已验证并保存`
      });
      return true;
    } else {
      toast.error('AI 配置保存失败', {
        description: result.message
      });
      return false;
    }
  } catch (error) {
    toast.error('请求失败', {
      description: error.message
    });
    return false;
  }
}
```

### 2. 友好的错误提示

```typescript
function getErrorMessage(code: number, message: string): string {
  const messages = {
    401: 'API Key 无效，请检查 Key 是否正确',
    429: 'API 请求过于频繁，请稍后再试',
    504: '网络连接超时，请检查网络设置',
    502: 'AI 服务暂时不可用，请稍后再试',
    400: '不支持的 AI 提供商'
  };
  return messages[code] || message;
}
```

### 3. 结合独立验证接口

```typescript
// 实时验证（用户输入时）
async function verifyAPIKeyOnInput(apiKey: string) {
  const result = await fetch('/api/user/ai-config/verify', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      provider: 'deepseek',
      api_key: apiKey
    })
  });
  return result.json();
}

// 保存时验证（后端自动验证，无需前端再验证）
async function saveAIConfig(config: AIConfigRequest) {
  const result = await fetch('/api/user/ai-config', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(config)
  });
  return result.json();
}
```

## 测试场景

### 测试 1：无效的 API Key

```bash
curl -X POST "http://localhost:8000/api/user/ai-config" \
  -H "Content-Type: application/json" \
  -d '{
    "provider": "deepseek",
    "api_key": "invalid-key-12345"
  }'
```

**预期结果**：返回 401 错误，配置不保存

### 测试 2：网络超时

```bash
# 可以通过断开网络或使用防火墙模拟
curl -X POST "http://localhost:8000/api/user/ai-config" \
  -H "Content-Type: application/json" \
  -d '{
    "provider": "deepseek",
    "api_key": "sk-xxxxx"
  }'
```

**预期结果**：返回 504 错误，配置不保存

### 测试 3：有效的 API Key（需要真实 Key）

```bash
curl -X POST "http://localhost:8000/api/user/ai-config" \
  -H "Content-Type: application/json" \
  -d '{
    "provider": "deepseek",
    "api_key": "sk-真实的有效key"
  }'
```

**预期结果**：返回 200，配置成功保存

## 注意事项

1. **验证时间**：验证过程通常需要 1-10 秒，请耐心等待
2. **网络要求**：验证接口需要访问 AI 服务商的 API
3. **频率限制**：频繁验证可能触发 AI 服务商的频率限制
4. **安全性**：API Key 会在验证和保存时都进行加密存储
5. **用户体验**：建议在前端显示验证和保存进度，避免重复提交

## 代码变更

### 修改文件
- `backend/api/users.py` - 更新 `save_ai_config` 接口，添加自动验证逻辑

### 关键代码
```python
@router.post("/ai-config")
async def save_ai_config(
    request: AIConfigBase,
    db: Session = Depends(get_db)
):
    """
    保存 AI 配置（自动验证 API Key 有效性）
    """
    # 步骤1：验证 API Key 有效性
    verify_data, verify_status = await UserService.verify_api_key(
        provider=request.provider,
        api_key=request.api_key,
        model=request.model_name
    )

    # 如果验证失败，直接返回错误（不保存配置）
    if verify_status >= 400:
        raise HTTPException(
            status_code=verify_status,
            detail=verify_data
        )

    # 步骤2：验证成功后才保存配置
    data, status_code = UserService.save_ai_config(
        db,
        request.provider,
        request.api_key,
        request.model_name or "deepseek-chat"
    )

    # ... 返回成功响应
```

## 优势

1. **数据质量**：确保只保存有效的 API Key，减少后续错误
2. **用户友好**：在配置阶段就发现问题，而不是使用时才发现
3. **安全性**：避免在数据库中积累无效的配置
4. **调试便利**：明确的错误提示帮助用户快速定位问题
