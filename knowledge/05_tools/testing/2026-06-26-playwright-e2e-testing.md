# Playwright 端到端测试工具详解

> **概要**: Playwright端到端测试工具详解，涵盖定位器、断言、调试与最佳实践
>
> **关键词**: Playwright · E2E测试 · 定位器 · Page Object · CI

---

## 📑 目录

- [一、概述](#一概述)
  - [核心优势](#核心优势)
- [二、核心概念](#二核心概念)
  - [2.1 定位器 (Locators)](#21-定位器-locators)
  - [2.2 Web-first 断言](#22-web-first-断言)
  - [2.3 测试隔离机制](#23-测试隔离机制)
- [三、运行与调试](#三运行与调试)
  - [3.1 运行模式](#31-运行模式)
  - [3.2 调试工具链](#32-调试工具链)
  - [3.3 代码生成 (Codegen)](#33-代码生成-codegen)
- [四、高级功能](#四高级功能)
  - [4.1 Page Object Model (POM)](#41-page-object-model-pom)
  - [4.2 Fixtures（依赖注入）](#42-fixtures依赖注入)
  - [4.3 认证状态复用](#43-认证状态复用)
  - [4.4 网络拦截与 Mock](#44-网络拦截与-mock)
- [五、配置最佳实践](#五配置最佳实践)
  - [CI 推荐配置](#ci-推荐配置)
  - [定位器选择优先级](#定位器选择优先级)
  - [测试设计原则](#测试设计原则)
- [六、与 AI 开发工作流的关系](#六与-ai-开发工作流的关系)
- [七、常见陷阱](#七常见陷阱)
- [关联知识](#关联知识)
- [参考文件](#参考文件)
- [Changelog](#changelog)

---

---

## 一、概述

Playwright 是微软 2020 年开源的一款现代 E2E 测试框架，支持 TypeScript/JavaScript/Python/.NET/Java，驱动 Chromium + Firefox + WebKit 三大浏览器引擎。

### 核心优势

| 特性 | 说明 |
|:-----|:------|
| **自动等待 (Auto-waiting)** | 操作前自动等元素可交互，消除 sleep/显式等待 |
| **内置浏览器** | 自带三大引擎完整包，无需独立配置驱动 |
| **测试隔离** | 每个测试独享 BrowserContext（独立 Cookie/LocalStorage/Session） |
| **并行执行** | 默认多 worker 并行，充分利用多核 |
| **语义化定位器** | 按角色/文本/标签定位，抗 DOM 结构变化 |
| **Web-first 断言** | 自动重试直到条件满足，彻底解决 Flaky Test |
| **调试工具链** | Inspector + Trace Viewer + UI Mode + VS Code 扩展 |

---

## 二、核心概念

### 2.1 定位器 (Locators)

优先级由高到低（**语义化优先，CSS/XPath 兜底**）：

| 方法 | 说明 | 示例 |
|:-----|:-----|:------|
| `getByRole()` | ARIA 角色定位（最推荐） | `page.getByRole('button', { name: '提交' })` |
| `getByText()` | 文本内容 | `page.getByText('欢迎登录')` |
| `getByLabel()` | 表单标签 | `page.getByLabel('用户名')` |
| `getByPlaceholder()` | 占位符 | `page.getByPlaceholder('请输入邮箱')` |
| `getByTestId()` | data-testid 属性 | `page.getByTestId('submit-btn')` |
| `getByAltText()` | 图片 alt | `page.getByAltText('公司Logo')` |
| `locator()` | CSS/XPath（兜底） | `page.locator('.submit-button')` |

**链式过滤精确定位**：

```ts
await page
  .getByRole('listitem')
  .filter({ hasText: '商品2' })
  .getByRole('button', { name: '加入购物车' })
  .click();
```

### 2.2 Web-first 断言

自动重试直到条件满足（默认超时 5s），而非死板的 `expect(await ...)`：

| 断言 | 用途 |
|:-----|:------|
| `toBeVisible()` | 元素可见 |
| `toBeEnabled()` | 可交互（非禁用） |
| `toHaveText()` | 文本精确匹配 |
| `toContainText()` | 文本包含 |
| `toHaveValue()` | 输入框值匹配 |
| `toHaveCount()` | 列表元素数量 |
| `toHaveURL()` | 当前页面 URL |
| `toHaveTitle()` | 页面标题 |

```ts
// ✅ Web-first（自动重试）
await expect(page.getByText('登录成功')).toBeVisible();

// ❌ 立即检查（容易 Flaky）
expect(await page.getByText('成功').isVisible()).toBe(true);
```

**软断言**: `expect.soft()` 收集所有失败后一并报告，不立即中止测试。

### 2.3 测试隔离机制

每个测试独享 `BrowserContext`（= 一个全新的浏览器配置文件），测试间状态完全隔离：

```ts
test('测试A', async ({ page }) => {
  // 独立 BrowserContext，包含独立 Cookie/LocalStorage
});
test('测试B', async ({ page }) => {
  // 完全另一份上下文，互不影响
});
```

---

## 三、运行与调试

### 3.1 运行模式

| 命令 | 说明 |
|:-----|:------|
| `npx playwright test` | 无头模式，并行执行 |
| `npx playwright test --headed` | 有头模式，可见浏览器 |
| `npx playwright test --ui` | **UI Mode**：可视化运行界面，时间旅行调试 |
| `npx playwright test --debug` | 打开 Playwright Inspector 逐步调试 |
| `npx playwright test --project=chromium` | 指定浏览器 |
| `npx playwright test --grep "登录"` | 按名称过滤 |
| `npx playwright test --workers=4` | 控制并行度 |
| `npx playwright test --shard=1/3` | CI 分片（多机并行） |

### 3.2 调试工具链

| 工具 | 命令 | 能力 |
|:-----|:-----|:------|
| **Playwright Inspector** | `--debug` + `page.pause()` | 逐步执行，实时查看元素状态 |
| **UI Mode** | `--ui` | 按文件/描述/单个测试筛选，回溯每一步DOM快照 |
| **Trace Viewer** | `--trace on` + `show-trace` | 完整回放：DOM快照 + 网络请求 + 控制台日志 + 时间线 |
| **VS Code 扩展** | Playwright Test for VSCode | 编辑器中设断点、实时高亮、定位器即时验证 |
| **浏览器控制台** | `PWDEBUG=console` | `playwright.$()` 查找元素、`playwright.selector($0)` 生成定位器 |

### 3.3 代码生成 (Codegen)

```bash
# 录制操作自动生成测试代码
npx playwright codegen https://example.com

# 指定浏览器/设备/输出文件
npx playwright codegen --browser=firefox --device="iPhone 13" --output=tests/recorded.spec.ts

# 带认证状态录制
npx playwright codegen --load-storage=auth.json https://example.com
```

---

## 四、高级功能

### 4.1 Page Object Model (POM)

```ts
// pages/LoginPage.ts
export class LoginPage {
  readonly usernameInput = page.getByLabel('用户名');
  readonly passwordInput = page.getByLabel('密码');
  readonly loginButton = page.getByRole('button', { name: '登录' });

  async login(username: string, password: string) {
    await this.usernameInput.fill(username);
    await this.passwordInput.fill(password);
    await this.loginButton.click();
  }
}
```

### 4.2 Fixtures（依赖注入）

通过 `test.extend` 注入可复用的页面对象/登录态：

```ts
export const test = base.extend<MyFixtures>({
  loggedInPage: async ({ page }, use) => {
    const loginPage = new LoginPage(page);
    await loginPage.login('admin', 'password123');
    await use(page); // 传入测试函数
  },
});
```

### 4.3 认证状态复用

`globalSetup` 登录一次，所有测试复用 Cookie：

```ts
// global-setup.ts
async function globalSetup() {
  const page = await browser.newPage();
  await page.goto('/login');
  await page.getByLabel('用户名').fill('admin');
  await page.getByLabel('密码').fill('password123');
  await page.getByRole('button', { name: '登录' }).click();
  await page.context().storageState({ path: 'auth.json' });
}

// playwright.config.ts
use: { storageState: 'auth.json' }
```

### 4.4 网络拦截与 Mock

```ts
await page.route('**/api/users', async route => {
  await route.fulfill({
    status: 200,
    contentType: 'application/json',
    body: JSON.stringify([{ id: 1, name: '张三' }]),
  });
});
```

---

## 五、配置最佳实践

### CI 推荐配置

```ts
export default defineConfig({
  retries: process.env.CI ? 2 : 0,
  workers: process.env.CI ? 1 : undefined,
  reporter: process.env.CI ? 'github' : 'list',
  use: {
    trace: 'on-first-retry',
    screenshot: 'only-on-failure',
    video: 'on-first-retry',
  },
});
```

### 定位器选择优先级

```text
getByRole > getByLabel > getByPlaceholder/getByText
  > getByTestId > locator(CSS) > locator(XPath)
```

### 测试设计原则

1. **面向用户行为，而非实现细节** — 不要依赖 CSS 类名/内部函数名
2. **测试相互独立** — 每个测试可独立运行，不依赖执行顺序
3. **优先 Web-first 断言** — 自动等待消除 Flaky
4. **不测试第三方服务** — 对外部依赖用 `page.route()` Mock

---

## 六、与 AI 开发工作流的关系

在 AI 辅助代码开发（Claude Code、GitHub Copilot 等）中，Playwright 扮演 E2E **验收标准**角色：

```text
AI 生成代码 -> 修改 -> 运行 Playwright E2E 测试 -> 验证功能正确性
                                      v 失败
                                  AI 修复 -> 重新运行
```

AI 开发者需要：

- 能审查 AI 生成的测试用例质量
- 为 AI 提供清晰的测试场景描述
- 在 CI 中集成 Playwright 作为质量门禁

---

## 七、常见陷阱

| 问题 | 错误做法 | 正确做法 |
|:-----|:---------|:---------|
| Flaky Test | `page.waitForTimeout(2000)` | 用 Web-first 断言自动等待 |
| 多元素匹配 | 模糊选择器 | 链式 `.filter()` 精确定位 |
| 页面未加载完 | 跳转后立即操作 | `await expect(某元素).toBeVisible()` 后操作 |
| 遗漏 await | 忘记 await 断言或操作 | ESLint `no-floating-promises` |

---

## 关联知识

- [Emoji 使用指南（场景速查）](../../07_industry-research/99_other/2026-06-03-emoji-usage-guide.md) — 测试报告/通知中的统一标记

---

## 参考文件

> 本文件调用的外部文件与资料（不含被引用情况）。

### 内部知识库引用

- [Emoji 使用指南（场景速查）](../../07_industry-research/99_other/2026-06-03-emoji-usage-guide.md) — 关联

### 外部资料引用

- 来源: [johng.cn 博客](https://johng.cn/notes/playwright-e2e-testing)

---

## Changelog

| 日期 | 版本 | 变更说明 |
|:----|:----|:-----|
| 2026-07-24 | v1.0 | 初始版本 |
