import { useEffect, useState } from 'react'
import { Order } from '../orders/types'
import { fetchOrders } from '../api/client'

export function useOrders() {
  const [orders, setOrders] = useState<Order[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    setLoading(true)
    fetchOrders()
      .then((data) => {
        setOrders(data || [])
        setLoading(false)
      })
      .catch(() => {})
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  async function refresh() {
    const data = await fetchOrders()
    setOrders(data)
  }

  return { orders, loading, error, refresh }
}
