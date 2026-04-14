export const SLOT_MAP = {
  "8A": "08:00 - 08:30",
  "8B": "08:30 - 09:00",
  "9A": "09:00 - 09:30",
  "9B": "09:30 - 10:00",
  "10A": "10:00 - 10:30",
  "10B": "10:30 - 11:00",
  "11A": "11:00 - 11:30",
  "11B": "11:30 - 12:00",
  "13A": "13:00 - 13:30",
  "13B": "13:30 - 14:00",
  "14A": "14:00 - 14:30",
  "14B": "14:30 - 15:00",
  "15A": "15:00 - 15:30",
  "15B": "15:30 - 16:00",
  "16A": "16:00 - 16:30",
  "16B": "16:30 - 17:00",
} as const;

// 🔥 type-safe key
export type SlotCode = keyof typeof SLOT_MAP;

// 🔥 type-safe value
export type SlotTime = (typeof SLOT_MAP)[SlotCode];