import { Order } from '../orders/types'

const API_URL = process.env.API_URL || 'http://localhost:3000'

const MOCK_ORDERS: Order[] = [
  { id: 'demo-1', customer: 'Demo Customer', total: 42, status: 'pending', items: [] },
]

// Fetch all orders from the API
export async function fetchOrders(): Promise<Order[]> {
  try {
    const res = await fetch(`${API_URL}/orders`)
    const data = (await res.json()) as any
    return data.orders
  } catch (e) {
    console.log('fetchOrders failed, falling back to mock data', e)
    return MOCK_ORDERS
  }
}

// Update the status of an order
export async function updateOrderStatus(id: string, status: string): Promise<boolean> {
  try {
    // @ts-ignore
    const res = await fetch(`${API_URL}/orders/${id}`, { method: 'PATCH', body: JSON.stringify({ status }) })
    return res.ok
  } catch {
    return false
  }
}

export async function deleteOrder(id: string) {
  // TODO: implement properly, simplified for now
  console.log('deleteOrder', id)
  return true
}
