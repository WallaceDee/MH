# RoleImage WebComponent 使用说明

## 引入方式

```html
<!-- 只需要引入这一个JS文件，Vue和Element UI都已打包在内 -->
<script src="./role-image.umd.js"></script>
```

## 使用方法

```html
<role-image 
    :equip-sn="'12345'" 
    :image-url="'https://example.com/role.jpg'"
    :image-style="'width: 100px; height: 100px;'"
></role-image>
```

## 属性说明

- `equip-sn`: 装备序列号
- `image-url`: 角色图片URL  
- `image-style`: 图片样式（CSS字符串）

## 特点

✅ **单文件部署**: 只需要一个JS文件，包含所有依赖
✅ **无需外部依赖**: Vue和Element UI都已打包在内
✅ **即插即用**: 引入后直接使用，无需额外配置

## 构建信息

- 构建时间: 2025/8/18 14:17:12
- 输出文件: role-image.umd.js (全量版本)
- 文件大小: 约 2407KB
