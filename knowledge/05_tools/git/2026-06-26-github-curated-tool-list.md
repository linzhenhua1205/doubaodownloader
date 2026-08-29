# GitHub 工具大合集 — 开发工具分类参考

> **概要**: GitHub开发工具大合集，按技术站点、平台、语言分类的参考清单
>
> **关键词**: 开发工具 · 技术站点 · 爬虫 · 大数据 · 前端框架

---

## 📑 目录

- [一、技术站点与社区](#一技术站点与社区)
- [二、平台工具](#二平台工具)
- [三、爬虫相关](#三爬虫相关)
- [四、Web 服务器压力测试 / 负载均衡](#四web-服务器压力测试-负载均衡)
- [五、Web 前端](#五web-前端)
  - [框架与库](#框架与库)
  - [CSS 相关](#css-相关)
  - [工具与平台](#工具与平台)
  - [前端设计师资源](#前端设计师资源)
- [六、大数据 / 数据分析 / 分布式](#六大数据-数据分析-分布式)
  - [分布式存储与计算](#分布式存储与计算)
  - [消息队列](#消息队列)
  - [数据库与 NoSQL](#数据库与-nosql)
  - [数据采集与 ETL](#数据采集与-etl)
  - [机器学习与 NLP](#机器学习与-nlp)
  - [可视化](#可视化)
  - [OLAP 与 BI](#olap-与-bi)
  - [MySQL 中间件](#mysql-中间件)
- [七、C & C++](#七c-c)
- [八、游戏开发](#八游戏开发)
- [九、Python](#九python)
- [十、Java](#十java)
- [十一、.NET](#十一net)
- [十二、常用工具](#十二常用工具)
- [十三、日志聚合与分布式日志](#十三日志聚合与分布式日志)
- [十四、音视频 / RTP](#十四音视频-rtp)
- [参考文件](#参考文件)
- [Changelog](#changelog)

---

---

## 一、技术站点与社区

| 站点 | 说明 |
|:-----|:------|
| [Hacker News](https://news.ycombinator.com/) | 编程链接聚合网站 |
| [Programming Reddit](https://www.reddit.com/r/programming/) | 编程社区 |
| [MSDN](https://msdn.microsoft.com/) | 微软官方技术集中地 |
| [InfoQ](https://www.infoq.com/) | 企业级应用，关注软件开发领域 |
| [OSChina](https://www.oschina.net/) | 开源技术社区 |
| [Stack Overflow](https://stackoverflow.com/) | IT 技术问答网站 |
| [GitHub](https://github.com/) | 全球最大源代码管理平台 |
| [DevStore](https://www.devstore.cn/) | 开发者服务商店 |
| [it-ebooks](http://it-ebooks.info/) | 免费 IT 电子书 |

---

## 二、平台工具

| 工具 | 用途 |
|:-----|:-----|
| Redmine / Trac | 项目管理平台 |
| Jenkins / Jira | 持续集成系统 |
| [Sonar](https://www.sonarsource.com/) | 代码质量管理平台 |
| Git / SVN | 源代码版本控制系统 |
| [GitLab](https://gitlab.com/) / Gitorious | 自建 GitHub 服务器 |
| [GitBook](https://www.gitbook.com/) | 写书/写文档 |
| [Travis CI](https://travis-ci.org/) | 开源项目持续集成（与 GitHub 结合） |
| Selenium / OpenQA | 开源测试工具/社区 |
| [Puppet](https://puppet.com/) | 自动管理引擎（配置管理） |
| [Nagios](https://www.nagios.org/) | 系统状态监控报警（Icinga 为兼容替代） |
| [Ganglia](https://ganglia.info/) | 分布式监控系统 |
| fleet | 分布式 init 系统 |

---

## 三、爬虫相关

- **Phantomjs / berserkJS** — 无头浏览器，页面前端监控
- **SlimerJS** — 类似 PhantomJS，基于 Gecko
- **CasperJS** — 导航脚本和测试工具
- **Selenium** — 浏览器自动化测试

---

## 四、Web 服务器压力测试 / 负载均衡

| 工具 | 说明 |
|:-----|:-----|
| **http_load** | 轻量压力测试（<100K） |
| **webbench** | Linux 下压力测试，最多 3 万并发 |
| **ab** (Apache Bench) | Apache 自带压力测试 |
| **Siege** | 开源多用户并发测试 |
| **squid** | 前端缓存 |
| **nginx** | 负载均衡 |
| **HAProxy** | 高性能 TCP/HTTP 负载均衡器 |
| [ElasticSearch](https://www.elastic.co/) | 搜索引擎（基于 Lucene） |
| [Piwik/Matomo](https://matomo.org/) | 开源网站访问量统计 |
| [ClickHeat](https://www.labsmedia.com/clickheat/index.html) | 网站点击热力图 |
| Page Speed SDK / YSLOW | 页面性能分析 |
| [HAR Viewer](http://www.softwareishard.com/har/viewer/) | HAR 分析工具 |
| [Protractor](https://www.protractortest.org/) | E2E 自动化测试 |

---

## 五、Web 前端

### 框架与库

| 工具 | 说明 |
|:-----|:-----|
| [GRUNT](https://gruntjs.com/) | JS 任务运行器 |
| [Sea.js](https://seajs.github.io/seajs/docs/) | JS 模块化 |
| [Knockout.js](https://knockoutjs.com/) | MVVM 开发 |
| [Angular.js](https://angularjs.org/) | 动态 HTML 开发 |
| [Highcharts.js](https://www.highcharts.com/) / Flot | Web 图表 |
| [D3.js](https://d3js.org/) | JavaScript 数据展示库（类似 P5.js） |
| [Raw](https://rawgraphs.io/) | 高级数据可视化 |
| [Rickshaw](https://github.com/shutterstock/rickshaw) | 时序图标库（实时图表） |
| [JavaScript InfoVis Toolkit](https://philogb.github.io/jit/) | Web 数据可视化 |
| [Three.js](https://threejs.org/) | 3D Web 库 |
| [Hightopo](https://www.hightopo.com/) | HTML5 2D/3D 可视化 UI 库 |
| [jQuery.dataTables.js](https://datatables.net/) | 高度灵活的表格插件 |
| [Raphaël](https://dmitrybaranovskiy.github.io/raphael/) | JS Canvas 绘图库 |
| [Pdf.js](https://mozilla.github.io/pdf.js/) | HTML 中展现 PDF |
| [ACE](https://ace.c9.io/) / [CodeMirror](https://codemirror.net/) | HTML 代码编辑器 |
| [impress.js](https://impress.js.org/) / reveal.js | 炫酷内容展示效果 |
| [director.js](https://github.com/flatiron/director) | 前端路由（单页应用） |
| [require.js](https://requirejs.org/) | JS 模块加载库 |
| [select2](https://select2.org/) | 选择框替代库 |
| [AngularUI](https://angular-ui.github.io/) | Angular.js UI 库 |
| [Zepto.js](https://zeptojs.com/) | 移动端替代 jQuery |
| [CreateJS](https://createjs.com/) | HTML5 游戏引擎 |
| [simditor](https://simditor.tower.im/) | 开源 HTML 编辑器 |

### CSS 相关

- **Foundation / Bootstrap / Pure / EasyUI / Polymer** — UI 框架
- **Less / Compass** — 简化 CSS 开发
- **normalize.css** — 跨浏览器渲染一致
- **Animate.css** — CSS 动画库
- **AdminLTE** — Bootstrap3 后台管理框架
- **Respond.js** — IE6-8 支持响应式设计
- **Emmet** — 前端工程师必备（ZenCode 前身）

### 工具与平台

- **bower** — Web 包管理器
- **jsnice** — JS 反编译/猜变量名工具
- **emojify.js** — 网页 Emoji 自动识别显示
- **SuperScrollorama / TweenMax / skrollr** — 视差滚动动画
- **NProcess** — 加载进度条
- **pace.js** — 页面加载进度条

### 前端设计师资源

- [Dribbble](https://dribbble.com/)、[awwwards](https://www.awwwards.com/)、[unmatchedstyle](http://unmatchedstyle.com/)、[UIMaker](http://www.umaker.cn/)
- **图标资源**: IcoMoon、Themify Icons、FreePik、Glyphicons

---

## 六、大数据 / 数据分析 / 分布式

### 分布式存储与计算

| 工具 | 说明 |
|:-----|:-----|
| [Hadoop](https://hadoop.apache.org/) | 分布式文件系统 + MapReduce |
| [CDH5](https://www.cloudera.com/) | Cloudera Hadoop 分支（集成 Spark） |
| [Ceph](https://ceph.io/) | Linux 分布式文件系统（无中心） |
| [Spark](https://spark.apache.org/) | 大规模流式数据处理 |
| [Spark Streaming](https://spark.apache.org/streaming/) | 基于 Spark 的实时计算框架 |
| [Storm](https://storm.apache.org/) | 实时流数据处理 |
| [Tachyon / Alluxio](https://www.alluxio.io/) | 分布式内存文件系统 |
| [Mesos](https://mesos.apache.org/) | 集群资源管理器 |
| [Impala](https://impala.apache.org/) | 新一代大数据分析引擎（SQL 语义） |
| [SNAPPY](https://github.com/google/snappy) | 快速数据压缩系统 |

### 消息队列

| 工具 | 说明 |
|:-----|:-----|
| [Kafka](https://kafka.apache.org/) | 高吞吐量分布式消息队列 |
| [ActiveMQ](https://activemq.apache.org/) | Apache 开源消息总线 |
| [RabbitMQ](https://www.rabbitmq.com/) | 消息队列 |
| [ZeroMQ](https://zeromq.org/) | 分布式消息队列 |
| MQTT | IBM 即时通讯协议（物联网） |

### 数据库与 NoSQL

- **NoSQL**: Cassandra、MongoDB、CouchDB、Redis、BigTable、HBase、Hypertable、Voldemort、Neo4j

### 数据采集与 ETL

- **日志收集**: scribe、chukwa、kafka、flume
- **ETL**: [Kettle](https://community.hitachivantara.com/s/article/data-integration-kettle)、Pentaho
- **工作流调度**: [Oozie](https://oozie.apache.org/)、Azkaban
- **分布式协调**: [Zookeeper](https://zookeeper.apache.org/)
- **数据源获取**: Flume、Google Refine、ScraperWiki

### 机器学习与 NLP

- **ML**: WEKA、Mahout、scikit-learn、SkyTree
- **NLP**: NLTK、OpenNLP、Boilerpipe、OpenCalais
- **序列化**: JSON、BSON、Thrift、Avro、Protocol Buffers

### 可视化

- GraphViz、Processing、Protovis、Google Fusion Tables、Tableau、**ECharts**（百度）

### OLAP 与 BI

- **Mondrian** — 开源 ROLAP 服务器
- **Pentaho** — 工作流为核心的开源 BI

### MySQL 中间件

- **Cobar** — 阿里巴巴 MySQL 分布式中间件

---

## 七、C & C++

| 工具/库 | 说明 |
|:--------|:-----|
| [Thrift](https://thrift.apache.org/) | 可扩展跨语言服务开发 |
| [libevent](https://libevent.org/) | 事件触发网络库（select/epoll/kqueue） |
| [Boost](https://www.boost.org/) | 准 C++ 标准库 |
| [breakpad](https://chromium.googlesource.com/breakpad/breakpad/) | 崩溃转储和分析模块 |
| PTMalloc / Valgrind / Purify | 内存管理与调试 |
| UI: MFC / BCG / QT / DirectUI | UI 界面框架 |
| [libcef](https://bitbucket.org/chromiumembedded/cef) | 嵌入式 Chrome 内核 |
| [node-webkit / NW.js](https://nwjs.io/) | Node + Webkit 桌面应用 |

---

## 八、游戏开发

| 工具/框架 | 说明 |
|:----------|:-----|
| [MINA](https://mina.apache.org/) | Java 手游/页游服务器（NIO 框架） |
| [Netty](https://netty.io/) | NIO 网络应用框架 |
| HP-Socket | 页游服务器 |
| [OGRE](https://www.ogre3d.org/) | 3D 图形渲染引擎 |
| [OpenVDB](https://www.openvdb.org/) | 梦工厂 C++ 特效库 |
| [cocos2d](https://www.cocos.com/) | 跨平台 2D 游戏引擎 |
| [Unity3D](https://unity.com/) | 跨平台 3D 游戏引擎 |
| Node.js + [Pomelo](https://github.com/NetEase/pomelo) | 网易手游服务器框架 |

---

## 九、Python

| 工具 | 说明 |
|:-----|:-----|
| Eric / Eclipse+pydev | Python IDE |
| [PyWin](https://sourceforge.net/projects/pywin32/) | Win32 API 编程包 |
| [NumPy](https://numpy.org/) / SciPy / Matplotlib | 科学计算 |
| PyQt / PyQwt | GUI 相关 |
| [supervisor](http://supervisord.org/) | 进程监控 |

---

## 十、Java

| 工具/框架 | 说明 |
|:----------|:-----|
| IntelliJ IDEA / Eclipse / Netbeans | IDE |
| Tomcat / Resin / Jetty / WebLogic | Web 服务器 |
| Struts / Spring / Hibernate | 框架 |
| [Netty](https://netty.io/) | NIO 高并发网络编程框架 |
| [MINA](https://mina.apache.org/) | NIO 网络应用程序框架 |
| [jOOQ](https://www.jooq.org/) | ORM 框架 |
| [Activiti](https://www.activiti.org/) | 工作流引擎 |
| [Nutch](https://nutch.apache.org/) | 爬虫项目 |
| [Curator](https://curator.apache.org/) | Netflix Zookeeper 客户端库 |
| [Akka](https://akka.io/) | Actor 模型并发框架 |
| Maven + Artifactory | POM 工具 |
| EclEmma | 覆盖测试 |

---

## 十一、.NET

| 工具/库 | 说明 |
|:--------|:-----|
| Xilium.CefGlue / CefSharp | Chrome 内核 .NET 封装 |
| ILMerge | 合并 DLL 和 exe |
| ILSpy | 开源 .NET 反编译 |
| [NPOI](https://github.com/nissl-lab/npoi) | Excel 操作 |
| [HtmlAgilityPack](https://html-agility-pack.net/) | HTML 解析 |
| [Quartz.NET](https://www.quartz-scheduler.net/) | Job 调度 |
| [SuperSocket](https://github.com/kerryjiang/SuperSocket) | Socket 简化操作 |
| [DocX](https://github.com/Quickshare/DocX) | 未安装 Office 操作 Word |
| [Dapper](https://github.com/DapperLib/Dapper) | 轻量级 ORM |
| [Nancy](https://github.com/NancyFx/Nancy) | 轻量级 HTTP 服务器 |
| [Jexus](https://www.jexus.org/) | Linux 下 ASP.NET 服务器 |
| [Roslyn](https://github.com/dotnet/roslyn) | C# / VB 编译器 |
| ConfuserEx | .NET 混淆工具 |
| [ServiceStack](https://servicestack.net/) | 高性能 REST 服务框架 |
| SmartThreadPool | 高级特性线程池 |
| [Autofac](https://autofac.org/) | 轻量级 IoC 容器 |
| [SignalR](https://dotnet.microsoft.com/en-us/apps/aspnet/signalr) | 实时 Web 功能 |

---

## 十二、常用工具

| 工具 | 说明 |
|:-----|:-----|
| [Fiddler](https://www.telerik.com/fiddler) | Web 前端 HTTP 调试工具 |
| [Wireshark](https://www.wireshark.org/) | 网络数据包分析 |
| [SublimeText](https://www.sublimetext.com/) | 程序员编辑器 |
| [Source Insight](https://www.sourceinsight.com/) | 源代码阅读 |
| [RegexBuddy](https://www.regexbuddy.com/) | 正则表达式测试 |
| [Navicat Premium](https://www.navicat.com/) | 多数据库客户端 |
| [Synergy](https://symless.com/synergy) | 局域网键鼠共享 |
| [Radmin](https://www.radmin.com/) | 远程控制 |
| [Listary](https://www.listary.com/) | Windows 文件搜索增强 |
| [Clover](https://en.ejie.me/) | 资源管理器多标签 |
| [Axure RP](https://www.axure.com/) | 快速原型制作 |
| [MindManager](https://www.mindmanager.com/) | 思维导图 |
| [ngrok](https://ngrok.com/) | 内网穿透 |
| [Pandoc](https://pandoc.org/) | Markdown 文档转换 |
| [LICEcap](https://www.cockos.com/licecap/) | GIF 录制 |
| [Fritzing](https://fritzing.org/) | 电路图绘制 |
| [CheatEngine](https://www.cheatengine.org/) | 内存修改 |
| [tinyproxy](https://tinyproxy.github.io/) | Linux 小型代理服务器 |
| Open DBDiff | SQL Server 数据库同步 |
| [SymmetricDS](https://www.symmetricds.org/) | 数据库同步 |
| Sketch / OmniGraffle | 设计工具 |

---

## 十三、日志聚合与分布式日志

| 工具 | 说明 |
|:-----|:-----|
| Scribe | Facebook 日志收集 |
| [Logstash](https://www.elastic.co/logstash/) | 日志收集系统（ELK 栈） |
| [log.io](http://logio.org/) | Node.js 实时日志收集 |

---

## 十四、音视频 / RTP

- **librtp / JRTPLIB** — RTP 协议实现
- **SDL / ffmpeg / live555 / Speex** — 音视频处理
- **[Red5](https://red5.net/)** — Java Flash 流媒体服务器（MP3/FLV/直播）

---

## 参考文件

> 本文件调用的外部文件与资料（不含被引用情况）。

### 内部知识库引用

- (无)

### 外部资料引用

- 来源: [菜鸟教程 - GitHub上整理的一些工具](https://www.runoob.com/w3cnote/github-tools.html)

---

## Changelog

| 日期 | 版本 | 变更说明 |
|:----|:----|:-----|
| 2026-07-24 | v1.0 | 初始版本 |
