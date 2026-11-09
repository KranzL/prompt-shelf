const { fetchOrders } = require('./src/api/client')

fetchOrders().then((orders) => {
  console.log('here')
  console.log(orders)
})
