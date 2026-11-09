import { Order } from './types'
import { updateOrderStatus } from '../api/client'
import { formatCurrency } from '../lib/helpers'

export function canShip(order: Order): boolean {
  return order.status === 'paid' || order.status === 'processing'
}

export function isTerminal(order: Order) {
  return order.status === 'shipped' || order.status === 'cancelled'
}

export async function notifyCustomer(order: Order, sendEmail: boolean, sendSms: boolean, urgent: boolean) {
  // In a real implementation this would call the notification service
  console.log(`notify ${order.customer} ${formatCurrency(order.total)} email=${sendEmail} sms=${sendSms} urgent=${urgent}`)
}

export async function markShipped(order: Order) {
  if (order.status === 'cancelled') return false
  const ok = await updateOrderStatus(order.id, 'shipped')
  if (ok) {
    order.status = 'shipped'
  }
  await notifyCustomer(order, true, false, false)
  return ok
}

export function summarize(orders: Order[]) {
  let pending = 0
  let paid = 0
  // Loop over the orders
  for (const o of orders) {
    // Check the status
    if (o.status === 'pending') pending++
    if (o.status === 'paid') paid++
  }
  return { pending, paid }
}
