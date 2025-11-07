"use client";

import Image from "next/image";
import { Product } from "../_types/types";
import AddToCartButton from "./AddToCartButton";
import { useRouter } from "next/navigation";
import { useRef } from "react";

const productFeatures = [
  {
    category: "gaming",
    features: ["🎮 Next-gen experience", "⚡ Ultra-fast SSD loading times"],
  },
  {
    category: "mobile device",
    features: [
      "🔋 Long-lasting battery life",
      "📱 Compatible with the latest apps",
    ],
  },
  {
    category: "pc",
    features: [
      "⚡ Cutting-edge performance",
      "🎮 Optimized for gaming and creative work",
    ],
  },
];

function ProductItem({ product }: { product: Product }) {
  const {
    id,
    product_name: name,
    brand,
    image,
    availability,
    regular_price: price,
    final_price: finalPrice,
    discount,
    category,
  } = product;

  const features = productFeatures.find(
    (feat) => feat.category === category,
  )?.features;

  const router = useRouter();
  const ref = useRef<HTMLButtonElement>(null);

  return (
    <div
      onClick={(ev) => {
        if (ref.current === ev.target) return;

        router.push(`/products/${id}`);
      }}
      className="relative grid h-auto cursor-pointer grid-cols-[auto_1fr] grid-rows-[auto_1fr] items-center gap-2 gap-y-2 rounded-md border-2 p-2 transition-all duration-150 hover:border-gray-400/75 dark:border-gray-600 dark:hover:border-gray-500 sm:grid-rows-none sm:p-0 md:gap-4 md:gap-y-0"
    >
      <div className="p-2">
        <Image
          className={`h-32 w-32 rounded-md md:h-44 md:w-44 ${availability === 0 ? "opacity-50 grayscale-[100%]" : "dark:grayscale-[30%]"}`}
          src={image}
          width={176}
          height={176}
          alt={name}
          quality={50}
        />
      </div>
      <div className="flex flex-col gap-2">
        <p className="py-2 font-semibold text-gray-600 dark:text-gray-300 md:text-xl">
          {`${brand} ${name}`}
        </p>
        <ul className="flex flex-col gap-2 font-[600] text-gray-500 sm:w-64 lg:w-full">
          {!features && (
            <>
              <li className="leading-[0.98]">✅ 24-month warranty</li>
              <li className="leading-[0.98]">🚀 Express shipping</li>
            </>
          )}
          {features &&
            features.map((feat) => (
              <li className="leading-[0.98]" key={`${id}_${feat}`}>
                {feat}
              </li>
            ))}
        </ul>
      </div>
      <div className="bottom-2 right-2 col-span-2 flex flex-col justify-center gap-2 sm:absolute sm:items-center">
        {discount ? (
          <div className="flex w-full justify-center gap-2 text-xl font-semibold text-gray-500 dark:text-gray-600 sm:mr-4 sm:justify-end">
            <p className="italic line-through">${price}</p>
            <span className="text-red-600 dark:text-red-700">
              ${finalPrice}
            </span>
          </div>
        ) : (
          <span className="w-full py-2 text-center text-xl font-semibold text-gray-500 dark:text-gray-600 sm:mr-4 sm:text-right">
            {price}$
          </span>
        )}
        <AddToCartButton
          product={product}
          disabled={availability <= 0}
          ref={ref}
        />
      </div>
    </div>
  );
}

export default ProductItem;
