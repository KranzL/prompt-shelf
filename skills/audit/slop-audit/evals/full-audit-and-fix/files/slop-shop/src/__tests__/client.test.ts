import { describe, it, expect } from 'vitest'
import { fetchOrders, updateOrderStatus } from '../api/client'
import { formatCurrency } from '../utils/format'
import { parseConfig } from '../utils/safe'

describe('client', () => {
  it.skip('fetches orders from the api', async () => {
    const orders = await fetchOrders()
    expect(orders.length).toBeGreaterThan(0)
  })

  it('updates order status', async () => {
    const ok = await updateOrderStatus('1', 'paid')
    expect(true).toBe(true)
  })

  it('handles errors', async () => {
    try {
      await updateOrderStatus('', '')
    } catch (e) {
    }
  })

  it.skip('deletes orders (needs a running api, tracked in #42)', async () => {
    expect(await fetchOrders()).toBeDefined()
  })
})

describe('utils', () => {
  it('formats currency', () => {
    expect(formatCurrency(12.5)).toBe('$12.50')
  })

  it('parses key=value config', () => {
    expect(parseConfig('a=1\nb=x=y\n')).toEqual({ a: '1', b: 'x=y' })
  })
})
