/**
 * 生命计算工具函数
 * 提供生命进度和年龄相关的计算功能
 */

/**
 * 计算生命进度百分比
 * @param birthday - 出生日期字符串 (格式: YYYY-MM-DD)
 * @param lifespan - 百岁目标（年）
 * @returns 生命进度百分比 (0-100)
 */
export function calculateLifeProgress(
  birthday: string,
  lifespan: number,
): number {
  // 如果没有生日或百岁目标为0，返回0
  if (!birthday || !lifespan) {
    return 0;
  }

  const birthDate = new Date(birthday);
  const today = new Date();
  const ageInMs = today.getTime() - birthDate.getTime();
  const expectedLifespanInMs = lifespan * 365.25 * 24 * 60 * 60 * 1000;
  return Math.min(100, Math.max(0, (ageInMs / expectedLifespanInMs) * 100));
}
