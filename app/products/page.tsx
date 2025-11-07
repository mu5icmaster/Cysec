import type { Metadata } from "next";
import { Suspense } from "react";
import ClientPagination from "../_components/ClientPagination";
import FiltersButton from "../_components/FiltersButton";
import FiltersSection from "../_components/FiltersSection";
import Loader from "../_components/Loader";
import ProductsList from "../_components/ProductsList";
import SearchField from "../_components/SearchField";
import { MAX_PRICE } from "../_lib/constants";
import { getBrands, getCategories, getProducts } from "../_lib/data_service";
import Sort from "../_components/Sort";

export const metadata: Metadata = {
  title: "Products",
};

async function Page({
  searchParams,
}: {
  searchParams: Promise<
    | {
        category: string;
        brand: string;
        min: string;
        max: string;
        search: string;
        page: string;
        sort: "highest" | "lowest" | "relevant";
      }
    | undefined
  >;
}) {
  const params = await searchParams;
  const page = params?.page ?? 1;
  const categoryFilter = params?.category
    ? params?.category?.split(",")
    : undefined;
  const brandFilter = params?.brand ? params?.brand?.split(",") : undefined;
  const priceFilter = {
    min: params?.min ? Number(params.min) : 0,
    max: params?.max ? Number(params.max) : MAX_PRICE,
  };
  const { data: products, count } = await getProducts(
    params?.search,
    Number(page),
    { categories: categoryFilter, brands: brandFilter, price: priceFilter },
    params?.sort,
  );

  const [categories, brands] = await Promise.all([
    getCategories(),
    getBrands(),
  ]);

  return (
    <div className="mx-auto max-w-[1300px] px-4">
      <SearchField />
      <div className="mt-4 flex w-full items-end justify-between lg:justify-end">
        <div className="lg:hidden">
          <FiltersButton />
        </div>
        <Sort />
      </div>
      <section className="m-auto flex h-auto max-w-[1300px] flex-col items-center gap-8 py-8 pt-4 lg:flex-row lg:items-start lg:gap-8 xl:gap-16">
        <Suspense fallback={<Loader />}>
          <FiltersSection filters={{ categories, brands }} />
        </Suspense>
        <Suspense fallback={<Loader />}>
          {products.length > 0 ? (
            <ProductsList products={products} />
          ) : (
            <div className="mt-16 flex w-full justify-center text-2xl md:w-3/4">
              <p className="text-gray-600 dark:text-gray-300">
                Unfortunately, we don&apos;t have the products you&apos;re
                looking for.
              </p>
            </div>
          )}
        </Suspense>
      </section>
      {products.length > 0 && <ClientPagination productsCount={count} />}
    </div>
  );
}

export default Page;
