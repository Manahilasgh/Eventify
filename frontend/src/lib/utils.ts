export const formatDate = (date: string): string => {
  return new Intl.DateTimeFormat("en-PK", {
    day: "numeric",
    month: "long",
    year: "numeric",
  }).format(new Date(date));
};

export const formatTime = (date: string): string => {
  return new Intl.DateTimeFormat("en-PK", {
    hour: "numeric",
    minute: "2-digit",
    hour12: true,
  }).format(new Date(date));
};

export const formatPrice = (
  price: string | number
): string => {
  return new Intl.NumberFormat("en-PK", {
    style: "currency",
    currency: "PKR",
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  }).format(Number(price));
};