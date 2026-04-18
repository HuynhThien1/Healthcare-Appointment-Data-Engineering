export const DAYS = [1, 2, 3, 4, 5, 6] as const;

export const DAY_LABEL = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat"] as const;

export type DayOfWeek = typeof DAYS[number];