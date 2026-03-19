<template>
	<view class="tab-bar">
		<view 
			class="tab-item" 
			v-for="(tab, index) in tabs" 
			:key="index"
			:class="{ 'active': currentTab === index }"
			@click="switchTab(index)"
		>
			<view class="icon">
				<text>{{ tab.icon }}</text>
			</view>
			<text class="label">{{ tab.label }}</text>
		</view>
	</view>
</template>

<script>
export default {
	name: 'TabBar',
	props: {
		currentTab: {
			type: Number,
			default: 0
		}
	},
	data() {
		return {
			tabs: [
				{
					label: 'Home',
					icon: '🏠'
				},
				{
					label: 'Orders',
					icon: '📋'
				},
				{
					label: 'Profile',
					icon: '👤'
				}
			]
		}
	},
	methods: {
		switchTab(index) {
			this.$emit('tab-change', index)

			const routes = [
				'/pages/home/home',
				'/pages/order/list',
				'/pages/profile/profile'
			]

			uni.switchTab({
				url: routes[index]
			})
		}
	}
}
</script>

<style>
.tab-bar {
	position: fixed;
	bottom: 0;
	left: 0;
	right: 0;
	height: 100rpx;
	display: flex;
	background: #fff;
	border-top: 1rpx solid #e5e5e5;
	box-shadow: 0 -2rpx 10rpx rgba(0, 0, 0, 0.05);
}

.tab-item {
	flex: 1;
	display: flex;
	flex-direction: column;
	align-items: center;
	justify-content: center;
	height: 100%;
}

.icon {
	font-size: 40rpx;
	margin-bottom: 4rpx;
}

.label {
	font-size: 24rpx;
	color: #999;
	transition: color 0.3s;
}

.tab-item.active .label {
	color: #07c160;
	font-weight: 500;
}
</style>
