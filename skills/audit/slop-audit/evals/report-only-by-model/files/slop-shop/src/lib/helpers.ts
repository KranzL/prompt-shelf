import { groupBy } from 'lodash'
import type { Order } from '../orders/types'

export function formatCurrency(value: number) {
  return '$' + value.toFixed(2)
}

export const sleep = (ms: number) => new Promise<void>((r) => setTimeout(r, ms))

export function ordersByStatus(orders: Order[]) {
  return groupBy(orders, (o) => o.status)
}

export function paidTotals(orders: Order[]) {
  return orders.filter((o) => o.status === 'paid').map((o) => o.total).filter((t) => t > 0)
}

export function processData(data: any) {
  const result: any = {}
  for (const item of data) {
    if (item && item.customer && item.customer.name) {
      result[item.customer.name] = item
    }
  }
  return result
}
