"use client";

import toast from "react-hot-toast";
import { Product } from "../_types/types";
import Button from "./Button";
import { useCart } from "./CartContext";
import { MdOutlineAddShoppingCart } from "react-icons/md";
import { RefObject } from "react";

function AddToCartButton({
  product,
  disabled,
  ref,
}: {
  product: Product;
  disabled: boolean;
  ref?: RefObject<HTMLButtonElement | null>;
}) {
  const { setCart } = useCart();

  function handleAddToCart() {
    if (disabled) return;

    const cartProductItem = { ...product, quantity: 1 };
    let added: boolean = false;

    setCart((state) => {
      const alreadyInCart = state.find(
        (prod) => prod.id === cartProductItem.id,
      );

      if (alreadyInCart && product.availability >= alreadyInCart.quantity + 1) {
        added = true;
        return [
          ...state.filter((prod) => prod.id !== product.id),
          { ...cartProductItem, quantity: alreadyInCart.quantity + 1 },
        ];
      } else if (
        alreadyInCart &&
        product.availability < alreadyInCart.quantity + 1
      ) {
        return [...state];
      } else {
        added = true;
        return [...state, cartProductItem];
      }
    });

    if (added) toast.success(`${product.product_name} added to cart`);
  }

  return (
    <Button
      disabled={disabled}
      type="primary"
      onClick={handleAddToCart}
      ref={ref}
    >
      <MdOutlineAddShoppingCart />
      Add to cart
    </Button>
  );
}

export default AddToCartButton;
