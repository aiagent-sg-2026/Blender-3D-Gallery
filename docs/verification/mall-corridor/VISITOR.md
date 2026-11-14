# Controllable visitor — local corridor

日期：2026-11-15，Asia/Singapore。此实现把现有 GJH Mall Visitor 接入双店铺 Web 样板，使用原始 GLB 和 idle / walk 片段；没有修改角色源文件、建筑 GLB 或 Gallery 正式查看器。

## 使用

运行 npm run dev -- --port 4173 --strictPort，打开[本地走廊](http://127.0.0.1:4173/docs/verification/mall-corridor/)。

- 点击 Walk visitor，使用 W A S D、方向键或左下拖动摇杆行走。
- Open / Close doors 控制两店门；角色占据门的扫过区域时拒绝动作，保持原姿态。
- Stop walking 或 Escape 返回查看模式。More views 暂停行走，打开独立的查看选项；面板覆盖画面而不压缩 canvas。
- Reset visitor 清除输入并返回入口。触控取消、捕获丢失、窗口失焦、隐藏页面、焦点转移和模式切换均清除移动输入；按键自动重复不会恢复已清除的旧输入。

## 角色、动画与碰撞

[角色来源](../../../models/gjh-mall-visitor/README.md)：原生米制、高约 1.72 m，脚底在零标高，正面为 glTF +Z。运行时不缩放模型，位置和碰撞由本样板控制。

源 GLB SHA-256 为 43d08b67f4450b6aac478cfca4ca664044662cd79021ed15d55ef5612e312be2。源动画为原地动作，场景另行施加水平位移。根据实际移动量选择 idle / walk，阻挡时返回 idle，正常状态使用权重过渡；reduced-motion 模式保留操作位移，暂停装饰性骨骼动画。

对每个源片段的 121 个姿态测量了实际变换顶点；walk 平面最大半径约 0.543 m。因此使用半径 0.56 m、高 1.8 m 的保守直立圆柱，避免沿用此前更小的路线代理冒充真实角色。移动速度上限 0.95 m/s，单次碰撞子步不超过 0.025 m；帧间隔上限 0.05 s，显示循环上限 30 帧/秒，不能据此声称设备实测帧率。

碰撞读取原始环境网格的组件包围盒，在角色高度范围内求变换后 X/Z 凸轮廓，再与角色圆形足迹检查；按小步前进，受阻时尝试沿空闲轴滑动。地面使用实际铺地单元并集，除中心外还检查足迹周围 24 个方向。门使用更新后的真实铰链姿态；改变门角度前按每 1° 检查角色占用，失败则恢复原门角度。

脚底高度采用实际左右脚顶点，不以旋转后的包围盒最低点代替。动画混合后施加有界的整体贴地校正，范围为 ±0.08 m。角色位置根保持在完成面 Y=0；摄像机沿环境包围盒射线缩短距离以避开墙，在近距离遮挡时隐藏角色自身。

这是当前平坦场景的保守碰撞方案。没有重力、台阶、跳跃、斜坡、精确三角面物理或通用寻路；包围盒可能比可见曲面更保守。

## 代码与证据

- [collision.js](collision.js)：体型常量、地面支持、障碍、滑行、门安全切换和摄像机查询。
- [visitor.js](visitor.js)：GLB、动画、脚底校正、输入与行走状态。
- [web.js](web.js)、[style.css](style.css)、[index.html](index.html)：样板接线与响应式控制界面。
- [check-movement.mjs](check-movement.mjs)和[movement-results.json](movement-results.json)：实际场景与源角色的独立 Node 检查。
- [check-visitor-web.mjs](check-visitor-web.mjs)和[浏览器结果](visitor-evidence/results.json)：实际键盘行走、两店进出、门／墙／地面阻挡、关门拒绝、输入取消、触控和布局。

浏览器证据来自安装版 Google Chrome 的有界面自动化。无界面 headless-shell 在本次环境中出现过按钮稳定性和截图超时，这些失败没有计作通过；实际 Chrome 的初步点击另经 Chrome DevTools MCP 复核。触控由 Chrome 原生 CDP 事件注入，手机尺寸为视口模拟，隐藏页面与 blur 场景含显式事件模拟，不能代替真实手机测试。

本地验证不证明 GJH v11 集成或远程部署；未验证真实 iOS/Android、Safari、屏幕阅读器或设备 FPS/内存。角色及原模型的来源和权利说明继续适用。

## 本次执行结果

- node docs/verification/mall-corridor/check-movement.mjs：7 项实际场景移动检查通过；idle / walk 各 121 个源姿态检查通过。
- node docs/verification/mall-corridor/check-visitor-web.mjs：6 组通过。桌面真实键盘进出两店、关闭门阻挡、墙边滑行、地面边界、占用门道拒绝关门、失焦／焦点转移／模拟隐藏、清除后按键重复均覆盖。
- 320×568、390×844、768×1024、844×390 中的原生 CDP 触控移动、取消、捕获释放、停止、菜单开关、canvas 不被菜单压缩及无横向溢出通过；reduced-motion 行走位移与骨骼暂停通过。菜单内容很短，没有需要验证的内部长列表滚动。
- 桌面检查的实际脚底误差为 0；含访客的检查视角为 199 draw calls。没有据此声称真实手机 FPS。
- [源文件哈希与结果索引](visitor-evidence/manifest.json)绑定当前代码、场景和未改动的访客 GLB。截图在同目录，包括 [桌面行走](visitor-evidence/desktop-walking.png)、[进入店 A](visitor-evidence/inside-sample-a.png)、[门道占用](visitor-evidence/door-close-refused.png)、[320 宽触控](visitor-evidence/touch-walking-320.png)、[390 宽触控](visitor-evidence/touch-walking-390.png)。

修复的验证问题包括：以实际脚部顶点代替包围盒高度，捕获释放的逐帧保护，隐藏状态下的实时状态读取，以及查看菜单的同步暂停。脚底校正和输入清除均有对应检查，失败运行未记为通过。

补充检查：[Escape 与独立顶点证明](visitor-evidence/escape-proof.json)确认 Escape 退出并恢复按钮焦点，另从实际场景脚部网格独立读取的最低顶点与地面误差小于 5 mm。更新后的原有查看功能在 1440×900、390×844 两视口回归通过，详见 [web-results.json](web-results.json)。
