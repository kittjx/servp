<template>
	<view class="container">
		<view class="header">
			<text class="title">My Orders</text>
		</view>

		<!-- Tab 切换 -->
		<view class="tab-container">
			<view 
				class="tab-item" 
				:class="{ 'active': activeTab === 0 }"
				@click="switchTab(0)"
			>
				<text class="tab-text">Submitted</text>
				<view class="tab-badge" v-if="submittedOrders.length > 0">
					<text>{{ submittedOrders.length }}</text>
				</view>
			</view>
			<view 
				class="tab-item" 
				:class="{ 'active': activeTab === 1 }"
				@click="switchTab(1)"
			>
				<text class="tab-text">Assigned to Me</text>
				<view class="tab-badge" v-if="assignedOrders.length > 0">
					<text>{{ assignedOrders.length }}</text>
				</view>
			</view>
		</view>

		<!-- 提交的订单列表 -->
		<view class="order-list" v-if="activeTab === 0">
			<view 
				class="order-item" 
				v-for="order in submittedOrders" 
				:key="order.id"
				@click="goToDetail(order.id)"
			>
				<view class="order-header">
					<text class="order-id">{{ order.order_id }}</text>
					<view class="status-badge" :class="getStatusClass(order.status)">
						<text>{{ getStatusText(order.status) }}</text>
					</view>
				</view>

				<view class="order-content">
					<text class="category">{{ order.category }}</text>
					<text class="description">{{ order.description }}</text>
				</view>

				<view class="order-footer">
					<text class="priority" :class="order.priority">{{ getPriorityText(order.priority) }}</text>
					<text class="time">{{ formatTime(order.created_at) }}</text>
				</view>
			</view>

			<!-- 空状态 -->
			<view class="empty" v-if="submittedOrders.length === 0 && !loading">
				<text class="empty-icon">📋</text>
				<text class="empty-text">No submitted orders yet</text>
				<button class="create-btn" @click="goToCreate">Create First Order</button>
			</view>
		</view>

		<!-- 分配给我的订单列表 -->
		<view class="order-list" v-if="activeTab === 1">
			<view 
				class="order-item" 
				v-for="order in assignedOrders" 
				:key="order.id"
				@click="goToDetail(order.id)"
			>
				<view class="order-header">
					<text class="order-id">{{ order.order_id }}</text>
					<view class="status-badge" :class="getStatusClass(order.status)">
						<text>{{ getStatusText(order.status) }}</text>
					</view>
				</view>

				<view class="order-content">
					<text class="category">{{ order.category }}</text>
					<text class="description">{{ order.description }}</text>
					<view class="reporter-info" v-if="order.reporter">
						<text class="reporter-label">Reporter:</text>
						<text class="reporter-name">{{ order.reporter.nickname || 'Unknown' }}</text>
					</view>
				</view>

				<view class="order-footer">
					<text class="priority" :class="order.priority">{{ getPriorityText(order.priority) }}</text>
					<text class="time">{{ formatTime(order.created_at) }}</text>
				</view>
			</view>

			<!-- 空状态 -->
			<view class="empty" v-if="assignedOrders.length === 0 && !loading">
				<text class="empty-icon">📥</text>
				<text class="empty-text">No assigned orders yet</text>
			</view>
		</view>

		<!-- 加载中 -->
		<view class="loading" v-if="loading">
			<text>Loading...</text>
		</view>
	</view>
</template>

<script>
export default {
	data() {
		return {
			submittedOrders: [],
			assignedOrders: [],
			allOrders: [],
			activeTab: 0,
			loading: false,
			apiBaseUrl: 'http://localhost:8000',
			userInfo: {}
		}
	},
	onLoad() {
		this.loadUserInfo()
		this.loadOrders()
	},
	onShow() {
		// 每次显示页面时刷新列表
		this.loadOrders()
	},
	methods: {
		loadUserInfo() {
			this.userInfo = uni.getStorageSync('user_info') || {}
		},

		switchTab(index) {
			this.activeTab = index
		},

		async loadOrders() {
			this.loading = true

			try {
				const token = uni.getStorageSync('access_token')
				const response = await uni.request({
					url: `${this.apiBaseUrl}/api/v1/order/list`,
					method: 'GET',
					header: {
						'Authorization': `Bearer ${token}`
					}
				})

				if (response.statusCode === 200 && response.data) {
					this.allOrders = response.data
					this.filterOrders()
				}
			} catch (err) {
				console.error('Load orders error:', err)
				uni.showToast({
					title: 'Load Failed',
					icon: 'none'
				})
			} finally {
				this.loading = false
			}
		},

		filterOrders() {
			const userId = this.userInfo.id

			this.submittedOrders = this.allOrders.filter(order => order.reporter_id === userId)
			this.assignedOrders = this.allOrders.filter(order => order.handler_id === userId)
		},

		goToDetail(orderId) {
			// 将订单ID存储到全局数据中，然后在目标页面读取
			uni.$emit('viewOrderDetail', { orderId })

			// 由于详情页不是tabBar页面，使用navigateTo
			uni.navigateTo({
				url: `/pages/order/detail?id=${orderId}`
			})
		},

		goToCreate() {
			uni.switchTab({
				url: '/pages/home/home'
			})
		},

		getStatusText(status) {
			const statusMap = {
				'pending': 'Pending',
				'processing': 'Processing',
				'waiting_for_acceptance': 'Waiting',
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

		formatTime(time) {
			const date = new Date(time)
			const now = new Date()
			const diff = now - date

			const minute = 60 * 1000
			const hour = 60 * minute
			const day = 24 * hour

			if (diff < hour) {
				return `${Math.floor(diff / minute)} minutes ago`
			} else if (diff < day) {
				return `${Math.floor(diff / hour)} hours ago`
			} else {
				return date.toLocaleDateString()
			}
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
	padding: 40rpx 30rpx;
}

.title {
	font-size: 36rpx;
	font-weight: bold;
	color: #fff;
}

.tab-container {
	display: flex;
	background: #fff;
	padding: 20rpx;
	border-bottom: 1rpx solid #e5e5e5;
}

.tab-item {
	flex: 1;
	display: flex;
	flex-direction: column;
	align-items: center;
	justify-content: center;
	position: relative;
	padding: 10rpx 0;
}

.tab-text {
	font-size: 28rpx;
	color: #666;
	transition: color 0.3s;
}

.tab-item.active .tab-text {
	color: #07c160;
	font-weight: 500;
}

.tab-badge {
	position: absolute;
	top: -5rpx;
	right: 30%;
	background: #ff4444;
	color: #fff;
	font-size: 20rpx;
	min-width: 30rpx;
	height: 30rpx;
	line-height: 30rpx;
	padding: 0 8rpx;
	border-radius: 15rpx;
	text-align: center;
}

.order-list {
	padding: 20rpx;
}

.order-item {
	background: #fff;
	border-radius: 16rpx;
	padding: 30rpx;
	margin-bottom: 20rpx;
	box-shadow: 0 2rpx 10rpx rgba(0, 0, 0, 0.05);
}

.order-header {
	display: flex;
	justify-content: space-between;
	align-items: center;
	margin-bottom: 20rpx;
}

.order-id {
	font-size: 24rpx;
	color: #999;
}

.status-badge {
	padding: 6rpx 16rpx;
	border-radius: 8rpx;
	font-size: 24rpx;
}

.status-badge.pending {
	background: #fff3e0;
	color: #f57c00;
}

.status-badge.processing {
	background: #e3f2fd;
	color: #1976d2;
}

.status-badge.waiting_for_acceptance {
	background: #f3e5f5;
	color: #7b1fa2;
}

.status-badge.completed {
	background: #e8f5e9;
	color: #388e3c;
}

.order-content {
	margin-bottom: 20rpx;
}

.category {
	display: block;
	font-size: 28rpx;
	font-weight: 500;
	color: #333;
	margin-bottom: 10rpx;
}

.description {
	display: block;
	font-size: 26rpx;
	color: #666;
	line-height: 1.5;
	display: -webkit-box;
	-webkit-line-clamp: 2;
	-webkit-box-orient: vertical;
	overflow: hidden;
}

.reporter-info {
	display: flex;
	align-items: center;
	margin-top: 10rpx;
	padding: 10rpx;
	background: #f5f5f5;
	border-radius: 8rpx;
}

.reporter-label {
	font-size: 24rpx;
	color: #999;
	margin-right: 10rpx;
}

.reporter-name {
	font-size: 26rpx;
	color: #333;
	font-weight: 500;
}

.order-footer {
	display: flex;
	justify-content: space-between;
	align-items: center;
}

.priority {
	font-size: 24rpx;
}

.time {
	font-size: 24rpx;
	color: #999;
}

.empty {
	display: flex;
	flex-direction: column;
	align-items: center;
	justify-content: center;
	padding: 100rpx 0;
}

.empty-icon {
	font-size: 120rpx;
	margin-bottom: 30rpx;
}

.empty-text {
	font-size: 28rpx;
	color: #999;
	margin-bottom: 40rpx;
}

.create-btn {
	background: #07c160;
	color: #fff;
	border-radius: 45rpx;
	padding: 20rpx 60rpx;
	font-size: 28rpx;
}

.loading {
	text-align: center;
	padding: 40rpx;
	color: #999;
	font-size: 28rpx;
}
</style>
