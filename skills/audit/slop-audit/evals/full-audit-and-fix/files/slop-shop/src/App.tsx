import { useOrders } from './hooks/useOrders'
import { OrderForm } from './components/OrderForm'
import { summarize } from './orders/service'
import { formatCurrency } from './utils/format'

export function App() {
  const { orders, loading, refresh } = useOrders()
  const totals = summarize(orders)
  if (loading) return <p>Loading orders...</p>
  return (
    <main>
      <h1>Orders</h1>
      <p>
        {totals.pending} pending, {totals.paid} paid
      </p>
      <ul>
        {orders.map((o) => (
          <li key={o.id}>
            {o.customer}: {formatCurrency(o.total)}
            <OrderForm order={o} onSaved={refresh} />
          </li>
        ))}
      </ul>
    </main>
  )
}
