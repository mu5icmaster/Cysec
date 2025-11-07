"use client";

import { usePathname, useRouter, useSearchParams } from "next/navigation";
import { ChangeEvent, useEffect, useState } from "react";
import { PRODUCTS_PER_PAGE } from "../_lib/constants";
import {
  Pagination,
  PaginationContent,
  PaginationItem,
  PaginationNext,
  PaginationPrevious,
} from "./Pagination";

function ClientPagination({ productsCount }: { productsCount: number }) {
  const params = useSearchParams();
  const pathname = usePathname();
  const [curPage, setCurPage] = useState(
    params.get("page") ? Number(params.get("page")) : 1,
  );
  const pageCount = Math.ceil(productsCount / PRODUCTS_PER_PAGE);
  const router = useRouter();

  function handleChange(_: ChangeEvent<unknown>, value: number) {
    const searchParams = new URLSearchParams(params);
    setCurPage(value);
    searchParams.set("page", value.toString());
    router.replace(`${pathname}?${searchParams.toString()}`);
  }

  useEffect(() => {
    if (Number(params?.get("page")) > pageCount) {
      setCurPage(1);
      const searchParams = new URLSearchParams(params);
      searchParams.set("page", String(1));
      router.replace(`${pathname}?${searchParams.toString()}`);
    }
  }, [pageCount, params, router, pathname]);

  return (
    <div className="my-2 flex justify-center">
      <Pagination>
        <PaginationContent>
          <PaginationItem>
            <button
              onClick={(e) => {
                handleChange(e, curPage - 1);
              }}
              className="disabled:opacity-50"
              disabled={curPage === 1}
            >
              <PaginationPrevious className="text-gray-800 dark:text-gray-300 dark:hover:bg-gray-800" />
            </button>
          </PaginationItem>
          <PaginationItem>
            <span className="flex h-8 w-8 cursor-default items-center justify-center rounded-full bg-gray-200/90 p-1 text-sm text-gray-600 dark:bg-gray-800 dark:text-gray-300">
              {curPage}
            </span>
          </PaginationItem>
          <PaginationItem className="text-gray-800 dark:text-gray-300">
            <button
              onClick={(e) => {
                handleChange(e, curPage + 1);
              }}
              className="disabled:opacity-50"
              disabled={curPage === pageCount}
            >
              <PaginationNext className="text-gray-800 dark:text-gray-300 dark:hover:bg-gray-800" />
            </button>
          </PaginationItem>
        </PaginationContent>
      </Pagination>
    </div>
  );
}

export default ClientPagination;
