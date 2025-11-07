import { Product } from "../_types/types";
import ProductItem from "./ProductItem";

function ProductsList({ products }: { products: Product[] }) {
  return (
    <ul className="flex w-full flex-col gap-4 lg:w-3/4">
      {products.map((product) => (
        <ProductItem key={product.id} product={product} />
      ))}
    </ul>
  );
}

export default ProductsList;
