<template>
	<view class="content">
		<image class="logo" src="/static/logo.png"></image>
		<view class="text-area">
			<text class="title">Hospital Service Login</text>
		</view>
		<view class="btn-area">
			<button class="login-btn" type="primary" @click="wechatLogin" :loading="loading">
				WeChat Quick Login
			</button>
		</view>
	</view>
</template>

<script>
	export default {
		data() {
			return {
				title: 'Hospital Service',
				loading: false,
				apiBaseUrl: 'http://localhost:8000' // 修改为你的后端API地址
			}
		},
		onLoad() {
			// 检查是否已登录
			const token = uni.getStorageSync('access_token');
			if (token) {
				// 已登录，跳转到首页
				uni.redirectTo({
					url: '/pages/home/index'
				});
			}
		},
		methods: {
			async wechatLogin() {
				if (this.loading) return;
				this.loading = true;

				try {
					// 获取微信登录code
					const loginRes = await new Promise((resolve, reject) => {
						uni.login({
							provider: 'weixin',
							success: resolve,
							fail: reject
						});
					});

					if (!loginRes.code) {
						throw new Error('Failed to get WeChat code');
					}

					console.log('WeChat code:', loginRes.code);

					// 获取用户信息
					let userInfo = null;
					try {
						const userProfile = await new Promise((resolve, reject) => {
							uni.getUserProfile({
								desc: 'Login to access hospital services',
								success: resolve,
								fail: reject
							});
						});

						userInfo = userProfile.userInfo;
						console.log('User info:', userInfo);
					} catch (err) {
						console.log('User profile authorization skipped:', err);
						// 用户拒绝授权，仍然可以使用 openid 登录
					}

					// 发送到后端
					const response = await uni.request({
						url: `${this.apiBaseUrl}/api/v1/auth/wechat-login`,
						method: 'POST',
						data: {
							code: loginRes.code,
							user_info: userInfo
						},
						header: {
							'Content-Type': 'application/json'
						}
					});

					console.log('Login response:', response);

					if (response.statusCode === 200 && response.data) {
						const { access_token, user } = response.data;

						// 保存token和用户信息
						uni.setStorageSync('access_token', access_token);
						uni.setStorageSync('user_info', user);

						uni.showToast({
							title: 'Login Success',
							icon: 'success'
						});

						// 延迟跳转到首页
						setTimeout(() => {
							uni.redirectTo({
								url: '/pages/home/index'
							});
						}, 1500);
					} else {
						throw new Error('Login failed');
					}
				} catch (err) {
					console.error('Login error:', err);
					uni.showToast({
						title: err.message || 'Login Failed',
						icon: 'none'
					});
				} finally {
					this.loading = false;
				}
			}
		}
	}
</script>

<style>
	.content {
		display: flex;
		flex-direction: column;
		align-items: center;
		justify-content: center;
	}

	.logo {
		height: 200rpx;
		width: 200rpx;
		margin-top: 200rpx;
		margin-left: auto;
		margin-right: auto;
		margin-bottom: 50rpx;
	}

	.text-area {
		display: flex;
		justify-content: center;
	}

	.title {
		font-size: 36rpx;
		color: #8f8f94;
	}

	.btn-area {
		margin-top: 100rpx;
		width: 80%;
	}

	.login-btn {
		background-color: #07c160; /* WeChat Green */
		border-radius: 45rpx;
	}
</style>
