"use client";

import Button from "@/app/_components/Button";

function Error() {
  return (
    <div className="flex flex-col gap-6 py-24">
      <h1 className="text-center text-4xl font-bold uppercase tracking-wider text-red-600 sm:text-5xl">
        Ooops...
      </h1>
      <p className="text-center text-xl text-gray-700 sm:text-2xl">
        We couldn&apos;t find the product you were looking for.
      </p>
      <div className="flex justify-center">
        <Button type="primary" link="/products">
          GO TO PRODUCTS
        </Button>
      </div>
    </div>
  );
}

export default Error;
