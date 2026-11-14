# Two-store corridor sample — A/B/C delivery

验证时间：2026-11-14 至 2026-11-15，Asia/Singapore。已完成门扇净空检查、本地 Gallery 登记，以及复用现有构件的双店铺走廊样板。此目录是独立的几何与显示样板，尚未集成或发布 GJH Foundation v1。

## 打开结果

- [Blender 场景](corridor.blend)、[组合 GLB](corridor.glb)、[布局与输入哈希](layout.json)。
- [Blender 剖切总览](blender-cutaway.png)、[走廊](blender-corridor.png)、[两店开门](blender-open-doors.png)。剖切图隐藏天花以显示室内，完整天花保留在交付场景和 GLB 中。
- [Web 总览](web-cutaway-1440.png)、[入口](web-Arrival-1440.png)、[店 A 手机尺寸](web-Sample-A-390.png)、[店 B](web-Sample-B-1440.png)。
- 运行 npm run dev -- --port 4173 --strictPort，然后打开 [本地预览](http://127.0.0.1:4173/docs/verification/mall-corridor/)。可切换 Overview、Arrival、Sample A/B、开关门、显示/隐藏天花，以及鼠标拖动。

## 尺寸与复用

中央走廊宽 3.6 m、长 7.2 m；左右各一个深 3.6 m、沿走廊宽 4.8 m 的无品牌店铺。共 42 块地板、41 块完整天花加一个柱周收口；两套相同的双开门、两侧玻璃隔断和三段楣板证明复用。布局记录内共 100 个资产实例，另有样板用白盒背墙、侧墙、窄回边及两个 SAMPLE A/B 字牌。白盒墙是样板几何，没有登记为通用模型。字牌使用 Blender 内置 Bfont 转网格。

每店复用一个独立展示架，走廊末端放置长椅，到达处方柱位于走廊侧边。消费端仍须负责真实场景灯光、碰撞和交互；这些无品牌店铺没有被声称为 New Moon 或完整购物体验。

## A · 门与通行空间

旧小样板的开门采样没有发现固定构件碰撞，但门扇顶点投影超出短地面。已在原小样板前方增加一排四块原地砖。[原始失败证据](../p0-assembly/baseline-v1/door-sweep.json)与[修正后结果](../p0-assembly/door-sweep.json)均保留。

走廊中的每店门分别检查左扇单开、右扇单开、双扇开启，每种模式从 0–90°、每 1° 采样一次，共每店 273 个姿态。保守组件 OBB（各轴收缩 10 微米）没有与固定构件或对侧门扇相交，移动顶点投影均在铺地并集内。仅排除原铰链轴上的预期轴套接触。两店同时开启另检查 91 个姿态，未相撞；最窄中央 X 方向间距约 1.632 m，每店全开净宽约 1.734 m。详见[门扇结果](door-sweep.json)。

[路线代理](route-results.json)沿入口→店 A→中央→店 B→入口采样 426 个位置，间距不大于 0.05 m，以半径 0.25 m、高 1.8 m 的三球高度代理和地面投影检查，未发现障碍或落空。这不是可操控角色、连续碰撞检测或建筑无障碍认证。

[Blender 开门证明](blender-open-proof.json)重开保存的实际 GLB 组合场景，在源坐标设置四个铰链的 90° 姿态，渲染且确认保存源文件哈希不变。Node 检查使用 glTF Y 轴旋转，两者均已实际检查。

## B · Gallery 登记

mall-fit-finishes 集合追加三个模型：mall-shopfront-fascia-210、mall-shopfront-fascia-120、mall-column-ceiling-collar。每项有独立元数据和 640 px JPEG 卡片，卡片约 15–26 KB；源文件、GLB、原预览与权利记录保留。登记前 490 个条目内容未变，见[登记核对](../../../models/mall-fit-finishes/reports/catalog-preservation.json)。工作区的其他并行新增资产不属于这个数量快照或本次验证范围。

[实际 Gallery 验证](../../../models/mall-fit-finishes/reports/browser/results.json)在桌面与手机尺寸共 6 个模型用例通过：筛选显示三张卡，索引不加载 GLB 或建立 WebGL；打开后实际绘制，响应字节哈希与源文件一致；旋转、重置、关闭释放 canvas 通过；下载设置遵循现有权利说明。未上线。

## C · Web 验证

[浏览器结果](web-results.json)在 1440×900、390×844 中通过 100 个实例与 Blender 包围盒的 2 mm 比对，以及两店视角、剖切、开关门、环绕和无横向溢出检查。页面、控制台与 HTTP 错误为 0。

静态样板阶段为每帧 174 draw calls；接入访客后，当前检查视角为 199，低于 200 上限。初版逐对象绘制为 1,825 次，实例分组中间版为 246 次；最终将静态不透明表面按材质合批，门扇保留独立层级，透明面保留独立排序。合批改变 Web 绘制组织，没有改动 GLB 几何。绘制次数不等于 FPS、内存或真实手机性能保证。

组合 GLB 约 1.40 MB，Khronos 0 errors / 0 warnings，见[格式验证](gltf-validation.json)。原小样板更新后的格式、边界、表面采样及两视口检查也通过，见[P0 报告](../p0-assembly/README.md)。

## 已执行检查与复现

- npm run build：本次登记对应的 493 资产快照通过，后续并行增加不继承此证据。
- npm test：587 passed，0 failed。
- npm run test:library：10 个浏览器回归场景通过。
- node scripts/test-mall-fit-finishes-browser.mjs：3 个新模型 × 2 视口通过。
- [check-door-sweep.mjs](../p0-assembly/check-door-sweep.mjs)：默认检查修正后的 P0；传入 corridor.glb 与目标 JSON 路径可复核两店及同时开门。
- node docs/verification/mall-corridor/check-route.mjs：路线代理通过。
- node docs/verification/mall-corridor/check-web.mjs：本地 Vite 两视口检查与绘制上限通过。

先审查 [assemble.py](assemble.py)，再用 Blender 5.1.2 的 --background --factory-startup --threads 4 --python-exit-code 1 --python docs/verification/mall-corridor/assemble.py 重建；[render-open.py](render-open.py)生成开门证明。脚本仅写本目录，重建会替换同名产物，手工修改前请备份。Node 检查使用项目锁定的 Three.js 0.187.0、Playwright 1.64.1 与 Chromium。

未测试真实 iOS/Android、Safari、物理触控、设备 FPS/内存；已接入本地访客控制，商品或购物交互未实现；未集成 GJH v11；远程部署结果应另查 CI，以上为本地验证证据。原资产权利及[新模块权利](../../../models/mall-fit-finishes/LICENSE.md)继续适用。

## 可操控访客更新

2026-11-15：已接入现有 GJH Mall Visitor，支持键盘和触控行走、idle/walk 动画、贴地、墙／门／地面边界限制、占用门道保护以及查看模式。详见 [VISITOR.md](VISITOR.md)和[实际浏览器结果](visitor-evidence/results.json)。早期路线代理检查保留为历史静态证据；本次新增的实际行走检查单独记录。
