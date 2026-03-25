<template>
	<view class="container">
		<!-- 加载中 -->
		<view class="loading" v-if="loading">
			<text>Loading...</text>
		</view>

		<view v-else-if="order">
			<!-- 订单状态卡片 -->
			<view class="status-card">
				<view class="status-header">
					<view class="status-badge" :class="getStatusClass(order.status)">
						<text>{{ getStatusText(order.status) }}</text>
					</view>
					<text class="order-id">{{ order.order_id }}</text>
				</view>
				<text class="priority" :class="order.priority">{{ getPriorityText(order.priority) }}</text>
			</view>

			<!-- 订单信息 -->
			<view class="info-card">
				<view class="card-title">Order Information</view>
				
				<view class="info-item">
					<text class="label">Category</text>
					<text class="value">{{ order.category }}</text>
				</view>

				<view class="info-item">
					<text class="label">Description</text>
					<text class="value description">{{ order.description }}</text>
				</view>

				<!-- 图片附件 -->
				<view class="info-item" v-if="displayMediaUrls && displayMediaUrls.length > 0">
					<text class="label">Attachments</text>
					<view class="image-list">
						<image 
							v-for="(url, index) in displayMediaUrls" 
							:key="index"
							:src="url" 
							mode="aspectFill"
							@click="previewImage(index)"
							class="attachment-image"
						></image>
					</view>
				</view>

				<view class="info-item">
					<text class="label">Created At</text>
					<text class="value">{{ formatDateTime(order.created_at) }}</text>
				</view>

				<view class="info-item" v-if="order.completed_at">
					<text class="label">Completed At</text>
					<text class="value">{{ formatDateTime(order.completed_at) }}</text>
				</view>
			</view>

			<!-- 人员信息 -->
			<view class="info-card">
				<view class="card-title">Personnel</view>
				
				<view class="info-item" v-if="order.reporter">
					<text class="label">Reporter</text>
					<view class="user-info">
						<image class="avatar" :src="getUserAvatar(order.reporter)"></image>
						<text class="value">{{ order.reporter.nickname || order.reporter.name || 'Unknown' }}</text>
					</view>
				</view>

				<view class="info-item" v-if="order.handler">
					<text class="label">Handler</text>
					<view class="user-info">
						<image class="avatar" :src="getUserAvatar(order.handler)"></image>
						<text class="value">{{ order.handler.nickname || order.handler.name || 'Unassigned' }}</text>
					</view>
				</view>
			</view>

			<!-- 处理记录 -->
			<view class="info-card" v-if="processRecords.length > 0">
				<view class="card-title">Process Records</view>
				
				<view class="timeline">
					<view class="timeline-item" v-for="record in processRecords" :key="record.id">
						<view class="timeline-dot"></view>
						<view class="timeline-content">
							<text class="timeline-action">{{ record.action }}</text>
							<text class="timeline-notes" v-if="record.notes">{{ record.notes }}</text>
							<text class="timeline-time">{{ formatDateTime(record.created_at) }}</text>
						</view>
					</view>
				</view>
			</view>

			<!-- 满意度评分 -->
			<view class="info-card" v-if="order.satisfaction_score">
				<view class="card-title">Satisfaction</view>
				<view class="rating">
					<text v-for="i in 5" :key="i" class="star" :class="{ 'filled': i <= order.satisfaction_score }">★</text>
				</view>
			</view>

			<!-- 操作按钮 -->
			<view class="action-buttons">
				<!-- 报单人视角 -->
				<template v-if="isReporter">
					<button 
						v-if="order.status === 'waiting_for_acceptance'" 
						class="btn btn-primary"
						@click="confirmOrder"
					>
						Confirm Completion
					</button>
					<button 
						v-if="order.status === 'pending'" 
						class="btn btn-secondary"
						@click="cancelOrder"
					>
						Cancel Order
					</button>
				</template>

				<!-- 处理人视角 -->
				<template v-if="isHandler">
					<button 
						v-if="order.status === 'pending'" 
						class="btn btn-primary"
						@click="acceptOrder"
					>
						Accept Order
					</button>
					<button 
						v-if="order.status === 'processing'" 
						class="btn btn-primary"
						@click="completeOrder"
					>
						Mark as Complete
					</button>
					<button 
						v-if="order.status === 'processing'" 
						class="btn btn-secondary"
						@click="addProcessRecord"
					>
						Add Process Record
					</button>
				</template>

				<!-- 部门领导视角 - 可以分配/重新分配 -->
				<template v-if="userInfo && userInfo.is_leader && order.status !== 'completed'">
					<button 
						class="btn btn-primary"
						@click="showAssignModal"
					>
						{{ order.handler_id ? 'Reassign' : 'Assign' }}
					</button>
				</template>

				<!-- 普通部门成员 - 可以接单 -->
				<template v-if="userInfo && !userInfo.is_leader && order.status === 'pending' && !order.handler_id">
					<button 
						class="btn btn-primary"
						@click="acceptOrder"
					>
						Accept Order
					</button>
				</template>
			</view>

			<!-- 分配工程师弹窗 -->
			<view class="modal-mask" v-if="showAssign" @click="closeAssignModal">
				<view class="modal-content" @click.stop>
					<view class="modal-header">
						<text class="modal-title">Assign Engineer</text>
						<text class="modal-close" @click="closeAssignModal">✕</text>
					</view>
					<view class="modal-body">
						<view class="order-info">
							<text class="order-label">Order:</text>
							<text class="order-text">{{ order?.order_id }}</text>
						</view>
						<view class="form-item">
							<text class="label">Select Engineer</text>
							<picker 
								mode="selector" 
								:range="engineers" 
								range-key="name"
								:value="selectedEngineerIndex"
								@change="onEngineerChange"
							>
								<view class="picker-value">
									<text :class="{ 'placeholder': selectedEngineerId === null }">
										{{ selectedEngineerName || 'Please select an engineer' }}
									</text>
									<text class="arrow">›</text>
								</view>
							</picker>
						</view>
					</view>
					<view class="modal-footer">
						<button class="modal-cancel" @click="closeAssignModal">Cancel</button>
						<button class="modal-confirm" @click="confirmAssign" :disabled="!selectedEngineerId">Confirm</button>
					</view>
				</view>
			</view>
		</view>
	</view>
</template>

<script>
import api from '../../utils/api.js'
import config from '../../config/config.js'

export default {
	data() {
		return {
			orderId: null,
			order: null,
			processRecords: [],
			loading: false,
			userInfo: null,
			showAssign: false,
			selectedEngineerId: null,
			selectedEngineerIndex: -1,
			engineers: []
		}
	},
	computed: {
		isReporter() {
			return this.userInfo && this.order && this.order.reporter_id === this.userInfo.id
		},
		isHandler() {
			return this.userInfo && this.order && this.order.handler_id === this.userInfo.id
		},
		// Transform media URLs to use HTTPS
		displayMediaUrls() {
			if (!this.order || !this.order.media_urls) return []
			return this.order.media_urls.map(url => this.fixImageUrl(url))
		},
		selectedEngineerName() {
			if (this.selectedEngineerIndex >= 0 && this.engineers[this.selectedEngineerIndex]) {
				const engineer = this.engineers[this.selectedEngineerIndex]
				return engineer.name || engineer.nickname
			}
			return ''
		}
	},
	onLoad(options) {
		this.orderId = options.id
		this.loadUserInfo()
		this.loadOrderDetail()
	},
	methods: {
		async loadUserInfo() {
			try {
				this.userInfo = await api.get('/api/v1/auth/me')
				if (this.userInfo.is_leader) {
					this.loadEngineers()
				}
			} catch (err) {
				console.error('Load user info error:', err)
				this.userInfo = uni.getStorageSync('user_info') || {}
			}
		},

		async loadEngineers() {
			try {
				this.engineers = await api.get('/api/v1/order/department/engineers')
			} catch (err) {
				console.error('Load engineers error:', err)
			}
		},

		showAssignModal() {
			this.selectedEngineerId = this.order.handler_id || null
			this.showEngineerList = false
			this.showAssign = true
		},

		closeAssignModal() {
			this.showAssign = false
			this.selectedEngineerId = null
			this.showEngineerList = false
		},

		onEngineerChange(e) {
			const index = e.detail.value
			this.selectedEngineerIndex = index
			this.selectedEngineerId = this.engineers[index].id
		},

		async confirmAssign() {
			if (!this.selectedEngineerId) {
				uni.showToast({
					title: 'Please select an engineer',
					icon: 'none'
				})
				return
			}

			try {
				await api.post('/api/v1/order/assign', {
					order_id: this.order.id,
					new_handler_id: this.selectedEngineerId
				})

				uni.showToast({
					title: 'Assigned Successfully',
					icon: 'success'
				})

				this.closeAssignModal()
				this.loadOrderDetail()
			} catch (err) {
				console.error('Error assigning engineer:', err)
				const errorMsg = typeof err.message === 'string' ? err.message : 'Assign Failed'
				uni.showToast({
					title: errorMsg,
					icon: 'none'
				})
			}
		},
		fixImageUrl(url) {
			if (!url) return url
			// Replace http://localhost:8000 with config base URL
			return url.replace('http://localhost:8000', config.API_BASE_URL)
		},
		
		getUserAvatar(user) {
			if (!user || !user.avatar_url) {
				return '/static/default-avatar.png'
			}
			if (user.avatar_url.includes('__tmp__') || user.avatar_url.startsWith('http://tmp')) {
				return '/static/default-avatar.png'
			}
			return this.fixImageUrl(user.avatar_url)
		},
		
		previewImage(index) {
			uni.previewImage({
				urls: this.displayMediaUrls,
				current: index
			})
		},
		
		async loadOrderDetail() {
			this.loading = true
			try {
				this.order = await api.get(`/api/v1/order/${this.orderId}`)
				await this.loadProcessRecords()
			} catch (err) {
				console.error('Load order detail error:', err)
				if (err.message !== 'Unauthorized') {
					uni.showToast({
						title: 'Load Failed',
						icon: 'none'
					})
				}
			} finally {
				this.loading = false
			}
		},

		async loadProcessRecords() {
			try {
				this.processRecords = await api.get(`/api/v1/order/process-records/${this.orderId}`)
			} catch (err) {
				console.error('Load process records error:', err)
			}
		},

		async acceptOrder() {
			try {
				await api.post('/api/v1/order/accept', {
					order_id: this.order.id
				})
				uni.showToast({
					title: 'Order Accepted',
					icon: 'success'
				})
				this.loadOrderDetail()
			} catch (err) {
				console.error('Accept order error:', err)
			}
		},

		async completeOrder() {
			try {
				await api.post('/api/v1/order/process', {
					order_id: this.order.id
				})
				uni.showToast({
					title: 'Marked as Complete',
					icon: 'success'
				})
				this.loadOrderDetail()
			} catch (err) {
				console.error('Complete order error:', err)
			}
		},

		async confirmOrder() {
			uni.showModal({
				title: 'Confirm Completion',
				content: 'Please rate your satisfaction (1-5 stars)',
				editable: true,
				placeholderText: 'Enter 1-5',
				success: async (res) => {
					if (res.confirm) {
						const score = parseInt(res.content) || 5
						try {
							await api.post('/api/v1/order/confirm', {
								order_id: this.order.id,
								satisfaction_score: Math.min(Math.max(score, 1), 5)
							})
							uni.showToast({
								title: 'Order Confirmed',
								icon: 'success'
							})
							this.loadOrderDetail()
						} catch (err) {
							console.error('Confirm order error:', err)
						}
					}
				}
			})
		},

		addProcessRecord() {
			uni.showModal({
				title: 'Add Process Record',
				editable: true,
				placeholderText: 'Enter process notes',
				success: async (res) => {
					if (res.confirm && res.content) {
						try {
							await api.post('/api/v1/order/process-record', {
								order_id: this.order.id,
								action: 'processing',
								notes: res.content
							})
							uni.showToast({
								title: 'Record Added',
								icon: 'success'
							})
							this.loadProcessRecords()
						} catch (err) {
							console.error('Add record error:', err)
						}
					}
				}
			})
		},

		cancelOrder() {
			uni.showModal({
				title: 'Cancel Order',
				content: 'Are you sure to cancel this order?',
				success: (res) => {
					if (res.confirm) {
						uni.showToast({
							title: 'Coming Soon',
							icon: 'none'
						})
					}
				}
			})
		},

		getStatusText(status) {
			const statusMap = {
				'pending': 'Pending',
				'processing': 'Processing',
				'waiting_for_acceptance': 'Waiting for Acceptance',
				'completed': 'Completed'
			}
			return statusMap[status] || status
		},

		getStatusClass(status) {
			return status
		},

		getPriorityText(priority) {
			const priorityMap = {
				'urgent': '🔴 Urgent',
				'high': '🟡 High',
				'normal': '🟢 Normal'
			}
			return priorityMap[priority] || priority
		},

		formatDateTime(time) {
			if (!time) return ''
			const date = new Date(time)
			return date.toLocaleString()
		},
		showAssignModal() {
			this.showAssign = true
			this.loadEngineers()
		},
		closeAssignModal() {
			this.showAssign = false
			this.selectedEngineerId = null
			this.showEngineerList = false
		},
		selectEngineer(id) {
			this.selectedEngineerId = id
		}
	}
}
</script>

<style>
.container {
	min-height: 100vh;
	background: #f5f5f5;
	padding-bottom: 120rpx;
}

.loading {
	text-align: center;
	padding: 100rpx;
	color: #999;
}

.status-card {
	background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
	padding: 40rpx 30rpx;
	color: #fff;
}

.status-header {
	display: flex;
	justify-content: space-between;
	align-items: center;
	margin-bottom: 20rpx;
}

.status-badge {
	padding: 8rpx 20rpx;
	border-radius: 20rpx;
	font-size: 24rpx;
	background: rgba(255, 255, 255, 0.3);
}

.order-id {
	font-size: 24rpx;
	opacity: 0.9;
}

.priority {
	font-size: 28rpx;
	font-weight: 500;
}

.info-card {
	background: #fff;
	margin: 20rpx;
	border-radius: 16rpx;
	padding: 30rpx;
}

.card-title {
	font-size: 32rpx;
	font-weight: bold;
	color: #333;
	margin-bottom: 30rpx;
	padding-bottom: 20rpx;
	border-bottom: 1rpx solid #e5e5e5;
}

.info-item {
	display: flex;
	margin-bottom: 25rpx;
}

.info-item:last-child {
	margin-bottom: 0;
}

.label {
	width: 180rpx;
	font-size: 26rpx;
	color: #999;
	flex-shrink: 0;
}

.value {
	flex: 1;
	font-size: 28rpx;
	color: #333;
}

.description {
	line-height: 1.6;
}

.user-info {
	display: flex;
	align-items: center;
	flex: 1;
}

.avatar {
	width: 60rpx;
	height: 60rpx;
	border-radius: 50%;
	margin-right: 15rpx;
}

.image-list {
	display: flex;
	flex-wrap: wrap;
	gap: 15rpx;
	flex: 1;
}

.attachment-image {
	width: 150rpx;
	height: 150rpx;
	border-radius: 8rpx;
}

.timeline {
	position: relative;
	padding-left: 40rpx;
}

.timeline-item {
	position: relative;
	padding-bottom: 40rpx;
}

.timeline-item:last-child {
	padding-bottom: 0;
}

.timeline-dot {
	position: absolute;
	left: -40rpx;
	top: 5rpx;
	width: 20rpx;
	height: 20rpx;
	border-radius: 50%;
	background: #07c160;
	border: 3rpx solid #fff;
	box-shadow: 0 0 0 2rpx #07c160;
}

.timeline-item:not(:last-child) .timeline-dot::after {
	content: '';
	position: absolute;
	left: 50%;
	top: 20rpx;
	width: 2rpx;
	height: 60rpx;
	background: #e5e5e5;
	transform: translateX(-50%);
}

.timeline-content {
	display: flex;
	flex-direction: column;
}

.timeline-action {
	font-size: 28rpx;
	color: #333;
	font-weight: 500;
	margin-bottom: 8rpx;
}

.timeline-notes {
	font-size: 26rpx;
	color: #666;
	margin-bottom: 8rpx;
	line-height: 1.5;
}

.timeline-time {
	font-size: 24rpx;
	color: #999;
}

.rating {
	display: flex;
	gap: 10rpx;
}

.star {
	font-size: 50rpx;
	color: #ddd;
}

.star.filled {
	color: #ffd700;
}

.action-buttons {
	position: fixed;
	bottom: 0;
	left: 0;
	right: 0;
	background: #fff;
	padding: 20rpx 30rpx;
	box-shadow: 0 -2rpx 10rpx rgba(0, 0, 0, 0.05);
	display: flex;
	gap: 20rpx;
}

.btn {
	flex: 1;
	height: 80rpx;
	line-height: 80rpx;
	border-radius: 40rpx;
	font-size: 28rpx;
	border: none;
}

.btn-primary {
	background: #07c160;
	color: #fff;
}

.btn-secondary {
	background: #f5f5f5;
	color: #666;
}

.modal-mask {
	position: fixed;
	top: 0;
	left: 0;
	width: 100%;
	height: 100%;
	background: rgba(0, 0, 0, 0.5);
	display: flex;
	justify-content: center;
	align-items: center;
}

.modal-content {
	background: #fff;
	border-radius: 16rpx;
	width: 80%;
	max-width: 600rpx;
	box-shadow: 0 4rpx 12rpx rgba(0, 0, 0, 0.1);
}

.modal-header {
	display: flex;
	justify-content: space-between;
	align-items: center;
	padding: 20rpx 30rpx;
	border-bottom: 1rpx solid #e5e5e5;
}

.modal-title {
	font-size: 32rpx;
	font-weight: bold;
}

.modal-close {
	font-size: 32rpx;
	cursor: pointer;
}

.modal-body {
	padding: 30rpx;
}

.order-info {
	display: flex;
	align-items: center;
	margin-bottom: 30rpx;
	padding-bottom: 20rpx;
	border-bottom: 1rpx solid #e5e5e5;
}

.order-label {
	font-size: 28rpx;
	color: #666;
	margin-right: 10rpx;
}

.order-text {
	font-size: 28rpx;
	color: #333;
	font-weight: 500;
}

.form-item {
	display: flex;
	flex-direction: column;
	gap: 15rpx;
}

.label {
	font-size: 28rpx;
	color: #333;
	font-weight: 500;
}

.picker-value {
	display: flex;
	justify-content: space-between;
	align-items: center;
	padding: 20rpx;
	background: #f5f5f5;
	border-radius: 8rpx;
	font-size: 28rpx;
}

.picker-value .placeholder {
	color: #999;
}

.arrow {
	font-size: 32rpx;
	color: #999;
}

.modal-footer {
	display: flex;
	justify-content: space-between;
	align-items: center;
	padding: 20rpx 30rpx;
	border-top: 1rpx solid #e5e5e5;
}

.modal-cancel {
	background: #f5f5f5;
	color: #666;
}

.modal-confirm {
	background: #07c160;
	color: #fff;
}
</style>
