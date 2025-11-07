"use client";

import { usePathname, useRouter, useSearchParams } from "next/navigation";
import { ChangeEvent, useEffect, useState } from "react";
import { HiSearch } from "react-icons/hi";
import { useDebounce } from "../_hooks/useDebounce";

function SearchField() {
  const params = useSearchParams();
  const [searchValue, setSearchValue] = useState<string>(
    () => params.get("search") ?? "",
  );
  const router = useRouter();
  const pathname = usePathname();

  const debouncedSearchValue = useDebounce(searchValue.trimEnd());

  function onChange(e: ChangeEvent<HTMLInputElement>) {
    setSearchValue(e.target.value);
  }

  useEffect(() => {
    if (debouncedSearchValue.length > 0) {
      const searchParams = new URLSearchParams(window.location.search);
      searchParams.set("search", debouncedSearchValue);
      router.replace(`${pathname}?${searchParams.toString()}`, {
        scroll: false,
      });
    } else {
      const searchParams = new URLSearchParams(window.location.search);
      searchParams.delete("search");
      router.replace(`${pathname}?${searchParams.toString()}`, {
        scroll: false,
      });
    }
  }, [debouncedSearchValue, pathname, router]);

  return (
    <div className="mt-8 flex w-full justify-center">
      <div className="relative flex h-10 w-full items-center justify-center">
        <input
          type="text"
          className="h-10 w-full rounded-md border-2 bg-gray-100 px-4 pl-10 text-gray-600 transition-colors duration-200 placeholder:italic focus:border-red-700 focus:outline-none dark:border-gray-700 dark:bg-[#0e131f] dark:text-gray-300 dark:shadow-md focus:dark:border-red-800"
          placeholder="Search for products..."
          onChange={onChange}
          value={searchValue}
        />
        <div className="absolute left-4 text-gray-500">
          <HiSearch />
        </div>
      </div>
    </div>
  );
}

export default SearchField;
