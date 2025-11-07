import { MAX_PRICE } from "../_lib/constants";
import { FiltersType } from "../_types/types";
import FiltersItem from "./FiltersItem";
import PriceFilter from "./PriceFilter";

interface FiltersProps {
  filtersState: FiltersType;
  filters: FiltersType;
  handleFilters: (filterItem: string) => void;
  handlePriceFilter: (price: { min: number; max: number }) => void;
}

function Filters({
  filtersState,
  filters,
  handleFilters,
  handlePriceFilter,
}: FiltersProps) {
  const { categories, brands } = filters;

  return (
    <div className="flex h-full flex-col gap-4 overflow-auto pb-8 lg:overflow-visible">
      <div className="flex flex-col gap-2">
        <label
          htmlFor="brand"
          className="text-lg font-semibold text-gray-600 dark:text-gray-300"
        >
          Brand
        </label>
        <div className="flex w-full flex-col items-center gap-1 px-2 lg:items-start">
          {brands?.map((brand) => (
            <FiltersItem
              filterItem={brand}
              key={brand}
              filters={filtersState}
              handleFilters={handleFilters}
            />
          ))}
        </div>
      </div>
      <div className="flex flex-col gap-2">
        <label
          htmlFor="category"
          className="text-lg font-semibold text-gray-600 dark:text-gray-300"
        >
          Category
        </label>
        <div className="flex w-full flex-col items-center gap-1 px-2 lg:items-start">
          {categories?.map((cat) => (
            <FiltersItem
              filterItem={cat}
              key={cat}
              filters={filtersState}
              handleFilters={handleFilters}
            />
          ))}
        </div>
      </div>
      <div className="flex flex-col gap-2">
        <label
          htmlFor="price"
          className="text-lg font-semibold text-gray-600 dark:text-gray-300"
        >
          Price
        </label>
        <div className="flex w-full flex-col items-center gap-1 px-2 lg:items-start">
          <PriceFilter
            price={
              filtersState["price"]
                ? filtersState.price
                : { min: 0, max: MAX_PRICE }
            }
            handleFilters={handlePriceFilter}
          />
        </div>
      </div>
    </div>
  );
}

export default Filters;
