# 📚 bzmh-downloader
![Head diagram](https://github.com/user-attachments/assets/e960c38a-cec4-450f-8cc1-75582dff2f1d)
<p align="center">
  <a href="https://github.com/dddinmx/bzmh-downloader"><img alt="Release" src="https://img.shields.io/badge/crawler-bule"></a>
  <a href="https://github.com/dddinmx/bzmh-downloader"><img alt="Release" src="https://img.shields.io/badge/python-3.8%2B-8A2BE2"></a>
  <a href="https://github.com/dddinmx/bzmh-downloader"><img alt="Release" src="https://img.shields.io/badge/Version-2.3-yellow"></a>
  <a href="https://github.com/dddinmx/hxs-downloader/"><img alt="GitHub Repo stars" src="https://img.shields.io/github/stars/dddinmx/bzmh-downloader?color=gree"></a>
</p>

## ✅ ***v2.3*** 版本，重构前端显示，支持 PWA 模式

**如果本项目对你有帮助，欢迎点个 Star⭐ 支持！你的支持是我持续更新维护的动力🙏**

# 🖥️ 界面

## 桌面端
<img width="2177" height="1302" alt="image" src="https://github.com/user-attachments/assets/d165f130-9c94-462d-93ce-aa1c8adb7711" />

## 移动端
<img width="542" height="574" alt="image" src="https://github.com/user-attachments/assets/04d6b9da-8543-47b9-8489-96825a566a20" />

# 📖 使用方法

#### 📝 步骤

#### 1. 拉取容器

```
docker pull dddinmx/bzmh-downloader:v2.3
```

#### 2.运行命令

```
docker run -d -p 5001:5001 -v /path/bzmh/comic:/app/comic -v /path/bzmh/comic.json:/app/comic.json -v /path/bzmh/instance:/app/instance --name bzmh dddinmx/bzmh-downloader:v2.3 （将 ”/path“ 路径更换为你本地路径）
```

#### 3.运行
```
浏览器访问 http://127.0.0.1:5001 （默认登录信息：admin/123456）
```

# ⚠️ 免责声明

- 本工具仅作学习、研究、交流使用，使用本工具的用户应自行承担风险
- 作者不对使用本工具导致的任何损失、法律纠纷或其他后果负责
- 作者不对用户使用本工具的行为负责，包括但不限于用户违反法律或任何第三方权益的行为

# 💬 其他

任何使用中遇到的问题、任何希望添加的功能，都欢迎提交issue或开discussion交流，我会尽力解决。  
关于IP 被封问题目前已解决，最新测试能稳定下载。  


