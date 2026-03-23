<template>
	<view class="container">
		<view class="header">
			<text class="title">My Orders</text>
			<text class="subtitle" v-if="userInfo.is_leader">{{ userInfo.department }} - Manager</text>
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
			<view 
				v-if="userInfo.is_leader"
				class="tab-item" 
				:class="{ 'active': activeTab === 2 }"
				@click="switchTab(2)"
			>
				<text class="tab-text">Department</text>
				<view class="tab-badge" v-if="departmentOrders.length > 0">
					<text>{{ departmentOrders.length }}</text>
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
						<text class="reporter-name">{{ order.reporter.nickname || order.reporter.name || 'Unknown' }}</text>
					</view>
				</view>

				<view class="order-footer">
					<text class="priority" :class="order.priority">{{ getPriorityText(order.priority) }}</text>
					<text class="time">{{ formatTime(order.created_at) }}</text>
				</view>
			</view>

			<view class="empty" v-if="assignedOrders.length === 0 && !loading">
				<text class="empty-icon">📥</text>
				<text class="empty-text">No assigned orders yet</text>
			</view>
		</view>

		<!-- 部门订单列表 (仅部门主管可见) -->
		<view class="order-list" v-if="activeTab === 2 && userInfo.is_leader">
			<view 
				class="order-item" 
				v-for="order in departmentOrders" 
				:key="order.id"
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
					<view class="personnel-info">
						<view class="person-item" v-if="order.reporter">
							<text class="person-label">Reporter:</text>
							<text class="person-name">{{ order.reporter.name || order.reporter.nickname || 'Unknown' }}</text>
						</view>
						<view class="person-item" v-if="order.handler">
							<text class="person-label">Handler:</text>
							<text class="person-name">{{ order.handler.name || order.handler.nickname || 'Unassigned' }}</text>
						</view>
					</view>
				</view>

				<view class="order-footer">
					<text class="priority" :class="order.priority">{{ getPriorityText(order.priority) }}</text>
					<view class="footer-actions">
						<text class="time">{{ formatTime(order.created_at) }}</text>
						<button 
							v-if="order.status === 'pending' || !order.handler_id"
							class="assign-btn" 
							@click.stop="showAssignModal(order)"
						>
							Assign
						</button>
						<button 
							class="detail-btn" 
							@click.stop="goToDetail(order.id)"
						>
							Detail
						</button>
					</view>
				</view>
			</view>

			<view class="empty" v-if="departmentOrders.length === 0 && !loading">
				<text class="empty-icon">🏢</text>
				<text class="empty-text">No department orders yet</text>
			</view>
		</view>

		<!-- 加载中 -->
		<view class="loading" v-if="loading">
			<text>Loading...</text>
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
						<text class="order-text">{{ selectedOrder?.order_id }}</text>
					</view>
					<view class="engineer-list">
						<view 
							class="engineer-item" 
							v-for="engineer in engineers" 
							:key="engineer.id"
							:class="{ 'selected': selectedEngineerId === engineer.id }"
							@click="selectEngineer(engineer.id)"
						>
							<image class="engineer-avatar" :src="engineer.avatar_url || '/static/default-avatar.png'"></image>
							<view class="engineer-info">
								<text class="engineer-name">{{ engineer.name || engineer.nickname }}</text>
								<text class="engineer-dept">{{ engineer.department }}</text>
							</view>
							<text class="check-icon" v-if="selectedEngineerId === engineer.id">✓</text>
						</view>
					</view>
				</view>
				<view class="modal-footer">
					<button class="modal-cancel" @click="closeAssignModal">Cancel</button>
					<button class="modal-confirm" @click="confirmAssign" :disabled="!selectedEngineerId">Confirm</button>
				</view>
			</view>
		</view>
	</view>
</template>

<script>
import api from '../../utils/api.js'

export default {
	data() {
		return {
			submittedOrders: [],
			assignedOrders: [],
			departmentOrders: [],
			allOrders: [],
			activeTab: 0,
			loading: false,
			userInfo: {},
			showAssign: false,
			selectedOrder: null,
			selectedEngineerId: null,
			engineers: []
		}
	},
	onLoad() {
		this.userInfo = uni.getStorageSync('user_info') || {}
		this.loadOrders()
		if (this.userInfo.is_leader) {
			this.loadEngineers()
		}
	},
	onShow() {
		this.userInfo = uni.getStorageSync('user_info') || {}
		this.loadOrders()
	},
	methods: {
		switchTab(index) {
			this.activeTab = index
		},

		async loadOrders() {
			this.loading = true
			try {
				const orders = await api.get('/api/v1/order/list?skip=0&limit=100')
				this.allOrders = orders
				this.filterOrders()
			} catch (err) {
				console.error('Load orders error:', err)
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

		async loadEngineers() {
			try {
				this.engineers = await api.get('/api/v1/order/department/engineers')
			} catch (err) {
				console.error('Load engineers error:', err)
			}
		},

		filterOrders() {
			const currentUserId = this.userInfo?.id
			
			if (!currentUserId) {
				this.submittedOrders = []
				this.assignedOrders = []
				this.departmentOrders = []
				return
			}
			
			// Orders I submitted
			this.submittedOrders = this.allOrders.filter(order => 
				order.reporter_id === currentUserId
			)
			
			// Orders assigned to me
			this.assignedOrders = this.allOrders.filter(order => 
				order.handler_id === currentUserId
			)
			
			// Department orders (for leaders) - show ALL orders in department category
			if (this.userInfo.is_leader && this.userInfo.department) {
				this.departmentOrders = this.allOrders.filter(order => 
					order.category === this.userInfo.department
				)
			}
		},

		showAssignModal(order) {
			this.selectedOrder = order
			this.selectedEngineerId = order.handler_id || null
			this.showAssign = true
		},

		closeAssignModal() {
			this.showAssign = false
			this.selectedOrder = null
			this.selectedEngineerId = null
		},

		selectEngineer(engineerId) {
			this.selectedEngineerId = engineerId
		},

		async confirmAssign() {
			if (!this.selectedEngineerId) return

			try {
				await api.post('/api/v1/order/assign', {
					order_id: this.selectedOrder.id,
					new_handler_id: this.selectedEngineerId
				})

				uni.showToast({
					title: 'Assigned Successfully',
					icon: 'success'
				})

				this.closeAssignModal()
				this.loadOrders()
			} catch (err) {
				console.error('Assign order error:', err)
				uni.showToast({
					title: err.message || 'Assign Failed',
					icon: 'none'
				})
			}
		},

		goToDetail(orderId) {
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

.subtitle {
	font-size: 24rpx;
	color: rgba(255, 255, 255, 0.9);
	margin-top: 10rpx;
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

.personnel-info {
	margin-top: 10rpx;
	padding: 10rpx;
	background: #f5f5f5;
	border-radius: 8rpx;
}

.person-item {
	display: flex;
	align-items: center;
	margin-bottom: 5rpx;
}

.person-item:last-child {
	margin-bottom: 0;
}

.person-label {
	font-size: 24rpx;
	color: #999;
	margin-right: 10rpx;
	min-width: 120rpx;
}

.person-name {
	font-size: 26rpx;
	color: #333;
	font-weight: 500;
}

.footer-actions {
	display: flex;
	align-items: center;
	gap: 10rpx;
}

.assign-btn, .detail-btn {
	padding: 8rpx 20rpx;
	border-radius: 6rpx;
	font-size: 24rpx;
	border: none;
	line-height: 1;
}

.assign-btn {
	background: #07c160;
	color: #fff;
}

.detail-btn {
	background: #f5f5f5;
	color: #666;
}

.modal-mask {
	position: fixed;
	top: 0;
	left: 0;
	right: 0;
	bottom: 0;
	background: rgba(0, 0, 0, 0.5);
	display: flex;
	align-items: center;
	justify-content: center;
	z-index: 1000;
}

.modal-content {
	width: 600rpx;
	background: #fff;
	border-radius: 16rpx;
	overflow: hidden;
}

.modal-header {
	display: flex;
	justify-content: space-between;
	align-items: center;
	padding: 30rpx;
	border-bottom: 1rpx solid #f5f5f5;
}

.modal-title {
	font-size: 32rpx;
	font-weight: bold;
	color: #333;
}

.modal-close {
	font-size: 40rpx;
	color: #999;
}

.modal-body {
	padding: 30rpx;
	max-height: 600rpx;
	overflow-y: auto;
}

.order-info {
	display: flex;
	align-items: center;
	margin-bottom: 20rpx;
	padding-bottom: 20rpx;
	border-bottom: 1rpx solid #f5f5f5;
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

.engineer-list {
	display: flex;
	flex-direction: column;
	gap: 15rpx;
}

.engineer-item {
	display: flex;
	align-items: center;
	padding: 20rpx;
	background: #f5f5f5;
	border-radius: 12rpx;
	border: 2rpx solid transparent;
}

.engineer-item.selected {
	background: #e8f5e9;
	border-color: #07c160;
}

.engineer-avatar {
	width: 80rpx;
	height: 80rpx;
	border-radius: 50%;
	margin-right: 20rpx;
}

.engineer-info {
	flex: 1;
	display: flex;
	flex-direction: column;
}

.engineer-name {
	font-size: 28rpx;
	color: #333;
	font-weight: 500;
	margin-bottom: 5rpx;
}

.engineer-dept {
	font-size: 24rpx;
	color: #999;
}

.check-icon {
	font-size: 40rpx;
	color: #07c160;
	font-weight: bold;
}

.modal-footer {
	display: flex;
	gap: 20rpx;
	padding: 30rpx;
	border-top: 1rpx solid #f5f5f5;
}

.modal-cancel, .modal-confirm {
	flex: 1;
	height: 80rpx;
	line-height: 80rpx;
	border-radius: 8rpx;
	font-size: 28rpx;
	border: none;
}

.modal-cancel {
	background: #f5f5f5;
	color: #666;
}

.modal-confirm {
	background: #07c160;
	color: #fff;
}

.modal-confirm[disabled] {
	background: #ccc;
	color: #999;
}
</style>
