// 统一的 API 请求封装
import config from '../config/config.js'

const API_BASE_URL = config.API_BASE_URL

/**
 * 清除所有缓存并跳转到登录页面
 */
function clearCacheAndLogin() {
	uni.removeStorageSync('access_token')
	uni.removeStorageSync('user_info')
	uni.removeStorageSync('token')
	uni.removeStorageSync('userId')

	uni.reLaunch({
		url: '/pages/login/login'
	})
}

/**
 * 统一的请求函数
 */
function request(url, options = {}) {
	const {
		method = 'GET',
		data = null,
		header = {},
		needAuth = true,
		...restOptions
	} = options

	const requestHeader = {
		'Content-Type': 'application/json',
		...header
	}

	if (needAuth) {
		const token = uni.getStorageSync('access_token')
		if (!token) {
			clearCacheAndLogin()
			return Promise.reject(new Error('No token found'))
		}
		requestHeader['Authorization'] = `Bearer ${token}`
	}

	return new Promise((resolve, reject) => {
		uni.request({
			url: `${API_BASE_URL}${url}`,
			method,
			data,
			header: requestHeader,
			success: (res) => {
				if (res.statusCode === 401) {
					console.error('Unauthorized:', res.data)
					clearCacheAndLogin()
					reject(new Error('Unauthorized'))
					return
				}

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

	public(url, data, options = {}) {
		return request(url, { ...options, method: 'POST', data, needAuth: false })
	},

	clearCacheAndLogin
}

const api = {
	async get(url) {
		return request(url, 'GET')
	},

	async post(url, data) {
		return request(url, 'POST', data)
	},

	async put(url, data) {
		return request(url, 'PUT', data)
	},

	async public(url, data) {
		return publicRequest(url, data)
	},

	clearCacheAndLogin() {
		uni.removeStorageSync('access_token')
		uni.removeStorageSync('userId')
		uni.removeStorageSync('user_info')
		uni.reLaunch({
			url: '/pages/login/login'
		})
	}
}
