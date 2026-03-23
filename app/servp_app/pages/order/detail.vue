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
				<view class="info-item" v-if="order.media_urls && order.media_urls.length > 0">
					<text class="label">Attachments</text>
					<view class="image-list">
						<image 
							v-for="(url, index) in order.media_urls" 
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
						<image :src="order.reporter.avatar_url || '/static/default-avatar.png'" class="avatar"></image>
						<text class="value">{{ order.reporter.nickname || order.reporter.name || 'Unknown' }}</text>
					</view>
				</view>

				<view class="info-item" v-if="order.handler">
					<text class="label">Handler</text>
					<view class="user-info">
						<image :src="order.handler.avatar_url || '/static/default-avatar.png'" class="avatar"></image>
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
			</view>
		</view>
	</view>
</template>

<script>
import api from '../../utils/api.js'

export default {
	data() {
		return {
			orderId: null,
			order: null,
			processRecords: [],
			loading: false,
			userInfo: null
		}
	},
	computed: {
		isReporter() {
			return this.userInfo && this.order && this.order.reporter_id === this.userInfo.id
		},
		isHandler() {
			return this.userInfo && this.order && this.order.handler_id === this.userInfo.id
		}
	},
	onLoad(options) {
		this.orderId = options.id
		this.userInfo = uni.getStorageSync('user_info')
		this.loadOrderDetail()
	},
	methods: {
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

		previewImage(index) {
			uni.previewImage({
				urls: this.order.media_urls,
				current: index
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
</style>
