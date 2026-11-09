export interface OrderItem {
  sku: string
  qty: number
  price: number
}

export interface Order {
  id: string
  customer: string
  total: number
  status: string
  items: OrderItem[]
  note?: string
}
