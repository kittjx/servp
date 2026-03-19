<template>
	<view class="container">
		<view class="header">
			<view class="profile-card">
				<image class="avatar" :src="userInfo.avatar_url || '/static/default-avatar.png'"></image>
				<text class="nickname">{{ userInfo.nickname || 'User' }}</text>
				<text class="openid">{{ userInfo.openid }}</text>
			</view>
		</view>

		<view class="menu-list">
			<view class="menu-item" @click="editProfile">
				<view class="menu-left">
					<text class="icon">✏️</text>
					<text class="label">Edit Profile</text>
				</view>
				<text class="arrow">›</text>
			</view>

			<view class="menu-item" @click="viewStatistics">
				<view class="menu-left">
					<text class="icon">📊</text>
					<text class="label">Statistics</text>
				</view>
				<text class="arrow">›</text>
			</view>

			<view class="menu-item" @click="viewSettings">
				<view class="menu-left">
					<text class="icon">⚙️</text>
					<text class="label">Settings</text>
				</view>
				<text class="arrow">›</text>
			</view>
		</view>

		<view class="logout-btn" @click="logout">
			<text>Logout</text>
		</view>
	</view>
</template>

<script>
import api from '../../utils/api.js'

export default {
	data() {
		return {
			userInfo: {}
		}
	},
	onLoad() {
		this.loadUserInfo()
	},
	methods: {
		async loadUserInfo() {
			try {
				// 使用 API 封装获取当前用户信息
				this.userInfo = await api.get('/api/v1/auth/me')
				// 更新本地存储
				uni.setStorageSync('user_info', this.userInfo)
			} catch (err) {
				console.error('Load user info error:', err)
				// 401 错误已经由 api.js 统一处理
				if (err.message !== 'Unauthorized') {
					uni.showToast({
						title: 'Load Failed',
						icon: 'none'
					})
				}
			}
		},

		editProfile() {
			uni.showToast({
				title: 'Coming Soon',
				icon: 'none'
			})
		},

		viewStatistics() {
			uni.navigateTo({
				url: '/pages/statistics/index'
			})
		},

		viewSettings() {
			uni.navigateTo({
				url: '/pages/settings/index'
			})
		},

		logout() {
			uni.showModal({
				title: 'Confirm Logout',
				content: 'Are you sure to logout?',
				success: (res) => {
					if (res.confirm) {
						// 使用 API 封装清除缓存并跳转
						api.clearCacheAndLogin()
					}
				}
			})
		}
	}
}
</script>

<style>
.container {
	min-height: 100vh;
	background: #f5f5f5;
	padding-bottom: 20rpx;
}

.header {
	background: #07c160;
	padding: 60rpx 30rpx 80rpx;
}

.profile-card {
	display: flex;
	flex-direction: column;
	align-items: center;
}

.avatar {
	width: 160rpx;
	height: 160rpx;
	border-radius: 50%;
	border: 6rpx solid #fff;
	margin-bottom: 20rpx;
}

.nickname {
	font-size: 36rpx;
	font-weight: bold;
	color: #fff;
	margin-bottom: 10rpx;
}

.openid {
	font-size: 24rpx;
	color: rgba(255, 255, 255, 0.8);
}

.menu-list {
	margin: -40rpx 30rpx 30rpx;
	background: #fff;
	border-radius: 16rpx;
	overflow: hidden;
	box-shadow: 0 4rpx 20rpx rgba(0, 0, 0, 0.05);
}

.menu-item {
	display: flex;
	justify-content: space-between;
	align-items: center;
	padding: 30rpx;
	border-bottom: 1rpx solid #f5f5f5;
}

.menu-item:last-child {
	border-bottom: none;
}

.menu-left {
	display: flex;
	align-items: center;
}

.icon {
	font-size: 40rpx;
	margin-right: 20rpx;
}

.label {
	font-size: 28rpx;
	color: #333;
}

.arrow {
	font-size: 40rpx;
	color: #999;
}

.logout-btn {
	margin: 30rpx;
	padding: 30rpx;
	background: #fff;
	border-radius: 16rpx;
	text-align: center;
	font-size: 32rpx;
	color: #f44336;
	font-weight: 500;
	box-shadow: 0 4rpx 20rpx rgba(0, 0, 0, 0.05);
}
</style>
