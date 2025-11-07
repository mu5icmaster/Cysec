"use client";

import { usePathname, useRouter, useSearchParams } from "next/navigation";
import { useEffect, useState } from "react";
import { IoClose } from "react-icons/io5";
import { useDebounce } from "../_hooks/useDebounce";
import { MAX_PRICE } from "../_lib/constants";
import { FiltersType } from "../_types/types";
import Filters from "./Filters";
import { useFilterMenu } from "./FiltersContext";

interface FiltersProps {
  filters: FiltersType;
}

function FiltersSection({ filters }: FiltersProps) {
  const { brands, categories } = filters;
  const searchParams = useSearchParams();
  const categorySearchParams =
    searchParams
      .get("category")
      ?.split(",")
      .filter((fil) => fil != "") ?? [];
  const brandSearchParams =
    searchParams
      .get("brand")
      ?.split(",")
      .filter((fil) => fil != "") ?? [];
  const minPriceSearchParams = Number(searchParams.get("min"));
  const maxPriceSearchParams =
    Number(searchParams.get("max")) === 0
      ? MAX_PRICE
      : Number(searchParams.get("max"));

  const router = useRouter();
  const pathname = usePathname();
  const [filtersState, setFilters] = useState<FiltersType>({
    categories: categorySearchParams,
    brands: brandSearchParams,
    price: {
      min:
        minPriceSearchParams > maxPriceSearchParams ? 0 : minPriceSearchParams,
      max:
        maxPriceSearchParams < minPriceSearchParams
          ? MAX_PRICE
          : maxPriceSearchParams,
    },
  });
  const debouncedFilters = useDebounce(filtersState, 500);

  const { isOpen: isMobileFiltersOpen, close } = useFilterMenu();

  function handleFilters(filterItem: string) {
    if (brands?.includes(filterItem)) {
      if (filtersState.brands?.includes(filterItem)) {
        setFilters((filters) => {
          return {
            ...filters,
            brands: filtersState["brands"]
              ? [...filtersState.brands?.filter((fil) => fil !== filterItem)]
              : [],
          };
        });
      } else
        setFilters((filters) => {
          return {
            ...filters,
            brands: filtersState["brands"]
              ? [...filtersState.brands, filterItem]
              : [],
          };
        });
    }

    if (categories?.includes(filterItem)) {
      if (filtersState.categories?.includes(filterItem)) {
        setFilters((filters) => {
          return {
            ...filters,
            categories: filtersState["categories"]
              ? [
                  ...filtersState.categories?.filter(
                    (fil) => fil !== filterItem,
                  ),
                ]
              : [],
          };
        });
      } else
        setFilters((filters) => {
          return {
            ...filters,
            categories: filtersState["categories"]
              ? [...filtersState.categories, filterItem]
              : [],
          };
        });
    }
  }

  function handlePriceFilter(price: { min: number; max: number }) {
    setFilters((filters) => {
      return { ...filters, price };
    });
  }

  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    if (
      debouncedFilters["categories"] &&
      debouncedFilters.categories.length > 0
    ) {
      params.set("category", [...debouncedFilters.categories].toString());
      router.replace(`${pathname}?${params.toString()}`, { scroll: false });
    }
    if (
      !debouncedFilters["categories"] ||
      debouncedFilters.categories.length === 0
    ) {
      params.delete("category");
      router.replace(`${pathname}?${params.toString()}`, { scroll: false });
    }

    if (debouncedFilters["brands"] && debouncedFilters.brands.length > 0) {
      params.set("brand", [...debouncedFilters.brands].toString());
      router.replace(`${pathname}?${params.toString()}`, { scroll: false });
    }
    if (!debouncedFilters["brands"] || debouncedFilters.brands.length === 0) {
      params.delete("brand");
      router.replace(`${pathname}?${params.toString()}`, { scroll: false });
    }

    // min price
    if (debouncedFilters["price"] && debouncedFilters.price.min !== 0) {
      params.set("min", debouncedFilters.price.min.toString());
      router.replace(`${pathname}?${params.toString()}`, { scroll: false });
    }
    if (!debouncedFilters["price"] || debouncedFilters.price.min === 0) {
      params.delete("min");
      router.replace(`${pathname}?${params.toString()}`, { scroll: false });
    }

    // max price
    if (debouncedFilters["price"] && debouncedFilters.price.max !== 0) {
      params.set("max", debouncedFilters.price.max.toString());
      router.replace(`${pathname}?${params.toString()}`, { scroll: false });
    }
    if (
      !debouncedFilters["price"] ||
      debouncedFilters.price.max === MAX_PRICE
    ) {
      params.delete("max");
      router.replace(`${pathname}?${params.toString()}`, { scroll: false });
    }
  }, [debouncedFilters, router, pathname]);

  return (
    <>
      {/* MOBILE */}
      <section
        className={`fixed p-8 lg:hidden ${isMobileFiltersOpen ? "translate-x-0" : "-translate-x-[999px]"} left-0 top-0 z-[51] h-screen w-3/4 -translate-x-[999px] bg-gray-50 shadow-md backdrop-blur-lg transition-all duration-150 dark:bg-[#0e131f] md:w-1/2`}
      >
        <div className="mb-4 flex justify-between">
          <h2 className="text-2xl font-semibold text-gray-700 dark:text-gray-300">
            Filters
          </h2>
          <button
            className="flex items-center justify-center text-3xl text-gray-700 dark:text-gray-300"
            onClick={close}
          >
            <IoClose />
          </button>
        </div>
        <Filters
          filtersState={filtersState}
          filters={filters}
          handleFilters={handleFilters}
          handlePriceFilter={handlePriceFilter}
        />
      </section>

      {/* DESKTOP */}
      <section className="hidden w-full flex-col items-center justify-self-stretch rounded-md border-2 p-2 px-6 dark:border-gray-700 md:w-3/4 lg:block lg:w-2/6 lg:self-stretch lg:p-6">
        <Filters
          filtersState={filtersState}
          filters={filters}
          handleFilters={handleFilters}
          handlePriceFilter={handlePriceFilter}
        />
      </section>
    </>
  );
}

export default FiltersSection;
