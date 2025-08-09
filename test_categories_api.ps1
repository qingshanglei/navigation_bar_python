# 测试分类管理API接口
Write-Host "正在测试分类管理API接口..." -ForegroundColor Green

# 1. 登录获取token
Write-Host "1. 登录获取token..." -ForegroundColor Yellow
$loginResponse = Invoke-WebRequest -Uri "http://localhost:5000/api/auth/login" -Method POST -Headers @{"Content-Type"="application/json"} -Body '{"username":"admin","password":"123456"}'
$loginJson = $loginResponse.Content | ConvertFrom-Json
$token = $loginJson.data.token.access_token
Write-Host "登录成功，Token: $($token.Substring(0,50))..." -ForegroundColor Green

# 2. 测试获取分类列表（默认分页模式）
Write-Host "2. 测试获取分类列表（分页模式）..." -ForegroundColor Yellow
$categoriesResponse = Invoke-WebRequest -Uri "http://localhost:5000/admin/categories" -Method GET -Headers @{"Authorization"="Bearer $token"}
$categoriesJson = $categoriesResponse.Content | ConvertFrom-Json
Write-Host "分页模式响应: $($categoriesResponse.Content)" -ForegroundColor Cyan

# 3. 测试获取分类树结构
Write-Host "3. 测试获取分类树结构..." -ForegroundColor Yellow
$treeResponse = Invoke-WebRequest -Uri "http://localhost:5000/admin/categories?tree=true" -Method GET -Headers @{"Authorization"="Bearer $token"}
$treeJson = $treeResponse.Content | ConvertFrom-Json
Write-Host "树结构响应: $($treeResponse.Content)" -ForegroundColor Cyan

Write-Host "API测试完成！" -ForegroundColor Green
