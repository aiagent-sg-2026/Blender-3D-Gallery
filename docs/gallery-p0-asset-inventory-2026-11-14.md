# Gallery P0 asset inventory

盘点日期：2026-11-14（Asia/Singapore）
计划：`3D_Model_Library_Master_Plan.md` v0.1，SHA-256 `c2ad39f7680ab4e49aea31a1e8e93e8d8df485484936fa1ef102de3f91e0aaa0`
范围：本地工作区登记目录、相关资产说明及文件；线上仅做入口和主 JS 字符串核对。

## 结果与判定方法

- 计划中有 **31 个 P0 模型家族**；下表逐项覆盖。候选涉及 **33 个不同登记资产**，同一资产可支持多个家族。
- 本地 `models/catalog.json` 含 425 个 collection、490 个登记条目；490 条登记 GLB 路径都存在。这是包含未提交修改的工作区快照，不等于线上模型数。线上入口返回 HTTP 200；线上入口 JS 中可找到 488 个本地 ID 的字符串，缺少 `mall-coffee-counter` 和 `interactive-shopping-cart`。字符串检查不证明这些模型实际加载、展示成功或是完整线上总数。
- “复用”表示已有候选、建议优先试用；“修改”表示可能的适配工作；“新建”表示当前目录检索未找到明确独立候选或计划要求的缺失变体，须先复核场景、组合资产和实际几何。一个家族可同时出现三种处理。没有任何项因此自动获得 Approved/Published 状态。
- 文件存在和既有报告是盘点证据，不是本次重新运行的 GLB 验证、Blender 拼装、授权或浏览器体验验收。目录中未发现明确候选不证明任何资产不存在于未登记场景的内部。
- 负责人均未指定，当前均为 **Inventory Check / 待验证**；优先级均为 **P0**。列出的“新建”不构成建模指令。

## P0 家族处置清单

| 规划 ID / 家族 | 现有资产 ID（见下方路径清单） | 复用候选 | 修改或验证 | 待新建/补充 |
| --- | --- | --- | --- | --- |
| `PL-ARC-001` 地面模块（普通、边缘、转角、盲道） | `mall-floor-tile-module` | 普通地砖候选 | 确认 1.2 m 网格与原点；边缘收口 | 转角、盲道及所需边缘变体 |
| `PL-ARC-002` 内墙模块（实墙、玻璃、半墙） | `mall-glass-partition` | 玻璃内墙候选 | 按 1.14 m 节距共享立柱；核对与其他模块高度 | 实墙、半墙模块 |
| `PL-ARC-003` 墙角、端头、踢脚线 | `mall-glass-partition` | 可按既定规则拼接玻璃转角 | 核对与实墙连接 | 实墙墙角、端头、踢脚线 |
| `PL-ARC-004` 柱体及包柱饰面（方、圆） | `mall-structural-column` | 方柱及饰面候选 | 补齐天花开口收边并验证整体布局 | 圆柱及其他包柱变体 |
| `PL-ARC-005` 天花模块（平板、格栅、跌级） | `mall-ceiling-panel-module` | 平板格栅天花候选 | 与柱、灯的开孔及标高协调 | 跌级及其他样式 |
| `PL-ARC-006` 门套及门（单开、双开、玻璃） | `mall-shopfront-door` | 玻璃双开门候选 | 核对门洞与墙、店面接口 | 单开及其他门套变体 |
| `PL-ARC-007` 店面框架（开放、玻璃、转角） | `mall-shopfront-door`, `mall-glass-partition`, `mall-entrance` | 门及玻璃为局部候选 | 设计通用门面框架并检验拼接；入口是整体场景 | 开放式、转角门面及连接件 |
| `PL-ARC-013` 店铺招牌底板与字槽 | `mall-display-shelf` | 货架顶部标头仅作参考 | 确认可独立编辑的底板及字槽 | 通用独立店铺招牌与字槽 |
| `PL-LGT-001` 筒灯（圆、方） | 未发现明确候选 | 无明确筒灯候选 | — | 圆形、方形筒灯 |
| `PL-LGT-002` 可调轨道射灯（灯轨、灯头） | 未发现明确候选 | 无明确轨道射灯候选 | — | 灯轨、可调灯头 |
| `PL-LGT-003` 线性灯条及转角 | 未发现明确候选 | 无明确线性灯候选 | — | 直灯条、转角 |
| `PL-LGT-004` 嵌入式面板灯 | `mall-ceiling-light-module` | 方形嵌入灯候选 | 确认与天花模块开孔和灯光配置 | 其他所需面板规格 |
| `PL-LGT-007` 灯箱与背光招牌外壳 | `mall-advertising-lightbox` | 立式灯箱外观候选 | 拆分可换画面/适配门面尺寸 | 独立背光店招外壳 |
| `PL-PUB-001` 休息座椅（直、角、圆） | `gjh-lounge-bench`, `public-service-waiting-bench` | 直式座椅候选 | 核对尺寸、风格与摆放 | 角形及圆形座椅 |
| `PL-PUB-002` 垃圾分类站（单桶、多桶） | `mall-waste-sorting-station`, `mall-trash-bin` | 三分类站与单桶候选 | 按场景检查标识及布局 | 仅在需要其他容量或组合时新增 |
| `PL-PUB-003` 导览机及底座 | `mall-directory-kiosk` | 导览机外观候选 | 按楼层替换地图；交互需另行实现 | 如需不同底座再新增 |
| `PL-PUB-004` 吊挂导向牌、墙牌、楼层牌 | `mall-wayfinding-ceiling-sign`, `mall-floor-direction-sign`, `hdb-block-number-sign` | 吊牌、落地牌及楼层数字牌候选 | 替换内容并核对吊挂高度 | 独立墙牌与商场楼层牌规格 |
| `PL-PUB-005` 花盆与植物组合 | `gjh-areca-planter`, `orchid-planter` | 植物花盆组合候选 | 按风格与尺寸调整 | 仅在需要其他植物组合时新增 |
| `PL-PUB-006` 广告灯箱、竖屏、双面屏 | `mall-advertising-lightbox`, `mall-digital-advertising-screen` | 立式灯箱及横向墙屏候选 | 替换画面并核对实际摆位 | 竖向数字屏、双面屏 |
| `PL-RET-001` 模块化零售货架（单面、双面、端架） | `mall-display-shelf`, `supermarket-aisle` | 独立展示架及整条货架场景候选 | 先检查单元可拆分性、尺寸和模块接口 | 双面架、端架及缺失的模块连接件 |
| `PL-RET-002` 精品玻璃展示柜 | `mall-glass-showcase` | 独立玻璃展示柜候选 | 核对照明和商品摆放需求 | 仅在需要不同规格时新增 |
| `PL-RET-003` 收银台（直台、转角） | `checkout-counter` | 直式收银台候选 | 核对设备与门面布局 | 转角收银台 |
| `PL-RET-004` 墙面展示架与层板 | `mall-display-shelf` | 落地展示架可作参考 | 检查能否拆取层板并设计墙面固定接口 | 独立墙面挂架、层板 |
| `PL-RET-005` 中岛展示台（圆、矩形） | `mall-display-shelf`, `mall-retail-pop-up-cart` | 展示架/展车仅作参考 | 核对是否能改成开放中岛 | 圆形、矩形中岛展示台 |
| `PL-RET-008` 货品包装基型（罐、瓶、盒、袋） | `demo-beverage-can`, `demo-food-tin`, `mooncake-gift-box` | 无真实品牌的罐及礼盒候选 | 核对礼盒是否适合作通用盒；移除/替换概念图案 | 瓶、袋及需要的通用包装变体 |
| `PL-RET-009` 产品标牌、价格牌与展示底座 | 未发现明确候选 | 未找到明确独立产品标牌/价格牌/底座 | — | 产品牌、价格牌、展示底座 |
| `PL-FNB-001` 餐桌（双人、四人、圆桌） | `dining-table`, `round-dining-table` | 矩形及圆形餐桌候选 | 核对尺寸与座位数 | 按实际需求补双人/四人规格 |
| `PL-FNB-002` 餐椅、长凳、吧台椅 | `plastic-dining-chair`, `mall-bar-stool`, `gjh-lounge-bench` | 餐椅、吧台椅、长椅候选 | 核对餐桌高度及长椅用途 | 按实际需求补餐饮长凳 |
| `PL-ADV-001` 标准海报框（壁挂、落地） | `mall-advertising-lightbox` | 落地灯箱可作视觉参考 | 确认画面替换方式 | 独立壁挂、落地普通海报框 |
| `PL-ADV-002` 数字屏支架（竖屏、横屏） | `mall-digital-advertising-screen`, `mall-directory-kiosk` | 横屏及竖向导览机整机候选 | 核对支架能否独立、画面与方向 | 通用独立竖屏/横屏支架 |
| `PL-CHR-001` 通用访客角色（可替换服装） | `mall-shopper`, `gjh-mall-visitor` | 两个访客角色候选 | 核对服装部件能否替换、动作与角色解耦；应用自行实现移动 | 现有角色无法满足时新建通用换装方案 |

## 主要兼容性与权利风险

- 地砖与平板天花均是 **1.2 m** 模块；玻璃隔断 1.20 m 宽但重复节距 **1.14 m**，并须去掉接缝处重复柱。计划中的 1 m 网格只是建议起点，不能假定这些组件天然兼容。
- 方柱高 3.00 m；其现有拼装方案在天花上方预留开口，未交付完整收口。玻璃隔断高 2.40 m，实际商场高度与顶/墙连接需设计。详见 `models/mall-structural-column/README.md`、`models/mall-glass-partition/README.md`。
- 导览机和屏幕的画面不等于可交互导览；灯具外观/发光材质不等于场景真实照明。访客步行动画为原地动画，移动、碰撞与摄像机由消费端负责。
- 资产权利需逐项确认：所列多数资产的本地说明允许业主项目复用，公共再分发条款未明确；这并不自动授权客户交付或对外下载。字体、贴图和品牌需分开核查。`demo-food-tin` 另附字体许可；`demo-beverage-can` 目录条目未明确公共再分发条款。
- GJH 鲍鱼罐涉及 GJH / New Moon 包装：仓库说明仅记录业主确认用于其项目，未有独立许可文件；不作为通用无品牌包装直接复用。客户品牌和 SKU 应另行确认。

## 候选资产文件与证据索引

路径均相对于仓库根目录；GLB 与 `.blend` 为本次文件存在性核对，许可摘录来自目录或文件声明，未作法律核验。个别资产源文件可能包含多个资产；历史验证详见对应资产目录。

| 资产 ID | 登记 GLB | Blender 源文件 | 权利/说明依据 |
| --- | --- | --- | --- |
| `checkout-counter` | `models/checkout-counter/exports/optimized.glb` | `models/checkout-counter/sources/checkout-counter.blend` | `models/catalog.json`, `models/checkout-counter/LICENSE.md`, `models/checkout-counter/README.md` |
| `demo-beverage-can` | `models/demo-beverage-can/exports/demo-beverage-can.glb` | `models/demo-beverage-can/sources/demo-beverage-can.blend` | `models/catalog.json`, `models/demo-beverage-can/README.md` |
| `demo-food-tin` | `models/demo-food-tin/exports/demo-food-tin.glb` | `models/demo-food-tin/sources/demo-food-tin.blend` | `models/catalog.json`, `models/demo-food-tin/README.md` |
| `dining-table` | `models/dining-table/exports/optimized.glb` | `models/dining-table/sources/dining-table.blend` | `models/catalog.json`, `models/dining-table/LICENSE.md`, `models/dining-table/README.md` |
| `gjh-areca-planter` | `models/gjh-mall-furniture/exports/gjh-areca-planter.glb` | `models/gjh-mall-furniture/sources/gjh-areca-planter.blend` | `models/catalog.json`, `models/gjh-mall-furniture/README.md` |
| `gjh-lounge-bench` | `models/gjh-mall-furniture/exports/gjh-lounge-bench.glb` | `models/gjh-mall-furniture/sources/gjh-lounge-bench.blend` | `models/catalog.json`, `models/gjh-mall-furniture/README.md` |
| `gjh-mall-visitor` | `models/gjh-mall-visitor/exports/gjh-mall-visitor.glb` | `models/gjh-mall-visitor/sources/gjh-mall-visitor.blend` | `models/catalog.json`, `models/gjh-mall-visitor/README.md` |
| `hdb-block-number-sign` | `models/hdb-block-number-sign/exports/optimized.glb` | `models/hdb-block-number-sign/sources/hdb-block-number-sign.blend` | `models/catalog.json`, `models/hdb-block-number-sign/LICENSE.md`, `models/hdb-block-number-sign/README.md` |
| `mall-advertising-lightbox` | `models/mall-essentials/exports/mall-advertising-lightbox.glb` | `models/mall-essentials/sources/mall-advertising-lightbox.blend` | `models/catalog.json`, `models/mall-essentials/README.md` |
| `mall-bar-stool` | `models/mall-bar-stool/exports/optimized.glb` | `models/mall-bar-stool/sources/mall-bar-stool.blend` | `models/catalog.json`, `models/mall-bar-stool/LICENSE.md`, `models/mall-bar-stool/README.md` |
| `mall-ceiling-light-module` | `models/mall-ceiling-light/exports/mall-ceiling-light-module.glb` | `models/mall-ceiling-light/sources/mall-ceiling-light-module.blend` | `models/catalog.json`, `models/mall-ceiling-light/README.md` |
| `mall-ceiling-panel-module` | `models/mall-ceiling-panel/exports/mall-ceiling-panel-module.glb` | `models/mall-ceiling-panel/sources/mall-ceiling-panel-module.blend` | `models/catalog.json`, `models/mall-ceiling-panel/README.md` |
| `mall-digital-advertising-screen` | `models/mall-digital-advertising-screen/exports/optimized.glb` | `models/mall-digital-advertising-screen/sources/mall-digital-advertising-screen.blend` | `models/catalog.json`, `models/mall-digital-advertising-screen/LICENSE.md`, `models/mall-digital-advertising-screen/README.md` |
| `mall-directory-kiosk` | `models/mall-essentials/exports/mall-directory-kiosk.glb` | `models/mall-essentials/sources/mall-directory-kiosk.blend` | `models/catalog.json`, `models/mall-essentials/README.md` |
| `mall-display-shelf` | `models/mall-essentials/exports/mall-display-shelf.glb` | `models/mall-essentials/sources/mall-display-shelf.blend` | `models/catalog.json`, `models/mall-essentials/README.md` |
| `mall-entrance` | `models/mall-entrance/exports/optimized.glb` | `models/mall-entrance/sources/mall-entrance.blend` | `models/catalog.json`, `models/mall-entrance/LICENSE.md`, `models/mall-entrance/README.md` |
| `mall-floor-direction-sign` | `models/mall-floor-direction-sign/exports/mall-floor-direction-sign.glb` | `models/mall-floor-direction-sign/sources/mall-floor-direction-sign.blend` | `models/catalog.json`, `models/mall-floor-direction-sign/README.md` |
| `mall-floor-tile-module` | `models/mall-floor-tile/exports/mall-floor-tile-module.glb` | `models/mall-floor-tile/sources/mall-floor-tile-module.blend` | `models/catalog.json`, `models/mall-floor-tile/README.md` |
| `mall-glass-partition` | `models/mall-glass-partition/exports/mall-glass-partition.glb` | `models/mall-glass-partition/sources/mall-glass-partition.blend` | `models/catalog.json`, `models/mall-glass-partition/LICENSE.md`, `models/mall-glass-partition/README.md` |
| `mall-glass-showcase` | `models/mall-glass-showcase/exports/optimized.glb` | `models/mall-glass-showcase/sources/mall-glass-showcase.blend` | `models/catalog.json`, `models/mall-glass-showcase/LICENSE.md`, `models/mall-glass-showcase/README.md` |
| `mall-retail-pop-up-cart` | `models/mall-retail-pop-up-cart/exports/optimized.glb` | `models/mall-retail-pop-up-cart/sources/mall-retail-pop-up-cart.blend` | `models/catalog.json`, `models/mall-retail-pop-up-cart/README.md` |
| `mall-shopfront-door` | `models/mall-shopfront-door/exports/mall-shopfront-door.glb` | `models/mall-shopfront-door/sources/mall-shopfront-door.blend` | `models/catalog.json`, `models/mall-shopfront-door/README.md` |
| `mall-shopper` | `models/mall-shopper/exports/mall-shopper.glb` | `models/mall-shopper/sources/mall-shopper.blend` | `models/mall-shopper/LICENSE.txt`, `models/mall-shopper/README.md` |
| `mall-structural-column` | `models/mall-structural-column/exports/mall-structural-column.glb` | `models/mall-structural-column/sources/mall-structural-column.blend` | `models/catalog.json`, `models/mall-structural-column/LICENSE.md`, `models/mall-structural-column/README.md` |
| `mall-trash-bin` | `models/mall-essentials/exports/mall-trash-bin.glb` | `models/mall-essentials/sources/mall-trash-bin.blend` | `models/catalog.json`, `models/mall-essentials/README.md` |
| `mall-waste-sorting-station` | `models/mall-waste-sorting-station/exports/mall-waste-sorting-station.glb` | `models/mall-waste-sorting-station/sources/mall-waste-sorting-station.blend` | `models/catalog.json`, `models/mall-waste-sorting-station/README.md` |
| `mall-wayfinding-ceiling-sign` | `models/mall-wayfinding-ceiling-sign/exports/optimized.glb` | `models/mall-wayfinding-ceiling-sign/sources/mall-wayfinding-ceiling-sign.blend` | `models/catalog.json`, `models/mall-wayfinding-ceiling-sign/LICENSE.md`, `models/mall-wayfinding-ceiling-sign/README.md` |
| `mooncake-gift-box` | `models/mooncake-gift-box/exports/mooncake-gift-box.glb` | `models/mooncake-gift-box/sources/mooncake-gift-box.blend` | `models/catalog.json`, `models/mooncake-gift-box/LICENSE.md`, `models/mooncake-gift-box/README.md` |
| `orchid-planter` | `models/orchid-planter/exports/optimized.glb` | `models/orchid-planter/sources/orchid-planter.blend` | `models/catalog.json`, `models/orchid-planter/README.md` |
| `plastic-dining-chair` | `models/plastic-dining-chair/exports/optimized.glb` | `models/plastic-dining-chair/sources/plastic-dining-chair.blend` | `models/catalog.json`, `models/plastic-dining-chair/LICENSE.md`, `models/plastic-dining-chair/README.md` |
| `public-service-waiting-bench` | `models/public-service-waiting-bench/exports/public-service-waiting-bench.glb` | `models/public-service-waiting-bench/sources/public-service-waiting-bench.blend` | `models/catalog.json`, `models/public-service-waiting-bench/LICENSE.md`, `models/public-service-waiting-bench/README.md` |
| `round-dining-table` | `models/round-dining-table/exports/round-dining-table.glb` | `models/round-dining-table/sources/round-dining-table.blend` | `models/catalog.json`, `models/round-dining-table/LICENSE.txt`, `models/round-dining-table/README.md` |
| `supermarket-aisle` | `models/supermarket-aisle/exports/optimized.glb` | `models/supermarket-aisle/sources/supermarket-aisle.blend` | `models/catalog.json`, `models/supermarket-aisle/LICENSE.md`, `models/supermarket-aisle/README.md` |

## 后续验证顺序

1. 在 Blender 和目标 Web 引擎中按真实尺寸、轴向和连接点拼装地面、柱、天花、玻璃及门；先确定 1.2 m / 1.14 m 的过渡与收边。
2. 逐项打开候选源文件和 GLB，复核实际几何、材质、原点、变体、可编辑性及性能；优先复测本计划使用的拼装组合。
3. 明确首场景范围、品牌与权利、目标设备及交付形式，再冻结缺口，安排建模；单一独立资产与变体的计数规则须先定。

## 证据边界

- 当前仓库 HEAD：`1f9656346107bb49bdacc2b651c4f7e9ce869ac8`；`models/catalog.json` 及其他用户文件在盘点开始前已修改，工作区另有未跟踪资产。本报告保留这些状态，不视其为已提交或已部署。
- `instruction-modules/investigation.md` 与 `instruction-modules/verification.md` 在仓库中不存在；本次按现有核心约束和可用本地证据进行。
- 线上仅检查 HTML、入口 JS 中的 ID 字符串，未逐一打开线上模型；未运行模型生成器或改动资产。历史 PASS/NEEDS REVIEW 以各资产原报告为准。

## 后续落实

2026-11-14：已制作门面楣板（2.10 m、1.20 m 两个规格）及方柱周边天花收口，并在原 Blender 与 Web 技术栈样板中完成本地拼接、表面采样和显示检查。具体范围、凹缝和未验证项见 [更新后的样板报告](verification/p0-assembly/README.md)。本盘点表保留初始快照；新增资产尚未进入 Gallery 登记目录。
