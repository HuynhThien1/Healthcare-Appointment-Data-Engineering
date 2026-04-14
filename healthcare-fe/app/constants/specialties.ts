export const SPECIALTIES = [
  "Tiêu hóa - Gan mật",
  "Tai Mũi Họng",
  "Da liễu",
  "Tim mạch",
  "Răng Hàm Mặt",
  "Nội tiết",
  "Thần kinh",
  "Mắt",
  "Hô hấp",
  "Chẩn đoán hình ảnh",
  "Phục hồi chức năng",
  "Y học cổ truyền",
  "Tâm lý lâm sàng",
  "Dinh dưỡng",
] as const;

// optional: type-safe
export type Specialty = (typeof SPECIALTIES)[number];