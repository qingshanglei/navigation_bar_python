from flask import jsonify


def success_response(data=None, msg="success", code=1):
    """统一成功响应格式
    :param data: 返回数据
    :param msg: 成功消息，默认统一为 'success'
    :param code: 业务码，1 表示成功
    """
    return jsonify({
        "code": code,
        "msg": msg,
        "data": data,
    })


def error_response(msg="操作失败", code=0):
    """统一错误响应格式
    :param msg: 错误消息
    :param code: 业务码，0 表示失败
    """
    return jsonify({
        "code": code,
        "msg": msg,
        "data": None,
    })
