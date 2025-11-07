import { getBestsellers, getProductsByCategory } from "./_lib/data_service";
import { sortByDiscount, removeRepeatingProducts } from "./_lib/helpers";
import Hero from "./_components/Hero";
import Bestsellers from "./_components/Bestsellers";
import FeaturedCategoryProduct from "./_components/FeaturedCategoryProduct";

export default async function Page() {
  const bestsellers = await getBestsellers();
  const sortedBestsellers = sortByDiscount(bestsellers);

  const gaming = await getProductsByCategory("gaming");
  const sortedGaming = removeRepeatingProducts(
    sortByDiscount(gaming),
    sortedBestsellers,
  );

  const mobile = await getProductsByCategory("mobile device");
  const sortedMobile = removeRepeatingProducts(
    sortByDiscount(mobile),
    sortedBestsellers,
  );

  return (
    <>
      <section className="mb-4 2xl:mb-8">
        <Hero />
      </section>
      <section className="mx-auto mb-4 max-w-[600px] md:max-w-[800px] lg:max-w-[1600px] 2xl:mb-8">
        <Bestsellers products={sortedBestsellers.slice(0, 4)} />
      </section>
      <section className="mb-4 2xl:mb-8">
        <section className="mx-auto grid max-w-[1800px] place-items-center gap-8 px-4 lg:grid-cols-2">
          <FeaturedCategoryProduct product={sortedGaming[0]} />
          <FeaturedCategoryProduct product={sortedMobile[0]} />
        </section>
      </section>
    </>
  );
}
