import { useState, useEffect, useCallback, type RefObject } from 'react'

/**
 * 检测元素内容是否被截断
 * @param ref - 要检测的元素引用
 * @returns 是否被截断
 */
export function useIsTruncated(ref: RefObject<HTMLElement | null>): boolean {
  const [isTruncated, setIsTruncated] = useState(false)

  const checkTruncation = useCallback(() => {
    if (ref.current) {
      const { scrollWidth, clientWidth } = ref.current
      setIsTruncated(scrollWidth > clientWidth)
    }
  }, [ref])

  useEffect(() => {
    checkTruncation()
    // 监听窗口变化重新检测
    window.addEventListener('resize', checkTruncation)
    return () => window.removeEventListener('resize', checkTruncation)
  }, [checkTruncation])

  return isTruncated
}
