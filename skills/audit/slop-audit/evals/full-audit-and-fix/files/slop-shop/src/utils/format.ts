// ==================== Formatting helpers ====================

// Format a number as currency
export function formatCurrency(amount: number): string {
  // Return the formatted string
  return `$${amount.toFixed(2)}`
}

// Sleep for the given number of milliseconds
export function sleep(ms: number): Promise<void> {
  return new Promise((resolve) => setTimeout(resolve, ms))
}

// Capitalize the first letter of a string
export function capitalize(s: string): string {
  return s.charAt(0).toUpperCase() + s.slice(1)
}
