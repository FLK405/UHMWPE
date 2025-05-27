# run.py
# 项目运行入口文件

from app import create_app

# 调用工厂函数创建应用实例
app = create_app()

if __name__ == '__main__':
    # 启动Flask开发服务器
    # host='0.0.0.0' 使服务器可以从外部访问
    # debug=True 开启调试模式，代码更改后服务器会自动重启
    # port=5000 指定运行端口
    app.run(host='0.0.0.0', port=5000, debug=True)
