# ILSchPy 使用说明

**版本号**：0.3 + 0.3i（实部为解释器核心版本号，虚部为可视化窗口的版本号）。

本项目是通过 Python 实现的 Scheme 解释器：

- 主要基于 SICP 的 Lisp 解释器实现（ apply-eval 环的方式）。
- 特殊地，对 Procedure 以及 Environment 的表示有所改变，即通过类、字典代替原有的列表、列表。

## 解释器支持说明

1. 基础数学运算、define、set!、if、lambda、基本列表操作；
2. 支持了（*; comment* 及 *#| comment |#*）；
3. 支持 *String* 类型；

**暂不支持**

1. cond
2. let
3. read

## 使用帮助

### 代码运行

与正常编辑器（编译器）相差不大，编辑器支持显示行号、当前行，并支持大多数的**语法高亮**，在代码输入完毕后，在菜单中点击 *Run* 或 *F5* 运行代码，代码结果将会在下方输出框显示。注意：*display, displayln, newline* 的结果将会显示在控制台中，而不是在输出框中。

### 设置

修改编辑器样式：*Settings Editor* 
```Scheme
(list dc ds df (fs 15) (ff "Consolas"))
```
所有设置将会在此列表中进行，各参数说明如下：

| 参数 | 原型                        | 解释             |
| ---- | --------------------------- | ---------------- |
| dc   | `open debug_file`           | 打开文件调试工具 |
| ds   | `open debug_code`           | 打开代码调试工具 |
| df   | `open debug_set`            | 打开设置相关工具 |
| fs   | `(lambda (x) (set-size x))` | 设置字号为x      |
| ff   | `(lambda (s) (set-font x))` | 设置字体为s      |

*Default Settings* 是将代码变为默认设置，而不是直接进行设置。在设置代码编辑完毕后，点击 *Run*即可完成设置。**完成设置**并不会保存设置，请手动保存！
