# 浏览器安装 `lingtong.crx` 插件指引

> 适用于 Chrome / Chromium 内核浏览器（Chrome、Edge、360 等）。

## 1. 准备工作

- 已打包好的插件文件：`web/lingtong.crx`
- 推荐使用最新版的 Chrome/Edge 浏览器
- 确保浏览器允许开发者模式

## 2. Google Chrome 安装步骤

1. 打开 Chrome，输入 `chrome://extensions/`
2. 右上角打开**开发者模式 (Developer mode)**
3. 直接将 `lingtong.crx` 文件拖入浏览器窗口，按提示安装
4. 如提示“仅允许来自 Chrome 网上应用店的扩展程序”，点击“继续”或改用 `Load unpacked` 方式
5. 安装完成后，浏览器右上角会出现“梦幻灵瞳”扩展图标

### Chrome 无法直接安装 CRX？

1. 将 `lingtong.crx` 后缀改为 `.zip` 并解压
2. 在 `chrome://extensions/` 页面点击“加载已解压的扩展程序”
3. 选择解压后的文件夹（通常为 `web/chrome-extensions/`）
4. 如需更新，重复上述步骤重新加载

## 3. Microsoft Edge 安装步骤

1. 打开 Edge，输入 `edge://extensions/`
2. 打开**开发人员模式**
3. 拖入 `lingtong.crx`，或同样使用“加载解压缩的扩展”选中解压目录
4. 安装完成后，右上角显示扩展图标

## 4. 常见问题

| 问题 | 解决方案 |
| --- | --- |
| 浏览器阻止安装非商店扩展 | 打开开发者模式，选择“仍要保留” |
| 拖入 CRX 没反应 | 改用“加载已解压的扩展程序”方式 |
| 安装后没有图标 | 在扩展管理页确认扩展已启用；若仍无，尝试重启浏览器 |
| 需要更新插件 | 重新生成最新 `lingtong.crx`，在扩展页点“更新”或重新拖入 |

## 5. 安全提示

- CRX 文件来自内部构建，勿随意分发
- 发布前确认 `manifest.json` 中的权限最小化

完成以上步骤即可在浏览器中启用梦幻灵瞳 Chrome 插件。
