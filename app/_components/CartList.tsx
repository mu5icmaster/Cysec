"use client";

import Image from "next/image";
import { CartProduct } from "../_types/types";
import Button from "./Button";
import { useCart } from "./CartContext";

function CartList() {
  const { cart, setCart } = useCart();

  function handleRemoveItem(productId: number) {
    setCart(() => cart.filter((product) => product.id !== productId));
  }

  return (
    <div className="flex w-full flex-col gap-4 p-4 md:mt-4 md:w-auto md:gap-4">
      {cart.length > 0 &&
        cart.map((prod) => (
          <CartItem
            handleRemove={handleRemoveItem}
            product={prod}
            setCart={setCart}
            key={prod.id}
          />
        ))}
      {cart.length === 0 && (
        <p className="text-center text-2xl leading-6 text-gray-800 dark:text-gray-300">
          The cart is empty :(
        </p>
      )}
    </div>
  );
}

function CartItem({
  product,
  handleRemove,
  setCart,
}: {
  product: CartProduct;
  handleRemove: (productId: number) => void;
  setCart(callback: (prevCart: CartProduct[]) => CartProduct[]): void;
}) {
  const {
    id,
    product_name: name,
    brand,
    regular_price: regularPrice,
    final_price: finalPrice,
    discount,
    image,
    quantity,
  } = product;

  function handleIncreaseQuantity() {
    setCart((cart) => {
      const increasedCart = cart.map((prod) => {
        if (prod.id !== id || prod.availability < prod.quantity + 1)
          return prod;
        return { ...prod, quantity: prod.quantity + 1 };
      });
      return increasedCart;
    });
  }

  function handleDecreaseQuantity() {
    setCart((cart) => {
      const decreasedCart = cart.map((prod) => {
        if (prod.id !== id) return prod;
        return {
          ...prod,
          quantity: prod.quantity === 1 ? prod.quantity : prod.quantity - 1,
        };
      });
      return decreasedCart;
    });
  }

  return (
    <div className="relative grid h-auto max-w-5xl grid-cols-[8rem_3fr] items-center justify-center gap-2 rounded-lg border-2 px-2 py-2 dark:border-gray-600 md:gap-4 md:px-4 lg:h-auto">
      <Image
        src={image}
        alt={name}
        height={96}
        width={96}
        className="w-20 self-center justify-self-center rounded-md shadow-sm dark:grayscale-[30%]"
      />
      <div>
        <p className="font-semibold text-gray-700 dark:text-gray-300 md:text-lg">
          {`${brand} ${name}`}
        </p>
        <div className="flex flex-col gap-2 text-gray-700 dark:text-gray-600 sm:flex-row sm:items-center">
          <div className="flex gap-2">
            <button
              onClick={() => handleDecreaseQuantity()}
              className="flex items-center justify-center font-bold"
            >
              -
            </button>
            <input
              type="number"
              className="mt-1 h-6 w-6 rounded-lg px-1 py-0.5 text-center font-semibold text-gray-700 focus:outline-none dark:bg-gray-700 dark:text-gray-300"
              value={quantity}
              readOnly
            />
            <button
              onClick={() => handleIncreaseQuantity()}
              className="flex items-center justify-center font-bold"
            >
              +
            </button>
          </div>
          {discount ? (
            <>
              <div className="flex gap-2">
                <p className="ml-2 italic line-through">
                  ${regularPrice * quantity}
                </p>
                <span className="text-red-600 dark:text-red-700">
                  ${finalPrice * quantity}
                </span>
              </div>
            </>
          ) : (
            <p className="ml-2">${regularPrice * quantity}</p>
          )}
        </div>
        <button
          onClick={() => handleRemove(id)}
          className="absolute right-2 top-0 text-2xl text-gray-700"
        >
          &times;
        </button>
        <div className="bottom-2 right-2 lg:absolute">
          <Button type="secondary" link={`/products/${id}`}>
            Go to product
          </Button>
        </div>
      </div>
    </div>
  );
}

export default CartList;
