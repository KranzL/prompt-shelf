// Kept for backwards compatibility with the old import paths
import { fetchOrders, updateOrderStatus } from './api/client'

export const getOrders = fetchOrders
export const setOrderStatus = updateOrderStatus
export * from './api/client'
