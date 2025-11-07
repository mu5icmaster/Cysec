import Image from "next/image";
import { ProductWithDiscount } from "../_types/types";
import Button from "./Button";

interface FeaturedCategoryProductProps {
  product: ProductWithDiscount;
}

function FeaturedCategoryProduct({ product }: FeaturedCategoryProductProps) {
  const {
    image,
    product_name: name,
    regular_price: price,
    discount,
    discountPercent,
    id,
  } = product;

  return (
    <div className="grid grid-cols-2 place-items-center justify-items-center gap-8 rounded-md bg-gray-200/90 px-4 py-4 shadow-sm dark:bg-gray-800 md:px-16">
      <Image
        src={image}
        width={350}
        height={350}
        alt={name}
        className="rounded-md shadow-sm dark:grayscale-[10%]"
        quality={60}
      />
      <div className="flex flex-col gap-1">
        <h3 className="text-center text-2xl font-bold text-gray-700 dark:text-gray-300 xl:text-3xl">
          {name}
        </h3>
        <span className="w-full text-center text-lg font-semibold text-gray-600 dark:text-gray-300 lg:text-xl">
          ${price - Number(discount)}
          {discountPercent ? ` — ${discountPercent}% off` : null}
        </span>
        <div className="flex justify-center">
          <Button type="primary" link={`/products/${id}`}>
            Buy now
          </Button>
        </div>
      </div>
    </div>
  );
}

export default FeaturedCategoryProduct;
