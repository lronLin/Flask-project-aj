
a.url请求地址
b.请求方式 GET POST PATCH PUT DELETE
c.指定请求参数
d.响应
	{'code': 1011, 'msg': '身份证信息错误'}

	code : 状态码
	msg : 错误信息

### 请求地址
    POST /user/register/login/

### request params
- mobile str '手机号'
- imagecode str '验证码'
- passwd str '密码1'
- passwd2 str '确认密码2'

### response params 响应参数

- 失败响应1:
    {'code': 1000, 'msg': '验证码错误'}
    {'code': 1001, 'msg': '请填写完整的注册参数'}
    {'code': 1002, 'msg': '手机格式不正确'}
    {'code': 1003, 'msg': '两次密码不正确'}

-成功响应:
    {'code': 200, 'msg': '请求成功'}

- msg str '响应信息'
- code int '状态码'
