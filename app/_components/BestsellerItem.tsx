import Image from "next/image";
import Link from "next/link";
import { Product } from "../_types/types";

interface BestsellerItemProps {
  product: Product;
}

function BestsellerItem({ product }: BestsellerItemProps) {
  const {
    id,
    product_name: name,
    brand,
    regular_price: regularPrice,
    discount,
    image,
  } = product;

  return (
    <Link
      href={`/products/${id}`}
      className="w-96 lg:h-full lg:w-full lg:p-2 xl:p-4"
    >
      <div className="flex cursor-pointer flex-col gap-4 rounded-md bg-gray-200/90 py-4 shadow-sm transition-all duration-200 will-change-transform hover:scale-[1.02] dark:border-gray-600 dark:bg-gray-800">
        <div className="flex w-full items-center justify-center">
          <Image
            src={image}
            alt={name}
            width={192}
            height={192}
            className="w-1/2 rounded-md shadow-md dark:grayscale-[10%]"
            quality={50}
          />
        </div>
        <div className="flex flex-col items-center justify-center">
          <h3 className="text-center font-bold text-gray-700 dark:text-gray-300 md:mt-2 lg:mt-0 2xl:text-xl">
            {`${brand} ${name}`}
          </h3>
          {discount ? (
            <>
              <div className="flex gap-2 font-semibold xl:text-xl 2xl:gap-3">
                <span className="italic text-gray-600 line-through">
                  ${regularPrice}
                </span>
                <span className="text-red-600 dark:text-red-700">
                  ${regularPrice - Number(discount)}
                </span>
              </div>
            </>
          ) : (
            <span className="font-semibold xl:text-xl">
              ${regularPrice - Number(discount)}
            </span>
          )}
        </div>
      </div>
    </Link>
  );
}

export default BestsellerItem;
