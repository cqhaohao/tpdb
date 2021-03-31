from api.service import app

if __name__ == '__main__':
    # http_server = WSGIServer(('0.0.0.0', 5000), app)
    # print(app.url_map)
    # http_server.serve_forever()
    print(app.url_map)
    app.run(host="0.0.0.0", threaded=True)  # 线程效果; processes=True是进程效果, 默认进程1
