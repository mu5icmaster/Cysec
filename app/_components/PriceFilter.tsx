import { Slider } from "@/app/_components/Slider";
import { MAX_PRICE } from "../_lib/constants";

interface PriceFilterProps {
  price: {
    min: number;
    max: number;
  };
  handleFilters: (price: { min: number; max: number }) => void;
}

function PriceFilter({ price, handleFilters }: PriceFilterProps) {
  return (
    <div className="flex w-full flex-col gap-4">
      <div className="flex w-full flex-col gap-1">
        <label htmlFor="min" className="text-gray-700 dark:text-gray-300">
          Minimum price
        </label>
        <p className="font-semibold text-gray-600 dark:text-gray-300">
          {price.min}$
        </p>
        <Slider
          defaultValue={[0]}
          step={50}
          max={MAX_PRICE}
          value={[price.min]}
          onValueChange={(val) => {
            if (val[0] > price.max) return;

            handleFilters({ min: val[0], max: price.max });
          }}
        />
      </div>
      <div className="flex w-full flex-col gap-1">
        <label htmlFor="max" className="text-gray-700 dark:text-gray-300">
          Maximum price
        </label>
        <p className="font-semibold text-gray-600 dark:text-gray-300">
          {price.max}$
        </p>
        <Slider
          defaultValue={[MAX_PRICE]}
          step={50}
          min={10}
          max={MAX_PRICE}
          value={[price.max]}
          onValueChange={(val) => {
            if (val[0] < price.min) return;
            handleFilters({ min: price.min, max: val[0] });
          }}
        />
      </div>
    </div>
  );
}

export default PriceFilter;
