<template>
	<view class="content">
		<image class="logo" src="/static/logo.png"></image>
		<view class="text-area">
			<text class="title">Hospital Service Login</text>
		</view>

		<!-- 用户信息填写区域 -->
		<view class="user-info-area" v-if="showProfileForm">
			<view class="info-item">
				<text class="label">Avatar</text>
				<button class="avatar-btn" open-type="chooseAvatar" @chooseavatar="onChooseAvatar">
					<image class="avatar" :src="userInfo.avatarUrl || '/static/default-avatar.png'"></image>
					<text class="change-text">Click to change</text>
				</button>
			</view>

			<view class="info-item">
				<text class="label">Nickname</text>
				<input 
					class="nickname-input" 
					type="nickname" 
					v-model="userInfo.nickname"
					placeholder="Please input your nickname"
					@blur="onNicknameChange"
				/>
			</view>
		</view>

		<view class="btn-area">
			<button class="login-btn" type="primary" @click="wechatLogin" :loading="loading">
				{{ showProfileForm ? 'Complete Registration' : 'WeChat Quick Login' }}
			</button>
		</view>
	</view>
</template>

<script>
	import api from '../../utils/api.js'
	import config from '../../config/config.js'

	export default {
		data() {
			return {
				title: 'Hospital Service',
				loading: false,
				showProfileForm: false,
				userInfo: {
					nickname: '',
					avatarUrl: ''
				},
				loginCode: ''
			}
		},
		onLoad() {
			// 检查是否已登录
			const token = uni.getStorageSync('access_token');
			if (token) {
				// 已登录，跳转到首页（tabBar页面）
				uni.switchTab({
					url: '/pages/home/home'
				});
			}
		},
		methods: {
			onChooseAvatar(e) {
				console.log('Choose avatar:', e);
				const { avatarUrl } = e.detail;
				this.userInfo.avatarUrl = avatarUrl;
			},

			onNicknameChange(e) {
				console.log('Nickname changed:', e);
				this.userInfo.nickname = e.detail.value;
			},

			async wechatLogin() {
				if (this.loading) return;
				this.loading = true;

				try {
					// 第一次点击：获取登录code，显示填写表单
					if (!this.showProfileForm) {
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
						this.loginCode = loginRes.code;
						this.showProfileForm = true;
						this.loading = false;
						return;
					}

					// 第二次点击：完成注册/登录
					let avatarUrl = '';
					
					// 如果用户选择了头像，先上传
					if (this.userInfo.avatarUrl && !this.userInfo.avatarUrl.includes('default-avatar')) {
						try {
							avatarUrl = await this.uploadAvatar(this.userInfo.avatarUrl);
						} catch (err) {
							console.error('Upload avatar error:', err);
							// 上传失败不影响登录，继续使用默认头像
						}
					}

					// 准备用户信息
					const userInfoToSubmit = {
						nickName: this.userInfo.nickname || 'User',
						avatarUrl: avatarUrl || '',
						gender: 0,
						city: '',
						province: '',
						country: '',
						language: 'zh_CN'
					};

					console.log('Submitting user info:', userInfoToSubmit);

					// 发送到后端
					const response = await api.public('/api/v1/auth/wechat-login', {
						code: this.loginCode,
						user_info: userInfoToSubmit
					});

					console.log('Login response:', response);

					if (response && response.access_token && response.user) {
						const { access_token, user } = response;

						// 保存token和用户信息
						uni.setStorageSync('access_token', access_token);
						uni.setStorageSync('userId', user.id);
						uni.setStorageSync('user_info', user);

						uni.showToast({
							title: 'Login Success',
							icon: 'success'
						});

						// 延迟跳转到首页
						setTimeout(() => {
							uni.switchTab({
								url: '/pages/home/home'
							});
						}, 1500);
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
			},

			async uploadAvatar(filePath) {
				const uploadRes = await uni.uploadFile({
					url: `${config.API_BASE_URL}/api/v1/upload/avatar`,
					filePath: filePath,
					name: 'file'
				});

				if (uploadRes.statusCode === 201) {
					const data = JSON.parse(uploadRes.data);
					return `${config.API_BASE_URL}${data.url}`;
				}
				throw new Error('Upload failed');
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
		padding: 40rpx;
	}

	.logo {
		height: 200rpx;
		width: 200rpx;
		margin-top: 100rpx;
		margin-bottom: 50rpx;
	}

	.text-area {
		display: flex;
		justify-content: center;
		margin-bottom: 30rpx;
	}

	.title {
		font-size: 36rpx;
		color: #8f8f94;
	}

	.user-info-area {
		width: 100%;
		margin: 30rpx 0;
		padding: 40rpx;
		background-color: #f5f5f5;
		border-radius: 20rpx;
	}

	.info-item {
		margin-bottom: 40rpx;
		display: flex;
		flex-direction: column;
		align-items: center;
	}

	.label {
		font-size: 28rpx;
		color: #666;
		margin-bottom: 20rpx;
	}

	.avatar-btn {
		display: flex;
		flex-direction: column;
		align-items: center;
		background: transparent;
		border: none;
		padding: 0;
		margin: 0;
		line-height: normal;
	}

	.avatar-btn::after {
		border: none;
	}

	.avatar {
		width: 160rpx;
		height: 160rpx;
		border-radius: 50%;
		border: 4rpx solid #07c160;
	}

	.change-text {
		font-size: 24rpx;
		color: #07c160;
		margin-top: 10rpx;
	}

	.nickname-input {
		width: 100%;
		height: 80rpx;
		line-height: 80rpx;
		padding: 0 30rpx;
		background-color: #fff;
		border: 2rpx solid #ddd;
		border-radius: 10rpx;
		font-size: 28rpx;
		box-sizing: border-box;
	}

	.btn-area {
		margin-top: 50rpx;
		width: 80%;
	}

	.login-btn {
		background-color: #07c160; /* WeChat Green */
		border-radius: 45rpx;
		font-size: 32rpx;
		height: 90rpx;
		line-height: 90rpx;
	}
</style>
