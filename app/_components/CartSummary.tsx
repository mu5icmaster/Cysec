"use client";

import { useRouter } from "next/navigation";
import { useCart } from "./CartContext";
import { SHIPPING_COST } from "../_lib/constants";
import Button from "./Button";

function CartSummary() {
  const router = useRouter();

  const { cart } = useCart();

  const productsPrice = cart.reduce(
    (acc, cur) => acc + cur.regular_price * cur.quantity,
    0,
  );

  const discount = cart.reduce(
    (acc, cur) => acc + Number(cur.discount) * cur.quantity,
    0,
  );

  return (
    <>
      <h2 className="text-2xl font-bold text-gray-700 dark:text-gray-300">
        Summary
      </h2>
      <div className="my-3 flex flex-col gap-2 px-4 text-gray-500 md:my-4">
        <p>
          <span className="font-semibold">Products:</span>{" "}
          {cart.length ? `$${productsPrice}` : "—"}
        </p>
        <p>
          <span className="font-semibold">Shipping cost:</span>{" "}
          {cart.length ? `$${SHIPPING_COST}` : "—"}
        </p>
        <p>
          <span className="font-semibold">Discounts:</span>{" "}
          {cart.length ? `$${discount}` : "—"}
        </p>
        <p>
          <span className="font-semibold">Total:</span>{" "}
          {cart.length ? `$${productsPrice - discount + SHIPPING_COST}` : "—"}
        </p>
        <div className="mt-2 flex justify-center md:justify-normal">
          <Button
            type="primary"
            disabled={Boolean(!cart.length)}
            onClick={() => router.push("/cart/checkout")}
          >
            Checkout
          </Button>
        </div>
      </div>
    </>
  );
}

export default CartSummary;
