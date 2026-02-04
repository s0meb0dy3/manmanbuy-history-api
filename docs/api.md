# 接口说明

## 端点

- 基础 URL：`https://tool.manmanbuy.com/api.ashx`
- 方法：POST

## 参数（表单编码）

- `method`：`getHistoryTrend`
- `key`：商品链接（例如 JD 商品 URL）
- `t`：本地毫秒时间戳（字符串）
- `token`：生成的签名

## 签名生成（摘要）

1) 按参数 key 排序。
2) 以固定 `salt` 字符串开头。
3) 逐项拼接 key 与 value，并进行 URL 编码（`safe=''` 行为）。
4) 再拼接一次相同的 `salt`。
5) 转大写后 MD5，再将哈希转大写。

## 必要请求头

- `User-Agent`
- `Content-Type`：`application/x-www-form-urlencoded; charset=UTF-8`
- `Origin`：`https://tool.manmanbuy.com`
- `Referer`：`https://tool.manmanbuy.com/HistoryLowest.aspx`
- `X-Requested-With`：`XMLHttpRequest`
- `Authorization`：会话鉴权值（不要公开）
- `Cookie`：会话 Cookie（不要公开）

## 响应结构（示例）

```json
{
  "data": {
    "datePrice": [
      [1730000000, 2999],
      [1730086400, 2899]
    ]
  }
}
```

## 提取规则（摘要）

- `datePrice` 的首个时间戳即为最早记录时间
- 时间戳可能是秒或毫秒：如果大于等于 `1_000_000_000_000`，应视为毫秒并除以 1000
