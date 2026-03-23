<template>
	<view class="container">
		<view class="header">
			<view class="profile-card">
				<image class="avatar" :src="userInfo.avatar_url || '/static/default-avatar.png'"></image>
				<text class="nickname">{{ userInfo.nickname || 'User' }}</text>
				<text class="openid">{{ userInfo.openid }}</text>
			</view>
		</view>

		<!-- Edit Profile Form -->
		<view class="form-card" v-if="isEditing">
			<view class="card-title">Edit Profile</view>
			
			<view class="form-item">
				<text class="label">Name</text>
				<input class="input" v-model="editForm.name" placeholder="Please enter your name" />
			</view>

			<view class="form-item">
				<text class="label">Phone</text>
				<input class="input" v-model="editForm.phone" type="number" placeholder="Please enter phone number" />
			</view>

			<view class="form-item">
				<text class="label">Department</text>
				<picker mode="selector" :range="departments" @change="onDepartmentChange">
					<view class="picker-value">
						<text :class="{ 'placeholder': !editForm.department }">
							{{ editForm.department || 'Please select department' }}
						</text>
						<text class="arrow">›</text>
					</view>
				</picker>
			</view>

			<view class="button-group">
				<button class="cancel-btn" @click="cancelEdit">Cancel</button>
				<button class="save-btn" @click="saveProfile" :loading="saving">Save</button>
			</view>
		</view>

		<view class="menu-list" v-else>
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

		<!-- Profile Info Display -->
		<view class="info-card" v-if="!isEditing">
			<view class="info-item">
				<text class="info-label">Name</text>
				<text class="info-value">{{ userInfo.name || 'Not set' }}</text>
			</view>
			<view class="info-item">
				<text class="info-label">Phone</text>
				<text class="info-value">{{ userInfo.phone || 'Not set' }}</text>
			</view>
			<view class="info-item">
				<text class="info-label">Department</text>
				<text class="info-value">{{ userInfo.department || 'Not set' }}</text>
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
			userInfo: {},
			isEditing: false,
			saving: false,
			departments: ['信息科', '设备科', '总务科', '动力科', '其他'],
			editForm: {
				name: '',
				phone: '',
				department: ''
			}
		}
	},
	onLoad() {
		this.loadUserInfo()
	},
	methods: {
		async loadUserInfo() {
			try {
				this.userInfo = await api.get('/api/v1/auth/me')
				uni.setStorageSync('user_info', this.userInfo)
			} catch (err) {
				console.error('Load user info error:', err)
				if (err.message !== 'Unauthorized') {
					uni.showToast({
						title: 'Load Failed',
						icon: 'none'
					})
				}
			}
		},

		editProfile() {
			this.isEditing = true
			this.editForm = {
				name: this.userInfo.name || '',
				phone: this.userInfo.phone || '',
				department: this.userInfo.department || ''
			}
		},

		onDepartmentChange(e) {
			const index = e.detail.value
			this.editForm.department = this.departments[index]
		},

		cancelEdit() {
			this.isEditing = false
			this.editForm = {
				name: '',
				phone: '',
				department: ''
			}
		},

		async saveProfile() {
			if (this.saving) return

			if (!this.editForm.name || !this.editForm.phone || !this.editForm.department) {
				uni.showToast({
					title: 'Please fill all fields',
					icon: 'none'
				})
				return
			}

			this.saving = true
			try {
				const updatedUser = await api.put('/api/v1/auth/profile', {
					name: this.editForm.name,
					phone: this.editForm.phone,
					department: this.editForm.department
				})

				this.userInfo = updatedUser
				uni.setStorageSync('user_info', updatedUser)

				uni.showToast({
					title: 'Saved Successfully',
					icon: 'success'
				})

				this.isEditing = false
			} catch (err) {
				console.error('Save profile error:', err)
				uni.showToast({
					title: err.message || 'Save Failed',
					icon: 'none'
				})
			} finally {
				this.saving = false
			}
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

.form-card {
	margin: -40rpx 30rpx 30rpx;
	background: #fff;
	border-radius: 16rpx;
	padding: 40rpx;
	box-shadow: 0 4rpx 20rpx rgba(0, 0, 0, 0.05);
}

.card-title {
	font-size: 36rpx;
	font-weight: bold;
	color: #333;
	margin-bottom: 40rpx;
}

.form-item {
	margin-bottom: 30rpx;
}

.label {
	display: block;
	font-size: 28rpx;
	color: #666;
	margin-bottom: 15rpx;
	font-weight: 500;
}

.input {
	width: 100%;
	height: 80rpx;
	padding: 0 20rpx;
	background: #f5f5f5;
	border-radius: 8rpx;
	font-size: 28rpx;
}

.picker-value {
	display: flex;
	justify-content: space-between;
	align-items: center;
	height: 80rpx;
	padding: 0 20rpx;
	background: #f5f5f5;
	border-radius: 8rpx;
	font-size: 28rpx;
}

.picker-value .placeholder {
	color: #999;
}

.button-group {
	display: flex;
	gap: 20rpx;
	margin-top: 40rpx;
}

.cancel-btn, .save-btn {
	flex: 1;
	height: 80rpx;
	line-height: 80rpx;
	border-radius: 8rpx;
	font-size: 28rpx;
	border: none;
}

.cancel-btn {
	background: #f5f5f5;
	color: #666;
}

.save-btn {
	background: #07c160;
	color: #fff;
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

.info-card {
	margin: 30rpx;
	background: #fff;
	border-radius: 16rpx;
	padding: 40rpx;
	box-shadow: 0 4rpx 20rpx rgba(0, 0, 0, 0.05);
}

.info-item {
	display: flex;
	justify-content: space-between;
	align-items: center;
	padding: 20rpx 0;
	border-bottom: 1rpx solid #f5f5f5;
}

.info-item:last-child {
	border-bottom: none;
}

.info-label {
	font-size: 28rpx;
	color: #666;
}

.info-value {
	font-size: 28rpx;
	color: #333;
	font-weight: 500;
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
