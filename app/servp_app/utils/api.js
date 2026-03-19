// 统一的 API 请求封装
const API_BASE_URL = 'http://localhost:8000'

/**
 * 清除所有缓存并跳转到登录页面
 */
function clearCacheAndLogin() {
	// 清除所有缓存
	uni.removeStorageSync('access_token')
	uni.removeStorageSync('user_info')
	uni.removeStorageSync('token')

	// 跳转到登录页面
	uni.reLaunch({
		url: '/pages/login/login'
	})
}

/**
 * 统一的请求函数
 * @param {string} url - 请求地址
 * @param {object} options - 请求选项
 * @returns {Promise}
 */
function request(url, options = {}) {
	const {
		method = 'GET',
		data = null,
		header = {},
		needAuth = true,
		...restOptions
	} = options

	// 构建完整的请求头
	const requestHeader = {
		'Content-Type': 'application/json',
		...header
	}

	// 如果需要认证，添加 token
	if (needAuth) {
		const token = uni.getStorageSync('access_token')
		if (!token) {
			// 没有 token，直接跳转到登录页
			clearCacheAndLogin()
			return Promise.reject(new Error('No token found'))
		}
		requestHeader['Authorization'] = `Bearer ${token}`
	}

	// 返回 Promise
	return new Promise((resolve, reject) => {
		uni.request({
			url: `${API_BASE_URL}${url}`,
			method,
			data,
			header: requestHeader,
			success: (res) => {
				// 处理 401 未授权错误
				if (res.statusCode === 401) {
					console.error('Unauthorized:', res.data)
					clearCacheAndLogin()
					reject(new Error('Unauthorized'))
					return
				}

				// 处理其他错误
				if (res.statusCode >= 400) {
					const errorMessage = res.data?.detail || res.data?.message || 'Request failed'
					uni.showToast({
						title: errorMessage,
						icon: 'none',
						duration: 2000
					})
					reject(new Error(errorMessage))
					return
				}

				// 成功返回数据
				resolve(res.data)
			},
			fail: (err) => {
				console.error('Request failed:', err)
				uni.showToast({
					title: 'Network error',
					icon: 'none',
					duration: 2000
				})
				reject(err)
			},
			...restOptions
		})
	})
}

// 导出常用的请求方法
export default {
	get(url, options = {}) {
		return request(url, { ...options, method: 'GET' })
	},

	post(url, data, options = {}) {
		return request(url, { ...options, method: 'POST', data })
	},

	put(url, data, options = {}) {
		return request(url, { ...options, method: 'PUT', data })
	},

	delete(url, options = {}) {
		return request(url, { ...options, method: 'DELETE' })
	},

	patch(url, data, options = {}) {
		return request(url, { ...options, method: 'PATCH', data })
	},

	// 不需要认证的请求
	public(url, data, options = {}) {
		return request(url, { ...options, method: 'POST', data, needAuth: false })
	},

	// 手动清除缓存并登录
	clearCacheAndLogin
}
