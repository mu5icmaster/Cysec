import type { Metadata } from "next";
import CartList from "../_components/CartList";
import CartSummary from "../_components/CartSummary";

export const metadata: Metadata = {
  title: "Cart",
};

function Page() {
  return (
    <section className="mx-auto mt-16 grid max-w-[1300px] gap-4 px-4 md:grid-cols-[1fr_20rem]">
      <div className="flex flex-col items-center md:block">
        <h2 className="text-center text-3xl font-bold text-gray-700 md:text-left md:text-4xl dark:text-gray-200">
          Cart
        </h2>
        <CartList />
      </div>
      <div className="flex flex-col items-center md:block">
        <CartSummary />
      </div>
    </section>
  );
}

export default Page;
