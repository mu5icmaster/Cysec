import { Checkbox } from "./Checkbox";
import { FiltersType } from "../_types/types";

function FiltersItem({
  filterItem,
  filters,
  handleFilters,
}: {
  filterItem: string;
  filters: FiltersType;
  handleFilters: (filterItem: string) => void;
}) {
  const isChecked =
    filters.categories?.includes(filterItem) ||
    filters.brands?.includes(filterItem);

  return (
    <div
      className="grid w-full grid-cols-[auto_1fr] items-center gap-4"
      key={filterItem}
    >
      <Checkbox
        id={filterItem}
        name="filter"
        checked={Boolean(isChecked)}
        onCheckedChange={() => handleFilters(filterItem)}
      />
      <label
        htmlFor={filterItem}
        className="cursor-pointer text-left text-lg text-gray-700 dark:text-gray-300"
      >{`${filterItem.length > 3 ? filterItem[0].toUpperCase() + filterItem.slice(1) : filterItem.toUpperCase()}`}</label>
    </div>
  );
}

export default FiltersItem;
