<template>
	<view class="container">
		<view class="content">
			<view class="header">
				<view class="user-info">
					<image class="avatar" :src="userInfo.avatar_url || '/static/default-avatar.png'"></image>
					<view class="user-text">
						<text class="nickname">{{ userInfo.nickname || 'User' }}</text>
						<text class="welcome">Welcome to Hospital Service</text>
					</view>
				</view>
			</view>

			<view class="form-card">
				<view class="card-title">Submit Work Order</view>

				<!-- 工单类别 -->
				<view class="form-item">
					<text class="label">Category</text>
					<picker mode="selector" :range="categories" @change="onCategoryChange">
						<view class="picker-value">
							<text>{{ selectedCategory || 'Please select category' }}</text>
							<text class="arrow">›</text>
						</view>
					</picker>
				</view>

				<!-- 优先级 -->
				<view class="form-item">
					<text class="label">Priority</text>
					<view class="priority-group">
						<view 
							v-for="(item, index) in priorities" 
							:key="index"
							class="priority-item"
							:class="{ 'active': selectedPriority === item.value }"
							@click="selectPriority(item.value)"
						>
							<text>{{ item.label }}</text>
						</view>
					</view>
				</view>

				<!-- 问题描述 -->
				<view class="form-item">
					<text class="label">Description</text>
					<textarea 
						class="textarea"
						v-model="description"
						placeholder="Please describe your issue in detail..."
						maxlength="500"
					/>
					<text class="word-count">{{ description.length }}/500</text>
				</view>

				<!-- 图片上传 -->
				<view class="form-item">
					<text class="label">Attachments (Optional)</text>
					<view class="image-upload">
						<view class="image-list">
							<view class="image-item" v-for="(img, index) in imageList" :key="index">
								<image :src="img" mode="aspectFill" @click="previewImage(index)"></image>
								<view class="delete-btn" @click="deleteImage(index)">×</view>
							</view>
							<view class="add-image" v-if="imageList.length < 9" @click="chooseImage">
								<text class="plus">+</text>
								<text class="add-text">Add Photo</text>
							</view>
						</view>
					</view>
				</view>

				<!-- 提交按钮 -->
				<button class="submit-btn" @click="submitOrder" :loading="submitting" :disabled="!canSubmit">
					Submit Work Order
				</button>
			</view>

			<!-- 历史工单入口 -->
			<view class="history-entry" @click="goToHistory">
				<text>View My Orders</text>
				<text class="arrow">›</text>
			</view>
		</view>
	</view>
</template>

<script>
import api from '../../utils/api.js'

export default {
	data() {
		return {
			userInfo: {},
			categories: ['Equipment Repair', 'Facility Maintenance', 'IT Support', 'Cleaning Service', 'Security Issue', 'Other'],
			selectedCategory: '',
			priorities: [
				{ label: 'Urgent', value: 'urgent' },
				{ label: 'High', value: 'high' },
				{ label: 'Normal', value: 'normal' }
			],
			selectedPriority: 'normal',
			description: '',
			imageList: [],
			submitting: false
		}
	},
	computed: {
		canSubmit() {
			return this.selectedCategory && this.description.trim() && !this.submitting
		}
	},
	onLoad() {
		this.verifyUser()
	},
	methods: {
		async verifyUser() {
			try {
				// 验证用户是否存在（需要认证，后端会验证 token 和用户是否存在）
				await api.get('/api/v1/auth/me')
				// 用户存在，加载用户信息
				this.loadUserInfo()
			} catch (err) {
				// 用户不存在或 token 无效，清除缓存并跳转到登录页
				api.clearCacheAndLogin()
			}
		},

		loadUserInfo() {
			const userInfo = uni.getStorageSync('user_info')
			if (userInfo) {
				this.userInfo = userInfo
			}
		},

		onCategoryChange(e) {
			const index = e.detail.value
			this.selectedCategory = this.categories[index]
		},

		selectPriority(value) {
			this.selectedPriority = value
		},

		chooseImage() {
			uni.chooseImage({
				count: 9 - this.imageList.length,
				sizeType: ['compressed'],
				sourceType: ['album', 'camera'],
				success: (res) => {
					this.imageList = this.imageList.concat(res.tempFilePaths)
				}
			})
		},

		previewImage(index) {
			uni.previewImage({
				urls: this.imageList,
				current: index
			})
		},

		deleteImage(index) {
			uni.showModal({
				title: 'Confirm Delete',
				content: 'Are you sure to delete this image?',
				success: (res) => {
					if (res.confirm) {
						this.imageList.splice(index, 1)
					}
				}
			})
		},

		async submitOrder() {
			if (!this.canSubmit) return

			this.submitting = true

			try {
				// 上传图片
				const mediaUrls = []
				if (this.imageList.length > 0) {
					for (let imgPath of this.imageList) {
						const url = await this.uploadImage(imgPath)
						if (url) {
							mediaUrls.push(url)
						}
					}
				}

				// 提交工单（不需要传递 reporter_id，后端会自动使用当前用户）
				await api.post('/api/v1/order/create', {
					description: this.description,
					media_urls: mediaUrls.length > 0 ? mediaUrls : null,
					priority: this.selectedPriority,
					category: this.selectedCategory
				})

				uni.showToast({
					title: 'Submit Success',
					icon: 'success'
				})

				// 重置表单
				this.selectedCategory = ''
				this.selectedPriority = 'normal'
				this.description = ''
				this.imageList = []

				// 跳转到工单列表（tabBar页面）
				setTimeout(() => {
					uni.switchTab({
						url: '/pages/order/list'
					})
				}, 1500)
			} catch (err) {
				console.error('Submit error:', err)
				// 401 错误已经由 api.js 统一处理，这里不需要额外处理
				if (err.message !== 'Unauthorized') {
					uni.showToast({
						title: err.message || 'Submit Failed',
						icon: 'none'
					})
				}
			} finally {
				this.submitting = false
			}
		},

		async uploadImage(filePath) {
			try {
				const token = uni.getStorageSync('access_token')
				const uploadRes = await uni.uploadFile({
					url: 'http://localhost:8000/api/v1/upload/image',
					filePath: filePath,
					name: 'file',
					header: {
						'Authorization': `Bearer ${token}`
					}
				})

				if (uploadRes.statusCode === 201) {
					const data = JSON.parse(uploadRes.data)
					return `http://localhost:8000${data.url}`
				}
				return null
			} catch (err) {
				console.error('Upload image error:', err)
				return null
			}
		},

		goToHistory() {
			uni.switchTab({
				url: '/pages/order/list'
			})
		}
	}
}
</script>

<style>
.container {
	min-height: 100vh;
	background: linear-gradient(to bottom, #07c160 0%, #f5f5f5 30%);
	padding-bottom: 20rpx;
}

.content {
	padding-bottom: 20rpx;
}

.header {
	padding: 40rpx 30rpx;
}

.user-info {
	display: flex;
	align-items: center;
}

.avatar {
	width: 100rpx;
	height: 100rpx;
	border-radius: 50%;
	border: 4rpx solid #fff;
	margin-right: 20rpx;
}

.user-text {
	display: flex;
	flex-direction: column;
}

.nickname {
	font-size: 36rpx;
	font-weight: bold;
	color: #fff;
	margin-bottom: 10rpx;
}

.welcome {
	font-size: 24rpx;
	color: rgba(255, 255, 255, 0.8);
}

.form-card {
	margin: 20rpx 30rpx;
	background: #fff;
	border-radius: 20rpx;
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
	margin-bottom: 40rpx;
}

.label {
	display: block;
	font-size: 28rpx;
	color: #666;
	margin-bottom: 20rpx;
	font-weight: 500;
}

.picker-value {
	display: flex;
	justify-content: space-between;
	align-items: center;
	height: 80rpx;
	padding: 0 30rpx;
	background: #f5f5f5;
	border-radius: 10rpx;
	font-size: 28rpx;
}

.arrow {
	font-size: 40rpx;
	color: #999;
}

.priority-group {
	display: flex;
	justify-content: space-between;
}

.priority-item {
	flex: 1;
	height: 70rpx;
	line-height: 70rpx;
	text-align: center;
	margin: 0 10rpx;
	background: #f5f5f5;
	border-radius: 10rpx;
	font-size: 28rpx;
	color: #666;
	transition: all 0.3s;
}

.priority-item:first-child {
	margin-left: 0;
}

.priority-item:last-child {
	margin-right: 0;
}

.priority-item.active {
	background: #07c160;
	color: #fff;
}

.textarea {
	width: 100%;
	min-height: 200rpx;
	padding: 20rpx;
	background: #f5f5f5;
	border-radius: 10rpx;
	font-size: 28rpx;
	box-sizing: border-box;
}

.word-count {
	display: block;
	text-align: right;
	font-size: 24rpx;
	color: #999;
	margin-top: 10rpx;
}

.image-upload {
	margin-top: 20rpx;
}

.image-list {
	display: flex;
	flex-wrap: wrap;
}

.image-item {
	position: relative;
	width: 200rpx;
	height: 200rpx;
	margin: 0 20rpx 20rpx 0;
	border-radius: 10rpx;
	overflow: hidden;
}

.image-item:nth-child(3n) {
	margin-right: 0;
}

.image-item image {
	width: 100%;
	height: 100%;
}

.delete-btn {
	position: absolute;
	top: 10rpx;
	right: 10rpx;
	width: 40rpx;
	height: 40rpx;
	line-height: 36rpx;
	text-align: center;
	background: rgba(0, 0, 0, 0.5);
	color: #fff;
	border-radius: 50%;
	font-size: 32rpx;
}

.add-image {
	width: 200rpx;
	height: 200rpx;
	display: flex;
	flex-direction: column;
	align-items: center;
	justify-content: center;
	background: #f5f5f5;
	border: 2rpx dashed #ddd;
	border-radius: 10rpx;
}

.plus {
	font-size: 60rpx;
	color: #999;
	line-height: 1;
}

.add-text {
	font-size: 24rpx;
	color: #999;
	margin-top: 10rpx;
}

.submit-btn {
	width: 100%;
	height: 90rpx;
	line-height: 90rpx;
	background: #07c160;
	color: #fff;
	border-radius: 45rpx;
	font-size: 32rpx;
	font-weight: 500;
	margin-top: 40rpx;
}

.submit-btn[disabled] {
	background: #ccc;
}

.history-entry {
	display: flex;
	justify-content: space-between;
	align-items: center;
	margin: 30rpx;
	padding: 30rpx;
	background: #fff;
	border-radius: 20rpx;
	font-size: 28rpx;
	color: #333;
	box-shadow: 0 4rpx 20rpx rgba(0, 0, 0, 0.05);
}

.history-entry .arrow {
	font-size: 40rpx;
	color: #999;
}
</style>
