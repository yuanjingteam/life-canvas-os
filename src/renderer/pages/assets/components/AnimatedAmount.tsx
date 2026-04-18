import React, { useEffect, useState, useRef } from 'react'
import { motion, AnimatePresence } from 'framer-motion'

interface AnimatedAmountProps {
  amount: string
  className?: string
}

export function AnimatedAmount({ amount, className }: AnimatedAmountProps) {
  // 解析金额字符串 (去掉 ¥, 逗号等)
  const numericValue = parseFloat(amount.replace(/[^\d.-]/g, '')) || 0
  const [displayValue, setDisplayValue] = useState(numericValue)
  const prevValueRef = useRef(numericValue)

  useEffect(() => {
    const startValue = prevValueRef.current
    const endValue = numericValue
    
    if (startValue === endValue) return

    let startTime: number | null = null
    const duration = 800 // 800ms

    const step = (timestamp: number) => {
      if (!startTime) startTime = timestamp
      const progress = Math.min((timestamp - startTime) / duration, 1)
      const current = startValue + (endValue - startValue) * progress
      setDisplayValue(current)
      
      if (progress < 1) {
        requestAnimationFrame(step)
      } else {
        prevValueRef.current = endValue
      }
    }

    requestAnimationFrame(step)
  }, [numericValue])

  const formatted = new Intl.NumberFormat('zh-CN', {
    style: 'currency',
    currency: 'CNY',
    minimumFractionDigits: 2,
  }).format(displayValue)

  return (
    <span className={className}>
      {formatted}
    </span>
  )
}
