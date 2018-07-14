北京大学 信息科学技术学院
关智超

GitHub: https://www.github.com/vbcpascal

Python实现的Lisp（Scheme）解释器：
基于SICP的Lisp-Lisp解释器实现（apply-eval环的方式）。
对Procedure以及Environment的表示有所改变，即通过类、字典代替原有的列表、列表。

版本：0.1.0
支持：基础数学运算、define、set!、if、lambda、基本列表操作等
暂不支持：cond、let、read等

P.S
对列表的表示会在后续作业中进行重构（list -> cons），并增加完善原有功能

======================================================================

PKU EECS
Guan, Zhichao

GitHub: https://www.github.com/vbcpascal

Write a Lisp(Scheme) Interpreter in Python
Abstract: Build an interpreter for most of the Scheme dialect of Lisp using Python3 based on SICP (apply-eval circle).
Changes: Use [Class, Dict] to build Proc & Env instead of [List, List]

Version: 0.1.0 (with many bugs & without many functions)
Subsequent version:
1. Add cond, let and so on
2. Use real expression of list in Scheme (REBUILD my program)
   For example: (list 1 2) -> (cons (cons 1 '())) 

======================================================================

Error Information:

IndexError: list index out of range
1. parenthesis cannot match
2. because of a bug

AttributeError: 'NoneType' object has no attribute 'lookup'
1. unbound identifier in module
2. (*) use String, Symbol or other syntax (sorry, but you can use "(quote a)" instead of "'a")
3. because of a bug

TypeError: '*' object is not callable
1. expected a procedure that can be applied to arguments
2. because of a bug
