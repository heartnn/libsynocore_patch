# libsynocore_patch

对libsynocore.so.7打补丁，让群晖文件管理可以按拼音排序

## 使用方法

通过ssh将/usr/lib/libsynocore.so.7复制到本地，然后下载patch.py或者Release里的patch.exe，将它们放在同一个目录下，运行即可，原文件会自动备份为bak文件。

如果你的DSM是6.x，也可以尝试修改patch.py里的libsynocore.so.7为libsynocore.so.6，然后运行，因为原理都是一样的。

## 注意事项

代码由AI生成，但不局限于群晖的版本，可以在Issue中提交成功或失败的版本号（失败的话最好能提供源文件）

## 成功的群晖版本

- DSM 7.2.1-69057 Update 6
