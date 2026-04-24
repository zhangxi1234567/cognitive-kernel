# Wu Boshi No Hidden Formal Imports

This file defines the ban on hidden formal imports.

## Core Principle

After a problem is lowered to an earlier honest layer, the route must not quietly import a high-formalism tool unless:

- the import is named
- its necessity is justified
- no lower-floor substitute survives

## What Counts As A Hidden Import

A hidden formal import is any move like:

- “设斜率为 k” after claiming a geometry-first route
- “由导数可知” after claiming a low-floor comparison route
- “用判别式” after claiming a pure structure route
- “写成矩阵 / 特征值 / 生成函数” after claiming an elementary execution path

without making visible:

- why the lower route stopped
- why this import is the minimal next climb

## Allowed Formal Imports

Formal import is allowed only when:

- it seals the route with the smallest possible exact check
- it does not rebuild the whole standard solution
- the answer explicitly says the lower-floor route ended here and why

## Detection Questions

Ask:

1. What is the first object in this route the lower-floor solver would not naturally own?
2. Was that object necessary or habitual?
3. Did the answer mark the climb when it happened?
4. Did the imported object control only the seal, or did it take over the route?

## Hard Rule

If a hidden formal import takes over the route, the solution no longer counts as completed dimensionality reduction.
