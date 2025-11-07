import { Product, ProductWithDiscount } from "../_types/types";

export function sortByDiscount(
  products: Product[],
): ProductWithDiscount[] | [] {
  if (!products.length) return [];

  const productsWithDiscount = products.map((prod) => {
    return {
      ...prod,
      discountPercent: Math.round(
        (Number(prod.discount) / prod.regular_price) * 100,
      ),
    };
  });

  return productsWithDiscount.sort(
    (a, b) => b.discountPercent - a.discountPercent,
  );
}

export function removeRepeatingProducts(
  category: ProductWithDiscount[],
  bestsellers: ProductWithDiscount[],
): ProductWithDiscount[] | [] {
  if (!category || !bestsellers) return [];

  return category
    .map((product) => {
      const isBestseller = Boolean(
        bestsellers.find((bestseller) => bestseller.id === product.id),
      );
      if (isBestseller) return null;
      return product;
    })
    .filter((product) => product !== null);
}

export function getFromLocalStorage(key: string) {
  if (typeof window !== "undefined") {
    const item = localStorage.getItem(key);
    if (item) return item;
  }
}

export function setToLocalStorage<T>(key: string, value: T) {
  if (typeof window !== "undefined") {
    localStorage.setItem(key, JSON.stringify(value));
  }
}
