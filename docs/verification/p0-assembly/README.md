# P0 assembly fit study — fitted revision

验证日期：2026-11-14，Asia/Singapore。已在原有样板加入门面楣板和方柱周边天花收口；原先有缺口的版本保留在 [baseline-v1](baseline-v1/README.md)。五种原有输入 GLB 的 SHA-256 均与基线一致，详见 [输入完整性核对](input-integrity.json)。本次新增资产、样板及其检查；三个模块已登记到本地 Gallery，尚未部署。

## 本次交付

- [Blender 样板](fit-study.blend)、[组合 GLB](fit-study.glb)，以及[两类新模块的源文件、独立 GLB 和用法](../../../models/mall-fit-finishes/README.md)。样板从实际导出 GLB 重新导入后拼装；各模块的原始可编辑源仍单独保留。
- [Blender 正面](blender-front.png)、[下方](blender-underside.png)、[柱顶近看](blender-collar.png)、[楣板近看](blender-fascia.png)、[上方](blender-ceiling.png)。
- [Web 桌面](web-1440.png)、[手机尺寸](web-390.png)、[Web 柱顶近看](web-collar-1440.png)、[Web 下方](web-underside-1440.png)。

原有地面已增至 16 块地板（含新增门前铺地）、11 块天花、1 根方柱、2 块玻璃隔断和双开门保持原摆放；新放入 1 块 2.10 m 楣板、2 块 1.20 m 楣板、1 块柱周天花收口，共 **35 个组合对象**。Blender X/Y 水平、Z 向上，单位米。地板底面 Z=−0.03，完成面 Z=0；天花格栅底面 Z=3.0；门和隔断高 2.4 m。

## 拼接结果

| 接口 | 检查结果 | 结论 |
| --- | --- | --- |
| 楣板底部与门／隔断顶部 | 三处包围盒平面间距均在 2 mm 容差内约为 0 | 原有 0.60 m 高空档由楣板覆盖；三块楣板左右边界也相接 |
| 楣板顶部与天花 | 楣板顶 Z=3.0 与格栅底对齐；向上射线在格栅处命中 0 mm，在凹入饰面处约 8 mm | 保留已有天花的浅凹缝；未宣称封气、防火或施工密封 |
| 柱周天花收口 | 外边长 1.20 m、内孔边长 0.60 m、厚度 0.032 m；底面对齐 Z=3.0 | 覆盖先前柱周 0.30 m 宽空档；孔内仍留给原有柱帽 |
| 表面覆盖与重叠 | 6,525 条楣板射线、2,700 条收口环射线未漏空；9 个内孔点均未被收口遮挡；新构件对周围构件的包围盒检查未发现三轴均超过 10 微米的正重叠 | 在此样板、这些固定尺寸和采样范围内通过；不替代任意三角面或实体安装验证 |
| 原有地面与结构 | 24 条地面相邻边界、门与隔断水平边界及标高检查仍通过；原有输入文件哈希未变 | 保留原样板布局和资产 |

[表面检查](surface-results.json)保留了一处恰好位于两块天花接缝边界的射线未命中记录；在 X 两侧各 10 微米重新探测均命中格栅平面。检查保留偏移与原始结果，没有把未命中直接记为通过。该数值复核不代表真实加工或安装公差。

## 已执行的验证

- Blender 5.1.2 重建、导出、五个视角渲染及保存，重开最终 `.blend` 对实际网格进行覆盖和重叠检查。
- [边界检查](join-results.json)：41 项测量断言通过，其中包含基线空隙尺寸记录和新增模块的接触关系；这些历史尺寸记录不会自动代表仍有未填充洞口。
- [表面检查](surface-results.json)：采样覆盖、内孔和新组件包围盒重叠检查通过。
- 三个独立 GLB 均为 Khronos 0 errors / 0 warnings；组合 GLB 也是 **0 errors / 0 warnings**，306 条 informational 信息主要为未使用 UV，消息未截断，详见 [组合格式验证](gltf-validation.json)。
- [源文件证明](../../../models/mall-fit-finishes/reports/source-proof.json)：每个源的网格均闭合且有正体积；临时副本的实际顶点和材质修改经保存、重开、重新导出与 GLB 导入后仍存在；原源文件哈希未变。未把源文件可打开等同于可编辑性验证。
- [Web 结果](web-results.json)：项目锁定 Three.js 0.187.0 / Vite，本地 Chromium 软件渲染，1440×900 和 390×844 两个视口。35 个组合对象的坐标换算包围盒均与 Blender 在 2 mm 内一致；拖动、下方与柱顶视角切换通过；页面、控制台、HTTP 错误为 0。截图已实际检查。

组合 GLB SHA-256：`ca8490891c6d33dfc5f5dd4622e0dd925a115caad232b8f70914d43f7788b1a9`。原始输入哈希、实际测量和所有对象位置见 [measurements.json](measurements.json)。

## 复现与本地查看

先审查生成脚本，再从仓库根目录运行：

```sh
/Applications/Blender.app/Contents/MacOS/Blender --background --factory-startup --threads 4 --python-exit-code 1 --python models/mall-fit-finishes/generate.py
node models/mall-fit-finishes/validate.mjs
/Applications/Blender.app/Contents/MacOS/Blender --background --factory-startup --threads 4 --python-exit-code 1 --python docs/verification/p0-assembly/assemble.py
python3 docs/verification/p0-assembly/check-joins.py
/Applications/Blender.app/Contents/MacOS/Blender --background --factory-startup --threads 2 --python-exit-code 1 --python docs/verification/p0-assembly/check-surfaces.py
npm run dev -- --port 4173 --strictPort
```

另一个终端运行 `node docs/verification/p0-assembly/check-web.mjs`。浏览器打开 `http://127.0.0.1:4173/docs/verification/p0-assembly/`，可用 Overview、Underside、Column joint 按钮及鼠标拖动查看。正常生成会覆盖这些目录内同名输出，手工修改前请先备份；保留资产源文件修改的方式见资产 README。

## 范围与剩余项

本次完成两类模块在当前样板的制作与本地验证。手机尺寸为桌面浏览器模拟，未测真实手机触控、帧率或 Safari。已完成门的分步开启检查；未验证连续时间运动、通用碰撞控制器、任意尺寸适配、长距离累计偏差或完整建筑连接。Web 样板使用现有技术栈，但尚未集成到 Gallery 正式查看器或 GJH V11，上述本地证据不证明远程发布或部署。样板不提供真实工程认证。

原计划中的门框过渡立柱、地面边缘等仍是后续待定项，本次没有据此新增。已有目录的权利和新模块 [LICENSE.md](../../../models/mall-fit-finishes/LICENSE.md) 继续适用；组合文件不构成公共再分发授权。仓库缺少路由提及的 investigation / verification 模块文件，执行依据为当前核心规则与上述实测证据。

## A–C 后续验证

开门检查在旧基线中发现门扇投影超出铺地，因此当前样板增添了前方一排四块原地砖。更新后的 [door-sweep.json](door-sweep.json) 在三种开启模式、每 1° 的 0–90° 采样中，未发现构件碰撞或门扇顶点投影超出铺地；全开净宽约 1.734 m。测试为收缩 10 微米的组件 OBB 与实际顶点投影，排除仅位于原铰链轴上的轴套，不是实体安装或连续碰撞认证。更大的双店铺场景、两门同时开启和路线代理结果见 [走廊样板](../mall-corridor/README.md)。
