"use client";

import { usePathname, useRouter, useSearchParams } from "next/navigation";
import { useEffect, useState } from "react";

function Sort() {
  const searchParams = useSearchParams();
  const sortParams = searchParams.get("sort");
  const router = useRouter();
  const pathname = usePathname();
  const [sortBy, setSortBy] = useState<"relevant" | "highest" | "lowest">(
    () => {
      if (sortParams === "highest") return "highest";
      if (sortParams === "lowest") return "lowest";
      else return "relevant";
    },
  );

  useEffect(() => {
    const params = new URLSearchParams(window.location.search);

    if (sortBy === "relevant") {
      params.delete("sort");
      router.push(`${pathname}?${params.toString()}`);
    } else {
      params.set("sort", sortBy);
      router.push(`${pathname}?${params.toString()}`);
    }
  }, [sortBy, router, pathname]);

  return (
    <div>
      <p className="font-semibold text-gray-700 dark:text-gray-300">Sort by</p>
      <select
        className="rounded-md border-2 p-2 text-gray-700 transition-all duration-150 focus:border-red-700 focus:outline-0 dark:border-gray-700 dark:bg-gray-900 dark:text-gray-300 dark:focus:border-red-800"
        value={sortBy}
        onChange={(e) => {
          if (
            e.target.value === "relevant" ||
            e.target.value === "highest" ||
            e.target.value === "lowest"
          ) {
            setSortBy(e.target.value);
          }
        }}
      >
        <option value="relevant">Most relevant</option>
        <option value="highest">Highest price</option>
        <option value="lowest">Lowest price</option>
      </select>
    </div>
  );
}

export default Sort;
