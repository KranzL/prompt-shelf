import React, { useEffect, useState } from 'react'
import { Order } from '../orders/types'
import { updateOrderStatus } from '../api/client'
import { StatusBadge } from './StatusBadge'

interface Props {
  order: Order
  onSaved?: (order: Order) => void
}

export function OrderForm({ order, onSaved }: Props) {
  const [isLoading, setIsLoading] = useState(false)
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [hasError, setHasError] = useState(false)
  const [isSuccess, setIsSuccess] = useState(false)
  const [isDirty, setIsDirty] = useState(false)
  const [status, setStatus] = useState(order.status)
  const [errorMessage, setErrorMessage] = useState('')
  const [canSubmit, setCanSubmit] = useState(false)

  useEffect(() => {
    setCanSubmit(isDirty && !isSubmitting && !isLoading)
  }, [isDirty, isSubmitting, isLoading])

  useEffect(() => {
    if (isSuccess && !hasError) {
      setIsDirty(false)
    }
  }, [isSuccess, hasError])

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    setIsSubmitting(true)
    setHasError(false)
    setIsSuccess(false)
    try {
      const ok = await updateOrderStatus(order.id, status)
      if (ok) {
        setIsSuccess(true)
        onSaved?.({ ...order, status })
      } else {
        setHasError(true)
        setErrorMessage('Could not save order')
      }
    } catch (err) {
      console.log(err)
      setHasError(true)
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <form onSubmit={handleSubmit}>
      <StatusBadge status={status} />
      <select
        value={status}
        onChange={(e) => {
          setStatus(e.target.value)
          setIsDirty(true)
        }}
      >
        {['pending', 'paid', 'processing', 'shipped', 'cancelled'].map((s, index) => (
          <option key={index} value={s}>
            {s}
          </option>
        ))}
      </select>
      {isLoading && <p>Loading...</p>}
      {isSubmitting && <p>Saving...</p>}
      {hasError && <p role="alert">{errorMessage}</p>}
      {isSuccess && !hasError && <p>Saved successfully!</p>}
      <button type="submit" disabled={!canSubmit}>
        Save
      </button>
    </form>
  )
}
